"""Command-line interface for OpenCoverage."""

from __future__ import annotations

import argparse

from opencoverage.io.config import load_planner_config
from opencoverage.mission_splitter import MissionSplitter
from opencoverage.planner import plan


def main() -> int:
    """Run mission planning from the command line."""
    parser = argparse.ArgumentParser(
        description="Plan a UAV coverage mission from a polygon and configuration file.",
    )
    parser.add_argument("polygon", help="Path to input polygon file (KML or Mission Planner)")
    parser.add_argument("config", help="Path to INI configuration file")
    parser.add_argument("output", help="Path to output QGroundControl waypoint file")
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use CuPy for optimal sweep angle search when available",
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help="Split the mission according to UAV flight time limits",
    )
    args = parser.parse_args()

    parsed_config = load_planner_config(args.config)
    result = plan(
        polygon=args.polygon,
        config=args.config,
        gpu=args.gpu,
        split=args.split,
    )
    missions = result if isinstance(result, list) else [result]

    reference = missions[0].reference
    if reference is None:
        raise SystemExit("Mission is missing a geodetic reference point.")

    if len(missions) == 1:
        mission = missions[0]
        mission.save_qgc(args.output, reference=reference)
        print(f"Saved {len(mission.path)} waypoints to {args.output}")
        print(f"Flight height: {mission.flight_height:.2f} m")
        return 0

    splitter = MissionSplitter(parsed_config["uav_model"])
    saved = splitter.save_qgc_files(missions, args.output, reference=reference)
    for path in saved:
        print(f"Saved mission segment to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
