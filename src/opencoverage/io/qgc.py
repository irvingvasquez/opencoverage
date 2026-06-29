"""QGroundControl waypoint file export."""

from __future__ import annotations

from pathlib import Path

from opencoverage.io.coords import path_to_geodetics
from opencoverage.models import GeodeticCoordinate


def _write_command(
    waypoint_id: int,
    is_current: int,
    coordinate_frame: int,
    command: int,
    param1: float,
    param2: float,
    param3: float,
    param4: float,
    latitude: float,
    longitude: float,
    altitude: float,
    auto_continue: int,
) -> str:
    return (
        f"{waypoint_id}\t{is_current}\t{coordinate_frame}\t{command}\t"
        f"{param1}\t{param2}\t{param3}\t{param4}\t"
        f"{latitude:.15f}\t{longitude:.15f}\t{altitude:.6f}\t{auto_continue}"
    )


def write_qgc_file(
    filename: str | Path,
    *,
    path: list[tuple[float, float]],
    flight_height: float,
    reference: GeodeticCoordinate,
    home: GeodeticCoordinate | None = None,
    takeoff: GeodeticCoordinate | None = None,
    auto_takeoff: bool = False,
) -> None:
    """
    Write a QGroundControl waypoint file from a local-meter path.

    Format follows the legacy QGC WPL 120 tab-separated layout.
    """
    geodetics = path_to_geodetics(path, reference, flight_height)
    lines = ["QGC WPL 120"]
    waypoint_id = 0
    current_id = 0
    auto_continue = 1

    if auto_takeoff and takeoff is not None:
        lines.append(
            _write_command(
                waypoint_id,
                1 if waypoint_id == current_id else 0,
                3,
                22,
                15,
                0,
                0,
                0,
                takeoff.latitude,
                takeoff.longitude,
                takeoff.altitude,
                auto_continue,
            )
        )
        waypoint_id += 1

    if geodetics:
        first = geodetics[0]
        lines.append(
            _write_command(
                waypoint_id,
                1 if waypoint_id == current_id else 0,
                3,
                16,
                0,
                0,
                0,
                0,
                first.latitude,
                first.longitude,
                first.altitude,
                auto_continue,
            )
        )
        waypoint_id += 1

    for geo in geodetics:
        lines.append(
            _write_command(
                waypoint_id,
                1 if waypoint_id == current_id else 0,
                3,
                16,
                0,
                0,
                0,
                0,
                geo.latitude,
                geo.longitude,
                geo.altitude,
                auto_continue,
            )
        )
        waypoint_id += 1

    if geodetics:
        first = geodetics[0]
        lines.append(
            _write_command(
                waypoint_id,
                1 if waypoint_id == current_id else 0,
                3,
                17,
                0,
                0,
                15,
                0,
                first.latitude,
                first.longitude,
                first.altitude,
                auto_continue,
            )
        )

    Path(filename).write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
