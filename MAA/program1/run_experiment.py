"""
Experiment runner for MAA Program Report I.

Runs GA and PSO on all benchmark functions, collects statistics,
and saves results to a JSON file for later plotting/reporting.
"""

import json
import time
import numpy as np
from pathlib import Path

from benchmark import FUNCTIONS
from ga import ga_minimize
from pso import pso_minimize


NUM_RUNS = 50
POP_SIZE = 50
MAX_ITERS = [100, 1000]
OUTPUT_DIR = Path(__file__).parent / "results"


def run_single(algo_func, func, bounds, pop_size, max_iter, seed, save_full=False):
    """Run a single optimization and return result dict."""
    result = algo_func(func, bounds, pop_size=pop_size, max_iter=max_iter, seed=seed)
    out = {
        'best_pos': result['best_pos'].tolist(),
        'best_val': float(result['best_val']),
        'convergence': result['convergence'].tolist(),
        'final_fitness': result['final_fitness'].tolist(),
    }
    if save_full:
        out['best_pos_history'] = result['best_pos_history'].tolist()
        out['final_pop'] = result['final_pop'].tolist()
    return out


def run_experiment(algo_name, algo_func, func_name, func_info, max_iter, num_runs):
    """Run num_runs experiments and collect all results."""
    func = func_info['func']
    bounds = func_info['bounds']

    runs = []
    for r in range(num_runs):
        save_full = (r == 0)  # save trajectory + final_pop for first run only
        result = run_single(algo_func, func, bounds, POP_SIZE, max_iter, seed=r,
                            save_full=save_full)
        runs.append(result)

    # --- Compute statistics ---
    best_vals = np.array([r['best_val'] for r in runs])
    best_positions = np.array([r['best_pos'] for r in runs])
    convergences = np.array([r['convergence'] for r in runs])

    # All final fitness values across all runs
    all_final_fitness = []
    for r in runs:
        all_final_fitness.extend(r['final_fitness'])
    all_final_fitness = np.array(all_final_fitness)

    # Distance error: ||x_best - x*|| (use nearest optimum if multiple exist)
    all_optima = func_info.get('all_optima_pos', [func_info['optima_pos']])
    distances = np.array([
        min(np.linalg.norm(np.array(r['best_pos']) - opt) for opt in all_optima)
        for r in runs
    ])

    stats = {
        'avg_best_so_far': float(np.mean(best_vals)),
        'std_best_so_far': float(np.std(best_vals)),
        'median_best_so_far': float(np.median(best_vals)),
        'avg_mean_fitness': float(np.mean(all_final_fitness)),
        'best_val_mean': float(np.mean(best_vals)),
        'best_val_std': float(np.std(best_vals)),
        'best_solution_mean': best_positions.mean(axis=0).tolist(),
        'best_solution_std': best_positions.std(axis=0).tolist(),
        'distance_error_mean': float(np.mean(distances)),
        'distance_error_std': float(np.std(distances)),
        'avg_convergence': convergences.mean(axis=0).tolist(),
    }

    return {
        'algo': algo_name,
        'function': func_name,
        'max_iter': max_iter,
        'pop_size': POP_SIZE,
        'num_runs': num_runs,
        'stats': stats,
        'sample_run': runs[0],  # keep run #0 for plotting search results
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    algorithms = {
        'GA': ga_minimize,
        'PSO': pso_minimize,
    }

    all_results = []

    for algo_name, algo_func in algorithms.items():
        for func_name, func_info in FUNCTIONS.items():
            for max_iter in MAX_ITERS:
                print(f"Running {algo_name} on {func_name} "
                      f"(iter={max_iter}, {NUM_RUNS} runs)...", end=" ", flush=True)
                t0 = time.time()
                result = run_experiment(
                    algo_name, algo_func, func_name, func_info, max_iter, NUM_RUNS
                )
                elapsed = time.time() - t0
                print(f"done in {elapsed:.1f}s  "
                      f"(avg best: {result['stats']['avg_best_so_far']:.6f})")
                all_results.append(result)

    # Save all results to JSON
    output_path = OUTPUT_DIR / "experiment_results.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
