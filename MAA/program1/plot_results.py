"""
Plot and table generator for MAA Program Report I.

Reads experiment_results.json and produces:
1. 3D surface plots of benchmark functions (D=2)
2. Search results plot (sample run particle/individual positions)
3. Convergence curves (avg best-so-far vs iteration)
4. Statistics tables printed to console (copy to report)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from pathlib import Path

from benchmark import FUNCTIONS


RESULTS_DIR = Path(__file__).parent / "results"
PLOTS_DIR = RESULTS_DIR / "plots"


def load_results():
    with open(RESULTS_DIR / "experiment_results.json") as f:
        return json.load(f)


# =========================================================
# 1. 3D surface plots
# =========================================================
def plot_3d_surfaces():
    """Plot 3D surface for each 2D benchmark function."""
    plot_dir = PLOTS_DIR / "3d_surfaces"
    plot_dir.mkdir(parents=True, exist_ok=True)

    for name, info in FUNCTIONS.items():
        if info['dim'] != 2:
            continue

        bounds = info['bounds']
        x = np.linspace(bounds[0][0], bounds[0][1], 200)
        y = np.linspace(bounds[1][0], bounds[1][1], 200)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)

        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = info['func'](np.array([X[i, j], Y[i, j]]))

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8,
                        edgecolor='none', rcount=100, ccount=100)
        ax.set_xlabel('$x_1$')
        ax.set_ylabel('$x_2$')
        ax.set_zlabel('$f(x)$')
        ax.set_title(f'{name} Function')
        plt.tight_layout()
        plt.savefig(plot_dir / f"{name.replace(' ', '_').lower()}_3d.png", dpi=150)
        plt.close()
        print(f"  3D plot saved: {name}")


# =========================================================
# 2. Search results plot (sample run)
# =========================================================
def plot_search_results(results):
    """Plot search trajectory and final population of sample run on 2D contour."""
    plot_dir = PLOTS_DIR / "search_results"
    plot_dir.mkdir(parents=True, exist_ok=True)

    for r in results:
        func_name = r['function']
        info = FUNCTIONS[func_name]
        if info['dim'] != 2:
            continue

        algo = r['algo']
        max_iter = r['max_iter']
        if max_iter != 1000:
            continue

        sample = r['sample_run']
        if 'best_pos_history' not in sample:
            continue

        bounds = info['bounds']
        x = np.linspace(bounds[0][0], bounds[0][1], 200)
        y = np.linspace(bounds[1][0], bounds[1][1], 200)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = info['func'](np.array([X[i, j], Y[i, j]]))

        trajectory = np.array(sample['best_pos_history'])
        final_pop = np.array(sample['final_pop'])
        best_pos = sample['best_pos']

        fig, ax = plt.subplots(figsize=(8, 6))
        contour = ax.contourf(X, Y, Z, levels=50, cmap='viridis')
        plt.colorbar(contour, ax=ax)

        # Plot final population positions
        ax.scatter(final_pop[:, 0], final_pop[:, 1], c='white', s=20,
                   alpha=0.6, edgecolors='gray', linewidths=0.5,
                   label='Final population', zorder=3)

        # Plot best-so-far trajectory
        ax.plot(trajectory[:, 0], trajectory[:, 1], 'r.-', markersize=4,
                linewidth=1, alpha=0.7, label='Best-so-far path', zorder=4)

        # Mark the final best solution
        ax.plot(best_pos[0], best_pos[1], 'r*', markersize=15,
                label=f"Best found: ({best_pos[0]:.4f}, {best_pos[1]:.4f})", zorder=5)

        # Mark the known optimum
        opt_pos = info['optima_pos']
        ax.plot(opt_pos[0], opt_pos[1], 'w^', markersize=10,
                label=f"Known optimum: ({opt_pos[0]:.4f}, {opt_pos[1]:.4f})", zorder=5)

        ax.set_xlabel('$x_1$')
        ax.set_ylabel('$x_2$')
        ax.set_title(f'{algo} on {func_name} (iter={max_iter}, sample run)')
        ax.legend(loc='upper right', fontsize=8)
        plt.tight_layout()

        fname = f"{algo}_{func_name.replace(' ', '_').lower()}_search.png"
        plt.savefig(plot_dir / fname, dpi=150)
        plt.close()
        print(f"  Search plot saved: {algo} - {func_name}")


# =========================================================
# 3. Convergence curves
# =========================================================
def plot_convergence(results):
    """Plot avg best-so-far vs iteration, GA vs PSO on same figure."""
    plot_dir = PLOTS_DIR / "convergence"
    plot_dir.mkdir(parents=True, exist_ok=True)

    # Group by (function, max_iter)
    groups = {}
    for r in results:
        key = (r['function'], r['max_iter'])
        if key not in groups:
            groups[key] = {}
        groups[key][r['algo']] = r['stats']['avg_convergence']

    for (func_name, max_iter), algos in groups.items():
        fig, ax = plt.subplots(figsize=(8, 5))
        for algo_name, conv in algos.items():
            ax.plot(range(1, len(conv) + 1), conv, label=algo_name)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Average Best-so-far')
        ax.set_title(f'{func_name} (iter={max_iter}, avg over 50 runs)')
        ax.legend()
        # Use log scale only if all values are positive
        all_vals = [v for conv in algos.values() for v in conv]
        if min(all_vals) > 0:
            ax.set_yscale('log')
        plt.tight_layout()

        fname = f"{func_name.replace(' ', '_').lower()}_iter{max_iter}_conv.png"
        plt.savefig(plot_dir / fname, dpi=150)
        plt.close()
        print(f"  Convergence plot saved: {func_name} iter={max_iter}")


# =========================================================
# 2b. Single-run search for high-dim functions (Kowalik)
# =========================================================
def plot_single_run_highdim(results):
    """For functions with dim > 2, show a single-run view of the search:
    (top) best-so-far convergence of run 0; (bottom) each coordinate of the
    best-so-far position over iterations. iter=1000 only."""
    plot_dir = PLOTS_DIR / "search_results"
    plot_dir.mkdir(parents=True, exist_ok=True)

    for r in results:
        func_name = r['function']
        info = FUNCTIONS[func_name]
        if info['dim'] <= 2 or r['max_iter'] != 1000:
            continue

        sample = r['sample_run']
        conv = np.array(sample['convergence'])
        traj = np.array(sample['best_pos_history'])  # shape (T, D)
        iters = np.arange(1, len(conv) + 1)

        fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

        ax_top.plot(iters, conv, 'b-', linewidth=1)
        ax_top.set_ylabel('Best-so-far $f(x)$')
        ax_top.set_title(f'{r["algo"]} on {func_name} (iter={r["max_iter"]}, sample run)')
        if conv.min() > 0:
            ax_top.set_yscale('log')
        ax_top.grid(True, alpha=0.3)

        opt = info['optima_pos']
        for d in range(info['dim']):
            line, = ax_bot.plot(iters, traj[:, d], label=f'$x_{d+1}$', linewidth=1)
            ax_bot.axhline(y=float(opt[d]), color=line.get_color(),
                           linestyle='--', alpha=0.5, linewidth=0.8)
        ax_bot.set_xlabel('Iteration')
        ax_bot.set_ylabel('Coordinate of $x_{best}$')
        ax_bot.legend(loc='best', fontsize=8, ncol=info['dim'])
        ax_bot.grid(True, alpha=0.3)
        plt.tight_layout()

        fname = f"{r['algo']}_{func_name.replace(' ', '_').lower()}_search.png"
        plt.savefig(plot_dir / fname, dpi=150)
        plt.close()
        print(f"  Single-run plot saved: {r['algo']} - {func_name}")


# =========================================================
# 4. Statistics tables (printed to console as Markdown)
# =========================================================
def print_tables(results):
    """Print Discussion requirement tables 4, 5, 6."""

    # --- Table 4: avg best-so-far, avg mean fitness, median best-so-far ---
    print("\n" + "=" * 80)
    print("TABLE 4: Averaged results over 50 runs (best-so-far at last iteration)")
    print("=" * 80)
    header = f"{'Function':15s} {'Algo':5s} {'Iter':>5s} {'Avg BSF':>14s} {'Avg Mean Fit':>14s} {'Median BSF':>14s}"
    print(header)
    print("-" * len(header))
    for r in results:
        s = r['stats']
        print(f"{r['function']:15s} {r['algo']:5s} {r['max_iter']:5d} "
              f"{s['avg_best_so_far']:14.8f} {s['avg_mean_fitness']:14.8f} "
              f"{s['median_best_so_far']:14.8f}")

    # --- Table 5: best solution (coordinates) mean & std, per dimension ---
    print("\n" + "=" * 80)
    print("TABLE 5: Best solution x_best (mean ± std over 50 runs, per dimension)")
    print("=" * 80)

    # Reorganize results by function, then by (algo, iter)
    by_func = {}
    for r in results:
        by_func.setdefault(r['function'], {})[(r['algo'], r['max_iter'])] = r['stats']

    def _fmt(v, std):
        def one(x):
            ax = abs(x)
            if ax == 0:
                return "0"
            if ax < 1e-3 or ax >= 1e4:
                return f"{x:.2e}"
            return f"{x:.4f}"
        return f"{one(v)} ± {one(std)}"

    order = [('GA', 100), ('GA', 1000), ('PSO', 100), ('PSO', 1000)]
    labels = "abcdefghijklmn"
    for lab, fname in zip(labels, FUNCTIONS.keys()):
        dim = len(by_func[fname][('GA', 100)]['best_solution_mean'])
        print(f"\n**Table 5{lab} — {fname}**\n")
        print("| Dim | GA (100) | GA (1000) | PSO (100) | PSO (1000) |")
        print("|---|---:|---:|---:|---:|")
        for d in range(dim):
            cells = [f"$x_{d+1}$"]
            for k in order:
                s = by_func[fname][k]
                cells.append(_fmt(s['best_solution_mean'][d],
                                  s['best_solution_std'][d]))
            print("| " + " | ".join(cells) + " |")

    # --- Table 6: distance error ---
    print("\n" + "=" * 80)
    print("TABLE 6: Distance error ||x_best - x*|| (mean and std over 50 runs)")
    print("=" * 80)
    header = f"{'Function':15s} {'Algo':5s} {'Iter':>5s} {'Mean Dist':>14s} {'Std Dist':>14s}"
    print(header)
    print("-" * len(header))
    for r in results:
        s = r['stats']
        print(f"{r['function']:15s} {r['algo']:5s} {r['max_iter']:5d} "
              f"{s['distance_error_mean']:14.8f} {s['distance_error_std']:14.8f}")


# =========================================================
# 7. Parameter settings summary
# =========================================================
def print_parameters():
    print("\n" + "=" * 80)
    print("TABLE 7: Parameter Settings")
    print("=" * 80)
    print("""
Common:
  Population size: 50
  Max iterations:  100 / 1000
  Number of runs:  50

GA (Real-valued):
  Selection:       Tournament (size=3)
  Crossover:       BLX-alpha (alpha=0.5), rate=0.8
  Mutation:        Gaussian (scale=0.1 * range), rate=0.1
  Elitism:         Best individual preserved

PSO:
  Inertia weight:  Linearly decreasing 0.9 -> 0.4
  c1 (cognitive):  2.0
  c2 (social):     2.0
  Velocity clamp:  0.2 * range
""")


def main():
    print("Loading results...")
    results = load_results()

    print("\n--- 3D Surface Plots ---")
    plot_3d_surfaces()

    print("\n--- Search Results Plots ---")
    plot_search_results(results)
    plot_single_run_highdim(results)

    print("\n--- Convergence Plots ---")
    plot_convergence(results)

    print_tables(results)
    print_parameters()

    print(f"\nAll plots saved to {PLOTS_DIR}/")


if __name__ == '__main__':
    main()
