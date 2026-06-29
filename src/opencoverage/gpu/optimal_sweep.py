"""GPU-accelerated optimal sweep angle search."""

from __future__ import annotations

import numpy as np

from opencoverage.gpu._backend import get_array_module


def find_optimal_sweep_angle(
    vertices: np.ndarray,
    n_steps: int = 10_000,
    prefer_gpu: bool = False,
) -> float:
    """
    Find the rotation angle in [0, pi) that minimizes sweep width.

    Parameters
    ----------
    vertices:
        Polygon vertices as an (N, 2) array in local meters.
    n_steps:
        Number of angles to evaluate.
    prefer_gpu:
        Use CuPy when available.
    """
    xp = get_array_module(prefer_gpu)
    points = xp.asarray(vertices, dtype=float)
    x = points[:, 0]
    y = points[:, 1]

    alphas = xp.linspace(0.0, xp.pi, n_steps, endpoint=False)
    cos_a = xp.cos(alphas)[:, xp.newaxis]
    sin_a = xp.sin(alphas)[:, xp.newaxis]

    rotated_x = cos_a * x - sin_a * y
    widths = rotated_x.max(axis=1) - rotated_x.min(axis=1)
    best_index = int(widths.argmin())

    if prefer_gpu and xp.__name__ == "cupy":
        return float(xp.asnumpy(alphas[best_index]))
    return float(alphas[best_index])
