"""Tests for long-edge coverage pattern."""

from shapely.geometry import Polygon

from opencoverage.geometry.map import SurveyMap
from opencoverage.models import PinholeCamera, TargetPlanning, UAV
from opencoverage.patterns.long_edge import LongEdgePattern


def test_long_edge_rectangular_field():
    polygon = Polygon([(0, 0), (120, 0), (120, 40), (0, 40)])
    survey_map = SurveyMap.from_polygon(polygon)
    uav = UAV(min_height=70, max_height=500, survey_velocity=17)
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
    )

    pattern = LongEdgePattern(uav, camera, survey_map)
    pattern.set_search_parameters(0.8, 0.7, 17.0, TargetPlanning.VELOCITY)
    mission = pattern.calculate()

    assert len(mission.path) >= 2
    assert mission.flight_height >= uav.min_height
