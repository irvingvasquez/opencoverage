"""Domain models for UAV survey planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Sequence

import numpy as np


class TargetPlanning(IntEnum):
    """Planning objective used to derive flight height and capture rate."""

    RESOLUTION = 1
    VELOCITY = 2
    ALTITUDE = 3


class SearchPatternType(IntEnum):
    """Available coverage sweep patterns."""

    BACK_AND_FORTH = 1
    LONG_EDGE = 2
    OPTIMAL_SWEEP = 3
    FOLLOWING_WIND = 4


@dataclass
class GeodeticCoordinate:
    """WGS84 geodetic coordinate."""

    latitude: float
    longitude: float
    altitude: float = 0.0


@dataclass
class CartesianCoordinate:
    """Local Cartesian coordinate in meters (north-east-down style x/y)."""

    x: float
    y: float
    z: float = 0.0


@dataclass
class PinholeCamera:
    """Pinhole camera model. All geometric parameters are in millimeters."""

    pixel_size_mm: float
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    capture_rate_s: float = 3.0

    @classmethod
    def from_config(cls, config: dict[str, float]) -> PinholeCamera:
        """Build a camera from parsed INI camera section values."""
        return cls(
            pixel_size_mm=config["pixel_size_mm"],
            focal_length_mm=config["focal_length_mm"],
            sensor_width_mm=config["sensor_width_mm"],
            sensor_height_mm=config["sensor_height_mm"],
            capture_rate_s=config.get("capture_rate_s", 3.0),
        )


@dataclass
class UAV:
    """Multirotor UAV flight constraints."""

    min_height: float = 70.0
    max_height: float = 500.0
    min_velocity: float = 5.0
    max_velocity: float = 20.0
    survey_velocity: float = 17.0
    flight_time_s: float = 0.0

    @classmethod
    def from_config(cls, config: dict[str, float]) -> UAV:
        """Build a UAV from parsed INI UAV section values."""
        return cls(
            min_height=config["min_height"],
            max_height=config["max_height"],
            min_velocity=config.get("min_velocity", 5.0),
            max_velocity=config.get("max_velocity", 20.0),
            survey_velocity=config.get("survey_velocity", config.get("velocity", 17.0)),
            flight_time_s=config.get("flight_time_s", 0.0),
        )

    def estimate_path_distance(self, path: Sequence[tuple[float, float]]) -> float:
        """Return total path length in meters."""
        if len(path) < 2:
            return 0.0
        points = np.asarray(path, dtype=float)
        deltas = np.diff(points, axis=0)
        return float(np.sum(np.hypot(deltas[:, 0], deltas[:, 1])))

    def estimate_flight_time(self, path: Sequence[tuple[float, float]]) -> float:
        """Return estimated flight duration in seconds."""
        if self.survey_velocity <= 0:
            return 0.0
        return self.estimate_path_distance(path) / self.survey_velocity


@dataclass
class FlightMission:
    """Planned survey mission with waypoint path in local coordinates."""

    path: list[tuple[float, float]] = field(default_factory=list)
    flight_height: float = 0.0
    home: GeodeticCoordinate | None = None
    takeoff: GeodeticCoordinate | None = None
    reference: GeodeticCoordinate | None = None
    auto_takeoff: bool = False
    forward_distance: float = 0.0
    lateral_distance: float = 0.0
    capture_rate: float = 0.0
    flight_time_s: float = 0.0

    def save_qgc(self, filename: str, reference: GeodeticCoordinate) -> None:
        """Export the mission as a QGroundControl waypoint file."""
        from opencoverage.io.qgc import write_qgc_file

        write_qgc_file(
            filename,
            path=self.path,
            flight_height=self.flight_height,
            reference=reference,
            home=self.home,
            takeoff=self.takeoff,
            auto_takeoff=self.auto_takeoff,
        )
