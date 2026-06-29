"""Optional GPU backend helpers (CuPy). CPU is always the default."""

from __future__ import annotations

from typing import Any


def cupy_available() -> bool:
    """Return True when CuPy is installed and a CUDA device is accessible."""
    try:
        import cupy as cp

        return cp.cuda.is_available()
    except ImportError:
        return False


def get_array_module(prefer_gpu: bool = False) -> Any:
    """
    Return NumPy or CuPy for numeric kernels.

    GPU is only selected when explicitly requested and CuPy is available.
    """
    if prefer_gpu:
        try:
            import cupy as cp

            if cp.cuda.is_available():
                return cp
        except ImportError:
            pass

    import numpy as np

    return np
