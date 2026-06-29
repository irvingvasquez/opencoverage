"""Survey polygon input readers."""

from __future__ import annotations

from pathlib import Path

from opencoverage.geometry.map import SurveyMap
from opencoverage.io.kml import read_polygon_from_kml
from opencoverage.io.mission_planner import read_polygon_from_mission_planner


def read_survey_map(path: str | Path) -> SurveyMap:
    """
    Load a survey map from KML or Mission Planner polygon file.

    Supported extensions: ``.kml``, ``.kmz`` (KML only), ``.poly``, ``.txt``.
    """
    suffix = Path(path).suffix.lower()
    if suffix in {".kml", ".kmz"}:
        return read_polygon_from_kml(path)
    return read_polygon_from_mission_planner(path)
