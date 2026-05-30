"""
Part I experiments: GA and PSO on three city subsets (first 12, 30, 52).

Six cells (2 algorithms x 3 subsets), 30 seeded runs each. Per cell the
representative run is the one with the lowest fitness; its tour drives the
route plots. Writes part1_results.json (per-run log + aggregates),
convergence.npz (cell x run x iter best-so-far curves), and best_tours.json
(representative tour per cell).

For a quick smoke run use a smaller --seeds / --max-iter and an alternate --out.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from lib.data import load_instance_24
from lib.fitness import make_part1_fitness, roundtrip_distance
from lib.ga import ga_minimize
from lib.pso import pso_minimize

SUBSETS = (12, 30, 52)
ALGORITHMS = ("ga", "pso")
DEFAULT_SEEDS = 30
DEFAULT_MAX_ITER = 500
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "Results" / "part1"


def cell_key(algo: str, k: int) -> str:
    return f"{algo}_{k}"


def run_cell(algo: str, k: int, D: np.ndarray, n_seeds: int, max_iter: int):
    """Run one (algorithm, subset) cell over ``n_seeds`` seeds."""
    D_sub = D[:k, :k]
    fitness_fn = make_part1_fitness(D_sub)
    runs = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        t0 = time.perf_counter()
        if algo == "ga":
            tour, fit, history = ga_minimize(fitness_fn, k, rng=rng, max_iter=max_iter)
        else:
            tour, fit, history = pso_minimize(fitness_fn, k, rng=rng, max_iter=max_iter)
        elapsed = time.perf_counter() - t0

        distance = roundtrip_distance(tour, D_sub)
        runs.append(
            {
                "seed": seed,
                "tour": [int(c) for c in tour],
                "distance": distance,
                "fitness": float(fit),
                "time": elapsed,
                "convergence": history.tolist(),
            }
        )
    return runs


def summarise(runs: list[dict]) -> dict:
    """Aggregate the four spec metrics, anchored on the min-fitness run."""
    representative = min(runs, key=lambda r: r["fitness"])
    distances = np.array([r["distance"] for r in runs])
    times = np.array([r["time"] for r in runs])
    return {
        "best_distance": representative["distance"],
        "best_fitness": representative["fitness"],
        "avg_distance": float(distances.mean()),
        "comp_time": float(times.mean()),
        "representative": {
            "seed": representative["seed"],
            "tour": representative["tour"],
            "distance": representative["distance"],
            "fitness": representative["fitness"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Part I GA/PSO TSP experiments")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--max-iter", type=int, default=DEFAULT_MAX_ITER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    coords, D = load_instance_24()
    print(f"Loaded instance 24: {coords.shape[0]} cities (distance matrix verified)")

    cells: dict[str, dict] = {}
    best_tours: dict[str, dict] = {}
    cell_labels: list[str] = []
    convergence_stack: list[np.ndarray] = []

    for algo in ALGORITHMS:
        for k in SUBSETS:
            key = cell_key(algo, k)
            print(f"Running {key} ({args.seeds} seeds x {args.max_iter} iter)...")
            runs = run_cell(algo, k, D, args.seeds, args.max_iter)
            stats = summarise(runs)

            cells[key] = {k2: v for k2, v in stats.items() if k2 != "representative"}
            cells[key]["runs"] = [
                {k3: r[k3] for k3 in ("seed", "distance", "fitness", "time")} for r in runs
            ]
            best_tours[key] = stats["representative"]

            cell_labels.append(key)
            convergence_stack.append(np.array([r["convergence"] for r in runs]))

            print(
                f"  best distance {stats['best_distance']:.2f} | "
                f"avg distance {stats['avg_distance']:.2f} | "
                f"mean time {stats['comp_time']:.3f}s"
            )

    args.out.mkdir(parents=True, exist_ok=True)
    output = {
        "config": {
            "part": 1,
            "n_seeds": args.seeds,
            "max_iter": args.max_iter,
            "subsets": list(SUBSETS),
            "cell_order": cell_labels,
        },
        "cells": cells,
    }
    (args.out / "part1_results.json").write_text(json.dumps(output, indent=2))
    (args.out / "best_tours.json").write_text(json.dumps(best_tours, indent=2))
    np.savez(
        args.out / "convergence.npz",
        convergence=np.array(convergence_stack),
        cell_labels=np.array(cell_labels),
    )
    print(f"Saved results to {args.out}")


if __name__ == "__main__":
    main()
