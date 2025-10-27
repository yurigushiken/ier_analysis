"""Integration test for AR-7 Event Dissociation Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar7_dissociation as ar7


def _create_sample_gaze_events_multi_condition(output_path: Path) -> pd.DataFrame:
    """Create sample gaze events across multiple conditions."""
    data = []

    conditions = [
        ("gw", "GIVE_WITH", ["toy_present", "man_face", "woman_face"]),
        ("hw", "HUG_WITH", ["man_face", "woman_face", "man_body"]),
        ("sw", "SHOW_WITH", ["toy_present", "man_face", "screen_nonAOI"]),
    ]

    for participant_id in ["P1", "P2", "P3"]:
        for cond_code, cond_name, aois in conditions:
            for trial_num in [1, 2]:
                for idx, aoi in enumerate(aois):
                    data.append(
                        {
                            "gaze_event_id": len(data) + 1,
                            "participant_id": participant_id,
                            "participant_type": "infant",
                            "age_months": 10,
                            "age_group": "10-month-olds",
                            "trial_number": trial_num,
                            "trial_number_global": len(data) // 10 + 1,
                            "condition": cond_code,
                            "condition_name": cond_name,
                            "segment": "action",
                            "aoi_category": aoi,
                            "gaze_start_frame": idx * 5 + 1,
                            "gaze_end_frame": (idx + 1) * 5,
                            "gaze_duration_frames": 5,
                            "gaze_duration_ms": 200.0,
                            "gaze_onset_time": idx * 0.2,
                            "gaze_offset_time": (idx + 1) * 0.2,
                        }
                    )

    df = pd.DataFrame(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def test_ar7_analysis_end_to_end(tmp_path: Path):
    """Test AR-7 analysis from gaze events to report generation."""
    # Setup
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"
    _create_sample_gaze_events_multi_condition(gaze_events_path)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    # Execute
    result = ar7.run(config=config)

    # Verify metadata
    assert result["report_id"] == "AR-7"
    assert result["title"] == "Event Dissociation Analysis"
    assert result["html_path"] != ""

    # Verify outputs
    ar7_output_dir = results_dir / "AR7_Dissociation"
    assert ar7_output_dir.exists()

    html_path = Path(result["html_path"])
    assert html_path.exists()

    # Verify CSV outputs
    data_csv = ar7_output_dir / "proportion_primary_aois_by_condition.csv"
    assert data_csv.exists()


def test_ar7_missing_gaze_events(tmp_path: Path):
    """Test AR-7 with missing gaze events file."""
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

    result = ar7.run(config=config)

    assert result["report_id"] == "AR-7"
    assert result["html_path"] == ""


def test_ar7_calculate_condition_metrics_integration():
    """Test condition metrics with realistic data structure."""
    gaze_events = pd.DataFrame(
        [
            {"participant_id": "P1", "condition_name": "GIVE", "aoi_category": "toy_present", "gaze_duration_ms": 600},
            {"participant_id": "P1", "condition_name": "GIVE", "aoi_category": "screen_nonAOI", "gaze_duration_ms": 400},
            {"participant_id": "P2", "condition_name": "HUG", "aoi_category": "man_face", "gaze_duration_ms": 500},
            {"participant_id": "P2", "condition_name": "HUG", "aoi_category": "screen_nonAOI", "gaze_duration_ms": 500},
        ]
    )

    result = ar7.calculate_condition_metrics(gaze_events)

    assert len(result) == 2  # Two participants, different conditions

    p1 = result[result["participant_id"] == "P1"]
    assert pytest.approx(p1.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.6

    p2 = result[result["participant_id"] == "P2"]
    assert pytest.approx(p2.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.5

