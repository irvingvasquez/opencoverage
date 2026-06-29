"""High-level mission planning API."""

from __future__ import annotations

from pathlib import Path

from shapely.geometry import Polygon

from opencoverage.geometry.map import SurveyMap
from opencoverage.io.config import load_planner_config
from opencoverage.io.survey_input import read_survey_map
from opencoverage.mission_splitter import MissionSplitter
from opencoverage.models import (
    FlightMission,
    GeodeticCoordinate,
    PinholeCamera,
    SearchPatternType,
    TargetPlanning,
    UAV,
)
from opencoverage.patterns.back_forth import BackAndForthPattern
from opencoverage.patterns.base import SearchPattern
from opencoverage.patterns.following_wind import FollowingWindPattern
from opencoverage.patterns.long_edge import LongEdgePattern
from opencoverage.patterns.optimal_sweep import OptimalSweepPattern

PATTERN_ALIASES: dict[str, SearchPatternType] = {
    "back_forth": SearchPatternType.BACK_AND_FORTH,
    "back-and-forth": SearchPatternType.BACK_AND_FORTH,
    "long_edge": SearchPatternType.LONG_EDGE,
    "long-edge": SearchPatternType.LONG_EDGE,
    "optimal_sweep": SearchPatternType.OPTIMAL_SWEEP,
    "optimal-sweep": SearchPatternType.OPTIMAL_SWEEP,
    "following_wind": SearchPatternType.FOLLOWING_WIND,
    "following-wind": SearchPatternType.FOLLOWING_WIND,
}


def _resolve_pattern_type(pattern: str | SearchPatternType) -> SearchPatternType:
    if isinstance(pattern, SearchPatternType):
        return pattern
    normalized = pattern.lower().replace(" ", "_")
    if normalized not in PATTERN_ALIASES:
        raise ValueError(f"Unknown pattern: {pattern}")
    return PATTERN_ALIASES[normalized]


def _resolve_target(
    target: str | TargetPlanning,
    target_value: float | None,
    config: dict | None,
) -> tuple[TargetPlanning, float]:
    if config is not None:
        planner = config["planner"]
        resolved_target = planner["target_planning"]
        if target_value is None:
            if resolved_target == TargetPlanning.RESOLUTION:
                target_value = planner["spatial_resolution_mm"]
            elif resolved_target == TargetPlanning.VELOCITY:
                target_value = planner["target_velocity"]
            else:
                target_value = config["uav"]["min_height"]
        return resolved_target, float(target_value)

    if isinstance(target, str):
        target_map = {
            "resolution": TargetPlanning.RESOLUTION,
            "velocity": TargetPlanning.VELOCITY,
            "altitude": TargetPlanning.ALTITUDE,
        }
        resolved_target = target_map[target.lower()]
    else:
        resolved_target = target

    if target_value is None:
        raise ValueError("target_value is required when no config file is provided")

    return resolved_target, float(target_value)


def _build_pattern(
    pattern_type: SearchPatternType,
    uav: UAV,
    camera: PinholeCamera,
    survey_map: SurveyMap,
    *,
    gpu: bool = False,
    wind_direction_deg: float = 0.0,
    n_angle_steps: int = 10_000,
) -> SearchPattern:
    if pattern_type == SearchPatternType.BACK_AND_FORTH:
        return BackAndForthPattern(uav, camera, survey_map)
    if pattern_type == SearchPatternType.LONG_EDGE:
        return LongEdgePattern(uav, camera, survey_map)
    if pattern_type == SearchPatternType.OPTIMAL_SWEEP:
        return OptimalSweepPattern(
            uav,
            camera,
            survey_map,
            gpu=gpu,
            n_angle_steps=n_angle_steps,
        )
    if pattern_type == SearchPatternType.FOLLOWING_WIND:
        return FollowingWindPattern(
            uav,
            camera,
            survey_map,
            wind_direction_deg=wind_direction_deg,
        )
    raise ValueError(f"Unsupported pattern: {pattern_type}")


def _load_survey_map(
    polygon: Polygon | str | Path,
    *,
    home: GeodeticCoordinate | None = None,
    takeoff: GeodeticCoordinate | None = None,
    reference: GeodeticCoordinate | None = None,
) -> SurveyMap:
    if isinstance(polygon, (str, Path)):
        survey_map = read_survey_map(polygon)
    elif isinstance(polygon, Polygon):
        survey_map = SurveyMap.from_polygon(polygon, reference=reference)
    else:
        raise TypeError("polygon must be a Shapely Polygon or a file path")

    if reference is not None:
        survey_map.reference = reference
    if home is not None:
        survey_map.home = home
    if takeoff is not None:
        survey_map.takeoff = takeoff
    return survey_map


def plan(
    *,
    polygon: Polygon | str | Path,
    config: str | Path | None = None,
    uav: UAV | None = None,
    camera: PinholeCamera | None = None,
    pattern: str | SearchPatternType = "back_forth",
    lateral_overlap: float | None = None,
    forward_overlap: float | None = None,
    target: str | TargetPlanning = "velocity",
    target_value: float | None = None,
    home: GeodeticCoordinate | None = None,
    takeoff: GeodeticCoordinate | None = None,
    reference: GeodeticCoordinate | None = None,
    split: bool = False,
    gpu: bool = False,
    wind_direction_deg: float = 0.0,
    n_angle_steps: int = 10_000,
) -> FlightMission | list[FlightMission]:
    """
    Plan a coverage mission for a survey polygon.

    When ``split`` is True, the mission is divided into segments that respect
    the UAV ``flight_time_s`` limit.
    """
    parsed_config = load_planner_config(config) if config is not None else None

    if parsed_config is not None:
        uav = uav or parsed_config["uav_model"]
        camera = camera or parsed_config["camera_model"]
        lateral_overlap = (
            lateral_overlap if lateral_overlap is not None else parsed_config["planner"]["lateral_overlap"]
        )
        forward_overlap = (
            forward_overlap
            if forward_overlap is not None
            else parsed_config["planner"]["forward_overlap"]
        )
        if isinstance(pattern, str) and pattern in {"back_forth", "back-and-forth"}:
            pattern = parsed_config["planner"]["search_pattern"]
        wind_direction_deg = parsed_config["planner"].get("wind_direction_deg", wind_direction_deg)
    else:
        if uav is None or camera is None:
            raise ValueError("uav and camera are required when no config file is provided")
        if lateral_overlap is None or forward_overlap is None:
            raise ValueError("overlap values are required when no config file is provided")

    pattern_type = _resolve_pattern_type(pattern)
    survey_map = _load_survey_map(
        polygon,
        home=home,
        takeoff=takeoff,
        reference=reference,
    )

    resolved_target, resolved_target_value = _resolve_target(target, target_value, parsed_config)

    search_pattern = _build_pattern(
        pattern_type,
        uav,
        camera,
        survey_map,
        gpu=gpu,
        wind_direction_deg=wind_direction_deg,
        n_angle_steps=n_angle_steps,
    )
    search_pattern.set_search_parameters(
        lateral_overlap=float(lateral_overlap),
        forward_overlap=float(forward_overlap),
        target_value=resolved_target_value,
        target=resolved_target,
    )
    mission = search_pattern.calculate()

    if parsed_config is not None:
        mission.auto_takeoff = parsed_config["planner"]["auto_takeoff"]

    should_split = bool(split)
    if should_split:
        return MissionSplitter(uav).split(mission)
    return mission
