"""Mission Planner polygon file reader."""

from __future__ import annotations

from pathlib import Path

from opencoverage.geometry.map import SurveyMap
from opencoverage.io.coords import geodetics_to_local_polygon
from opencoverage.models import GeodeticCoordinate


def read_polygon_from_mission_planner(path: str | Path) -> SurveyMap:
    """
    Read a polygon from a Mission Planner poly file.

    Each non-empty line contains ``latitude longitude`` in decimal degrees.
    """
    geodetics: list[GeodeticCoordinate] = []
    content = Path(path).read_text(encoding="utf-8")

    for line in content.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        latitude = float(parts[0])
        longitude = float(parts[1])
        altitude = float(parts[2]) if len(parts) > 2 else 0.0
        geodetics.append(GeodeticCoordinate(latitude=latitude, longitude=longitude, altitude=altitude))

    if len(geodetics) < 3:
        raise ValueError(f"Mission Planner file must contain at least three points: {path}")

    reference = geodetics[0]
    polygon = geodetics_to_local_polygon(geodetics, reference)
    return SurveyMap.from_polygon(polygon, reference=reference)
