"""
Permutation Genetic Algorithm for the TSP (minimization).

Operators: tournament selection (k=3), order crossover (OX), swap mutation,
and elitism. Every non-elite child is mutated by exactly one swap. The skeleton
mirrors Program II's binary GA layout (initialize -> loop -> select -> cross ->
mutate -> elitism -> record), with the operators rewritten for permutation
encoding so that every individual stays a valid tour without repair.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def ga_minimize(
    fitness_fn: Callable[[np.ndarray], float],
    n: int,
    *,
    rng: np.random.Generator,
    pop_size: int = 100,
    max_iter: int = 500,
    tournament_size: int = 3,
    elitism: int = 2,
    crossover_rate: float = 0.8,
) -> tuple[np.ndarray, float, np.ndarray]:
    """Return ``(best_tour, best_fitness, history)``.

    ``history`` is a length ``max_iter + 1`` array of best-so-far fitness, with
    index 0 holding the best of the initial population.
    """
    pop = np.array([rng.permutation(n) for _ in range(pop_size)])
    fitness = np.array([fitness_fn(ind) for ind in pop])

    best_idx = int(np.argmin(fitness))
    best_tour = pop[best_idx].copy()
    best_fitness = float(fitness[best_idx])

    history = np.empty(max_iter + 1)
    history[0] = best_fitness

    for gen in range(1, max_iter + 1):
        order = np.argsort(fitness)
        new_pop = np.empty_like(pop)
        new_pop[:elitism] = pop[order[:elitism]]

        i = elitism
        while i < pop_size:
            p1 = _tournament_select(pop, fitness, tournament_size, rng)
            p2 = _tournament_select(pop, fitness, tournament_size, rng)

            if rng.random() < crossover_rate:
                c1, c2 = _order_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()

            new_pop[i] = _swap_mutate(c1, rng)
            i += 1
            if i < pop_size:
                new_pop[i] = _swap_mutate(c2, rng)
                i += 1

        pop = new_pop
        fitness = np.array([fitness_fn(ind) for ind in pop])

        gen_best = int(np.argmin(fitness))
        if fitness[gen_best] < best_fitness:
            best_fitness = float(fitness[gen_best])
            best_tour = pop[gen_best].copy()

        history[gen] = best_fitness

    return best_tour, best_fitness, history


def _tournament_select(pop, fitness, k, rng):
    indices = rng.choice(len(pop), size=k, replace=False)
    winner = indices[int(np.argmin(fitness[indices]))]
    return pop[winner].copy()


def _order_crossover(p1, p2, rng):
    """OX: keep a random segment of one parent, fill the rest from the other."""
    a, b = np.sort(rng.choice(len(p1), size=2, replace=False))
    b += 1  # half-open segment [a, b)
    return _ox_child(p1, p2, a, b), _ox_child(p2, p1, a, b)


def _ox_child(donor, filler, a, b):
    n = len(donor)
    child = np.full(n, -1, dtype=donor.dtype)
    child[a:b] = donor[a:b]
    taken = set(donor[a:b].tolist())

    fill = [city for city in np.roll(filler, -b) if city not in taken]
    positions = [(b + k) % n for k in range(n - (b - a))]
    for pos, city in zip(positions, fill):
        child[pos] = city
    return child


def _swap_mutate(ind, rng):
    out = ind.copy()
    i, j = rng.choice(len(out), size=2, replace=False)
    out[i], out[j] = out[j], out[i]
    return out
