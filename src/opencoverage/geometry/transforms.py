"""Coordinate transforms for polygons and waypoint paths."""

from __future__ import annotations

import math

import numpy as np
from shapely.affinity import rotate as shapely_rotate
from shapely.geometry import Polygon


def rotate_polygon(polygon: Polygon, angle_rad: float, origin: tuple[float, float] = (0.0, 0.0)) -> Polygon:
    """Rotate a polygon by angle_rad around origin."""
    return shapely_rotate(polygon, angle_rad, origin=origin, use_radians=True)


def rotate_points(
    points: list[tuple[float, float]],
    angle_rad: float,
    origin: tuple[float, float] = (0.0, 0.0),
) -> list[tuple[float, float]]:
    """Rotate a list of 2D points by angle_rad around origin."""
    if not points:
        return []

    ox, oy = origin
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rotated: list[tuple[float, float]] = []

    for x, y in points:
        dx = x - ox
        dy = y - oy
        rotated.append((ox + cos_a * dx - sin_a * dy, oy + sin_a * dx + cos_a * dy))

    return rotated


def rotation_matrix(angle_rad: float) -> np.ndarray:
    """Return a 2x2 rotation matrix for angle_rad."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return np.array([[cos_a, -sin_a], [sin_a, cos_a]], dtype=float)
