"""Survey parameter calculations derived from camera and UAV models."""

from __future__ import annotations

from opencoverage.models import PinholeCamera, TargetPlanning, UAV


def flight_height_from_resolution(spatial_resolution_mm: float, camera: PinholeCamera) -> float:
    """Compute flight height in meters for a target ground resolution."""
    height_m = (spatial_resolution_mm * camera.focal_length_mm) / camera.pixel_size_mm
    return height_m / 1000.0


def spatial_resolution_from_height(flight_height_m: float, camera: PinholeCamera) -> float:
    """Compute ground resolution in mm/pixel for a given flight height."""
    resolution_m = camera.pixel_size_mm * flight_height_m / camera.focal_length_mm
    return resolution_m * 1000.0


def lateral_line_spacing(
    flight_height_m: float,
    lateral_overlap: float,
    camera: PinholeCamera,
) -> float:
    """Distance between adjacent sweep lines in meters."""
    return (
        (flight_height_m / camera.focal_length_mm)
        * camera.sensor_width_mm
        * (1.0 - lateral_overlap)
    )


def forward_trigger_distance(
    flight_height_m: float,
    forward_overlap: float,
    camera: PinholeCamera,
) -> float:
    """Forward camera trigger distance in meters."""
    return (
        (flight_height_m / camera.focal_length_mm)
        * camera.sensor_height_mm
        * (1.0 - forward_overlap)
    )


def cruise_height_for_velocity(
    velocity_m_s: float,
    forward_overlap: float,
    camera: PinholeCamera,
) -> float:
    """Compute flight height that matches velocity and camera capture rate."""
    return (
        velocity_m_s
        * camera.capture_rate_s
        * camera.focal_length_mm
        / (camera.sensor_height_mm * (1.0 - forward_overlap))
    )


def capture_rate_for_height(
    flight_height_m: float,
    forward_overlap: float,
    velocity_m_s: float,
    camera: PinholeCamera,
) -> float:
    """Required capture interval in seconds for the given flight parameters."""
    trigger_distance = forward_trigger_distance(flight_height_m, forward_overlap, camera)
    return trigger_distance / velocity_m_s


def minimum_survey_height(
    forward_overlap: float,
    camera: PinholeCamera,
    uav: UAV,
) -> float:
    """Minimum feasible survey height given UAV minimum velocity."""
    min_trigger = camera.capture_rate_s * uav.min_velocity
    return (min_trigger * camera.focal_length_mm) / (
        camera.sensor_height_mm * (1.0 - forward_overlap)
    )


def resolve_survey_parameters(
    *,
    uav: UAV,
    camera: PinholeCamera,
    lateral_overlap: float,
    forward_overlap: float,
    target: TargetPlanning,
    target_value: float,
) -> dict[str, float]:
    """
    Resolve flight height, spatial resolution, velocity, and trigger distance.

    Mirrors the parameter selection logic from the original C++ SearchPattern class.
    """
    if target == TargetPlanning.RESOLUTION:
        flight_height = flight_height_from_resolution(target_value, camera)
        spatial_resolution = target_value
        velocity = uav.survey_velocity
    elif target == TargetPlanning.ALTITUDE:
        flight_height = target_value
        spatial_resolution = spatial_resolution_from_height(flight_height, camera)
        velocity = uav.survey_velocity
    elif target == TargetPlanning.VELOCITY:
        velocity = target_value
        flight_height = cruise_height_for_velocity(velocity, forward_overlap, camera)
        spatial_resolution = spatial_resolution_from_height(flight_height, camera)
    else:
        raise ValueError(f"Unsupported planning target: {target}")

    if flight_height < uav.min_height:
        flight_height = uav.min_height
        spatial_resolution = spatial_resolution_from_height(flight_height, camera)

    if flight_height > uav.max_height:
        flight_height = uav.max_height
        spatial_resolution = spatial_resolution_from_height(flight_height, camera)

    trigger_distance = forward_trigger_distance(flight_height, forward_overlap, camera)
    required_capture_rate = capture_rate_for_height(
        flight_height, forward_overlap, velocity, camera
    )

    return {
        "flight_height": flight_height,
        "spatial_resolution": spatial_resolution,
        "velocity": velocity,
        "trigger_distance": trigger_distance,
        "required_capture_rate": required_capture_rate,
        "lateral_spacing": lateral_line_spacing(flight_height, lateral_overlap, camera),
    }
