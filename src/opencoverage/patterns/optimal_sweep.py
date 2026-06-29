"""Optimal sweep direction coverage pattern."""

from __future__ import annotations

from opencoverage.gpu.optimal_sweep import find_optimal_sweep_angle
from opencoverage.models import FlightMission
from opencoverage.patterns.back_forth import BackAndForthPattern


class OptimalSweepPattern(BackAndForthPattern):
    """
    Find the sweep rotation that minimizes horizontal coverage width.

    Uses a brute-force search over [0, pi). When ``gpu=True`` and CuPy is
    installed, the search runs on the GPU.
    """

    def __init__(
        self,
        uav,
        camera,
        survey_map,
        *,
        gpu: bool = False,
        n_angle_steps: int = 10_000,
    ) -> None:
        super().__init__(uav, camera, survey_map)
        self.gpu = gpu
        self.n_angle_steps = n_angle_steps

    def calculate(self) -> FlightMission:
        angle = find_optimal_sweep_angle(
            self.survey_map.vertices,
            n_steps=self.n_angle_steps,
            prefer_gpu=self.gpu,
        )
        waypoints = self.generate_rotated_pattern(angle)
        return self.build_mission(waypoints)
