"""Long-edge aligned coverage sweep pattern."""

from __future__ import annotations

import math

from opencoverage.models import FlightMission
from opencoverage.patterns.back_forth import BackAndForthPattern


class LongEdgePattern(BackAndForthPattern):
    """Align sweep lines perpendicular to the polygon longest edge."""

    def calculate(self) -> FlightMission:
        rotation = self._long_edge_rotation()
        waypoints = self.generate_rotated_pattern(rotation)
        return self.build_mission(waypoints)

    def _long_edge_rotation(self) -> float:
        """Return rotation angle that aligns the longest edge with the x-axis."""
        coords = list(self.survey_map.polygon.exterior.coords[:-1])
        origin = coords[0]
        target = coords[1]
        max_distance = 0.0

        for index, start in enumerate(coords):
            end = coords[(index + 1) % len(coords)]
            distance = (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
            if distance > max_distance:
                max_distance = distance
                origin = start
                target = end

        edge_angle = math.atan2(target[1] - origin[1], target[0] - origin[0])
        return math.pi / 2.0 - edge_angle
