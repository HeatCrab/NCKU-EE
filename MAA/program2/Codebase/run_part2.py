"""
Part II run (spec: 10 repeats × 5-fold stratified CV).

Per outer fold: fit Age scaler on the outer training fold only, run GA and
PSO once each with inner 3-fold StratifiedKFold fitness on the outer
training data, take the best mask, retrain LR on the full outer training
fold with that mask, and evaluate classification (5 metrics) plus KMeans
clustering on the outer test fold.

Writes Results/part2/part2_results.json with per-fold logs and aggregated
mean ± std across the 50 outer folds, for both algorithms.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold

from lib.classifier import compute_metrics, fit_predict_accuracy, make_lr
from lib.cluster import cluster_classify
from lib.data import (
    N_FEATURES,
    apply_age_scaler,
    fit_age_scaler,
    load_dataset,
    mask_to_columns,
)
from lib.fitness import FitnessFunction, bits_to_int
from lib.ga import ga_maximize
from lib.pso import pso_maximize

N_REPEATS = 10
N_FOLDS = 5
INNER_FOLDS = 3
POP_SIZE = 50
MAX_ITER = 100
LAMBDA = 0.005
RESULTS_DIR = Path(__file__).resolve().parent.parent / "Results" / "part2"


def make_cv_fitness(X_train, y_train, seed):
    skf = StratifiedKFold(n_splits=INNER_FOLDS, shuffle=True, random_state=seed)
    splits = list(skf.split(X_train, y_train))

    def accuracy_fn(cols):
        accs = [
            fit_predict_accuracy(
                X_train[tr][:, cols], y_train[tr],
                X_train[te][:, cols], y_train[te],
            )
            for tr, te in splits
        ]
        return float(np.mean(accs))

    return FitnessFunction(accuracy_fn=accuracy_fn, lambda_penalty=LAMBDA)


def evaluate_mask(mask, X_tr, y_tr, X_te, y_te):
    if not mask:
        raise ValueError(
            "Optimizer returned empty mask; fitness layer should have ruled this out via -inf sentinel"
        )
    cols = mask_to_columns(mask)
    Xtr_sub, Xte_sub = X_tr[:, cols], X_te[:, cols]
    model = make_lr()
    model.fit(Xtr_sub, y_tr)
    train_pred = model.predict(Xtr_sub)
    test_pred = model.predict(Xte_sub)
    train_metrics = compute_metrics(y_tr, train_pred)
    test_metrics = compute_metrics(y_te, test_pred)
    clustering_test_acc = cluster_classify(Xtr_sub, y_tr, X_eval=Xte_sub, y_eval=y_te)
    return train_metrics.as_dict(), test_metrics.as_dict(), float(clustering_test_acc)


def run_one_fold(X_tr, y_tr, X_te, y_te, fold_seed):
    fold = {}
    for name, algo in (("ga", ga_maximize), ("pso", pso_maximize)):
        f = make_cv_fitness(X_tr, y_tr, seed=fold_seed)
        r = algo(f, pop_size=POP_SIZE, max_iter=MAX_ITER, seed=fold_seed)
        mask = bits_to_int(r["best_pos"])
        train_m, test_m, clust = evaluate_mask(mask, X_tr, y_tr, X_te, y_te)
        fold[name] = {
            "mask": int(mask),
            "n_features": int(r["best_pos"].sum()),
            "best_val": float(r["best_val"]),
            "convergence": r["convergence"].tolist(),
            "train_metrics": train_m,
            "test_metrics": test_m,
            "clustering_test_acc": clust,
        }
    return fold


def aggregate(folds, key, sub):
    arr = np.array([f[key][sub] for f in folds])
    return float(arr.mean()), float(arr.std())


def aggregate_metric(folds, key, sub, metric):
    arr = np.array([f[key][sub][metric] for f in folds])
    return float(arr.mean()), float(arr.std())


def main():
    print("Loading dataset (Age scaling applied per outer fold)...")
    X_raw, y, _ = load_dataset()
    print(f"  X shape {X_raw.shape}, y {int(y.sum())} pos / {int((1-y).sum())} neg\n")

    outer = RepeatedStratifiedKFold(
        n_splits=N_FOLDS, n_repeats=N_REPEATS, random_state=0
    )
    n_total = N_FOLDS * N_REPEATS

    folds = []
    t0 = time.perf_counter()
    for fold_i, (tr_idx, te_idx) in enumerate(outer.split(X_raw, y)):
        X_tr_raw, X_te_raw = X_raw[tr_idx], X_raw[te_idx]
        y_tr, y_te = y[tr_idx], y[te_idx]
        mean, std = fit_age_scaler(X_tr_raw)
        X_tr = apply_age_scaler(X_tr_raw, mean, std)
        X_te = apply_age_scaler(X_te_raw, mean, std)

        fold_out = run_one_fold(X_tr, y_tr, X_te, y_te, fold_seed=fold_i)
        fold_out["fold_index"] = fold_i
        folds.append(fold_out)

        elapsed = time.perf_counter() - t0
        eta = elapsed * (n_total - fold_i - 1) / (fold_i + 1)
        print(
            f"  fold {fold_i + 1:>2}/{n_total}: "
            f"GA test {fold_out['ga']['test_metrics']['accuracy']:.4f}, "
            f"PSO test {fold_out['pso']['test_metrics']['accuracy']:.4f}  "
            f"(elapsed {elapsed:.0f}s eta {eta:.0f}s)"
        )

    total = time.perf_counter() - t0
    print(f"\nDone in {total:.0f}s.\n")

    stats = {}
    for name in ("ga", "pso"):
        algo_stats = {}
        for which in ("train_metrics", "test_metrics"):
            for metric in ("accuracy", "sensitivity", "specificity", "precision", "f_measure"):
                m, s = aggregate_metric(folds, name, which, metric)
                algo_stats[f"{which}_{metric}_mean"] = m
                algo_stats[f"{which}_{metric}_std"] = s
        ct_m, ct_s = aggregate(folds, name, "clustering_test_acc")
        algo_stats["clustering_test_acc_mean"] = ct_m
        algo_stats["clustering_test_acc_std"] = ct_s
        nf_m, nf_s = aggregate(folds, name, "n_features")
        algo_stats["n_features_mean"] = nf_m
        algo_stats["n_features_std"] = nf_s
        stats[name] = algo_stats

        print(
            f"=== {name.upper()} ({n_total} outer folds, "
            f"pop {POP_SIZE} iter {MAX_ITER}, inner {INNER_FOLDS}-fold) ===\n"
            f"  train accuracy:    {algo_stats['train_metrics_accuracy_mean']:.4f} "
            f"± {algo_stats['train_metrics_accuracy_std']:.4f}\n"
            f"  test  accuracy:    {algo_stats['test_metrics_accuracy_mean']:.4f} "
            f"± {algo_stats['test_metrics_accuracy_std']:.4f}\n"
            f"  test  F-measure:   {algo_stats['test_metrics_f_measure_mean']:.4f} "
            f"± {algo_stats['test_metrics_f_measure_std']:.4f}\n"
            f"  clustering test:   {ct_m:.4f} ± {ct_s:.4f}\n"
            f"  n_features:        {nf_m:.1f} ± {nf_s:.1f}\n"
        )

    output = {
        "config": {
            "n_repeats": N_REPEATS,
            "n_folds": N_FOLDS,
            "inner_folds": INNER_FOLDS,
            "pop_size": POP_SIZE,
            "max_iter": MAX_ITER,
            "lambda_penalty": LAMBDA,
            "n_features": int(X_raw.shape[1]),
            "preprocessing": "Age z-score fit on outer training fold only",
            "elapsed_seconds": round(total, 2),
        },
        "folds": folds,
        "stats": stats,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "part2_results.json"
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
