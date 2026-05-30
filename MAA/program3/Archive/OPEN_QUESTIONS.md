# Program III — Open Spec Questions

Status as of 2026-05-21. To be resolved (most likely) by asking 李祖聖 老師 in person at the Monday MAA class (2026-05-25), since the spec ambiguities are broader than initially flagged in the planning memory and waiting on email replies would delay the start.

Source: independent re-read of `MAA Program III_05 2026.pdf` plus an independent Codex scan of the same PDF. Together they surface more than just the two ambiguities the earlier planning notes recorded.

## Priority 1 — must clarify before implementation can start

These have multiple plausible interpretations that lead to materially different code. Implementing the wrong one is rework, not a documentation tweak.

### Q1. Part II — "all the even-numbered cities are not connected"

Two sub-questions wrapped together.

**(a) Index base.** Cities `2, 4, 6, ..., 30` (1-indexed) or `0, 2, 4, ..., 28` (0-indexed)? Same number of constrained cities (15) either way, but the specific set differs.

**(b) Semantics of "not connected".** At least five readings:

1. Drop the even-numbered cities entirely → reduces the problem to TSP on the ~15 odd cities.
2. Keep all 30 cities; forbid edges *between* even cities only (even-odd edges still allowed).
3. Forbid *all* edges touching any even city — makes a feasible tour impossible.
4. Treat the forbidden edges as infinite-penalty rather than truly removed.
5. Something else (custom graph topology).

The spec's hint "the fitness function is different from Part I" weakly favours interpretation #2 or #4 (a 15-city subset has the same fitness shape as Part I, so reading #1 doesn't really demand a different fitness function). But this is inference, not confirmation.

### Q2. Part II — "shortest route path" vs the Discussions' "Best Roundtrip route"

Part II body uses the phrase **route path** (suggests open path A → … → B). Discussion (II) asks to plot the **Best Roundtrip route for Parts I and II** (suggests closed cycle returning to origin). One of these is a typo or both Parts are roundtrip. Worth asking — open vs closed changes the encoding and fitness definition.

### Q3. Part II — fitness function "different from Part I", in what way?

Spec asserts but doesn't define. Implementation candidates:

- Penalty-augmented length: `sum of edge distances + λ × (count of forbidden edges used)`.
- Hard feasibility: reject any individual that uses a forbidden edge (return ∞).
- Distance-matrix modification: set forbidden edges to ∞ inside the matrix, then the algorithm sees a modified TSP with the same Part-I fitness shape.

The instructor may have a specific formulation in mind, or may leave it to the student to justify. Either answer is fine, but the difference matters.

### Q4. "First 12 / first 30 / all 52 cities" — first by what ordering?

Candidate orderings: the order of the `city_coordinates` list as printed in the spec; some canonical ID column after parsing the CSV; row-order of the Kaggle CSV's instance_id 24. These three usually agree but not guaranteed. A one-line confirmation from the instructor resolves it.

## Priority 2 — worth asking opportunistically (if class time allows)

Implementation can still proceed without these, but a brief clarification removes guesswork.

### Q5. Number of repeated runs / seeds

Spec is silent on run count. Program I used 50, Program II used 30 seeds (Part I) / 50 folds (Part II). Default for Program III is unclear. Without a class-wide standard, "Average Distance" comparisons across teams are awkward.

### Q6. "Average Distance" — averaged over what?

Across repeated runs of the same algorithm? Across iterations within a run? Across instances? The column header is ambiguous on its own.

### Q7. "Computation Time" — measured how?

Single run wall-clock? Mean of repeated runs? Time-to-best? Total time across the 3 city-count cases?

## Priority 3 — self-decide, document the choice in the report

No need to ask. Justify the choice in the report and move on.

- "At least two different metaheuristic algorithms" — two algorithm *families* (e.g. GA + ACO) is clearly safer than two variants of the same family. PSO is doable on TSP via permutation-PSO variants but awkward; GA + ACO is the natural pair.
- Stopping condition — pick one (fixed iterations, time budget, convergence threshold) and document.
- Number of plots in the visualization — at minimum one best-route plot per city-count case per algorithm; the instructor will accept more.
- `Best_Route` column in the Kaggle CSV — "encoded as integers", i.e. a categorical target for ML route-prediction tasks, not a coordinate sequence. Not useful for our optimization task. Ignore.

## Notes on Priority 1 items considered but not asked

These could be ambiguities but on closer reading they're resolvable from the spec alone:

- **"20 cities" vs "52 cities" for instance_id 24** — the "20 cities" line is generic Kaggle-style dataset boilerplate. The spec immediately specifies instance 24 = 52 cities, and the embedded coordinate list confirms 52. Use 52, no need to ask.
- **Coordinates vs distance_matrix** — Euclidean distance on the printed coordinates should reproduce the printed matrix. We will verify when ingesting the data; if they disagree, that's a separate question for the instructor.
- **"Best Distance" vs "Best fitness value"** — under the standard TSP fitness `f = total path length`, the two are the same number. The two columns may be redundant on purpose (one labelled "Distance", one labelled "fitness"). If our fitness function later includes a transformation (e.g. penalty term in Part II), the columns will diverge naturally. No clarification needed.

## After the Monday class

Resolved answers should be incorporated into the eventual `Codebase/PLAN.md`. Update this file in place to mark each question as answered (with the answer) rather than deleting, so the rationale stays in the repository.
