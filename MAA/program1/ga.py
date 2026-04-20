"""
Real-valued Genetic Algorithm (GA) for function minimization.

Key operators:
- Selection: Tournament selection
- Crossover: BLX-alpha (blend crossover)
- Mutation: Gaussian perturbation
- Elitism: Best individual always survives
"""

import numpy as np


def ga_minimize(func, bounds, pop_size=50, max_iter=100, seed=None):
    """
    Minimize func using a real-valued GA.

    Parameters
    ----------
    func : callable
        Objective function, takes np.array of shape (D,), returns scalar.
    bounds : list of (low, high)
        Search range for each dimension.
    pop_size : int
        Population size.
    max_iter : int
        Number of generations.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict with keys:
        'best_pos'       : np.array, best solution found
        'best_val'       : float, best fitness value
        'convergence'    : np.array of shape (max_iter,), best-so-far per generation
        'final_pop'      : np.array of shape (pop_size, D), final population
        'final_fitness'  : np.array of shape (pop_size,), final fitness values
    """
    rng = np.random.default_rng(seed)
    D = len(bounds)
    lower = np.array([b[0] for b in bounds])
    upper = np.array([b[1] for b in bounds])

    # GA hyperparameters
    tournament_size = 3
    crossover_rate = 0.8
    mutation_rate = 0.1
    alpha = 0.5          # BLX-alpha parameter
    mutation_scale = 0.1  # fraction of range for Gaussian std

    # --- Initialize population uniformly ---
    pop = rng.uniform(lower, upper, size=(pop_size, D))
    fitness = np.array([func(ind) for ind in pop])

    # Track best-so-far
    best_idx = np.argmin(fitness)
    best_pos = pop[best_idx].copy()
    best_val = fitness[best_idx]
    convergence = np.zeros(max_iter)
    best_pos_history = np.zeros((max_iter, D))

    for gen in range(max_iter):
        new_pop = np.empty_like(pop)

        # Elitism: keep the best individual
        new_pop[0] = best_pos.copy()

        # Fill the rest via selection + crossover + mutation
        i = 1
        while i < pop_size:
            # --- Tournament selection (pick 2 parents) ---
            parent1 = _tournament_select(pop, fitness, tournament_size, rng)
            parent2 = _tournament_select(pop, fitness, tournament_size, rng)

            # --- BLX-alpha crossover ---
            if rng.random() < crossover_rate:
                child1, child2 = _blx_crossover(parent1, parent2, alpha, lower, upper, rng)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # --- Gaussian mutation ---
            child1 = _mutate(child1, mutation_rate, mutation_scale, lower, upper, rng)
            child2 = _mutate(child2, mutation_rate, mutation_scale, lower, upper, rng)

            new_pop[i] = child1
            i += 1
            if i < pop_size:
                new_pop[i] = child2
                i += 1

        pop = new_pop
        fitness = np.array([func(ind) for ind in pop])

        # Update best-so-far
        gen_best_idx = np.argmin(fitness)
        if fitness[gen_best_idx] < best_val:
            best_val = fitness[gen_best_idx]
            best_pos = pop[gen_best_idx].copy()

        convergence[gen] = best_val
        best_pos_history[gen] = best_pos.copy()

    return {
        'best_pos': best_pos,
        'best_val': best_val,
        'convergence': convergence,
        'best_pos_history': best_pos_history,
        'final_pop': pop,
        'final_fitness': fitness,
    }


def _tournament_select(pop, fitness, k, rng):
    """Select one individual via tournament of size k (minimization)."""
    indices = rng.choice(len(pop), size=k, replace=False)
    winner = indices[np.argmin(fitness[indices])]
    return pop[winner].copy()


def _blx_crossover(p1, p2, alpha, lower, upper, rng):
    """BLX-alpha blend crossover, producing 2 children."""
    d = np.abs(p1 - p2)
    lo = np.minimum(p1, p2) - alpha * d
    hi = np.maximum(p1, p2) + alpha * d
    child1 = rng.uniform(lo, hi)
    child2 = rng.uniform(lo, hi)
    # Clip to bounds
    child1 = np.clip(child1, lower, upper)
    child2 = np.clip(child2, lower, upper)
    return child1, child2


def _mutate(ind, rate, scale, lower, upper, rng):
    """Gaussian mutation: each gene mutated independently with probability rate."""
    D = len(ind)
    mask = rng.random(D) < rate
    if np.any(mask):
        sigma = scale * (upper - lower)
        ind[mask] += rng.normal(0, sigma[mask])
        ind = np.clip(ind, lower, upper)
    return ind
