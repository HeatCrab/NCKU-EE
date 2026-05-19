"""
KMeans-based clustering with majority-vote label mapping (PLAN §6.6).
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans


def cluster_classify(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray | None = None,
    y_eval: np.ndarray | None = None,
    n_clusters: int = 2,
    random_state: int = 0,
) -> float:
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    train_clusters = km.fit_predict(X_train)

    mapping = {}
    for c in range(n_clusters):
        in_c = train_clusters == c
        mapping[c] = int(np.round(y_train[in_c].mean())) if in_c.any() else 0

    if X_eval is None:
        eval_clusters = train_clusters
        eval_y = y_train
    else:
        eval_clusters = km.predict(X_eval)
        eval_y = y_eval

    predicted = np.array([mapping[c] for c in eval_clusters])
    return float((predicted == eval_y).mean())
