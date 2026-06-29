"""OpenCoverage: coverage path planning for UAV aerial surveying."""

from opencoverage.mission_splitter import MissionSplitter
from opencoverage.models import (
    FlightMission,
    GeodeticCoordinate,
    PinholeCamera,
    SearchPatternType,
    TargetPlanning,
    UAV,
)
from opencoverage.planner import plan

__all__ = [
    "FlightMission",
    "GeodeticCoordinate",
    "MissionSplitter",
    "PinholeCamera",
    "SearchPatternType",
    "TargetPlanning",
    "UAV",
    "plan",
    "__version__",
]

__version__ = "0.2.0"
