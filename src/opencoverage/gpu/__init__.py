"""Optional GPU acceleration backends."""

from opencoverage.gpu._backend import cupy_available, get_array_module

__all__ = ["cupy_available", "get_array_module"]
