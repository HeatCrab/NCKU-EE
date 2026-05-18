"""
Exhaustive Logistic Regression sweep over all 2^16 - 1 non-empty feature masks.

Reports the best resubstitution accuracy under the current LR configuration
(spec's Part I protocol: train and evaluate on the full dataset). Used as a
reference optimum for sanity-checking GA / PSO results in later milestones.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from lib.classifier import fit_predict_accuracy, fit_predict_full
from lib.data import (
    FEATURE_ORDER,
    N_FEATURES,
    apply_age_scaler,
    fit_age_scaler,
    load_dataset,
    mask_to_columns,
)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "Results" / "exhaustive"


def _mask_features(mask: int) -> list[str]:
    cols = mask_to_columns(mask)
    return [FEATURE_ORDER[c] for c in cols]


def _tiebreak_key(mask: int, accuracy: float) -> tuple[float, int, int]:
    return (-accuracy, bin(mask).count("1"), mask)


def run_exhaustive(
    X: np.ndarray,
    y: np.ndarray,
    log_every: int = 5000,
) -> np.ndarray:
    n_masks = (1 << N_FEATURES) - 1
    accuracies = np.empty(n_masks, dtype=np.float32)

    t0 = time.perf_counter()
    for mask in range(1, n_masks + 1):
        cols = mask_to_columns(mask)
        X_sub = X[:, cols]
        accuracies[mask - 1] = fit_predict_accuracy(X_sub, y, X_sub, y)
        if mask % log_every == 0:
            elapsed = time.perf_counter() - t0
            rate = mask / elapsed
            eta = (n_masks - mask) / rate
            print(
                f"  {mask:>5d} / {n_masks} "
                f"({100 * mask / n_masks:5.1f}%) "
                f"elapsed {elapsed:6.1f}s, eta {eta:6.1f}s"
            )

    return accuracies


def summarise(accuracies: np.ndarray, top_k: int = 10) -> dict:
    n_masks = accuracies.size
    order = sorted(
        range(n_masks),
        key=lambda i: _tiebreak_key(i + 1, float(accuracies[i])),
    )
    top_indices = order[:top_k]
    top = [
        {
            "mask": int(idx + 1),
            "accuracy": float(accuracies[idx]),
            "n_features": bin(int(idx + 1)).count("1"),
            "features": _mask_features(int(idx + 1)),
        }
        for idx in top_indices
    ]
    best = top[0]

    return {
        "n_masks_evaluated": int(n_masks),
        "best_mask": best["mask"],
        "best_accuracy": best["accuracy"],
        "best_n_features": best["n_features"],
        "best_features": best["features"],
        "tiebreak_rule": "accuracy desc, then n_features asc, then mask asc",
        "top_k": top,
    }


def main() -> None:
    print("Loading dataset...")
    X_raw, y, feature_names = load_dataset()
    print(f"  X shape: {X_raw.shape}, y shape: {y.shape}")
    pos = int(y.sum())
    neg = int((1 - y).sum())
    print(f"  class balance: positive={pos}, negative={neg}")

    mean, std = fit_age_scaler(X_raw)
    X = apply_age_scaler(X_raw, mean, std)
    print(f"  age scaler fit on full dataset: mean={mean:.4f}, std={std:.4f}")

    all_features_acc = fit_predict_accuracy(X, y, X, y)
    majority_class_acc = max(pos, neg) / (pos + neg)
    print(f"  all-features LR resubstitution accuracy: {all_features_acc:.4f}")
    print(f"  majority-class baseline:                 {majority_class_acc:.4f}")

    print(f"\nFitting LR on all {(1 << N_FEATURES) - 1} non-empty masks...")
    accuracies = run_exhaustive(X, y)
    print(f"Done. {int(accuracies.size)} masks evaluated.")

    summary = summarise(accuracies)
    summary["all_features_accuracy"] = float(all_features_acc)
    summary["majority_class_accuracy"] = float(majority_class_acc)

    print("\n=== Best mask under current LR configuration (Part I, resubstitution) ===")
    print(f"Best accuracy: {summary['best_accuracy']:.4f}")
    print(f"Best mask: {summary['best_mask']} (0b{summary['best_mask']:016b})")
    print(f"Best n_features: {summary['best_n_features']}")
    print(f"Best features: {summary['best_features']}")

    print("\nTop 10 masks (tiebreak: accuracy desc, n_features asc, mask asc):")
    for i, row in enumerate(summary["top_k"], 1):
        print(
            f"  {i:>2d}. acc={row['accuracy']:.4f} "
            f"n={row['n_features']:>2d} "
            f"mask={row['mask']}"
        )

    print("\nFull 5 metrics on best mask:")
    cols = mask_to_columns(summary["best_mask"])
    metrics = fit_predict_full(X[:, cols], y, X[:, cols], y)
    for k, v in metrics.as_dict().items():
        print(f"  {k}: {v:.4f}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    np.save(RESULTS_DIR / "accuracies.npy", accuracies)
    with (RESULTS_DIR / "summary.json").open("w") as f:
        json.dump(
            {**summary, "best_mask_metrics": metrics.as_dict()},
            f,
            indent=2,
        )
    print(f"\nSaved results to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
