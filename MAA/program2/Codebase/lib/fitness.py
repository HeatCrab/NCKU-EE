"""
Penalized fitness for feature-subset selection, with integer-mask caching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .classifier import fit_predict_accuracy
from .data import N_FEATURES, mask_to_columns


def bits_to_int(bits: np.ndarray, n_features: int = N_FEATURES) -> int:
    """LSB-first bit-packing, matching data.mask_to_columns."""
    mask = 0
    for i in range(n_features):
        if bits[i]:
            mask |= 1 << i
    return mask


@dataclass
class FitnessFunction:
    accuracy_fn: Callable[[np.ndarray], float]
    lambda_penalty: float = 0.005
    n_features: int = N_FEATURES
    cache: dict[int, float] = field(default_factory=dict)
    raw_accuracy: dict[int, float] = field(default_factory=dict)
    n_evaluations: int = 0
    n_cache_hits: int = 0

    def __call__(self, bits: np.ndarray) -> float:
        mask = bits_to_int(bits, self.n_features)
        if mask == 0:
            return float("-inf")
        if mask in self.cache:
            self.n_cache_hits += 1
            return self.cache[mask]
        cols = mask_to_columns(mask, self.n_features)
        acc = float(self.accuracy_fn(cols))
        size_ratio = mask.bit_count() / self.n_features
        score = acc - self.lambda_penalty * size_ratio
        self.cache[mask] = score
        self.raw_accuracy[mask] = acc
        self.n_evaluations += 1
        return score


def make_resub_fitness(
    X: np.ndarray,
    y: np.ndarray,
    lambda_penalty: float = 0.005,
) -> FitnessFunction:
    def evaluate(cols: np.ndarray) -> float:
        X_sub = X[:, cols]
        return fit_predict_accuracy(X_sub, y, X_sub, y)

    return FitnessFunction(accuracy_fn=evaluate, lambda_penalty=lambda_penalty)
