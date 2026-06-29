"""Base class for coverage search patterns."""

from __future__ import annotations

from abc import ABC, abstractmethod

from opencoverage.geometry.map import SurveyMap
from opencoverage.models import FlightMission, PinholeCamera, TargetPlanning, UAV
from opencoverage.parameters import resolve_survey_parameters


class SearchPattern(ABC):
    """Abstract coverage path planner."""

    def __init__(self, uav: UAV, camera: PinholeCamera, survey_map: SurveyMap) -> None:
        self.uav = uav
        self.camera = camera
        self.survey_map = survey_map
        self.lateral_overlap = 0.0
        self.forward_overlap = 0.0
        self.target = TargetPlanning.VELOCITY
        self.target_value = 0.0
        self.flight_height = 0.0
        self.spatial_resolution = 0.0
        self.velocity = 0.0
        self.trigger_distance = 0.0
        self.lateral_spacing = 0.0
        self.flight_time_s = 0.0

    def set_search_parameters(
        self,
        lateral_overlap: float,
        forward_overlap: float,
        target_value: float,
        target: TargetPlanning,
    ) -> None:
        """Configure overlap ratios and the planning objective."""
        self.lateral_overlap = lateral_overlap
        self.forward_overlap = forward_overlap
        self.target = target
        self.target_value = target_value

        params = resolve_survey_parameters(
            uav=self.uav,
            camera=self.camera,
            lateral_overlap=lateral_overlap,
            forward_overlap=forward_overlap,
            target=target,
            target_value=target_value,
        )
        self.flight_height = params["flight_height"]
        self.spatial_resolution = params["spatial_resolution"]
        self.velocity = params["velocity"]
        self.trigger_distance = params["trigger_distance"]
        self.lateral_spacing = params["lateral_spacing"]

    def build_mission(self, waypoints: list[tuple[float, float]]) -> FlightMission:
        """Create a FlightMission from a local waypoint path."""
        capture_rate = self.trigger_distance / self.velocity if self.velocity else 0.0
        return FlightMission(
            path=waypoints,
            flight_height=self.flight_height,
            home=self.survey_map.home,
            takeoff=self.survey_map.takeoff,
            reference=self.survey_map.reference,
            forward_distance=self.trigger_distance,
            lateral_distance=self.lateral_spacing,
            capture_rate=capture_rate,
            flight_time_s=self.uav.estimate_flight_time(waypoints),
        )

    @abstractmethod
    def calculate(self) -> FlightMission:
        """Compute the coverage mission."""
