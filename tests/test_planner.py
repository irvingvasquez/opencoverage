"""Integration tests for the planner API."""

from pathlib import Path

from shapely.geometry import Polygon

import opencoverage as oc


def test_plan_back_forth_local_polygon():
    polygon = Polygon([(0, 0), (100, 0), (100, 80), (0, 80)])
    mission = oc.plan(
        polygon=polygon,
        uav=oc.UAV(min_height=70, max_height=500, survey_velocity=17),
        camera=oc.PinholeCamera(
            pixel_size_mm=0.0032,
            focal_length_mm=8.43,
            sensor_width_mm=6.55,
            sensor_height_mm=4.92,
        ),
        pattern="back_forth",
        lateral_overlap=0.8,
        forward_overlap=0.7,
        target="velocity",
        target_value=17.0,
    )
    assert isinstance(mission, oc.FlightMission)
    assert len(mission.path) >= 4


def test_plan_with_config_file():
    config = Path(__file__).resolve().parents[1] / "config" / "quad_tetracam.ini"
    polygon = Polygon([(0, 0), (100, 0), (100, 80), (0, 80)])
    mission = oc.plan(polygon=polygon, config=config, pattern="long_edge")
    assert len(mission.path) >= 4


def test_plan_optimal_sweep():
    polygon = Polygon([(0, 0), (150, 0), (150, 60), (0, 60)])
    mission = oc.plan(
        polygon=polygon,
        uav=oc.UAV(min_height=70, max_height=500, survey_velocity=17),
        camera=oc.PinholeCamera(
            pixel_size_mm=0.0032,
            focal_length_mm=8.43,
            sensor_width_mm=6.55,
            sensor_height_mm=4.92,
        ),
        pattern="optimal_sweep",
        lateral_overlap=0.8,
        forward_overlap=0.7,
        target="velocity",
        target_value=17.0,
        n_angle_steps=200,
    )
    assert len(mission.path) >= 4
