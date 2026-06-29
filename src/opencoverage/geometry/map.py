"""Polygon map representation backed by Shapely."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from opencoverage.geometry.transforms import rotate_polygon
from opencoverage.models import GeodeticCoordinate


@dataclass
class SurveyMap:
    """Survey area defined as a local-meter polygon."""

    polygon: Polygon
    reference: GeodeticCoordinate | None = None
    home: GeodeticCoordinate | None = None
    takeoff: GeodeticCoordinate | None = None
    _home_local: tuple[float, float] | None = field(default=None, repr=False)

    @classmethod
    def from_polygon(cls, polygon: Polygon, **kwargs) -> SurveyMap:
        """Create a map from an existing Shapely polygon."""
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError("Survey polygon must be non-empty and valid")
        return cls(polygon=polygon, **kwargs)

    def copy(self) -> SurveyMap:
        """Return a shallow copy of the map."""
        return SurveyMap(
            polygon=Polygon(self.polygon),
            reference=self.reference,
            home=self.home,
            takeoff=self.takeoff,
            _home_local=self._home_local,
        )

    def rotated_copy(self, angle_rad: float) -> SurveyMap:
        """Return a new map with the polygon rotated by angle_rad."""
        rotated = rotate_polygon(self.polygon, angle_rad)
        return SurveyMap(
            polygon=rotated,
            reference=self.reference,
            home=self.home,
            takeoff=self.takeoff,
            _home_local=self._home_local,
        )

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Return polygon axis-aligned bounds (minx, miny, maxx, maxy)."""
        return self.polygon.bounds

    @property
    def vertices(self) -> np.ndarray:
        """Return exterior vertices as an (N, 2) array."""
        coords = list(self.polygon.exterior.coords[:-1])
        return np.asarray(coords, dtype=float)

    def extreme_vertices(self) -> dict[str, tuple[float, float]]:
        """Return left, right, top, and bottom vertices of the polygon."""
        coords = list(self.polygon.exterior.coords[:-1])
        left = min(coords, key=lambda p: p[0])
        right = max(coords, key=lambda p: p[0])
        bottom = min(coords, key=lambda p: p[1])
        top = max(coords, key=lambda p: p[1])
        return {"left": left, "right": right, "bottom": bottom, "top": top}

    def sweep_width(self) -> float:
        """Return horizontal extent used for back-and-forth sweep planning."""
        extremes = self.extreme_vertices()
        return extremes["right"][0] - extremes["left"][0]

    def sweep_height(self) -> float:
        """Return vertical extent of the polygon."""
        extremes = self.extreme_vertices()
        return extremes["top"][1] - extremes["bottom"][1]

    def intersect_vertical_line(self, x: float) -> list[tuple[float, float]]:
        """
        Intersect the polygon with a vertical line at coordinate x.

        Returns intersection points sorted by ascending y.
        """
        minx, miny, maxx, maxy = self.bounds
        line = LineString([(x, miny - 1.0), (x, maxy + 1.0)])
        intersection = self.polygon.intersection(line)

        points: list[tuple[float, float]] = []
        if intersection.is_empty:
            return points

        if isinstance(intersection, Point):
            points.append((intersection.x, intersection.y))
        elif intersection.geom_type == "MultiPoint":
            points.extend((point.x, point.y) for point in intersection.geoms)
        elif intersection.geom_type == "LineString":
            points.extend(intersection.coords)
        elif intersection.geom_type == "MultiLineString":
            for segment in intersection.geoms:
                points.extend(segment.coords)

        unique: list[tuple[float, float]] = []
        seen: set[tuple[float, float]] = set()
        for point in sorted(points, key=lambda p: p[1]):
            key = (round(point[0], 9), round(point[1], 9))
            if key not in seen:
                seen.add(key)
                unique.append(point)
        return unique

    def replace_polygon(self, polygon: Polygon) -> None:
        """Replace the internal polygon, for example after rotation."""
        self.polygon = polygon
