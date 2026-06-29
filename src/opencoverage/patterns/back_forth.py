"""Back-and-forth (boustrophedon) coverage sweep pattern."""

from __future__ import annotations

from opencoverage.geometry.map import SurveyMap
from opencoverage.geometry.transforms import rotate_points
from opencoverage.models import FlightMission
from opencoverage.patterns.base import SearchPattern


class BackAndForthPattern(SearchPattern):
    """Generate parallel sweep lines across the polygon bounding width."""

    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = -1
    BOTTOM_UP = 1
    TOP_DOWN = -1

    def calculate(self) -> FlightMission:
        waypoints = self.generate_pattern(self.survey_map)
        return self.build_mission(waypoints)

    def generate_rotated_pattern(self, angle_rad: float) -> list[tuple[float, float]]:
        """Generate a back-and-forth path after rotating the map by angle_rad."""
        rotated_map = self.survey_map.rotated_copy(angle_rad)
        waypoints = self.generate_pattern(rotated_map)
        return rotate_points(waypoints, -angle_rad)

    def generate_pattern(self, survey_map: SurveyMap) -> list[tuple[float, float]]:
        """Generate waypoint path for the given map."""
        extremes = survey_map.extreme_vertices()
        left_point = extremes["left"]
        right_point = extremes["right"]

        horizontal_order = self.LEFT_TO_RIGHT
        vertical_order = self.BOTTOM_UP
        lateral_displacement = self.lateral_spacing * horizontal_order

        if horizontal_order == self.LEFT_TO_RIGHT:
            line_x = left_point[0]
            min_x = left_point[0]
            max_x = right_point[0]
        else:
            line_x = right_point[0]
            min_x = left_point[0]
            max_x = right_point[0]

        waypoints: list[tuple[float, float]] = []

        while min_x <= line_x <= max_x:
            points = survey_map.intersect_vertical_line(line_x)
            points.sort(key=lambda p: p[1], reverse=vertical_order == self.TOP_DOWN)
            vertical_order *= -1
            waypoints.extend(points)
            line_x += lateral_displacement

        return waypoints
