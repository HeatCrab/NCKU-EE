# MAA Program Report III — TSP via GA/PSO

- Author: N26140804 張暐俊 (Group 17, solo)
- Report: `Report/Report.pdf`
- Dataset: TSPLIB Kaggle dataset, instance 24 (52 cities)

## Layout

| Path | Purpose |
|---|---|
| `Codebase/lib/data.py` | Loads instance 24, parses coordinates, recomputes the distance matrix as a cross-check |
| `Codebase/lib/fitness.py` | Part I pure roundtrip length; Part II adds a penalty per forbidden edge |
| `Codebase/lib/ga.py` | Permutation GA: tournament k=3, order crossover, swap mutation, elitism 2 |
| `Codebase/lib/pso.py` | Random-keys PSO in [0,1]^n with argsort decoding, inertia 0.9→0.4, c1=c2=1.5 |
| `Codebase/run_part1.py` | Part I: GA and PSO on the first 12, 30, 52 cities, 30 seeds, max_iter 500 |
| `Codebase/run_part2.py` | Part II: first 30 cities, even-numbered cities forbidden to connect |
| `Codebase/plot_results.py` | Reads `Results/` and writes the route and convergence figures to `Report/Pics/` |
| `Results/part1/` | Part I per-run log, convergence curves, representative tours |
| `Results/part2/` | Part II per-run log, convergence curves, representative tours |
| `Report/Report.pdf` | Final report |
| `Report/Pics/` | Figures referenced by the report |

## Dataset

The raw CSV is too large to bundle (225.98 MB). Download `tsp_dataset.csv` from
the Kaggle dataset and place it at `Data/tsp_dataset.csv` (create the `Data/`
folder next to `Codebase/`). The loader filters `instance_id == 24` in memory;
no trimmed copy is kept.

https://www.kaggle.com/datasets/ziya07/traveling-salesman-problem-tsplib-dataset

Only the experiment scripts need the CSV. `plot_results.py` redraws every figure
from `Results/` alone, so the figures reproduce without downloading anything.

## Environment

Python ≥ 3.11. Dependencies: `numpy`, `pandas`, `matplotlib`. Exact versions
pinned in `uv.lock`.

```bash
uv sync
uv run python Codebase/run_part1.py     # GA/PSO over the three subsets
uv run python Codebase/run_part2.py     # Part II with forbidden edges
uv run python Codebase/plot_results.py  # reads Results/, writes Report/Pics/
```

Or with pip: `pip install "numpy>=2.4.4" "pandas>=3.0.3" "matplotlib>=3.10.8"`,
then run the scripts the same way.

## Reproducibility

Seeds are deterministic. Each cell runs `seed = 0..29` for both GA and PSO.
Shared search settings: `max_iter = 500`, GA population 100, PSO swarm 50.
Part II uses the penalty weight `lambda = 2 * n * max(D)`, large enough that any
feasible tour outranks any infeasible one. No repair or retry is applied;
infeasible representatives are flagged rather than fixed.

The loader recomputes the distance matrix from the coordinates and aborts if it
disagrees with the CSV beyond a 1e-6 tolerance, so every run shares one clean
distance source.
