"""Tests for survey map input readers."""

from pathlib import Path

from opencoverage.io.survey_input import read_survey_map


def test_read_kml_example():
    path = Path(__file__).resolve().parents[1] / "examples" / "sample_field.kml"
    survey_map = read_survey_map(path)
    assert survey_map.reference is not None
    assert not survey_map.polygon.is_empty


def test_read_mission_planner_example():
    path = Path(__file__).resolve().parents[1] / "examples" / "sample_field.poly"
    survey_map = read_survey_map(path)
    assert survey_map.reference is not None
    assert survey_map.polygon.area > 0
