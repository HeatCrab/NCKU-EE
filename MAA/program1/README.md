# MAA Program Report I — GA vs PSO

- Author: N26140804 張暐俊 (Group 17, solo)
- Report: `MAA_Program_I_report.pdf`

## Files

| File | Purpose |
|---|---|
| `benchmark.py` | Seven benchmark functions with bounds and known optima |
| `ga.py` | Real-valued GA: tournament (k=3), BLX-α, Gaussian mutation, elitism |
| `pso.py` | Standard PSO: linear inertia 0.9→0.4, c1=c2=2, v_max = 0.2 × range |
| `run_experiment.py` | Driver — runs {GA, PSO} × 7 functions × {100, 1000} iters × 50 seeds, writes `results/experiment_results.json` |
| `plot_results.py` | Reads the JSON, writes figures to `results/plots/` and prints stats tables |

## Environment

Python ≥ 3.11. Dependencies: `numpy`, `matplotlib`. Exact versions pinned in `uv.lock`.

```bash
uv sync
uv run python run_experiment.py   # ~2 min
uv run python plot_results.py
```

Or with pip: `pip install "numpy>=2.4.4" "matplotlib>=3.10.8"`, then run the scripts directly.

## Reproducibility

Each experiment uses `seed = 0..49` (deterministic). `NUM_RUNS = 50`, `POP_SIZE = 50`, `MAX_ITERS = [100, 1000]`. Output paths are resolved as `Path(__file__).parent / "results"`, independent of cwd.

Branin has three global optima; `distance_error` takes the nearest.
