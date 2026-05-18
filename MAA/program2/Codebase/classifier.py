"""
Logistic Regression wrapper and the five classification metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f_measure: float

    def as_dict(self) -> dict[str, float]:
        return {
            "accuracy": self.accuracy,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "precision": self.precision,
            "f_measure": self.f_measure,
        }


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> ClassificationMetrics:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))

    n = tp + tn + fp + fn
    accuracy = (tp + tn) / n if n else 0.0
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    f_measure = (
        2 * precision * sensitivity / (precision + sensitivity)
        if (precision + sensitivity)
        else 0.0
    )

    return ClassificationMetrics(
        accuracy=accuracy,
        sensitivity=sensitivity,
        specificity=specificity,
        precision=precision,
        f_measure=f_measure,
    )


def make_lr(random_state: int = 0) -> LogisticRegression:
    # max_iter=1000: sklearn default 100 fails to converge on small subsets.
    return LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        random_state=random_state,
    )


def fit_predict_accuracy(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray,
    y_eval: np.ndarray,
    random_state: int = 0,
) -> float:
    model = make_lr(random_state=random_state)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_eval)
    return float(np.mean(y_pred == y_eval))


def fit_predict_full(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray,
    y_eval: np.ndarray,
    random_state: int = 0,
) -> ClassificationMetrics:
    model = make_lr(random_state=random_state)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_eval)
    return compute_metrics(y_eval, y_pred)
