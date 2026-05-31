"""Regenerate Part I route figures as two combined panels (GA row, PSO row).

One figure per algorithm, each a 1x3 grid over the 12/30/52-city subsets, in the
same subplot-grid style as the convergence figure. Reads the existing
``Results/part1/best_tours.json`` and city coordinates; writes
``Report/Pics/route_part1_ga.png`` and ``route_part1_pso.png``.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

from lib.data import load_instance_24
from plot_results import _draw_route


def main():
    root = Path(__file__).resolve().parent.parent
    fig_dir = root / "Report" / "Pics"
    coords_full, _D = load_instance_24()
    best = json.loads((root / "Results" / "part1" / "best_tours.json").read_text())

    for algo in ("ga", "pso"):
        label = "GA" if algo == "ga" else "PSO"
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
        for ax, n in zip(axes, (12, 30, 52)):
            rep = best[f"{algo}_{n}"]
            _draw_route(
                ax,
                coords_full[:n],
                rep["tour"],
                f"Part I {label} K={n} (dist {rep['distance']:.1f})",
            )
        fig.tight_layout()
        out = fig_dir / f"route_part1_{algo}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
