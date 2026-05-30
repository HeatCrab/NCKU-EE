# MAA Program III — Codebase PLAN

**Scope**: This document specifies the code structure, algorithm design, experiment protocol, and output artifacts for Program III. It does **not** cover report writing. Once experiments are complete and all artifacts listed in §9 are in place, this document is archived to `Archive/`.

---

## §1 Task Definition

Implement two metaheuristic algorithms (GA and PSO) to solve the TSP on instance 24 (52 cities) of the TSPLIB dataset, and compare their performance across different city subsets and connectivity constraints.

- **Part I**: For each of three city subsets (first 12, first 30, all 52), run both GA and PSO and compare four metrics: Best Distance, Best fitness value, Average Distance, Computation Time. All tours are roundtrips (closing edge included).
- **Part II**: First 30 cities only. Edges between even-numbered cities are forbidden (1-indexed; forbidden set = `{2, 4, ..., 30}`). Fitness includes a penalty term. Tours are also roundtrips.

Algorithm count = 2 (spec requires ≥ 2; minimum chosen). Part I has 6 cells (2 algos × 3 subsets), Part II has 2 cells (2 algos × 1 subset), 8 cells total.

---

## §2 Data Pipeline

Source: `MAA/program3/Data/tsp_dataset.csv` (raw Kaggle download, 215.5 MB, added to root `.gitignore`; user downloaded manually and placed at this path).

`Codebase/lib/data.py` provides `load_instance_24() -> (coords: np.ndarray[52, 2], D: np.ndarray[52, 52])`:

1. Read the entire CSV with `pandas.read_csv`.
2. Filter `instance_id == 24` and take that row.
3. Parse the `city_coordinates` string column into a `(52, 2)` numpy array (use `ast.literal_eval`, **not** `eval`).
4. Parse the `distance_matrix` string column into a `(52, 52)` numpy array, named `D_csv` (same `ast.literal_eval` policy).
5. Compute pairwise Euclidean distance to obtain `D_self`; verify `np.max(np.abs(D_self - D_csv)) < 1e-6`, raise `ValueError` otherwise.
6. Return `(coords, D_self)`. **All downstream experiments use `D_self`** to avoid float-truncation noise from CSV string serialization.

Verification runs once at startup; passing it is treated as evidence that dataset and spec agree.

---

## §3 Subset Construction

A subset is `coords[:K]` (first K entries in the original CSV `city_coordinates` list order), K ∈ {12, 30, 52}. The corresponding distance matrix is `D[:K, :K]`.

The "first" in "first K" refers to list order; no sorting or ID re-numbering is introduced.

---

## §4 Part II — Forbidden Edge Encoding

**Forbidden scope**: All edges between any two cities in the 1-indexed set `{2, 4, ..., 30}` (even–even edges). Even–odd and odd–odd edges remain available. Number of forbidden edges = C(15, 2) = 105, which is 24.1% of the C(30, 2) = 435 edges in the 30-city complete graph.

**Data structures**:
- `D` — full Euclidean distance matrix (no 0-sentinel substitution).
- `forbidden_mask` — `(30, 30)` boolean matrix; `forbidden_mask[i, j] = True` iff `(i+1) % 2 == 0 and (j+1) % 2 == 0 and i != j` (in code i, j are 0-indexed; physical meaning maps to 1-indexed even numbers). Symmetric; diagonal is False.

**Correspondence to the instructor's "even encoded as 0" hint**: In class the instructor hinted that forbidden edges are represented as 0 in the distance matrix (including the partial fragment "起點的 even 是 0", presumably referring to the 0 sentinel at even–even positions in the matrix's upper-left). For clarity of fitness computation, this implementation keeps `D` complete and maintains `forbidden_mask` separately. For reporting purposes a visualized matrix `D_visual = D * (1 - forbidden_mask.astype(float))` can be produced to match the hint.

---

## §5 Algorithm 1 — Genetic Algorithm (permutation variant)

`Codebase/lib/ga.py`, signature: `ga_minimize(fitness_fn, n, *, rng, **params) -> (best_tour, best_fitness, history)`.

| Item | Setting |
|---|---|
| Encoding | Permutation: length-n `np.ndarray[int]` of city indices, each city exactly once |
| Population size | 100 |
| Selection | Tournament k=3 |
| Elitism | Top 2 individuals carry directly to next generation |
| Crossover | OX (Order Crossover), rate = 0.8 |
| Mutation | Swap mutation, per-individual rate = 1.0 (every non-elite individual is mutated by one swap); swap positions chosen uniformly from distinct indices |
| Max iterations | 500 |
| Stopping | Fixed at max iter (no convergence-based early stop) |

