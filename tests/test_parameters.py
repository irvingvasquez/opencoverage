"""Tests for survey parameter calculations."""

from opencoverage.models import PinholeCamera, TargetPlanning, UAV
from opencoverage.parameters import (
    forward_trigger_distance,
    lateral_line_spacing,
    resolve_survey_parameters,
    spatial_resolution_from_height,
)


def test_spatial_resolution_roundtrip():
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
    )
    height = 100.0
    resolution = spatial_resolution_from_height(height, camera)
    assert resolution > 0


def test_line_spacing_and_trigger_distance():
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
    )
    spacing = lateral_line_spacing(100.0, 0.8, camera)
    trigger = forward_trigger_distance(100.0, 0.7, camera)
    assert spacing > 0
    assert trigger > 0


def test_resolve_velocity_target():
    uav = UAV(min_height=70, max_height=500, survey_velocity=17)
    camera = PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
        capture_rate_s=3,
    )
    params = resolve_survey_parameters(
        uav=uav,
        camera=camera,
        lateral_overlap=0.8,
        forward_overlap=0.7,
        target=TargetPlanning.VELOCITY,
        target_value=17.0,
    )
    assert 70 <= params["flight_height"] <= 500
    assert params["trigger_distance"] > 0
