"""
Particle Swarm Optimization with continuous positions in [0,1]^n,
thresholded at 0.5 for binary feature-subset selection (maximization).

The raw continuous position is internal bookkeeping; the reported solution
is always the thresholded mask. Empty thresholded masks are handled by the
fitness function (returning -inf), so the swarm is pushed back into valid
territory without explicit repair.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def pso_maximize(
    fitness_fn: Callable[[np.ndarray], float],
    n_features: int = 16,
    pop_size: int = 50,
    max_iter: int = 100,
    seed: int | None = None,
    c1: float = 2.0,
    c2: float = 2.0,
    w_max: float = 0.9,
    w_min: float = 0.4,
    v_clamp_ratio: float = 0.2,
) -> dict:
    rng = np.random.default_rng(seed)
    lower, upper = 0.0, 1.0
    v_max = v_clamp_ratio * (upper - lower)

    pos = rng.uniform(lower, upper, size=(pop_size, n_features))
    vel = rng.uniform(-v_max, v_max, size=(pop_size, n_features))

    def threshold(p: np.ndarray) -> np.ndarray:
        return (p >= 0.5).astype(int)

    fitness = np.array([fitness_fn(threshold(p)) for p in pos])

    pbest_pos = pos.copy()
    pbest_val = fitness.copy()

    gbest_idx = int(np.argmax(fitness))
    gbest_pos = pos[gbest_idx].copy()
    gbest_val = float(fitness[gbest_idx])

    convergence = np.zeros(max_iter)

    for t in range(max_iter):
        w = w_max - (w_max - w_min) * t / (max_iter - 1) if max_iter > 1 else w_min

        for i in range(pop_size):
            r1 = rng.random(n_features)
            r2 = rng.random(n_features)

            vel[i] = (
                w * vel[i]
                + c1 * r1 * (pbest_pos[i] - pos[i])
                + c2 * r2 * (gbest_pos - pos[i])
            )
            vel[i] = np.clip(vel[i], -v_max, v_max)
            pos[i] = np.clip(pos[i] + vel[i], lower, upper)

            fit_i = float(fitness_fn(threshold(pos[i])))
            fitness[i] = fit_i

            if fit_i > pbest_val[i]:
                pbest_val[i] = fit_i
                pbest_pos[i] = pos[i].copy()

            if fit_i > gbest_val:
                gbest_val = fit_i
                gbest_pos = pos[i].copy()

        convergence[t] = gbest_val

    return {
        "best_pos": threshold(gbest_pos),
        "best_pos_continuous": gbest_pos,
        "best_val": gbest_val,
        "convergence": convergence,
        "final_pop": pos,
        "final_fitness": fitness,
    }
