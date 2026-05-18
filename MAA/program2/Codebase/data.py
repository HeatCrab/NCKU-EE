"""
Load and preprocess the UCI Early Stage Diabetes Risk Prediction dataset (#529).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "Data" / "diabetes_data_upload.csv"

N_FEATURES = 16

SYMPTOM_COLUMNS = (
    "Polyuria",
    "Polydipsia",
    "sudden weight loss",
    "weakness",
    "Polyphagia",
    "Genital thrush",
    "visual blurring",
    "Itching",
    "Irritability",
    "delayed healing",
    "partial paresis",
    "muscle stiffness",
    "Alopecia",
    "Obesity",
)

FEATURE_ORDER = ("Age", "Gender", *SYMPTOM_COLUMNS)

_EXPECTED_GENDER = {"Male", "Female"}
_EXPECTED_YESNO = {"Yes", "No"}
_EXPECTED_CLASS = {"Positive", "Negative"}


def _check_categorical(series: pd.Series, allowed: set[str], col: str) -> None:
    unexpected = set(series.unique()) - allowed
    if unexpected:
        raise ValueError(f"column {col!r} has unexpected values: {sorted(unexpected)}")


def load_dataset(
    path: Path | str = DATA_PATH,
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    df = pd.read_csv(path)

    if len(df) != 520:
        raise ValueError(f"expected 520 rows, got {len(df)}")
    if df.isna().any().any():
        raise ValueError("dataset has missing values; spec says none should exist")

    _check_categorical(df["Gender"], _EXPECTED_GENDER, "Gender")
    for col in SYMPTOM_COLUMNS:
        _check_categorical(df[col], _EXPECTED_YESNO, col)
    _check_categorical(df["class"], _EXPECTED_CLASS, "class")

    encoded = pd.DataFrame(index=df.index)
    encoded["Age"] = df["Age"].astype(float)
    encoded["Gender"] = (df["Gender"] == "Male").astype(int)
    for col in SYMPTOM_COLUMNS:
        encoded[col] = (df[col] == "Yes").astype(int)

    X = encoded[list(FEATURE_ORDER)].to_numpy(dtype=float)
    y = (df["class"] == "Positive").astype(int).to_numpy()

    if X.shape != (520, N_FEATURES):
        raise ValueError(f"unexpected X shape {X.shape}")

    return X, y, FEATURE_ORDER


def fit_age_scaler(X_train: np.ndarray) -> tuple[float, float]:
    age = X_train[:, 0]
    mean = float(age.mean())
    std = float(age.std(ddof=0))
    if std == 0:
        std = 1.0
    return mean, std


def apply_age_scaler(X: np.ndarray, mean: float, std: float) -> np.ndarray:
    out = X.copy()
    out[:, 0] = (X[:, 0] - mean) / std
    return out


def mask_to_columns(mask: int, n_features: int = N_FEATURES) -> np.ndarray:
    """Bit i (LSB-first) -> column i in FEATURE_ORDER."""
    if mask <= 0 or mask >= (1 << n_features):
        raise ValueError(f"mask {mask} out of range for {n_features} features")
    cols = [i for i in range(n_features) if (mask >> i) & 1]
    return np.array(cols, dtype=int)
