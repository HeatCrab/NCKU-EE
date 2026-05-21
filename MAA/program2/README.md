# MAA Program Report II-2 — Diabetes Risk Prediction via GA/PSO Feature Selection

- Author: N26140804 張暐俊 (Group 17, solo)
- Report: `Report/Report.pdf`
- Dataset: UCI Early Stage Diabetes Risk Prediction (520 rows × 17 columns, 320 Positive / 200 Negative)

## Layout

| Path | Purpose |
|---|---|
| `Codebase/lib/data.py` | CSV loading, categorical encoding, Age scaler fit/apply |
| `Codebase/lib/classifier.py` | Logistic Regression wrapper and 5-metric computation |
| `Codebase/lib/fitness.py` | Fitness dataclass with integer-mask cache and empty-mask sentinel |
| `Codebase/lib/ga.py` | Binary GA: tournament k=3, uniform crossover, bit-flip mutation, elitism |
| `Codebase/lib/pso.py` | PSO in [0,1]^16 with 0.5 threshold, inertia 0.9→0.4, c1=c2=2 |
| `Codebase/lib/cluster.py` | KMeans wrapper with majority-vote label mapping |
| `Codebase/exhaustive_baseline.py` | Enumerates all 65,535 non-empty 16-bit masks |
| `Codebase/run_part1.py` | Part I: train = test resubstitution, 30 seeds, pop = 50, max_iter = 100 |
| `Codebase/run_part2.py` | Part II: 10 × 5-fold stratified CV (50 outer folds), inner 3-fold CV fitness |
| `Codebase/plot_results.py` | Reads `Results/` JSON and writes the five figures used in the report |
| `Data/diabetes_data_upload.csv` | UCI dataset |
| `Results/exhaustive/` | Exhaustive sweep output (`accuracies.npy`, `summary.json`) |
| `Results/part1/part1_results.json` | Part I 30-seed × 2-algorithm log |
| `Results/part2/part2_results.json` | Part II 50-fold × 2-algorithm log |
| `Report/Report.pdf` | Final report |
| `Report/Pics/` | Five figures referenced by the report |

## Environment

Python ≥ 3.11. Dependencies: `numpy`, `scikit-learn`, `matplotlib`, `pandas`. Exact versions pinned in `uv.lock`.

```bash
uv sync
uv run python Codebase/exhaustive_baseline.py   # ~80 s
uv run python Codebase/run_part1.py             # ~41 s
uv run python Codebase/run_part2.py             # ~180 s
uv run python Codebase/plot_results.py          # reads Results/, writes Report/Pics/
```

Or with pip: `pip install "numpy>=2.4.4" "scikit-learn>=1.8.0" "matplotlib>=3.10.8" "pandas>=3.0.3"`, then run the scripts the same way.

## Reproducibility

Seeds are deterministic. Part I uses `seed = 0..29` for each of GA and PSO. Part II uses `seed = fold_index ∈ 0..49`. Shared search settings: `POP_SIZE = 50`, `MAX_ITER = 100`, `LAMBDA = 0.005` (feature-count penalty). LR configuration: `solver = 'lbfgs'`, `C = 1.0`, `max_iter = 1000`, threshold 0.5.

In Part II the Age z-score scaler is fit on the outer training fold only, so the outer test fold never enters the search loop.
