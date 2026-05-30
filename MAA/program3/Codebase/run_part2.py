"""
Part II experiments: GA and PSO on the first 30 cities with forbidden edges.

Edges between even-numbered cities (1-indexed) are forbidden; fitness is the
roundtrip distance plus a penalty per forbidden edge used. Two cells (GA, PSO),
30 seeded runs each. Alongside the four Part I metrics, each cell also reports
the representative tour's forbidden-edge count, the minimum pure distance across
runs (regardless of feasibility), and an infeasibility flag. No repair or retry
is applied; infeasible representatives are flagged and reported.

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
from lib.fitness import (
    build_forbidden_mask,
    count_forbidden_edges,
    make_part2_fitness,
    penalty_lambda,
    roundtrip_distance,
)
from lib.ga import ga_minimize
from lib.pso import pso_minimize

K = 30
ALGORITHMS = ("ga", "pso")
DEFAULT_SEEDS = 30
DEFAULT_MAX_ITER = 500
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "Results" / "part2"


def run_cell(algo, D_sub, forbidden_mask, lam, n_seeds, max_iter):
    """Run one algorithm cell over ``n_seeds`` seeds."""
    fitness_fn = make_part2_fitness(D_sub, forbidden_mask, lam)
    runs = []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        t0 = time.perf_counter()
        if algo == "ga":
            tour, fit, history = ga_minimize(fitness_fn, K, rng=rng, max_iter=max_iter)
        else:
            tour, fit, history = pso_minimize(fitness_fn, K, rng=rng, max_iter=max_iter)
        elapsed = time.perf_counter() - t0

        runs.append(
            {
                "seed": seed,
                "tour": [int(c) for c in tour],
                "distance": roundtrip_distance(tour, D_sub),
                "fitness": float(fit),
                "forbidden_edges": count_forbidden_edges(tour, forbidden_mask),
                "time": elapsed,
                "convergence": history.tolist(),
            }
        )
    return runs


def summarise(runs: list[dict]) -> dict:
    representative = min(runs, key=lambda r: r["fitness"])
    distances = np.array([r["distance"] for r in runs])
    times = np.array([r["time"] for r in runs])
    forbidden = representative["forbidden_edges"]
    return {
        "best_distance": representative["distance"],
        "best_fitness": representative["fitness"],
        "avg_distance": float(distances.mean()),
        "comp_time": float(times.mean()),
        "forbidden_edge_count": forbidden,
        "min_pure_distance": float(distances.min()),
        "infeasibility_flag": forbidden >= 1,
        "representative": {
            "seed": representative["seed"],
            "tour": representative["tour"],
            "distance": representative["distance"],
            "fitness": representative["fitness"],
            "forbidden_edge_count": forbidden,
            "infeasibility_flag": forbidden >= 1,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Part II GA/PSO TSP experiments")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--max-iter", type=int, default=DEFAULT_MAX_ITER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    _, D = load_instance_24()
    D_sub = D[:K, :K]
    forbidden_mask = build_forbidden_mask(K)
    lam = penalty_lambda(D_sub)
    print(
        f"Part II: {K} cities, {int(forbidden_mask.sum() // 2)} forbidden edges, "
        f"lambda {lam:.2f}"
    )

    cells: dict[str, dict] = {}
    best_tours: dict[str, dict] = {}
    cell_labels: list[str] = []
    convergence_stack: list[np.ndarray] = []

    for algo in ALGORITHMS:
        print(f"Running {algo} ({args.seeds} seeds x {args.max_iter} iter)...")
        runs = run_cell(algo, D_sub, forbidden_mask, lam, args.seeds, args.max_iter)
        stats = summarise(runs)

        cells[algo] = {k: v for k, v in stats.items() if k != "representative"}
        cells[algo]["runs"] = [
            {k: r[k] for k in ("seed", "distance", "fitness", "forbidden_edges", "time")}
            for r in runs
        ]
        best_tours[algo] = stats["representative"]

        cell_labels.append(algo)
        convergence_stack.append(np.array([r["convergence"] for r in runs]))

        print(
            f"  best distance {stats['best_distance']:.2f} | "
            f"fitness {stats['best_fitness']:.2f} | "
            f"forbidden {stats['forbidden_edge_count']} | "
            f"infeasible {stats['infeasibility_flag']}"
        )

    args.out.mkdir(parents=True, exist_ok=True)
    output = {
        "config": {
            "part": 2,
            "n_seeds": args.seeds,
            "max_iter": args.max_iter,
            "n_cities": K,
            "lambda": lam,
            "cell_order": cell_labels,
        },
        "cells": cells,
    }
    (args.out / "part2_results.json").write_text(json.dumps(output, indent=2))
    (args.out / "best_tours.json").write_text(json.dumps(best_tours, indent=2))
    np.savez(
        args.out / "convergence.npz",
        convergence=np.array(convergence_stack),
        cell_labels=np.array(cell_labels),
    )
    print(f"Saved results to {args.out}")


if __name__ == "__main__":
    main()
