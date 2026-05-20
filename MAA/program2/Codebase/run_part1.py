"""
Part I run (spec: train=test resubstitution).

30 seeded runs of GA and PSO at pop=50, max_iter=100. For each algorithm's
best mask across the 30 runs, reports the five spec metrics for both the
classification and the KMeans clustering branch. Also fits an all-features
Random Forest once as a strong-baseline reference (PLAN §6.3).

Writes Results/part1/part1_results.json with the full per-seed log and the
aggregated stats needed by the report.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from lib.classifier import fit_predict_full
from lib.cluster import cluster_classify_full
from lib.data import apply_age_scaler, fit_age_scaler, load_dataset, mask_to_columns
from lib.fitness import bits_to_int, make_resub_fitness
from lib.ga import ga_maximize
from lib.pso import pso_maximize

N_SEEDS = 30
POP_SIZE = 50
MAX_ITER = 100
LAMBDA = 0.005
RESULTS_DIR = Path(__file__).resolve().parent.parent / "Results" / "part1"


def run_one_algo(algorithm, X, y):
    runs = []
    t0 = time.perf_counter()
    for seed in range(N_SEEDS):
        f = make_resub_fitness(X, y, lambda_penalty=LAMBDA)
        r = algorithm(f, pop_size=POP_SIZE, max_iter=MAX_ITER, seed=seed)
        mask = bits_to_int(r["best_pos"])
        history_masks = [bits_to_int(b) for b in r["best_pos_history"]]
        raw_convergence = [
            float(f.raw_accuracy.get(m, float("nan"))) for m in history_masks
        ]
        runs.append(
            {
                "seed": seed,
                "best_val": float(r["best_val"]),
                "raw_acc": float(f.raw_accuracy.get(mask, float("nan"))),
                "mask": int(mask),
                "n_features": int(r["best_pos"].sum()),
                "convergence": r["convergence"].tolist(),
                "raw_convergence": raw_convergence,
                "evals": int(f.n_evaluations),
                "cache_hits": int(f.n_cache_hits),
            }
        )
    return runs, time.perf_counter() - t0


def summarise_seeds(runs):
    raw = np.array([r["raw_acc"] for r in runs])
    return {
        "raw_acc_mean": float(raw.mean()),
        "raw_acc_std": float(raw.std()),
        "raw_acc_min": float(raw.min()),
        "raw_acc_max": float(raw.max()),
        "n_hit_global_optimum": int(np.sum(raw >= 0.95 - 1e-9)),
    }


def best_run_metrics(best_run, X, y):
    cols = mask_to_columns(best_run["mask"])
    metrics = fit_predict_full(X[:, cols], y, X[:, cols], y)
    clustering = cluster_classify_full(X[:, cols], y)
    return {**metrics.as_dict(), "clustering": clustering.as_dict()}


def rf_baseline(X, y, random_state=0):
    rf = RandomForestClassifier(random_state=random_state)
    rf.fit(X, y)
    return float(np.mean(rf.predict(X) == y))


def main():
    print("Loading dataset and applying Age scaling on full data...")
    X_raw, y, _ = load_dataset()
    mean, std = fit_age_scaler(X_raw)
    X = apply_age_scaler(X_raw, mean, std)
    print(f"  X shape {X.shape}, y {int(y.sum())} pos / {int((1-y).sum())} neg")

    print("Fitting all-features Random Forest baseline...")
    rf_acc = rf_baseline(X, y)
    print(f"  RF resubstitution accuracy: {rf_acc:.4f}\n")

    output = {
        "config": {
            "n_seeds": N_SEEDS,
            "pop_size": POP_SIZE,
            "max_iter": MAX_ITER,
            "lambda_penalty": LAMBDA,
            "n_features": int(X.shape[1]),
            "preprocessing": "Age z-score on full data, binary cols 0/1",
        },
        "references": {
            "exhaustive_best_accuracy": 0.95,
            "exhaustive_best_masks": [12239, 61135],
            "all_features_lr_accuracy": 0.9308,
            "majority_class_accuracy": 320 / 520,
            "all_features_rf_accuracy": rf_acc,
        },
    }

    for name, algo in (("ga", ga_maximize), ("pso", pso_maximize)):
        print(f"Running {name.upper()} ({N_SEEDS} seeds × pop {POP_SIZE} × iter {MAX_ITER})...")
        runs, elapsed = run_one_algo(algo, X, y)
        stats = summarise_seeds(runs)
        best = min(runs, key=lambda r: (-r["raw_acc"], r["n_features"], r["mask"]))
        best_metrics = best_run_metrics(best, X, y)
        output[name] = {
            "elapsed_seconds": round(elapsed, 2),
            "runs": runs,
            "best_run": {
                k: best[k] for k in ("seed", "best_val", "raw_acc", "mask", "n_features")
            },
            "best_mask_metrics": best_metrics,
            "stats_across_seeds": stats,
        }
        print(
            f"  done in {elapsed:.1f}s | "
            f"raw mean {stats['raw_acc_mean']:.4f} ± {stats['raw_acc_std']:.4f} | "
            f"hits 0.95: {stats['n_hit_global_optimum']}/{N_SEEDS}"
        )
        print(
            f"  best mask {best['mask']} ({best['n_features']} features), "
            f"acc {best_metrics['accuracy']:.4f}, "
            f"sensitivity {best_metrics['sensitivity']:.4f}, "
            f"specificity {best_metrics['specificity']:.4f}, "
            f"precision {best_metrics['precision']:.4f}, "
            f"F-measure {best_metrics['f_measure']:.4f}, "
            f"clustering acc {best_metrics['clustering']['accuracy']:.4f}\n"
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "part1_results.json"
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