**OX crossover**: For parent1, pick a random segment `[a, b)` and copy it into child1 at the same positions. Fill remaining positions of child1 with cities from parent2 (in parent2's order, skipping those already placed), starting at position b and wrapping around. Symmetric construction yields child2. Both children are valid permutations.

**Swap mutation**: Pick two distinct indices uniformly and swap their contents. Simple, preserves permutation validity.

The skeleton (initialize → loop → tournament select → crossover → mutate → elitism → record history) reuses Program II's `lib/ga.py` layout. Operators are rewritten for permutation encoding.

---

## §6 Algorithm 2 — Particle Swarm Optimization (random-keys variant)

`Codebase/lib/pso.py`, signature: `pso_minimize(fitness_fn, n, *, rng, **params) -> (best_tour, best_fitness, history)`.

**Random-keys encoding**: Each particle's position `x ∈ R^n` has each dimension sampled independently from `[0, 1]`. **Before fitness evaluation**, compute `tour = np.argsort(x)` to obtain a valid permutation; only the permutation is passed to `fitness_fn`. Velocity updates remain in continuous space and follow the standard PSO formula unchanged from Program I/II. Position is neither repaired nor wrapped.

| Item | Setting |
|---|---|
| Swarm size | 50 |
| Position dim | n (number of cities) |
| Position init | `Uniform(0, 1)` per dim |
| Velocity init | `Uniform(-0.1, 0.1)` per dim |
| Inertia ω | Linear decrease from 0.9 to 0.4 over iterations |
| Cognitive c1 | 1.5 |
| Social c2 | 1.5 |
| Velocity clamp | `±0.5` per dim per step |
| Position clamp | None (argsort depends on order, not magnitude) |
| Max iterations | 500 |
| Stopping | Fixed at max iter |

Update: `v ← ω·v + c1·r1·(pbest - x) + c2·r2·(gbest - x)`, with `r1, r2 ~ Uniform(0, 1)^n`, then `x ← x + v`.

The skeleton reuses Program II's `lib/pso.py`; the only differences are the argsort step before evaluation and the removal of the binary/sigmoid step from Program II.

---

## §7 Fitness Functions

`Codebase/lib/fitness.py`.

**Part I**: roundtrip total distance.
```
f_part1(tour, D) = sum(D[tour[k], tour[k+1]] for k in 0..n-2) + D[tour[-1], tour[0]]
```
In this setting Best Distance and Best fitness value are **the same number** (both metrics report identical values).

**Part II**: roundtrip total distance plus forbidden-edge penalty.
```
edges = [(tour[k], tour[k+1]) for k in 0..n-2] + [(tour[-1], tour[0])]
f_part2(tour, D, forbidden_mask) = sum(D[i, j] for (i, j) in edges)
                                 + λ × sum(forbidden_mask[i, j] for (i, j) in edges)
```
where
```
λ = 2 × n × max(D)
```
For n = 30 and `max(D[:30, :30])` on the order of ~120 (a 100×100 box diagonal), λ ≈ 7200. This is large enough that the penalty from a single forbidden edge exceeds the total distance differential of any feasible tour, so algorithms heavily prefer "no forbidden edges" solutions. Yet the penalty (rather than a hard reject) provides a usable gradient during early generations, when populations may still contain infeasible individuals.

In Part II, Best Distance (pure distance component) and Best fitness value (with penalty) are **reported separately**:
- If the best tour uses no forbidden edges: the two are equal.
- If the best tour still uses forbidden edges (algorithm did not converge to fully feasible): fitness exceeds distance by λ × (forbidden-edge count). Reporting both columns surfaces this case.

---

## §8 Experiment Protocol

**Cell enumeration** (8 cells total):

| Cell | Algorithm | Subset | Part | Fitness |
|---|---|---|---|---|
| 1 | GA | 12 | I | `f_part1` |
| 2 | GA | 30 | I | `f_part1` |
| 3 | GA | 52 | I | `f_part1` |
| 4 | PSO | 12 | I | `f_part1` |
| 5 | PSO | 30 | I | `f_part1` |
| 6 | PSO | 52 | I | `f_part1` |
| 7 | GA | 30 | II | `f_part2` |
| 8 | PSO | 30 | II | `f_part2` |

**Repetitions**: 30 runs per cell, seeds `0..29`, injected via `np.random.default_rng(seed)`. GA and PSO share the same seed sequence so that, at a given seed, both algorithms start from the same random state.

**Timing**: each run wraps the algorithm's main loop with `time.perf_counter()` (initialization included; data loading, fitness function setup, and seed setup excluded).

**Representative run per cell**: the run with the lowest **fitness** (not pure distance) is the cell's representative. Its tour is the "best tour" shown in route plots and stored in `best_tours.json` (§9). This ties Best Distance and Best fitness to the same tour and prevents reporting mismatched numbers from different runs in Part II.

**Reported metrics** (each cell summarizes 30 runs):
- **Best Distance**: the representative run's pure distance (Part I and Part II).
- **Best fitness value**: the representative run's fitness (Part I: equals Best Distance; Part II: penalty-inclusive value, equals Best Distance iff the representative tour uses no forbidden edges).
- **Average Distance**: arithmetic mean of per-run best-tour pure distances over 30 runs.
- **Computation Time**: arithmetic mean of per-run wall-clock times over 30 runs (seconds).
- **Forbidden Edge Count** (Part II only): number of forbidden edges in the representative tour; 0 means fully feasible.
- **Min Pure Distance** (Part II only, diagnostic): the minimum pure distance across the 30 runs, regardless of feasibility. If lower than Best Distance, then some other (infeasible) run had a shorter raw distance than the representative — surface this discrepancy in the report rather than hiding it.

**Infeasibility policy**: if a cell's representative tour uses ≥ 1 forbidden edge, mark the cell as `infeasibility_flag = true` in `part2_results.json` and proceed. No retry, no repair, no seed re-roll. The report discusses why the algorithm failed to find a fully feasible tour.

**Convergence curve**: every run also records best-so-far fitness at each iteration, stored as a length-501 array (including iter 0, the best of the initial population). Used for plotting.

---

## §9 Output Artifacts

PLAN-archive criterion: every file below exists, and `run_part1.py` + `run_part2.py` reproduce consistent results from a clean environment.

<!-- requirements.txt was dropped after M1. Program I and II ship no such file;
     the real environment contract is the shared uv project at the MAA/ level
     (pyproject.toml + uv.lock + .python-version), which pins versions more
     strictly than a loose requirements.txt and is what gets committed for the
     grader. A Codebase-level requirements.txt would be both redundant and
     inconsistent with the established layout. This supersedes M0 finding #5. -->

**Code**:
- `Codebase/lib/__init__.py`
- `Codebase/lib/data.py` — instance 24 load + verification (§2)
- `Codebase/lib/fitness.py` — Part I / Part II fitness (§7)
- `Codebase/lib/ga.py` — GA permutation variant (§5)
- `Codebase/lib/pso.py` — PSO random-keys variant (§6)
- `Codebase/run_part1.py` — runs cells 1–6, writes results JSON + convergence npz + best_tours
- `Codebase/run_part2.py` — runs cells 7–8, writes results JSON + convergence npz + best_tours
- `Codebase/plot_results.py` — reads `Results/` and produces all figures

<!-- Smoke-test affordance (added at M1): the three scripts take optional
     argparse flags whose defaults equal the spec values, so a quick correctness
     run can use a reduced workload without touching the real Results/ output.
       run_part{1,2}.py : --seeds (default 30), --max-iter (default 500),
                          --out (default Results/part{1,2})
       plot_results.py  : --results-root (default Results/)
     The full experiment is just the no-flag invocation. The M1 smoke test ran
     --seeds 3 --max-iter 25 into a throwaway dir and confirmed: distance-matrix
     self-verification passes, both algorithms emit valid tours, the Part II
     penalty/infeasibility path fires correctly, and all 10 figures render. -->


**Data results**:
- `Results/part1/part1_results.json` — 6 cells × {Best Distance, Best fitness, Average Distance, Computation Time}
- `Results/part2/part2_results.json` — 2 cells × {Best Distance, Best fitness, Average Distance, Computation Time, Forbidden Edge Count, Min Pure Distance, infeasibility_flag}
- `Results/part1/convergence.npz` — shape `(6, 30, 501)`, dims = (cell, run, iter)
- `Results/part2/convergence.npz` — shape `(2, 30, 501)`, dims = (cell, run, iter)
- `Results/part1/best_tours.json` — for each of the 6 cells: representative run's seed, tour (length-K int list), pure distance, fitness
- `Results/part2/best_tours.json` — for each of the 2 cells: representative run's seed, tour (length-30 int list), pure distance, fitness, forbidden_edge_count, infeasibility_flag

**Figures**:
- `Results/figures/route_part1_{algo}_{K}.png` — representative tour visualization, algo ∈ {ga, pso}, K ∈ {12, 30, 52}, 6 plots total. City labels in plot annotations are 1-indexed.
- `Results/figures/route_part2_{algo}.png` — Part II representative tour, with forbidden edges marked in red dashed lines if any are used, 2 plots total. City labels are 1-indexed; even-numbered cities are highlighted distinctly so the reader can verify the forbidden-edge interpretation.
- `Results/figures/convergence_part1.png` — convergence panel over 6 cells (mean ± std envelope across 30 runs)
- `Results/figures/convergence_part2.png` — convergence panel over 2 cells

Material in `Results/figures/` will be consumed by the report-writing stage; report writing itself is out of scope here.

---

## Frozen Decisions (not re-litigated)

- **Algorithm pair**: GA + PSO (PSO via random-keys variant). Confirmed in the 2026-05-25 session, after a brief detour through a "switch to GA + ACO" proposal that was abandoned.
- **Data source**: raw Kaggle CSV downloaded manually to `Data/tsp_dataset.csv`; every run filters in-memory; no separate trimmed copy is kept.
- **Part II forbidden scope**: even–even edges only (1-indexed `{2, ..., 30}` pairwise).
- **Forbidden-edge handling**: full `D` + independent `forbidden_mask` + penalty term. Not a hard reject; not a 0-sentinel substitution into `D`.
- **Stopping**: 500 iterations fixed; no early-stop.
- **Seeds**: 30 runs per cell.
- **Part II tours are roundtrips**: follows Discussion (II)'s "Best Roundtrip route for Parts I **and II**", which overrides the Part II body's "shortest route **path**" phrasing.
