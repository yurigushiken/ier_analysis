"""Integration test for AR-6 Trial-Order Effects Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis import ar6_learning as ar6


def _create_sample_gaze_events_with_trials(output_path: Path) -> pd.DataFrame:
    """Create sample gaze events showing trial-order effects."""
    data = []
    for participant_id in ["P1", "P2", "P3"]:
        for trial_num in range(1, 4):  # 3 trials per participant
            # Simulate decreasing looking time (habituation)
            base_duration = 600 - (trial_num * 50)  # 600, 550, 500

            data.extend(
                [
                    {
                        "gaze_event_id": len(data) + 1,
                        "participant_id": participant_id,
                        "participant_type": "infant",
                        "age_months": 10,
                        "age_group": "10-month-olds",
                        "trial_number": trial_num,
                        "trial_number_global": trial_num,
                        "condition": "gw",
                        "condition_name": "GIVE_WITH",
                        "segment": "action",
                        "aoi_category": "toy_present",
                        "gaze_start_frame": 1,
                        "gaze_end_frame": 10,
                        "gaze_duration_frames": 10,
                        "gaze_duration_ms": float(base_duration),
                        "gaze_onset_time": 0.0,
                        "gaze_offset_time": 0.6,
                    },
                    {
                        "gaze_event_id": len(data) + 2,
                        "participant_id": participant_id,
                        "participant_type": "infant",
                        "age_months": 10,
                        "age_group": "10-month-olds",
                        "trial_number": trial_num,
                        "trial_number_global": trial_num,
                        "condition": "gw",
                        "condition_name": "GIVE_WITH",
                        "segment": "action",
                        "aoi_category": "screen_nonAOI",
                        "gaze_start_frame": 11,
                        "gaze_end_frame": 15,
                        "gaze_duration_frames": 5,
                        "gaze_duration_ms": 400.0,
                        "gaze_onset_time": 0.6,
                        "gaze_offset_time": 1.0,
                    },
                ]
            )

    df = pd.DataFrame(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def test_ar6_analysis_end_to_end(tmp_path: Path):
    """Test AR-6 analysis from gaze events to report generation."""
    # Setup
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"
    _create_sample_gaze_events_with_trials(gaze_events_path)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    # Execute
    result = ar6.run(config=config)

    # Verify metadata
    assert result["report_id"] == "AR-6"
    assert result["title"] == "Trial-Order Effects Analysis"
    assert result["html_path"] != ""

    # Verify outputs
    ar6_output_dir = results_dir / "AR6_Learning"
    assert ar6_output_dir.exists()

    html_path = Path(result["html_path"])
    assert html_path.exists()

    # Verify CSV outputs
    trial_csv = ar6_output_dir / "proportion_primary_aois_by_trial.csv"
    assert trial_csv.exists()

    summary_csv = ar6_output_dir / "proportion_primary_aois_trial_summary.csv"
    assert summary_csv.exists()


def test_ar6_missing_gaze_events(tmp_path: Path):
    """Test AR-6 with missing gaze events file."""
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    result = ar6.run(config=config)

    assert result["report_id"] == "AR-6"
    assert result["html_path"] == ""

