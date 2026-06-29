"""Tests for INI configuration loading."""

from pathlib import Path

from opencoverage.io.config import load_planner_config
from opencoverage.models import TargetPlanning


def test_load_config_without_target_planning_defaults_to_velocity():
    """Legacy INI files may omit TargetPlanning when TargetVelocity is set."""
    config_path = Path(__file__).resolve().parents[1] / "config" / "RascalTetracam.ini"
    parsed = load_planner_config(config_path)
    assert parsed["planner"]["target_planning"] == TargetPlanning.VELOCITY
    assert parsed["planner"]["target_velocity"] == 10.0
