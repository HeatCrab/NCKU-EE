"""
Roundtrip-distance fitness for the TSP, in two flavors.

Part I fitness is the pure roundtrip length (closing edge included). Part II
adds a penalty for every forbidden even-even edge the tour uses, so the search
is steered away from infeasible tours without a hard reject. The factory
functions close over the distance matrix and return a callable taking a tour
permutation, matching the ``fitness_fn(tour) -> float`` contract the GA and PSO
expect.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def roundtrip_distance(tour: np.ndarray, D: np.ndarray) -> float:
    """Total length of the closed tour ``tour[0] -> ... -> tour[-1] -> tour[0]``."""
    idx = np.asarray(tour)
    return float(D[idx, np.roll(idx, -1)].sum())


def build_forbidden_mask(n: int) -> np.ndarray:
    """``(n, n)`` boolean mask of forbidden even-even edges (1-indexed cities).

    Entry ``[i, j]`` is True iff both ``i+1`` and ``j+1`` are even and ``i != j``.
    Symmetric, zero diagonal.
    """
    even = (np.arange(n) + 1) % 2 == 0
    mask = np.outer(even, even)
    np.fill_diagonal(mask, False)
    return mask


def count_forbidden_edges(tour: np.ndarray, forbidden_mask: np.ndarray) -> int:
    """Number of forbidden edges used by the closed tour."""
    idx = np.asarray(tour)
    return int(forbidden_mask[idx, np.roll(idx, -1)].sum())


def penalty_lambda(D: np.ndarray) -> float:
    """Penalty weight ``2 * n * max(D)`` (one forbidden edge dominates any tour)."""
    return 2.0 * D.shape[0] * float(D.max())


def make_part1_fitness(D: np.ndarray) -> Callable[[np.ndarray], float]:
    """Part I: fitness equals pure roundtrip distance."""

    def fitness(tour: np.ndarray) -> float:
        idx = np.asarray(tour)
        return float(D[idx, np.roll(idx, -1)].sum())

    return fitness


def make_part2_fitness(
    D: np.ndarray,
    forbidden_mask: np.ndarray,
    lam: float,
) -> Callable[[np.ndarray], float]:
    """Part II: pure roundtrip distance plus ``lam`` per forbidden edge used."""

    def fitness(tour: np.ndarray) -> float:
        idx = np.asarray(tour)
        nxt = np.roll(idx, -1)
        dist = float(D[idx, nxt].sum())
        forbidden = int(forbidden_mask[idx, nxt].sum())
        return dist + lam * forbidden

    return fitness
