"""
Benchmark functions for MAA Program Report I.

All functions take a numpy array x of shape (D,) and return a scalar.
Each function also has metadata: dim, bounds, optima_value, optima_pos.
"""

import numpy as np


# --- Unimodal ---

def schwefel_222(x):
    """F2: Schwefel 2.22"""
    return np.sum(np.abs(x)) + np.prod(np.abs(x))


def step(x):
    """F6: Step function"""
    return np.sum((np.floor(x + 0.5)) ** 2)


# --- Multimodal (fixed dimension) ---

def rastrigin(x):
    """F9: Rastrigin"""
    D = len(x)
    return np.sum(x**2 - 10 * np.cos(2 * np.pi * x) + 10)


def griewank(x):
    """F11: Griewank"""
    D = len(x)
    sum_part = np.sum(x**2) / 4000
    prod_part = np.prod(np.cos(x / np.sqrt(np.arange(1, D + 1))))
    return sum_part - prod_part + 1


def _u(x, a, k, m):
    """Helper for Penalized function."""
    result = np.zeros_like(x)
    mask_upper = x > a
    mask_lower = x < -a
    result[mask_upper] = k * (x[mask_upper] - a) ** m
    result[mask_lower] = k * (-x[mask_lower] - a) ** m
    return result


def penalized(x):
    """F13: Penalized"""
    D = len(x)
    term1 = 0.1 * (np.sin(np.pi * 3 * x[0])) ** 2

    term2 = 0.0
    for i in range(D - 1):
        term2 += (x[i] - 1) ** 2 * (1 + (np.sin(3 * np.pi * x[i + 1])) ** 2)
    term2 *= 0.1  # note: the outer 0.1 is part of the {} block

    term3 = (x[D - 1] - 1) ** 2 * (1 + (np.sin(2 * np.pi * x[D - 1])) ** 2)
    term3 *= 0.1  # same outer 0.1

    penalty = np.sum(_u(x, 5, 100, 4))

    # Re-reading the PDF formula more carefully:
    # F13 = 0.1 * { sin^2(pi*3*x1) + sum[(xi-1)^2 * (1+sin^2(3*pi*x_{i+1}))]
    #              + (xD-1)^2 * (1+sin^2(2*pi*xD)) } + sum[u(xi,5,100,4)]
    return term1 + term2 + term3 + penalty


# Kowalik data (Table A.2)
_KOWALIK_A = np.array([
    0.1957, 0.1947, 0.1735, 0.1600, 0.0844,
    0.0627, 0.0456, 0.0342, 0.0342, 0.0235, 0.0246
])
_KOWALIK_B_INV = np.array([
    0.25, 0.5, 1, 2, 4,
    6, 8, 10, 12, 14, 16
])
_KOWALIK_B = 1.0 / _KOWALIK_B_INV


def kowalik(x):
    """F15: Kowalik (4D)"""
    x1, x2, x3, x4 = x[0], x[1], x[2], x[3]
    b = _KOWALIK_B
    numerator = x1 * (b**2 + b * x2)
    denominator = b**2 + b * x3 + x4
    return np.sum((_KOWALIK_A - numerator / denominator) ** 2)


def branin(x):
    """F17: Branin (2D, asymmetric bounds)"""
    x1, x2 = x[0], x[1]
    term1 = (x2 - (5.1 / (4 * np.pi**2)) * x1**2 + (5 / np.pi) * x1 - 6) ** 2
    term2 = 10 * (1 - 1 / (8 * np.pi)) * np.cos(x1)
    return term1 + term2 + 10


# --- Function registry ---

FUNCTIONS = {
    "Schwefel 2.22": {
        "func": schwefel_222,
        "dim": 2,
        "bounds": [(-10, 10)] * 2,
        "optima_value": 0.0,
        "optima_pos": np.array([0.0, 0.0]),
    },
    "Step": {
        "func": step,
        "dim": 2,
        "bounds": [(-100, 100)] * 2,
        "optima_value": 0.0,
        "optima_pos": np.array([0.0, 0.0]),
    },
    "Rastrigin": {
        "func": rastrigin,
        "dim": 2,
        "bounds": [(-5.12, 5.12)] * 2,
        "optima_value": 0.0,
        "optima_pos": np.array([0.0, 0.0]),
    },
    "Griewank": {
        "func": griewank,
        "dim": 2,
        "bounds": [(-600, 600)] * 2,
        "optima_value": 0.0,
        "optima_pos": np.array([0.0, 0.0]),
    },
    "Penalized": {
        "func": penalized,
        "dim": 2,
        "bounds": [(-50, 50)] * 2,
        "optima_value": 0.0,
        "optima_pos": np.array([1.0, 1.0]),  # x*=1 for all dims
    },
    "Kowalik": {
        "func": kowalik,
        "dim": 4,
        "bounds": [(-5, 5)] * 4,
        "optima_value": 0.0003075,
        "optima_pos": np.array([0.1928, 0.1908, 0.1231, 0.1358]),
    },
    "Branin": {
        "func": branin,
        "dim": 2,
        "bounds": [(-5, 10), (0, 15)],
        "optima_value": 0.398,
        "optima_pos": np.array([np.pi, 2.275]),
        "all_optima_pos": [
            np.array([-np.pi, 12.275]),
            np.array([np.pi, 2.275]),
            np.array([9.42478, 2.475]),
        ],
    },
}
