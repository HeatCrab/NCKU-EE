"""
Load instance 24 (52 cities) from the TSPLIB Kaggle dataset.

The raw CSV stores one TSP instance per row. Instance 24 is filtered out,
its coordinate list and distance matrix are parsed, and the distance matrix
is recomputed from the coordinates as a cross-check before any experiment
runs. Downstream code always uses the self-computed matrix to avoid float
truncation noise from the CSV's string serialization.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "Data" / "tsp_dataset.csv"

INSTANCE_ID = 24
N_CITIES = 52


def load_instance_24(path: Path | str = DATA_PATH) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(coords, D)`` for instance 24.

    ``coords`` is ``(52, 2)`` float; ``D`` is the ``(52, 52)`` symmetric
    Euclidean distance matrix computed from ``coords``. Raises ``ValueError``
    if the dataset disagrees with that matrix beyond a 1e-6 tolerance.
    """
    df = pd.read_csv(path)

    rows = df[df["instance_id"] == INSTANCE_ID]
    if len(rows) != 1:
        raise ValueError(f"expected exactly 1 row for instance {INSTANCE_ID}, got {len(rows)}")
    row = rows.iloc[0]

    coords = np.array(ast.literal_eval(row["city_coordinates"]), dtype=float)
    if coords.shape != (N_CITIES, 2):
        raise ValueError(f"unexpected coords shape {coords.shape}")

    d_csv = np.array(ast.literal_eval(row["distance_matrix"]), dtype=float)
    if d_csv.shape != (N_CITIES, N_CITIES):
        raise ValueError(f"unexpected distance_matrix shape {d_csv.shape}")

    diff = coords[:, None, :] - coords[None, :, :]
    d_self = np.sqrt((diff**2).sum(axis=-1))

    max_dev = float(np.max(np.abs(d_self - d_csv)))
    if max_dev >= 1e-6:
        raise ValueError(
            f"self-computed distances disagree with CSV (max deviation {max_dev:.3e})"
        )

    return coords, d_self
