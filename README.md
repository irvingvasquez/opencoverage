# OpenCoverage

Coverage path planning for UAV aerial surveying. OpenCoverage computes waypoint
flight paths that fully cover a terrain polygon, with support for camera overlap,
flight constraints, and multiple sweep patterns.

Python reimplementation of the original UAV Planning library, using Shapely
instead of CGAL. CPU execution is the default; optional GPU acceleration via CuPy
is available for the optimal sweep search.

## Features

- **Search patterns**: back-and-forth, long-edge, optimal sweep, following-wind
- **Planning targets**: spatial resolution, cruise velocity, or fixed altitude
- **Mission splitting** by UAV flight-time limits
- **Input formats**: KML polygons, Mission Planner `.poly` files, INI configuration
- **Output**: QGroundControl WPL 120 waypoint files
- **Optional GPU**: CuPy acceleration for optimal sweep angle search

## Installation

```bash
pip install -e ".[dev]"
```

Optional GPU support:

```bash
pip install -e ".[gpu]"
```

## Quick start

```python
from shapely.geometry import Polygon

import opencoverage as oc

polygon = Polygon([(0, 0), (100, 0), (100, 80), (0, 80)])

mission = oc.plan(
    polygon=polygon,
    uav=oc.UAV(min_height=70, max_height=500, survey_velocity=17),
    camera=oc.PinholeCamera(
        pixel_size_mm=0.0032,
        focal_length_mm=8.43,
        sensor_width_mm=6.55,
        sensor_height_mm=4.92,
        capture_rate_s=3,
    ),
    pattern="optimal_sweep",
    lateral_overlap=0.8,
    forward_overlap=0.7,
    target="velocity",
    target_value=17.0,
)

print(len(mission.path), "waypoints at", mission.flight_height, "m")
```

## Command line

```bash
opencoverage examples/sample_field.kml config/quad_tetracam.ini mission.txt
opencoverage examples/sample_field.poly config/quad_tetracam.ini mission.txt --split
opencoverage examples/sample_field.kml config/quad_tetracam.ini mission.txt --gpu
```

## Patterns

| Pattern | Description |
|---------|-------------|
| `back_forth` | Standard boustrophedon sweep |
| `long_edge` | Sweep lines perpendicular to the longest polygon edge |
| `optimal_sweep` | Minimize horizontal sweep width over rotation angles |
| `following_wind` | Align sweeps with meteorological wind direction |

## Project layout

```
src/opencoverage/
├── models.py            # UAV, camera, mission dataclasses
├── parameters.py        # Survey parameter formulas
├── planner.py           # High-level plan() API
├── mission_splitter.py  # Flight-time mission splitting
├── geometry/            # Shapely map and transforms
├── patterns/            # Coverage search patterns
├── io/                  # Config, KML, QGC, coordinate conversion
└── gpu/                 # Optional CuPy kernels
```

## License

MIT License. Copyright (c) J. Irving Vasquez-Gomez.
