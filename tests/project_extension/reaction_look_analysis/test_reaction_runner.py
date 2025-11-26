from pathlib import Path

import pandas as pd
import pytest

from project_extension.analyses.time_window_look_analysis import run, stats


def _write_fixations(tmp_path: Path) -> None:
    rows = [
        {
            "participant_id": "P1",
            "trial_number": 1,
            "condition": "sw",
            "participant_age_months": 7,
            "gaze_start_frame": 68,
            "gaze_end_frame": 75,
            "aoi_category": "man_face",
        },
        {
            "participant_id": "P2",
            "trial_number": 1,
            "condition": "sw",
            "participant_age_months": 10,
            "gaze_start_frame": 80,
            "gaze_end_frame": 90,
            "aoi_category": "man_face",
        },
    ]
    pd.DataFrame(rows).to_csv(tmp_path / "fixations.csv", index=False)


def test_run_analysis_produces_outputs(tmp_path: Path):
    _write_fixations(tmp_path)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"input_fixations: \"{(tmp_path / 'fixations.csv').as_posix()}\"",
                "condition_codes: [\"sw\"]",
                "target_aoi: \"man_face\"",
                "window_start: 70",
                "window_end: 90",
                "cohorts:",
                "  - label: \"7-month-olds\"",
                "    min_months: 7",
                "    max_months: 7",
                "  - label: \"Adults\"",
                "    min_months: 216",
                "    max_months: 600",
            ]
        ),
        encoding="utf-8",
    )
    run.run_analysis(config_path)
    output_dir = config_path.with_suffix("")
    assert (output_dir / "tables" / f"{config_path.stem}_time_window_summary.csv").exists()
    assert (output_dir / "figures" / f"{config_path.stem}_time_window_forest_plot.png").exists()


def test_stats_outputs():
    df = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "participant_age_months": 216,
                "looked_at_target": 1,
            },
            {
                "participant_id": "P2",
                "participant_age_months": 7,
                "looked_at_target": 0,
            },
        ]
    )
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "Adults", "min_months": 216, "max_months": 600},
    ]
    adult_results, _ = stats.run_adult_reference_gee(df, cohorts)
    assert "odds_ratio" in adult_results.columns
    trend, _ = stats.run_linear_trend(df, infant_cohorts=[cohorts[0]])
    assert "coef" in trend

