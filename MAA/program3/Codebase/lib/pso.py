"""
Random-keys Particle Swarm Optimization for the TSP (minimization).

Each particle holds a continuous position in ``[0, 1]^n``; the permutation it
represents is recovered by ``argsort`` just before fitness evaluation. Velocity
updates stay in continuous space and follow the standard PSO formula unchanged
from Program I/II. Positions are neither clamped nor repaired, since argsort
depends only on relative order, not magnitude.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def pso_minimize(
    fitness_fn: Callable[[np.ndarray], float],
    n: int,
    *,
    rng: np.random.Generator,
    pop_size: int = 50,
    max_iter: int = 500,
    c1: float = 1.5,
    c2: float = 1.5,
    w_max: float = 0.9,
    w_min: float = 0.4,
    v_clamp: float = 0.5,
) -> tuple[np.ndarray, float, np.ndarray]:
    """Return ``(best_tour, best_fitness, history)``.

    ``history`` is a length ``max_iter + 1`` array of best-so-far fitness, with
    index 0 holding the best of the initial swarm.
    """

    def evaluate(position: np.ndarray) -> float:
        return fitness_fn(np.argsort(position))

    pos = rng.uniform(0.0, 1.0, size=(pop_size, n))
    vel = rng.uniform(-0.1, 0.1, size=(pop_size, n))

    fitness = np.array([evaluate(p) for p in pos])
    pbest_pos = pos.copy()
    pbest_val = fitness.copy()

    gbest_idx = int(np.argmin(fitness))
    gbest_pos = pos[gbest_idx].copy()
    gbest_val = float(fitness[gbest_idx])

    history = np.empty(max_iter + 1)
    history[0] = gbest_val

    for t in range(1, max_iter + 1):
        w = w_max - (w_max - w_min) * (t - 1) / (max_iter - 1) if max_iter > 1 else w_min

        for i in range(pop_size):
            r1 = rng.random(n)
            r2 = rng.random(n)
            vel[i] = (
                w * vel[i]
                + c1 * r1 * (pbest_pos[i] - pos[i])
                + c2 * r2 * (gbest_pos - pos[i])
            )
            vel[i] = np.clip(vel[i], -v_clamp, v_clamp)
            pos[i] = pos[i] + vel[i]

            fit_i = evaluate(pos[i])
            fitness[i] = fit_i

            if fit_i < pbest_val[i]:
                pbest_val[i] = fit_i
                pbest_pos[i] = pos[i].copy()

            if fit_i < gbest_val:
                gbest_val = fit_i
                gbest_pos = pos[i].copy()

        history[t] = gbest_val

    best_tour = np.argsort(gbest_pos)
    return best_tour, gbest_val, history
