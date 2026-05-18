# Program II-2 Plan: Diabetes Risk Prediction via Metaheuristic Feature Selection

Status: **reviewed by codex 2026-05-17, decisions locked, ready for implementation**.
Author: HeatCrab (N26140804).
Last updated: 2026-05-17.

## 1. Task Selection: II-2 over II-1

The course offers two parallel options:

- **II-1**: Ball-and-beam control. Tune a PID / SMC / FLC controller with GA/PSO/etc.
- **II-2**: Early-stage diabetes risk prediction. Clustering + classification on UCI dataset 529.

We pick **II-2** because:

1. No control-systems background. II-1 needs dynamic-system modelling and controller design knowledge we do not currently have; debugging a divergent simulation without that grounding is an open-ended time sink.
2. II-2 reuses the **GA/PSO operator-level infrastructure already built and validated for Program I**. Structural changes are the chromosome/particle representation (real-valued coordinates → binary feature mask) and the fitness function (benchmark value → classification metric). The experiment runner and plotter are mostly new (see §7).
3. Research-first priority: as a graduate student, course work should not consume cycles that belong to thesis research. II-2 has a tighter, more predictable scope.

## 2. Files for Reviewer Reference

When sending to `/codex-review`, the reviewer should consult:

- `MAA/program2/MAA Program II-2_04 2026.pdf` — official spec.
- `MAA/program2/Archive/MAA Program II-1_04 2026.pdf` — the other option, for context on why II-2 was chosen.
- `MAA/program2/Refs/Likelihood Prediction of Diabetes at Early Stage Using Data Mining Techniques.pdf` — Islam et al. 2019, the paper cited at the end of the spec.
- `MAA/program2/Data/diabetes_data_upload.csv` — the actual dataset (520 rows, 17 columns).
- `MAA/program1/` — Program I source code. Specifically, the reviewer should look at:
  - `program1/ga.py` — current real-valued GA (tournament, BLX-α, Gaussian mutation, elitism). We keep tournament + elitism, replace BLX-α with uniform crossover, replace Gaussian mutation with bit-flip.
  - `program1/pso.py` — current standard PSO (inertia 0.9→0.4, c1=c2=2, velocity clamp). We keep the velocity update and inertia schedule; we add a position-threshold step at evaluation time, plus mask caching and empty-mask handling.
  - `program1/run_experiment.py` — current run-loop / seed-management scaffolding. Patterns reusable; concrete code is benchmark-specific and will be rewritten.
  - `program1/plot_results.py` — current table/plot emission. Style sensibility reusable (booktabs LaTeX tables, log-scale convergence); concrete plotting code is benchmark-specific and will be rewritten for feature-selection visualisations.

## 3. Problem Summary (from the spec)

The spec is two pages. Distilled:

