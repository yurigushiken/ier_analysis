## Project Extension: Multi-Threshold Gaze Fixations & Tri-Argument Analyses

This subproject serves two complementary purposes:

1. **Generate filtered, threshold-aware fixation CSVs** directly from the
   human-verified frame-level inputs under `data/csvs_human_verified_vv/`. The
   generator enforces ≥30 on-screen frames (i.e., not `What=no/Where=signal`,
   tracked via both `trial_number` and `trial_number_global` so repeated
   exposures are filtered independently) per participant×trial×condition before
   any fixations are detected, and it now supports tougher requirements (e.g.,
   ≥75 frames for “50 % on-screen” datasets or ≥105 frames for “70 % on-screen”
   datasets).
2. **Run tri-argument analyses** (GW/GWO/SW/SWO) that answer the core research
   question: *“At what age do participants reliably fixate every verb argument
   (giver/show-er, recipient/observer, object or its location) within an event?”*

### Research questions & configurations

| YAML             | Condition (frames)                                 | Research question                                                                                   |
|------------------|----------------------------------------------------|------------------------------------------------------------------------------------------------------|
| `gw_min4.yaml`   | GIVE-with-toy (frames 1–150, min4 fixations)       | Do cohorts fixate giver+recipient+toy when the object is present?                                    |
| `gwo_min4.yaml`  | GIVE-without-toy (frames 1–150, min4)              | Do cohorts still encode toy *locations* when the object disappears?                                  |
| `sw_min4.yaml`   | SHOW-with-toy (frames 45–115, min4)                | During the core interaction, do they look at show-er, observer, and toy?                             |
| `swo_min4.yaml`  | SHOW-without-toy (frames 45–115, min4)             | Same as above, but the toy must be inferred.                                                         |
| `gw_min3.yaml`   | GIVE-with-toy (min3 sensitivity analysis)          | How do results shift with a looser fixation threshold?                                               |
| `gwo_min3.yaml`  | GIVE-without-toy (min3)                            | Sensitivity analysis for the absence-of-toy case.                                                    |
| `sw_min3.yaml`   | SHOW-with-toy (min3)                               | Sensitivity analysis for SHOW during the interaction window.                                         |
| `swo_min3.yaml`  | SHOW-without-toy (min3)                            | Sensitivity analysis for SHOW-without-toy.                                                           |

Across all configs we hypothesize a developmental step, with 10–11 month-olds
and adults exhibiting significantly higher tri-argument coverage than 7–9 month
cohorts. Adults should always form the upper bound. Each analysis runs a
statsmodels **GEE (Binomial, logit link)** clustered on participant ID (random
intercept analogue), reporting odds ratios vs the 7-month reference.

### Layout

```
project_extension/
├── README.md
├── outputs/                  # Generated CSVs (gitignored)
├── src/
│   ├── __init__.py
│   ├── config.py            # Constants (thresholds, paths)
│   ├── loader.py            # Frame CSV ingestion & ≥30-frame trial filter
│   ├── aoi_mapper.py        # Local What/Where → AOI logic
│   ├── gaze_detector.py     # Threshold-based fixation detection
│   └── generator.py         # CLI entry point
└── analyses/
    └── tri_argument_fixation/
        ├── run.py           # Shared runner (plots, reports, GEE)
        ├── gw_min4.yaml …   # Condition-specific configs
        └── gw_min4/…        # Per-config outputs (tables/figures/reports)
```

### Running the fixation generator

```
conda activate ier_analysis
python -m project_extension.src.generator `
    --thresholds 3 4 5 `
    --output-root project_extension/outputs `
    --min-onscreen-frames 105 `
    --dir-suffix -70_percent
```

- Default inputs are `data/csvs_human_verified_vv/child` and `/adult`. Override
  with repeated `--child-dir`/`--adult-dir` flags if needed.
- Pass `--exclude-screen-nonroi` to drop `screen_nonAOI` fixations from the exported CSVs
  while still counting them toward on-screen frame totals (useful for the new “no
  screen-other” datasets under `min4-50_percent_no_screen_nonroi` and
  `min4-70_percent_no_screen_nonroi`).
- Outputs per threshold include:
  - `project_extension/outputs/min3/gaze_fixations_child_min3.csv`
  - `project_extension/outputs/min3/gaze_fixations_adult_min3.csv`
  - `project_extension/outputs/min3/gaze_fixations_combined_min3.csv`
  - additional 50 % / 70 % directories such as `min3-50_percent` or
    `min4-70_percent` when `--dir-suffix` is provided.
- Each CSV contains `min_frames` (threshold used), `cohort`, and the requested
  on-screen-frame filter already applied.
- **Current focus:** we primarily use the 70 % datasets
  (`project_extension/outputs/min3-70_percent/…`, `min4-70_percent/…`)
  for the most conservative analyses. Config names ending in `_70_percent`
  reference these directories; `_50_percent` configs point at the ≥75-frame
  datasets; all other configs use the default ≥30-frame outputs.

### Running the tri-argument analyses

```
conda activate ier_analysis
python project_extension/analyses/tri_argument_fixation/run.py --config project_extension/analyses/tri_argument_fixation/gw_min4_70_percent.yaml
# Repeat for gwo_min4, sw_min4, swo_min4, gw_min3, gwo_min3, sw_min3, swo_min3 (+ 50% / 70% variants)
```

