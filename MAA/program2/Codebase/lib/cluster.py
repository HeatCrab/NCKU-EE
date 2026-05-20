"""
KMeans-based clustering with majority-vote label mapping (PLAN §6.6).

The spec treats clustering and classification as co-equal diagnostics, so the
clustering branch is evaluated on the same five metrics as the classification
branch and reuses compute_metrics from the classifier module.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans

from .classifier import ClassificationMetrics, compute_metrics


def _fit_and_map(X_train, y_train, n_clusters, random_state):
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    train_clusters = km.fit_predict(X_train)
    mapping = {}
    for c in range(n_clusters):
        in_c = train_clusters == c
        mapping[c] = int(np.round(y_train[in_c].mean())) if in_c.any() else 0
    return km, mapping, train_clusters


def cluster_classify_full(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray | None = None,
    y_eval: np.ndarray | None = None,
    n_clusters: int = 2,
    random_state: int = 0,
) -> ClassificationMetrics:
    """Fit KMeans on X_train, map each cluster to a class label by the
    training-data majority vote, then evaluate the five metrics on X_eval
    (or on X_train itself when X_eval is None, i.e. the Part I
    resubstitution case)."""
    km, mapping, train_clusters = _fit_and_map(
        X_train, y_train, n_clusters, random_state
    )
    if X_eval is None:
        eval_clusters = train_clusters
        eval_y = y_train
    else:
        eval_clusters = km.predict(X_eval)
        eval_y = y_eval

    predicted = np.array([mapping[c] for c in eval_clusters])
    return compute_metrics(eval_y, predicted)


def cluster_classify(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray | None = None,
    y_eval: np.ndarray | None = None,
    n_clusters: int = 2,
    random_state: int = 0,
) -> float:
    """Accuracy-only convenience wrapper around cluster_classify_full."""
    return cluster_classify_full(
        X_train, y_train, X_eval, y_eval, n_clusters, random_state
    ).accuracy
