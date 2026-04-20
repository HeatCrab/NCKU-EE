"""
Particle Swarm Optimization (PSO) for function minimization.

Standard PSO with inertia weight (linearly decreasing from w_max to w_min).
"""

import numpy as np


def pso_minimize(func, bounds, pop_size=50, max_iter=100, seed=None):
    """
    Minimize func using PSO.

    Parameters
    ----------
    func : callable
        Objective function, takes np.array of shape (D,), returns scalar.
    bounds : list of (low, high)
        Search range for each dimension.
    pop_size : int
        Number of particles (swarm size).
    max_iter : int
        Number of iterations.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        'best_pos'       : np.array, global best position
        'best_val'       : float, global best fitness
        'convergence'    : np.array of shape (max_iter,), best-so-far per iteration
        'final_pop'      : np.array of shape (pop_size, D), final particle positions
        'final_fitness'  : np.array of shape (pop_size,), final fitness values
    """
    rng = np.random.default_rng(seed)
    D = len(bounds)
    lower = np.array([b[0] for b in bounds])
    upper = np.array([b[1] for b in bounds])

    # PSO hyperparameters
    c1 = 2.0   # cognitive (personal best) coefficient
    c2 = 2.0   # social (global best) coefficient
    w_max = 0.9
    w_min = 0.4
    v_max = 0.2 * (upper - lower)  # velocity clamp

    # --- Initialize particles ---
    pos = rng.uniform(lower, upper, size=(pop_size, D))
    vel = rng.uniform(-v_max, v_max, size=(pop_size, D))
    fitness = np.array([func(p) for p in pos])

    # Personal best
    pbest_pos = pos.copy()
    pbest_val = fitness.copy()

    # Global best
    gbest_idx = np.argmin(fitness)
    gbest_pos = pos[gbest_idx].copy()
    gbest_val = fitness[gbest_idx]

    convergence = np.zeros(max_iter)
    best_pos_history = np.zeros((max_iter, D))

    for t in range(max_iter):
        # Linearly decreasing inertia weight
        w = w_max - (w_max - w_min) * t / (max_iter - 1)

        for i in range(pop_size):
            r1 = rng.random(D)
            r2 = rng.random(D)

            # Velocity update
            vel[i] = (w * vel[i]
                      + c1 * r1 * (pbest_pos[i] - pos[i])
                      + c2 * r2 * (gbest_pos - pos[i]))

            # Clamp velocity
            vel[i] = np.clip(vel[i], -v_max, v_max)

            # Position update
            pos[i] = pos[i] + vel[i]

            # Clip to bounds
            pos[i] = np.clip(pos[i], lower, upper)

            # Evaluate
            fitness[i] = func(pos[i])

            # Update personal best
            if fitness[i] < pbest_val[i]:
                pbest_val[i] = fitness[i]
                pbest_pos[i] = pos[i].copy()

            # Update global best
            if fitness[i] < gbest_val:
                gbest_val = fitness[i]
                gbest_pos = pos[i].copy()

        convergence[t] = gbest_val
        best_pos_history[t] = gbest_pos.copy()

    return {
        'best_pos': gbest_pos,
        'best_val': gbest_val,
        'convergence': convergence,
        'best_pos_history': best_pos_history,
        'final_pop': pos,
        'final_fitness': fitness,
    }
