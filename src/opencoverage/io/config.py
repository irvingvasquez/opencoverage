"""INI configuration file loader."""

from __future__ import annotations

import configparser
from pathlib import Path

from opencoverage.models import PinholeCamera, SearchPatternType, TargetPlanning, UAV


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_value(raw: str) -> str | float | int | bool:
    """Parse INI value, stripping inline comments after semicolon."""
    cleaned = raw.split(";", 1)[0].strip()
    if cleaned.lower() in {"true", "false"}:
        return _parse_bool(cleaned)
    if "." in cleaned:
        return float(cleaned)
    try:
        return int(cleaned)
    except ValueError:
        return cleaned


def load_planner_config(path: str | Path) -> dict:
    """
    Load planner, UAV, and camera settings from an INI file.

    Returns a dictionary with keys: planner, uav, camera, and model instances.
    """
    parser = configparser.ConfigParser()
    parser.read(path)

    planner_section = {key: _parse_value(value) for key, value in parser.items("Planner")}
    uav_section = {key: _parse_value(value) for key, value in parser.items("UAV")}
    camera_section = {key: _parse_value(value) for key, value in parser.items("Camera")}

    planner = {
        "search_pattern": SearchPatternType(int(planner_section["searchpattern"])),
        "auto_takeoff": bool(planner_section.get("autotakeoff", False)),
        "lateral_overlap": float(planner_section["lateraloverlap"]),
        "forward_overlap": float(
            planner_section.get("forwardoverlap", planner_section.get("fordwardoverlap", 0.7))
        ),
        "spatial_resolution_mm": float(planner_section.get("spatialresolution", 40)),
        "target_velocity": float(planner_section.get("targetvelocity", 17)),
        "target_planning": TargetPlanning(
            int(planner_section.get("targetplanning", TargetPlanning.VELOCITY))
        ),
        "wind_direction_deg": float(planner_section.get("winddirection", 0)),
    }

    uav_config = {
        "flight_time_s": float(uav_section.get("flighttime", 0)),
        "survey_velocity": float(uav_section.get("velocity", planner["target_velocity"])),
        "min_height": float(uav_section["minheight"]),
        "max_height": float(uav_section["maxheight"]),
        "min_velocity": float(uav_section.get("minvelocity", 5)),
        "max_velocity": float(uav_section.get("maxvelocity", 20)),
    }

    camera_config = {
        "pixel_size_mm": float(camera_section["pixelsize"]),
        "focal_length_mm": float(camera_section["focallenght"]),
        "sensor_width_mm": float(camera_section["sensorwidth"]),
        "sensor_height_mm": float(camera_section["sensorheight"]),
        "capture_rate_s": float(camera_section.get("capturerate", 3)),
    }

    return {
        "planner": planner,
        "uav": uav_config,
        "camera": camera_config,
        "uav_model": UAV.from_config(uav_config),
        "camera_model": PinholeCamera.from_config(camera_config),
    }
