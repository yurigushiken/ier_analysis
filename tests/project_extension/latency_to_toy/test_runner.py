from pathlib import Path

import pandas as pd
import pytest

from project_extension.analyses.latency_to_toy import run, stats


def _write_sample_fixations(target_dir: Path) -> None:
    rows = [
        {
            "participant_id": "P1",
            "trial_number": 1,
            "condition": "gw",
            "participant_age_months": 7,
            "gaze_start_frame": 25,
            "gaze_end_frame": 35,
            "aoi_category": "toy_present",
        },
        {
            "participant_id": "P2",
            "trial_number": 1,
            "condition": "gw",
            "participant_age_months": 10,
            "gaze_start_frame": 40,
            "gaze_end_frame": 50,
            "aoi_category": "toy_present",
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(target_dir / "fixations.csv", index=False)


def test_run_analysis_produces_outputs(tmp_path: Path):
    _write_sample_fixations(tmp_path)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"input_threshold_dir: \"{tmp_path.as_posix()}\"",
                "input_filename: \"fixations.csv\"",
                "condition_codes: [\"gw\"]",
                "toy_aois: [\"toy_present\"]",
                "window:",
                "  start_frame: 30",
                "  end_frame: 80",
                "cohorts:",
                "  - label: \"7-month-olds\"",
                "    min_months: 7",
                "    max_months: 7",
                "  - label: \"10-month-olds\"",
                "    min_months: 10",
                "    max_months: 10",
                "gee:",
                "  reference_label: \"7-month-olds\"",
            ]
        ),
        encoding="utf-8",
    )
    run.run_analysis(config_path)
    output_dir = config_path.with_suffix("")
    summary = output_dir / "tables" / f"{config_path.stem}_latency_stats.csv"
    assert summary.exists()
    assert (output_dir / "figures" / f"{config_path.stem}_latency_forest_plot.png").exists()


def test_infant_trend_output(tmp_path: Path):
    latency_df = pd.DataFrame(
        [
            {"participant_id": "P1", "participant_age_months": 7, "latency_frames": 0},
            {"participant_id": "P2", "participant_age_months": 9, "latency_frames": 5},
        ]
    )
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "9-month-olds", "min_months": 9, "max_months": 9},
        {"label": "Adults", "min_months": 216, "max_months": 600},
    ]
    results, report = stats.run_adult_reference_gee(latency_df, cohorts=cohorts)
    assert "Adults" in results["cohort"].values
    assert "Reference cohort" in report

