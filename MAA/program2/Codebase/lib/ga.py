"""
Binary Genetic Algorithm for feature-subset selection (maximization).

Operators: tournament selection (k=3), uniform crossover, bit-flip mutation,
elitism. Empty masks are handled by the fitness function (returning -inf),
so selection deprioritizes them without explicit repair.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def ga_maximize(
    fitness_fn: Callable[[np.ndarray], float],
    n_features: int = 16,
    pop_size: int = 50,
    max_iter: int = 100,
    seed: int | None = None,
    tournament_size: int = 3,
    crossover_rate: float = 0.8,
    mutation_rate: float | None = None,
) -> dict:
    rng = np.random.default_rng(seed)
    if mutation_rate is None:
        mutation_rate = 1.0 / n_features

    pop = rng.integers(0, 2, size=(pop_size, n_features))
    for i in range(pop_size):
        while not pop[i].any():
            pop[i] = rng.integers(0, 2, size=n_features)

    fitness = np.array([fitness_fn(ind) for ind in pop])

    best_idx = int(np.argmax(fitness))
    best_pos = pop[best_idx].copy()
    best_val = float(fitness[best_idx])
    convergence = np.zeros(max_iter)

    for gen in range(max_iter):
        new_pop = np.empty_like(pop)
        new_pop[0] = best_pos.copy()

        i = 1
        while i < pop_size:
            p1 = _tournament_select(pop, fitness, tournament_size, rng)
            p2 = _tournament_select(pop, fitness, tournament_size, rng)

            if rng.random() < crossover_rate:
                c1, c2 = _uniform_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()

            c1 = _bitflip_mutate(c1, mutation_rate, rng)
            c2 = _bitflip_mutate(c2, mutation_rate, rng)

            new_pop[i] = c1
            i += 1
            if i < pop_size:
                new_pop[i] = c2
                i += 1

        pop = new_pop
        fitness = np.array([fitness_fn(ind) for ind in pop])

        gen_best_idx = int(np.argmax(fitness))
        if fitness[gen_best_idx] > best_val:
            best_val = float(fitness[gen_best_idx])
            best_pos = pop[gen_best_idx].copy()

        convergence[gen] = best_val

    return {
        "best_pos": best_pos,
        "best_val": best_val,
        "convergence": convergence,
        "final_pop": pop,
        "final_fitness": fitness,
    }


def _tournament_select(pop, fitness, k, rng):
    indices = rng.choice(len(pop), size=k, replace=False)
    winner = indices[int(np.argmax(fitness[indices]))]
    return pop[winner].copy()


def _uniform_crossover(p1, p2, rng):
    swap = rng.random(len(p1)) < 0.5
    c1 = np.where(swap, p2, p1).copy()
    c2 = np.where(swap, p1, p2).copy()
    return c1, c2


def _bitflip_mutate(ind, rate, rng):
    flip = rng.random(len(ind)) < rate
    return (ind ^ flip.astype(ind.dtype)).copy()
