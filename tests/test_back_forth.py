"""Tests for the back-and-forth coverage pattern."""

from shapely.geometry import Polygon

from opencoverage.models import PinholeCamera, TargetPlanning, UAV
from opencoverage.patterns.back_forth import BackAndForthPattern
from opencoverage.geometry.map import SurveyMap


def test_back_and_forth_rectangular_field():
    polygon = Polygon([(0, 0), (100, 0), (100, 80), (0, 80)])
    survey_map = SurveyMap.from_polygon(polygon)

    uav = UAV(min_height=70, max_height=500, survey_velocity=17)
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
        capture_rate_s=3,
    )

    pattern = BackAndForthPattern(uav, camera, survey_map)
    pattern.set_search_parameters(
        lateral_overlap=0.8,
        forward_overlap=0.7,
        target_value=17.0,
        target=TargetPlanning.VELOCITY,
    )
    mission = pattern.calculate()

    assert len(mission.path) >= 4
    assert mission.flight_height >= uav.min_height
    assert mission.flight_time_s > 0
