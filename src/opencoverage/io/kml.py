"""KML polygon reader."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from shapely.geometry import Polygon

from opencoverage.geometry.map import SurveyMap
from opencoverage.io.coords import geodetics_to_local_polygon
from opencoverage.models import GeodeticCoordinate


def _parse_coordinates(text: str) -> list[GeodeticCoordinate]:
    """Parse KML coordinate tuples (lon, lat, alt)."""
    coords: list[GeodeticCoordinate] = []
    for chunk in text.strip().split():
        parts = chunk.split(",")
        if len(parts) < 2:
            continue
        lon = float(parts[0])
        lat = float(parts[1])
        alt = float(parts[2]) if len(parts) > 2 else 0.0
        coords.append(GeodeticCoordinate(latitude=lat, longitude=lon, altitude=alt))
    return coords


def read_polygon_from_kml(path: str | Path) -> SurveyMap:
    """Read the first polygon found in a KML file into a SurveyMap."""
    tree = ET.parse(path)
    root = tree.getroot()

    coordinates_text = None
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag == "coordinates" and element.text:
            coordinates_text = element.text
            break

    if not coordinates_text:
        raise ValueError(f"No polygon coordinates found in KML file: {path}")

    geodetics = _parse_coordinates(coordinates_text)
    if len(geodetics) < 3:
        raise ValueError("KML polygon must contain at least three coordinates")

    reference = geodetics[0]
    polygon = geodetics_to_local_polygon(geodetics, reference)
    return SurveyMap.from_polygon(polygon, reference=reference)
