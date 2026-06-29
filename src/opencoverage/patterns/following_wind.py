"""Wind-aligned coverage sweep pattern."""

from __future__ import annotations

import math

from opencoverage.models import FlightMission
from opencoverage.patterns.back_forth import BackAndForthPattern


class FollowingWindPattern(BackAndForthPattern):
    """
    Align sweep lines with a wind direction.

    Wind direction uses meteorological convention in degrees:
    0 = from north, 90 = from east, 180 = from south, 270 = from west.
    """

    def __init__(
        self,
        uav,
        camera,
        survey_map,
        *,
        wind_direction_deg: float = 0.0,
    ) -> None:
        super().__init__(uav, camera, survey_map)
        self.wind_direction_deg = wind_direction_deg

    def calculate(self) -> FlightMission:
        rotation = math.radians(self.wind_direction_deg)
        waypoints = self.generate_rotated_pattern(rotation)
        return self.build_mission(waypoints)
