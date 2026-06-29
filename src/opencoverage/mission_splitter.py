"""Split long missions according to UAV flight-time limits."""

from __future__ import annotations

from pathlib import Path

from opencoverage.models import FlightMission, GeodeticCoordinate, UAV


class MissionSplitter:
    """Divide a mission into segments that fit within UAV flight time."""

    def __init__(self, uav: UAV) -> None:
        self.uav = uav

    def split(self, mission: FlightMission) -> list[FlightMission]:
        """
        Split a mission into sub-missions when flight_time_s is configured.

        When flight_time_s is zero, the original mission is returned unchanged.
        """
        if self.uav.flight_time_s <= 0 or not mission.path:
            return [mission]

        segments: list[FlightMission] = []
        partial_path: list[tuple[float, float]] = []
        last_point: tuple[float, float] | None = None

        for point in mission.path:
            partial_path.append(point)
            elapsed = self.uav.estimate_flight_time(partial_path)
            if elapsed > self.uav.flight_time_s:
                partial_path.pop()
                if partial_path:
                    segments.append(self._clone_mission(mission, partial_path))
                partial_path = []
                if last_point is not None:
                    partial_path.append(last_point)
                partial_path.append(point)

            last_point = point

        if partial_path:
            segments.append(self._clone_mission(mission, partial_path))

        return segments or [mission]

    def save_qgc_files(
        self,
        missions: list[FlightMission],
        base_filename: str | Path,
        reference: GeodeticCoordinate,
    ) -> list[Path]:
        """Save each mission segment as a numbered QGroundControl file."""
        base_path = Path(base_filename)
        stem = base_path.stem
        suffix = base_path.suffix or ".txt"
        parent = base_path.parent

        saved: list[Path] = []
        for index, mission in enumerate(missions, start=1):
            output = parent / f"{stem}{index}{suffix}"
            mission.save_qgc(output, reference=reference)
            saved.append(output)
        return saved

    def _clone_mission(
        self,
        mission: FlightMission,
        path: list[tuple[float, float]],
    ) -> FlightMission:
        return FlightMission(
            path=list(path),
            flight_height=mission.flight_height,
            home=mission.home,
            takeoff=mission.takeoff,
            reference=mission.reference,
            auto_takeoff=mission.auto_takeoff,
            forward_distance=mission.forward_distance,
            lateral_distance=mission.lateral_distance,
            capture_rate=mission.capture_rate,
            flight_time_s=self.uav.estimate_flight_time(path),
        )