**Task**. Apply metaheuristic-based **feature extraction, clustering, and
classification** to the Early Stage Diabetes Risk Prediction dataset (UCI #529). All
three components are named in both Part I and Part II.

**Part I**. Perform feature extraction, clustering, and classification using the same
data for both training and testing. Report:

- Accuracy
- Sensitivity (= Recall, = True Positive Rate)
- Specificity (= True Negative Rate)
- Precision
- F-measure

**Part II**. Perform **10 repetitions of 5-fold cross-validation** for feature
extraction, clustering, and classification. Report **mean and standard deviation** of
accuracy for both training and testing folds.

**Discussion questions** (at the end of the spec):

1. Do you have to use all the attributes?
2. Is it possible to find the best combination of attributes for the highest
   classification accuracy?

The two questions explicitly point to **feature selection** as the metaheuristic's
role. The "clustering" requirement is handled in parallel: after the metaheuristic
picks a feature subset, we report both a classifier result (LR) and a clustering
result (KMeans on the same subset) — see §6.3 and §6.6.

## 4. Dataset

`Data/diabetes_data_upload.csv` — 520 rows × 17 columns. Verified locally
2026-05-17.

| Column | Type | Notes |
|---|---|---|
| `Age` | integer | Observed range **16–90** (paper bucketed into 6 bins; UCI raw form is integer; the bucket table in the paper is descriptive, not enforced) |
| `Gender` | categorical | `Male` (328) / `Female` (192) |
| 14 symptom columns | categorical | `Yes` / `No` each (Polyuria, Polydipsia, sudden weight loss, weakness, Polyphagia, Genital thrush, visual blurring, Itching, Irritability, delayed healing, partial paresis, muscle stiffness, Alopecia, Obesity) |
| `class` | categorical | `Positive` (320) / `Negative` (200) — target label |

Zero empty cells. Class is imbalanced (62 % positive); we use stratified splits in §8
to preserve this ratio.

Discrepancy with paper: the paper reports 500 instances / 314 positive / 186
negative after preprocessing, while the released UCI version is 520 / 320 / 200 with
no missing values. We use the UCI version as-is.

## 5. Baseline: Islam et al. 2019

The cited paper does **not** use any metaheuristic. It runs four standard classifiers
in WEKA with two evaluation protocols. We use it as a sanity-check baseline.

| Classifier | 10-fold CV | Percentage Split (80:20) |
|---|---|---|
| Naive Bayes (NB) | 87.4 % | 88 % |
| Logistic Regression (LR) | 92.4 % | 91 % |
| J48 Decision Tree | 95.6 % | 95 % |
| **Random Forest (RF)** | **97.4 %** | **99 %** |

Paper-reported per-class metrics (TP/FP rate, Precision, Recall, F-measure) match the
metrics the spec asks for in Part I — useful for cross-checking that our
implementation produces sane numbers.

The **metaheuristic + feature-selection** angle is our contribution, not the paper's.

## 6. Our Approach

### 6.1 Metaheuristic role

Both GA and PSO will search over **feature subsets**. Each candidate solution is a
**16-bit binary mask** (one bit per attribute, excluding `class`). A bit = 1 means
that feature is included in the classifier's input.

This implements the spec's "feature (attribute) extraction" requirement directly and
answers the two discussion questions.

### 6.2 Algorithms: GA + PSO

Sticking with **GA and PSO** for continuity with Program I and to keep scope bounded.

**GA** changes from Program I:

- Genome: binary string of length 16 (was: real vector).
- Crossover: **uniform crossover** with per-bit swap probability 0.5 (was: BLX-α).
- Mutation: **bit-flip** with per-bit probability 1/16 ≈ 0.0625 (was: Gaussian noise).
- Selection: keep **tournament (k=3)** and elitism unchanged.
- Initialisation: random uniform Bernoulli(0.5) per bit; reject and resample any
  all-zero mask (empty subset is degenerate).

**PSO** changes from Program I:

- Position: continuous in [0, 1]^16; classify a feature as selected if position ≥ 0.5
  at evaluation time. Standard "thresholded continuous BPSO" — keeps the velocity
  update from Program I almost verbatim. We accept this is weaker than Kennedy &
  Eberhart's sigmoid-velocity BPSO, but it minimises code churn and is well-precedented.
- Inertia, c1, c2, velocity clamp: unchanged from Program I.
- **Empty-mask handling**: if a thresholded mask is all-zero, assign it the worst
  possible fitness (`-inf`) so the swarm is pushed back into valid territory rather
  than crashing the classifier.
- **Reporting**: always emit the **thresholded mask** as the solution, not the raw
  continuous position. The position is bookkeeping only.

**Shared optimisation**: both algorithms use a **mask cache** keyed by the integer
representation of the bitmask. Duplicate masks (very common under thresholded PSO
and after GA crossover) hit the cache instead of refitting the classifier. Expected
hit rate is high enough to matter for Part II's compute budget.

### 6.3 Classifier (decision)

**Logistic Regression (LR)** is the single classifier inside the GA/PSO search loop.
Reasons:

- The spec asks about feature selection benefit; LR shows it most cleanly because it
  has no built-in feature selection of its own.
- LR is much faster than RF, which matters because we run it inside the GA/PSO
  inner loop (population × generations × runs × CV folds = a lot of fits).
- One classifier in the loop keeps the report focused on the metaheuristic
  comparison rather than turning into a classifier-shootout (that is the paper's
  contribution, not ours).

**RF baseline (outside the loop)**: we additionally fit Random Forest **once** on the
full dataset with all 16 features, to give a "strong baseline" reference number that
the report can quote against the metaheuristic-selected LR result. Cheap, single fit,
no GA/PSO involvement.

### 6.4 Fitness function (decision)

`fitness(mask) = accuracy(mask) − λ · (|selected| / 16)`, with `λ = 0.005`.

- `accuracy(mask)` is **inner-CV accuracy** in Part II (see §8.2) or full-data
  resubstitution accuracy in Part I.
- λ acts as a **tie-breaker**: when two masks give equivalent classification
  accuracy, the smaller one wins. Too small to override real accuracy differences
  larger than ~0.5 %.
- We always **report raw accuracy separately** in tables, never just the penalised
  composite. This keeps Part I/II metrics directly comparable to the paper.

### 6.5 Preprocessing

Decisions:

- `Yes` / `No` → `1` / `0` for the 14 symptom columns.
- `Male` / `Female` → `1` / `0` for Gender.
- `Positive` / `Negative` → `1` / `0` for the class label.
- **Age**: keep as raw integer (do not bucket as the paper did — the bin thresholds
  are arbitrary and lossy; raw integer is what UCI ships, and Age values up to 90
  exceed the paper's bin range anyway).
- **Standardisation**: z-score Age column only. Symptom and Gender columns stay 0/1.
  Critical for LR convergence because Age has range ~74 while symptoms have range 1.
- No imputation needed (zero empty cells).

### 6.6 Clustering

To satisfy the spec's explicit "clustering" requirement, after each Part I /
Part II evaluation we additionally run `KMeans(n_clusters=2)` on the **selected
features** of the training data:

1. Fit KMeans on `X_train[:, mask]`.
2. Map each cluster to a class label by majority vote of training labels in that
   cluster.
3. Predict test-set labels by cluster assignment + this mapping.
4. Report clustering accuracy alongside classification accuracy.

Clustering is **not** in the GA/PSO objective — the metaheuristic optimises
classification accuracy, and clustering is reported as a parallel view on the same
selected features. This keeps the search clean while satisfying the spec literally.

## 7. Code Architecture

What can be **reused verbatim** from `program1/`: nothing wholesale. The genuine
reuses are operator-level patterns:

- `ga.py` — tournament selection and elitism functions can be copied; crossover and
  mutation must be rewritten for binary genomes.
- `pso.py` — velocity update with inertia schedule can be copied; add the
  thresholding, empty-mask handling, and cache lookup.

What must be **rewritten** (patterns inspire, code does not transfer):

- `run_experiment.py` — current code imports `FUNCTIONS`, loops over benchmark
  functions, and computes distance to known optima. None of that applies. The new
  runner loops over (algorithm, Part-I-or-II, run-seed) and writes JSON.
- `plot_results.py` — current code draws 3D benchmark surfaces and search
  trajectories on 2D contour maps. None of that applies. The new plotter produces
  convergence curves, selected-feature frequency histograms, and confusion
  matrices.

New modules in `program2/Codebase/`:

- `data.py` — CSV load, encoding, train/test split, stratified k-fold iterators.
- `classifier.py` — sklearn-backed LR wrapper exposing `fit`, `predict`, and the 5
  spec metrics (Accuracy, Sensitivity, Specificity, Precision, F-measure).
- `cluster.py` — KMeans wrapper with majority-vote label mapping.
- `fitness.py` — `evaluate_subset(mask, X_train, y_train, mode)` returning the
  penalised fitness; handles mask caching and empty-mask sentinel.
- `ga.py`, `pso.py` — adapted from Program I per the changes above.
- `run_experiment.py` — orchestrates Part I and Part II runs, writes
  `results/experiment_results.json`.
- `exhaustive_baseline.py` — see §8.3.
- `plot_results.py` — emits tables and figures for the report.

Dependency additions to `MAA/pyproject.toml`: `scikit-learn`, `pandas` (for cleaner
CSV handling than stdlib `csv`).

## 8. Experimental Design

### 8.1 Part I protocol

Per the spec: "using the same data for both training and testing". This is
resubstitution, not a real generalisation estimate — the spec asks for it
explicitly, so we comply.

- Train and evaluate LR on all 520 rows.
- GA and PSO each run for **30 independent seeded runs** (seeds 0–29).
- Population 50, max 100 iterations.
- For each algorithm, report: best mask found (across the 30 runs), best fitness,
  full 5-metric breakdown on that mask (Accuracy, Sensitivity, Specificity,
  Precision, F-measure), plus mean ± std of best-fitness across the 30 runs to
  give the algorithm's run-to-run variability.
- Also report the KMeans clustering accuracy on the best mask (§6.6).

### 8.2 Part II protocol (leakage-proof)

Outer evaluation: **10 repetitions × 5-fold StratifiedKFold** → 50 outer folds. The
stratification preserves the 62/38 class ratio in each fold.

For each outer fold:

1. Split into 4 training folds (~416 rows) + 1 test fold (~104 rows).
2. Run **one** GA search and **one** PSO search, **each using only the training
   folds**. Fitness inside the search is computed as **inner 3-fold StratifiedKFold
   accuracy on the training folds** — the outer test fold is never touched during
   search.
3. Take the best mask from each search, retrain LR on the full 4 training folds
   with that mask, and evaluate on the outer test fold.
4. Record outer training-fold accuracy and outer test-fold accuracy for both
   algorithms.

Aggregate: report **mean ± std** of training and testing accuracy across the 50
outer folds, per algorithm. This is what the spec asks for.

Cost: 50 outer folds × 2 algorithms × ~5000 fitness evals per search (pop 50 × 100
iter, before cache) × ~3 inner-CV LR fits = on the order of 1.5 M LR fits before
caching. With mask caching the effective fit count drops by 5–10×. Wall-clock
target: under 30 minutes on the Mac.

### 8.3 Exhaustive LR baseline

The search space is small enough to brute-force: $2^{16} - 1 = 65{,}535$ non-empty
masks. We exhaustively fit LR on every mask using the Part I protocol (full-data
train + eval) and record the global best. This gives:

- A **ground-truth optimum** for Part I — we can state directly whether GA/PSO
  found the global optimum or fell short by how much.
- A **feature-importance map**: the marginal effect of each feature, averaged over
  all masks containing it.
- Concrete evidence for discussion question 2 ("is it possible to find the best
  combination?"). The answer is empirically yes, and we can compare what GA/PSO
  found vs the exhaustive winner.

Expected runtime: 65k × ~1ms per LR fit ≈ 1–2 minutes single-threaded. Trivially
parallelisable if needed.

The exhaustive baseline only makes sense for Part I (resubstitution); for Part II
the outer-fold structure changes per fold, so an exhaustive sweep per fold (50 ×
65k = 3.3M fits) is the wrong tool. Part II stays GA/PSO-only.

### 8.4 Seeds

Deterministic seeds 0–29 for Part I; 0–49 for Part II outer folds. Same pattern as
Program I so results are reproducible.

## 9. Report Pipeline

Markdown → pandoc + xelatex → PDF, per the recipe in
`memory/reference_pandoc_pdf.md` (validated on ESL Project 1). Word is out of the
loop entirely.

`Report/Report.md` will use the same conventions as Program I's `report.md`:

- English headings, Traditional Chinese prose body, English/math for terms and
  tables.
- YAML frontmatter with the page-budget settings from the reference recipe.
- Raw-LaTeX blocks only for tables and side-by-side figure pairs.

Draft section structure:

1. **Introduction** — task, dataset, why metaheuristic feature selection.
2. **Data and Preprocessing** — schema, encodings, train/test setup.
3. **Algorithms** — GA and PSO design choices (binary chromosome, uniform crossover,
   bit-flip mutation for GA; thresholded continuous PSO with mask caching).
4. **Fitness Function and Penalty** — definition, λ choice, raw-vs-penalised
   reporting policy.
5. **Experimental Setup** — population, iterations, runs, seeds, classifier choice,
   inner/outer CV structure, exhaustive baseline.
6. **Discussions** — answers the spec's required items:
   - 6.1 Part I results (5 metrics on best mask, GA vs PSO vs exhaustive)
   - 6.2 Part II results (10 × 5-fold CV mean/std, GA vs PSO)
   - 6.3 Clustering results (KMeans on selected features, Part I and Part II)
   - 6.4 Feature-selection findings (which features survive, frequency map,
     answers to the two discussion questions head-on)
   - 6.5 GA vs PSO comparison (convergence, subset size, run-to-run variance)
7. **Conclusion** — short synthesis.

## 10. Decisions Made (was: Open Questions)

Resolved through codex review and user consensus on 2026-05-17:

1. **Classifier**: **LR only in the search loop**, plus a single all-features RF fit
   as a reference baseline outside the loop.
2. **Fitness penalty**: **λ = 0.005**, used as a tie-breaker; raw accuracy always
   reported separately.
3. **Part I budget**: **30 runs × pop 50 × 100 iter**, plus exhaustive LR baseline
   (§8.3) as ground truth.
4. **Part II depth**: **1 GA search + 1 PSO search per outer fold**, fitness uses
   inner 3-fold StratifiedKFold on training folds only (no outer-test leakage).

## 11. Out of Scope

- No replication of the paper's four-classifier comparison. Our contribution is the
  metaheuristic feature-selection layer, not yet-another-classifier-shootout.
- No end-user web tool (paper §6).
- No deep learning. Dataset too small (520 rows, 16 features).
- No GPU. CPU on Mac handles this comfortably.

## 12. Next Steps

After this plan is approved by user:

1. Set up `MAA/program2/Codebase/` with the modules listed in §7. Add `scikit-learn`
   and `pandas` to `MAA/pyproject.toml`.
2. Implement, starting with `data.py` + `classifier.py` + `exhaustive_baseline.py`
   (the baseline grounds everything else and runs fast).
3. Implement `fitness.py` (with cache), then port `ga.py` and `pso.py`.
4. Implement `run_experiment.py` for Part I, run, sanity-check vs exhaustive
   baseline.
5. Extend `run_experiment.py` for Part II, run.
6. `plot_results.py` for figures and tables.
7. Write `Report/Report.md`, render via pandoc + xelatex.
8. Codex-review the final report before submission.
9. Submit (email to instructor + Moodle if a slot opens).
