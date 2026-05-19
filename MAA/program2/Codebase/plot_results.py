"""
Generate the five report figures from part1_results.json and part2_results.json.

Outputs to MAA/program2/Report/Pics/:
  - part1_convergence.png       Part I raw-accuracy convergence, mean ± std over 30 seeds
  - part1_feature_freq.png      Part I feature selection frequency across 30 seeds
  - part2_convergence.png       Part II inner-CV accuracy convergence, mean ± std over 50 folds
  - part2_test_boxplot.png      Part II outer-test accuracy distribution across 50 folds
  - part2_feature_freq.png      Part II feature selection frequency across 50 folds
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

CODEBASE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODEBASE))

from lib.data import FEATURE_ORDER, N_FEATURES

PROGRAM = CODEBASE.parent
PART1_JSON = PROGRAM / "Results" / "part1" / "part1_results.json"
PART2_JSON = PROGRAM / "Results" / "part2" / "part2_results.json"
PICS_DIR = PROGRAM / "Report" / "Pics"

GA_COLOR = "C0"
PSO_COLOR = "C1"
REF_COLOR = "gray"
DPI = 150

# Reference values from the M1 exhaustive sweep and Islam et al. 2019
GLOBAL_BEST_MASK = 12239
GLOBAL_BEST_ACC = 0.95
PAPER_LR_CV = 0.924


def mask_to_bits(mask: int, n: int = N_FEATURES) -> np.ndarray:
    """LSB-first unpacking, matching lib.data.mask_to_columns convention."""
    return np.array([(mask >> i) & 1 for i in range(n)], dtype=int)


def feature_counts(masks: list[int]) -> np.ndarray:
    bits = np.array([mask_to_bits(m) for m in masks])
    return bits.sum(axis=0)


def plot_convergence(
    ga_curves: np.ndarray,
    pso_curves: np.ndarray,
    ylabel: str,
    output: Path,
    refs: list[tuple[float, str]] | None = None,
) -> None:
    iters = np.arange(1, ga_curves.shape[1] + 1)
    ga_mean, ga_std = ga_curves.mean(0), ga_curves.std(0)
    pso_mean, pso_std = pso_curves.mean(0), pso_curves.std(0)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(iters, ga_mean - ga_std, ga_mean + ga_std,
                    color=GA_COLOR, alpha=0.2)
    ax.fill_between(iters, pso_mean - pso_std, pso_mean + pso_std,
                    color=PSO_COLOR, alpha=0.2)
    ax.plot(iters, ga_mean, color=GA_COLOR, label="GA", linewidth=1.5)
    ax.plot(iters, pso_mean, color=PSO_COLOR, label="PSO", linewidth=1.5)

    if refs:
        for y, label in refs:
            ax.axhline(y, color=REF_COLOR, linestyle="--", linewidth=0.8,
                       label=label)

    ax.set_xlabel("Iteration")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
    fig.tight_layout()
    fig.savefig(output, dpi=DPI)
    plt.close(fig)


def plot_feature_freq(
    ga_counts: np.ndarray,
    pso_counts: np.ndarray,
    n_runs: int,
    output: Path,
) -> None:
    y = np.arange(N_FEATURES)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    bar_h = 0.4
    ax.barh(y - bar_h / 2, ga_counts, bar_h, color=GA_COLOR, label="GA")
    ax.barh(y + bar_h / 2, pso_counts, bar_h, color=PSO_COLOR, label="PSO")
    ax.set_yticks(y)
    ax.set_yticklabels(FEATURE_ORDER)
    for i, tick in enumerate(ax.get_yticklabels()):
        if (GLOBAL_BEST_MASK >> i) & 1:
            tick.set_color("black")
            tick.set_fontweight("bold")
        else:
            tick.set_color("gray")
    ax.invert_yaxis()
    ax.set_xlim(0, n_runs)
    ax.set_xlabel(f"Number of times selected (out of {n_runs})")
    ax.grid(alpha=0.3, axis="x")
    ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
    fig.tight_layout()
    fig.savefig(output, dpi=DPI)
    plt.close(fig)


def plot_test_boxplot(
    ga_acc: list[float],
    pso_acc: list[float],
    output: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    positions = [1, 2]
    bp = ax.boxplot(
        [ga_acc, pso_acc],
        positions=positions,
        widths=0.5,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.2),
        showfliers=False,
    )
    for patch, c in zip(bp["boxes"], [GA_COLOR, PSO_COLOR]):
        patch.set_facecolor(c)
        patch.set_alpha(0.4)

    rng = np.random.default_rng(0)
    for i, accs in enumerate([ga_acc, pso_acc]):
        x = rng.normal(positions[i], 0.05, size=len(accs))
        ax.scatter(x, accs, color=[GA_COLOR, PSO_COLOR][i], alpha=0.5, s=15)

    ax.axhline(PAPER_LR_CV, color=REF_COLOR, linestyle="--", linewidth=0.8,
               label=f"Islam 2019 LR 10-fold CV = {PAPER_LR_CV}")
    ax.set_xticks(positions)
    ax.set_xticklabels(["GA", "PSO"])
    ax.set_ylabel("Test accuracy (50 outer folds)")
    ax.grid(alpha=0.3, axis="y")
    ax.legend(loc="lower right", framealpha=0.9, fontsize=9)
    fig.tight_layout()
    fig.savefig(output, dpi=DPI)
    plt.close(fig)


def main() -> None:
    PICS_DIR.mkdir(parents=True, exist_ok=True)

    with PART1_JSON.open() as fp:
        part1 = json.load(fp)
    ga1 = np.array([r["raw_convergence"] for r in part1["ga"]["runs"]])
    pso1 = np.array([r["raw_convergence"] for r in part1["pso"]["runs"]])
    plot_convergence(
        ga1, pso1,
        ylabel="Raw accuracy",
        output=PICS_DIR / "part1_convergence.png",
        refs=[(GLOBAL_BEST_ACC, f"Exhaustive optimum = {GLOBAL_BEST_ACC}")],
    )
    ga1_masks = [r["mask"] for r in part1["ga"]["runs"]]
    pso1_masks = [r["mask"] for r in part1["pso"]["runs"]]
    plot_feature_freq(
        feature_counts(ga1_masks),
        feature_counts(pso1_masks),
        n_runs=len(ga1_masks),
        output=PICS_DIR / "part1_feature_freq.png",
    )

    with PART2_JSON.open() as fp:
        part2 = json.load(fp)
    ga2 = np.array([fld["ga"]["raw_convergence"] for fld in part2["folds"]])
    pso2 = np.array([fld["pso"]["raw_convergence"] for fld in part2["folds"]])
    plot_convergence(
        ga2, pso2,
        ylabel="Inner 3-fold CV accuracy",
        output=PICS_DIR / "part2_convergence.png",
        refs=None,
    )
    ga2_acc = [fld["ga"]["test_metrics"]["accuracy"] for fld in part2["folds"]]
    pso2_acc = [fld["pso"]["test_metrics"]["accuracy"] for fld in part2["folds"]]
    plot_test_boxplot(ga2_acc, pso2_acc, output=PICS_DIR / "part2_test_boxplot.png")
    ga2_masks = [fld["ga"]["mask"] for fld in part2["folds"]]
    pso2_masks = [fld["pso"]["mask"] for fld in part2["folds"]]
    plot_feature_freq(
        feature_counts(ga2_masks),
        feature_counts(pso2_masks),
        n_runs=len(ga2_masks),
        output=PICS_DIR / "part2_feature_freq.png",
    )

    print(f"Saved 5 figures to {PICS_DIR}")


if __name__ == "__main__":
    main()
