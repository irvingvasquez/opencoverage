"""Tests for optimal sweep coverage pattern."""

from shapely.geometry import Polygon

from opencoverage.geometry.map import SurveyMap
from opencoverage.gpu.optimal_sweep import find_optimal_sweep_angle
from opencoverage.models import PinholeCamera, TargetPlanning, UAV
from opencoverage.patterns.optimal_sweep import OptimalSweepPattern


def test_find_optimal_angle_rectangle():
    polygon = Polygon([(0, 0), (200, 0), (200, 50), (0, 50)])
    angle = find_optimal_sweep_angle(SurveyMap.from_polygon(polygon).vertices, n_steps=500)
    assert 0.0 <= angle < 3.14159


def test_optimal_sweep_pattern():
    polygon = Polygon([(0, 0), (200, 0), (200, 50), (0, 50)])
    survey_map = SurveyMap.from_polygon(polygon)
    uav = UAV(min_height=70, max_height=500, survey_velocity=17)
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
    )

    pattern = OptimalSweepPattern(uav, camera, survey_map, n_angle_steps=500)
    pattern.set_search_parameters(0.8, 0.7, 17.0, TargetPlanning.VELOCITY)
    mission = pattern.calculate()

    assert len(mission.path) >= 4
