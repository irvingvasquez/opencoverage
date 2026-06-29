"""Coordinate conversion between geodetic and local meters."""

from __future__ import annotations

from pyproj import Transformer
from shapely.geometry import Polygon

from opencoverage.models import GeodeticCoordinate


def _local_crs(reference: GeodeticCoordinate) -> str:
    return (
        "+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs".format(
            lat=reference.latitude,
            lon=reference.longitude,
        )
    )


def geodetics_to_local_polygon(
    geodetics: list[GeodeticCoordinate],
    reference: GeodeticCoordinate,
) -> Polygon:
    """Project geodetic coordinates to a local meter polygon."""
    transformer = Transformer.from_crs(
        "EPSG:4326",
        _local_crs(reference),
        always_xy=True,
    )

    local_coords: list[tuple[float, float]] = []
    for geo in geodetics:
        x, y = transformer.transform(geo.longitude, geo.latitude)
        local_coords.append((x, y))

    if local_coords[0] != local_coords[-1]:
        local_coords.append(local_coords[0])

    return Polygon(local_coords)


def local_to_geodetic(
    x: float,
    y: float,
    reference: GeodeticCoordinate,
    altitude: float | None = None,
) -> GeodeticCoordinate:
    """Convert local meter coordinates back to geodetic."""
    transformer = Transformer.from_crs(
        _local_crs(reference),
        "EPSG:4326",
        always_xy=True,
    )
    lon, lat = transformer.transform(x, y)
    return GeodeticCoordinate(
        latitude=lat,
        longitude=lon,
        altitude=reference.altitude if altitude is None else altitude,
    )


def path_to_geodetics(
    path: list[tuple[float, float]],
    reference: GeodeticCoordinate,
    flight_height_m: float,
) -> list[GeodeticCoordinate]:
    """Convert a local waypoint path to geodetic coordinates at flight height."""
    waypoint_altitude = reference.altitude + flight_height_m
    return [
        local_to_geodetic(x, y, reference, altitude=waypoint_altitude)
        for x, y in path
    ]
