"""Tests for mission splitting."""

from opencoverage.mission_splitter import MissionSplitter
from opencoverage.models import FlightMission, UAV


def test_split_mission_by_flight_time():
    uav = UAV(survey_velocity=10.0, flight_time_s=30.0)
    path = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
    mission = FlightMission(path=path, flight_height=100.0, flight_time_s=500.0)

    segments = MissionSplitter(uav).split(mission)
    assert len(segments) >= 2
    for segment in segments:
        assert uav.estimate_flight_time(segment.path) <= uav.flight_time_s + 1e-6 or len(segment.path) <= 2


def test_no_split_when_flight_time_disabled():
    uav = UAV(survey_velocity=10.0, flight_time_s=0.0)
    mission = FlightMission(path=[(0, 0), (10, 0), (10, 10)], flight_height=80.0)
    segments = MissionSplitter(uav).split(mission)
    assert len(segments) == 1