Outputs per config (e.g., `project_extension/analyses/tri_argument_fixation/gw_min4/`), with
each filename prefixed by the config name (e.g., `gw_min4_tri_argument_success.png`):

- `tables/{config}_tri_argument_summary.csv`
- `figures/{config}_tri_argument_success.png` – high-DPI bar chart with
  significance brackets ( * p<0.05, ** p<0.01, *** p<0.001 vs the reference
  cohort ), using the friendly condition label (e.g., `"Give"`).
- `figures/{config}_forest_plot_odds_ratios.png` – odds ratios + 95 % CI on a
  log scale with auto-wrapped titles.
- `figures/{config}_trials_per_participant.png` – valid trial counts per
  participant (color-coded by cohort).
- `tables/{config}_event_structure_breakdown.csv`
  & `figures/{config}_event_structure_breakdown.png`
  – event-structure analysis showing monads, dyads, and Trifecta coverage
  (including successful trials) for every config.
- `reports/{config}_tri_argument_report.{txt,html,pdf}` – descriptive summaries +
  embedded figures.
- `reports/{config}_gee_results.txt` – descriptive stats (trial counts, class
  balance), model diagnostics (QIC, scale, covariance type, working
  correlation), and GEE coefficients.

### Tri-argument design highlights (for reuse)

- **Config-driven workflow:** every analysis is defined by a single YAML file
  (inputs, AOI groups, frame windows, cohort bins, reporting text). Adding new
  variants (e.g., `_50_percent`, `_70_percent`) only requires copying the YAML
  and pointing to the desired dataset.
- **Prefixed output naming:** plots, tables, and reports all include the config
  name (e.g., `gw_min4_70_percent_*`). This keeps large result trees organized
  and prevents overwrites when running multiple variants back-to-back.
- **High-DPI visuals with descriptive titles:** plots render at 300 dpi, use
  reader-friendly condition labels (e.g., `"Give"` / `"Show"`), and maintain
  consistent color palettes across Tri-argument success, forest odds ratios,
  trials-per-participant, and event-structure breakdown charts.
- **Event-structure coverage + success integration:** every run now produces the
  `event_structure_breakdown` pair, capturing monads, dyads, and Trifecta
  coverage (including successful trials) so we can see where partial trials are
  converting to full coverage as cohorts age.
- **Robust reporting & testing:** the runner writes aligned TXT/HTML/PDF reports,
  GEE diagnostics, and has targeted pytest coverage (unit + CLI) to ensure new
  configs keep producing all expected outputs.

### Gaze transition analysis (new)

Located under `project_extension/analyses/gaze_transition_analysis/`, this
analysis examines the order of AOI fixations (currently focused on the `"Give"`
condition with 70 % on-screen data).

Run it with:

```
conda activate ier_analysis
python project_extension/analyses/gaze_transition_analysis/run.py `
    --config project_extension/analyses/gaze_transition_analysis/gw_transitions_70_percent.yaml
```

- Outputs per config (prefixed by the config name, e.g.,
  `gw_transitions_min4_70_percent_*`) include:
  - `tables/*_transition_counts.csv` – raw per-participant/trial transition
    counts (one column per AOI→AOI jump, excluding `off_screen`).
  - `tables/*_transition_matrix.csv` – cohort-level mean transition counts for
    each AOI pair (used by the heatmap).
  - `figures/*_transition_heatmap.png` – stacked heatmap visualizing cohort
    differences in transition frequencies.
  - `tables/*_strategy_proportions.csv` & `tables/*_strategy_summary.csv` –
    normalized “Agent-Agent Attention / Agent-Object Binding / Motion
    Tracking” proportions per trial and cohort.
  - `figures/*_gaze_strategy_comparison.png` – grouped bar chart with
    significance brackets showing strategy proportions per cohort.
  - `reports/*_stats_agent_agent_attention.txt`,
    `reports/*_stats_motion_tracking.txt`, and
    `reports/*_stats_agent_object_binding.txt` – GEE summaries for each
    strategy plus the infant linear trend tests (7–11 mo). Linear trend
    summaries are stored alongside these reports.
  - `figures/*_linear_trend_agent_agent_attention.png`,
    `figures/*_linear_trend_motion_tracking.png`, and
    `figures/*_linear_trend_agent_object_binding.png` – scatter/trend-line
    visualizations of each strategy vs. age (7–11 mo).
  - `reports/*_transition_summary.txt` – cohort-organized lists of the top AOI
    transitions, plus total transition counts.

The module reuses the same configuration conventions (YAML inputs, named
cohorts, prefixed outputs) so we can replicate this pattern in future analyses.

### Tests

Project-specific tests live under `tests/project_extension/`:

```
conda activate ier_analysis
pytest tests/project_extension -k project_extension
```

These tests cover both the fixation generator (trial filtering, min-frame
thresholds) and the tri-argument reporting pipeline (bar chart annotations,
forest plots, GEE outputs).
The dedicated tri-argument unit + CLI fixtures live under
`tests/project_extension/tri_argument_fixation/`.

