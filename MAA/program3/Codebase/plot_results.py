"""
Generate route and convergence figures from the Part I / Part II results.

Reads best_tours.json and convergence.npz from Results/part1 and Results/part2,
plus the instance-24 coordinates, and writes to Report/Pics/:
  - route_part1_{algo}_{K}.png   representative tours, 6 plots, 1-indexed labels
  - route_part2_{algo}.png       representative tours, forbidden edges in red
  - convergence_part1.png        mean +/- std curves over the 6 cells
  - convergence_part2.png        mean +/- std curves over the 2 cells
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CODEBASE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODEBASE))

from lib.data import load_instance_24
from lib.fitness import build_forbidden_mask

DEFAULT_RESULTS_ROOT = CODEBASE.parent / "Results"
DEFAULT_FIG_DIR = CODEBASE.parent / "Report" / "Pics"

GA_COLOR = "C0"
PSO_COLOR = "C1"
DPI = 150


def plot_route(coords, tour, title, output, *, forbidden_mask=None, mark_even=False):
    """Draw a closed tour over the city coordinates with 1-indexed labels."""
    tour = np.asarray(tour)
    loop = np.append(tour, tour[0])

    fig, ax = plt.subplots(figsize=(6, 6))
    for a, b in zip(loop[:-1], loop[1:]):
        is_forbidden = forbidden_mask is not None and forbidden_mask[a, b]
        ax.plot(
            [coords[a, 0], coords[b, 0]],
            [coords[a, 1], coords[b, 1]],
            color="red" if is_forbidden else "C7",
            linestyle="--" if is_forbidden else "-",
            linewidth=1.4 if is_forbidden else 0.9,
            zorder=1,
        )

    even = (tour + 1) % 2 == 0
    if mark_even:
        ax.scatter(coords[tour[even], 0], coords[tour[even], 1],
                   color="C3", s=45, zorder=2, label="even city")
        ax.scatter(coords[tour[~even], 0], coords[tour[~even], 1],
                   color="C0", s=30, zorder=2, label="odd city")
        ax.legend(loc="best", fontsize=8, framealpha=0.9)
    else:
        ax.scatter(coords[tour, 0], coords[tour, 1], color="C0", s=30, zorder=2)

    for c in tour:
        ax.annotate(str(int(c) + 1), (coords[c, 0], coords[c, 1]),
                    fontsize=7, xytext=(3, 3), textcoords="offset points")

    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=DPI)
    plt.close(fig)


def plot_convergence_panel(curves, labels, output, *, ncols):
    """One subplot per cell: mean best-so-far fitness with a +/- std band."""
    n = len(labels)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.5 * ncols, 3.5 * nrows),
                             squeeze=False)
    iters = np.arange(curves.shape[2])

    for idx, label in enumerate(labels):
        ax = axes[idx // ncols][idx % ncols]
        mean = curves[idx].mean(axis=0)
        std = curves[idx].std(axis=0)
        color = GA_COLOR if str(label).startswith(("ga", "GA")) else PSO_COLOR
        ax.fill_between(iters, mean - std, mean + std, color=color, alpha=0.2)
        ax.plot(iters, mean, color=color, linewidth=1.5)
        ax.set_title(str(label))
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Best-so-far fitness")
        ax.grid(alpha=0.3)

    for idx in range(n, nrows * ncols):
        axes[idx // ncols][idx % ncols].axis("off")

    fig.tight_layout()
    fig.savefig(output, dpi=DPI)
    plt.close(fig)


def load_npz(path):
    data = np.load(path, allow_pickle=True)
    return data["convergence"], [str(x) for x in data["cell_labels"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot Part I/II route + convergence figures")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--fig-dir", type=Path, default=DEFAULT_FIG_DIR)
    args = parser.parse_args()

    part1_dir = args.results_root / "part1"
    part2_dir = args.results_root / "part2"
    fig_dir = args.fig_dir
    fig_dir.mkdir(parents=True, exist_ok=True)
    coords, _ = load_instance_24()

    part1_tours = json.loads((part1_dir / "best_tours.json").read_text())
    for key, rep in part1_tours.items():
        algo, k = key.split("_")
        plot_route(
            coords[: int(k)],
            rep["tour"],
            title=f"Part I {algo.upper()} K={k} (dist {rep['distance']:.1f})",
            output=fig_dir / f"route_part1_{key}.png",
        )
    curves1, labels1 = load_npz(part1_dir / "convergence.npz")
    plot_convergence_panel(curves1, labels1, fig_dir / "convergence_part1.png", ncols=3)

    part2_tours = json.loads((part2_dir / "best_tours.json").read_text())
    forbidden_mask = build_forbidden_mask(30)
    for algo, rep in part2_tours.items():
        plot_route(
            coords[:30],
            rep["tour"],
            title=(
                f"Part II {algo.upper()} (dist {rep['distance']:.1f}, "
                f"forbidden {rep['forbidden_edge_count']})"
            ),
            output=fig_dir / f"route_part2_{algo}.png",
            forbidden_mask=forbidden_mask,
            mark_even=True,
        )
    curves2, labels2 = load_npz(part2_dir / "convergence.npz")
    plot_convergence_panel(curves2, labels2, fig_dir / "convergence_part2.png", ncols=2)

    print(f"Saved figures to {fig_dir}")


if __name__ == "__main__":
    main()
