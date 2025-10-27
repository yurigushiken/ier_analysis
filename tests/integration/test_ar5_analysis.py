"""Integration test for AR-5 Developmental Trajectory Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar5_development as ar5


def _create_sample_gaze_events_with_age(output_path: Path) -> pd.DataFrame:
    """Create sample gaze events with age variation for integration testing."""
    data = pd.DataFrame(
        [
            # Younger infants (8 months) - show developmental pattern
            {
                "gaze_event_id": 1,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 10,
                "gaze_duration_frames": 10,
                "gaze_duration_ms": 400.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.4,
            },
            {
                "gaze_event_id": 2,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "man_face",
                "gaze_start_frame": 11,
                "gaze_end_frame": 16,
                "gaze_duration_frames": 6,
                "gaze_duration_ms": 300.0,
                "gaze_onset_time": 0.4,
                "gaze_offset_time": 0.7,
            },
            # Middle age (10 months)
            {
                "gaze_event_id": 3,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 10,
                "age_group": "10-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 12,
                "gaze_duration_frames": 12,
                "gaze_duration_ms": 500.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.5,
            },
            {
                "gaze_event_id": 4,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 10,
                "age_group": "10-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "woman_face",
                "gaze_start_frame": 13,
                "gaze_end_frame": 20,
                "gaze_duration_frames": 8,
                "gaze_duration_ms": 400.0,
                "gaze_onset_time": 0.5,
                "gaze_offset_time": 0.9,
            },
            # Older infants (12 months) - different pattern
            {
                "gaze_event_id": 5,
                "participant_id": "P3",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 15,
                "gaze_duration_frames": 15,
                "gaze_duration_ms": 600.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.6,
            },
            {
                "gaze_event_id": 6,
                "participant_id": "P3",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "man_face",
                "gaze_start_frame": 16,
                "gaze_end_frame": 20,
                "gaze_duration_frames": 5,
                "gaze_duration_ms": 350.0,
                "gaze_onset_time": 0.6,
                "gaze_offset_time": 0.95,
            },
            # Add HUG condition data for comparison
            {
                "gaze_event_id": 7,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 5,
                "gaze_duration_frames": 5,
                "gaze_duration_ms": 200.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_event_id": 8,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 10,
                "age_group": "10-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 6,
                "gaze_duration_ms": 240.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.24,
            },
            {
                "gaze_event_id": 9,
                "participant_id": "P3",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 7,
                "gaze_duration_frames": 7,
                "gaze_duration_ms": 280.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.28,
            },
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    return data


def test_ar5_analysis_end_to_end(tmp_path: Path):
    """Test AR-5 analysis from gaze events to report generation."""
    # Setup: Create sample gaze events with age variation
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"
    _create_sample_gaze_events_with_age(gaze_events_path)

    # Setup: Create results directory
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Setup: Create config
    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar5_development": {
                "age_modeling": {
                    "use_continuous_age": True,
                    "test_nonlinear": True,
                },
                "metrics": {
                    "dependent_variables": ["proportion_primary_aois"],
                },
            },
        },
    }

    # Execute: Run AR-5 analysis
    result = ar5.run(config=config)

    # Verify: Check metadata
    assert result["report_id"] == "AR-5"
    assert result["title"] == "Developmental Trajectory Analysis"
    assert result["html_path"] != ""
    assert result["pdf_path"] != ""

    # Verify: Check output files exist
    ar5_output_dir = results_dir / "AR5_Development"
    assert ar5_output_dir.exists()

    # Verify: HTML report exists
    html_path = Path(result["html_path"])
    assert html_path.exists()
    assert html_path.suffix == ".html"

    # Verify: CSV outputs exist
    data_csv = ar5_output_dir / "proportion_primary_aois_by_age_condition.csv"
    assert data_csv.exists()
    data_df = pd.read_csv(data_csv)
    assert not data_df.empty
    assert "age_months" in data_df.columns
    assert "condition_name" in data_df.columns
    assert "proportion_primary_aois" in data_df.columns

    # Verify: Summary CSV exists
    summary_csv = ar5_output_dir / "proportion_primary_aois_summary.csv"
    assert summary_csv.exists()
    summary_df = pd.read_csv(summary_csv)
    assert not summary_df.empty

    # Verify: Coefficients CSV exists
    coef_csv = ar5_output_dir / "proportion_primary_aois_coefficients.csv"
    assert coef_csv.exists()

    # Verify: ANOVA CSV exists
    anova_csv = ar5_output_dir / "proportion_primary_aois_anova.csv"
    assert anova_csv.exists()

    # Verify: Figure was generated
    fig_path = ar5_output_dir / "proportion_primary_aois_age_by_condition.png"
    assert fig_path.exists()


def test_ar5_calculate_proportion_primary_aois():
    """Test proportion calculation with real-like data structure."""
    gaze_events = pd.DataFrame(
        [
            {"participant_id": "P1", "age_months": 8, "condition_name": "GIVE", "aoi_category": "toy_present", "gaze_duration_ms": 500},
            {"participant_id": "P1", "age_months": 8, "condition_name": "GIVE", "aoi_category": "screen_nonAOI", "gaze_duration_ms": 500},
            {"participant_id": "P2", "age_months": 12, "condition_name": "GIVE", "aoi_category": "man_face", "gaze_duration_ms": 800},
            {"participant_id": "P2", "age_months": 12, "condition_name": "GIVE", "aoi_category": "screen_nonAOI", "gaze_duration_ms": 200},
        ]
    )

    result = ar5.calculate_proportion_primary_aois(gaze_events)

    # P1: 500 / 1000 = 0.5
    p1_row = result[result["participant_id"] == "P1"]
    assert pytest.approx(p1_row.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.5

    # P2: 800 / 1000 = 0.8
    p2_row = result[result["participant_id"] == "P2"]
    assert pytest.approx(p2_row.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.8


def test_ar5_missing_gaze_events_file(tmp_path: Path):
    """Test AR-5 analysis when gaze events file is missing."""
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

    # Execute: Run AR-5 analysis
    result = ar5.run(config=config)

    # Verify: Analysis returns empty metadata when file is missing
    assert result["report_id"] == "AR-5"
    assert result["html_path"] == ""
    assert result["pdf_path"] == ""


def test_ar5_empty_gaze_events(tmp_path: Path):
    """Test AR-5 analysis with empty gaze events file."""
    # Setup: Create empty gaze events file
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"

    processed_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["gaze_duration_ms", "participant_id", "age_months"]).to_csv(
        gaze_events_path, index=False
    )

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    # Execute: Run AR-5 analysis
    result = ar5.run(config=config)

    # Verify: Analysis returns empty metadata
    assert result["report_id"] == "AR-5"
    assert result["html_path"] == ""
    assert result["pdf_path"] == ""

