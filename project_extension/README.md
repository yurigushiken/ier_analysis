## Project Extension: Multi-Threshold Gaze Fixations

This self-contained subproject generates gaze-fixation CSV exports directly
from the frame-level inputs stored under `data/csvs_human_verified_vv/`.
Unlike the main pipeline, the code here does not import modules from `src/`;
it ships its own lightweight loader, AOI mapper, and fixation detector so it
can evolve independently.

### Goals

- Consume the original human-verified frame CSVs for child and adult cohorts.
- Detect gaze fixations using consecutive-frame thresholds (defaults: 3, 4, 5).
- Emit threshold-aware outputs under `project_extension/outputs/`, e.g.
  `outputs/min3/gaze_fixations_child_min3.csv`.
- Provide a simple CLI so new thresholds can be generated without touching the
  legacy pipeline.

### Layout

```
project_extension/
├── README.md
├── outputs/                  # Generated CSVs (gitignored)
└── src/
    ├── __init__.py
    ├── config.py            # Constants (thresholds, paths)
    ├── loader.py            # Frame CSV ingestion & validation
    ├── aoi_mapper.py        # Local What/Where → AOI logic
    ├── gaze_detector.py     # Threshold-based fixation detection
    └── generator.py         # CLI entry point (upcoming)
```

Subsequent steps will add the remaining modules plus pytest coverage to drive
development.

### Running the generator

```
conda activate ier_analysis
python -m project_extension.src.generator `
    --thresholds 3 4 5 `
    --output-root project_extension/outputs
```

- Input CSVs are read from `data/csvs_human_verified_vv/child` and `/adult` by
  default. Override with repeated `--child-dir` / `--adult-dir` flags if needed.
- Outputs are organized per threshold, for example:
  - `project_extension/outputs/min3/gaze_fixations_child_min3.csv`
  - `project_extension/outputs/min3/gaze_fixations_adult_min3.csv`
  - `project_extension/outputs/min3/gaze_fixations_combined_min3.csv`
- Each CSV includes a `min_frames` column documenting the threshold applied plus
  a `cohort` column so downstream scripts can filter easily.

### Tests

Project-specific tests live under `tests/project_extension/`:

```
conda activate ier_analysis
pytest tests/project_extension -k project_extension
```

These tests cover both the fixation detector logic and the threshold-aware
output layout of the generator CLI.

