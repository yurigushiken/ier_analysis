"""Integration test for AR-4 Dwell Time Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar4_dwell_times as ar4


def _create_sample_gaze_fixations(output_path: Path) -> pd.DataFrame:
    """Create sample gaze fixations data with varying dwell times."""
    data = pd.DataFrame(
        [
            # Participant P1 - GIVE_WITH condition
            {
                "gaze_fixation_id": 1,
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
                "gaze_duration_ms": 500.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.5,
            },
            {
                "gaze_fixation_id": 2,
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
                "gaze_onset_time": 0.5,
                "gaze_offset_time": 0.8,
            },
            # Participant P1 - HUG_WITH condition (shorter dwell times)
            {
                "gaze_fixation_id": 3,
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
                "gaze_end_frame": 4,
                "gaze_duration_frames": 4,
                "gaze_duration_ms": 200.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_fixation_id": 4,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "woman_face",
                "gaze_start_frame": 5,
                "gaze_end_frame": 8,
                "gaze_duration_frames": 4,
                "gaze_duration_ms": 200.0,
                "gaze_onset_time": 0.2,
                "gaze_offset_time": 0.4,
            },
            # Participant P2 - GIVE_WITH condition
            {
                "gaze_fixation_id": 5,
                "participant_id": "P2",
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
                "gaze_duration_ms": 750.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.75,
            },
            {
                "gaze_fixation_id": 6,
                "participant_id": "P2",
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
                "gaze_duration_ms": 250.0,
                "gaze_onset_time": 0.75,
                "gaze_offset_time": 1.0,
            },
            # Participant P2 - HUG_WITH condition
            {
                "gaze_fixation_id": 7,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 1,
                "gaze_end_frame": 5,
                "gaze_duration_frames": 5,
                "gaze_duration_ms": 250.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.25,
            },
            {
                "gaze_fixation_id": 8,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "woman_body",
                "gaze_start_frame": 6,
                "gaze_end_frame": 9,
                "gaze_duration_frames": 4,
                "gaze_duration_ms": 200.0,
                "gaze_onset_time": 0.25,
                "gaze_offset_time": 0.45,
            },
            # Add a very short dwell time to test filtering
            {
                "gaze_fixation_id": 9,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "screen_nonAOI",
                "gaze_start_frame": 10,
                "gaze_end_frame": 11,
                "gaze_duration_frames": 2,
                "gaze_duration_ms": 50.0,
                "gaze_onset_time": 0.45,
                "gaze_offset_time": 0.5,
            },
        ]
    )

    # Save to file for the analysis module to load
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    return data


def test_ar4_analysis_end_to_end(tmp_path: Path):
    """Test AR-4 analysis from gaze fixations to report generation."""
    # Setup: Create sample gaze fixations
    processed_dir = tmp_path / "data" / "processed"
    gaze_fixations_path = processed_dir / "gaze_fixations_child.csv"
    _create_sample_gaze_fixations(gaze_fixations_path)

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
            "ar4_dwell_times": {
                "dwell_time": {
                    "min_dwell_time_ms": 100,
                    "max_dwell_time_ms": 10000,
                    "outlier_threshold_sd": 3,
                },
                "aoi_analysis": {
                    "min_gaze_fixations_per_aoi": 2,
                },
            },
        },
    }

    # Execute: Run AR-4 analysis
    result = ar4.run(config=config)

    # Verify: Check metadata
    assert result["report_id"] == "AR-4"
    assert result["title"] == "Dwell Time Analysis"
    assert result["html_path"] != ""
    assert result["pdf_path"] != ""

    # Verify: Check output files exist
    ar4_output_dir = results_dir / "AR4_Dwell_Times"
    assert ar4_output_dir.exists()

    # Verify: HTML report exists
    html_path = Path(result["html_path"])
    assert html_path.exists()
    assert html_path.suffix == ".html"

    # Verify: CSV outputs exist
    participant_csv = ar4_output_dir / "participant_dwell_times.csv"
    assert participant_csv.exists()
    participant_df = pd.read_csv(participant_csv)
    assert not participant_df.empty
    assert "participant_id" in participant_df.columns
    assert "condition_name" in participant_df.columns
    assert "mean_dwell_time_ms" in participant_df.columns

    # Verify: Expected number of participant-condition combinations
    # P1: GIVE_WITH, HUG_WITH; P2: GIVE_WITH, HUG_WITH = 4 total
    assert len(participant_df) == 4

    # Verify: Condition summary
    condition_csv = ar4_output_dir / "condition_summary.csv"
    assert condition_csv.exists()
    condition_df = pd.read_csv(condition_csv)
    assert not condition_df.empty
    assert "condition_name" in condition_df.columns
    assert "mean_dwell_time_ms" in condition_df.columns
    assert "n_participants" in condition_df.columns

    # Verify: Both conditions present
    assert set(condition_df["condition_name"]) == {"GIVE_WITH", "HUG_WITH"}

    # Verify: Correct number of participants per condition
    for _, row in condition_df.iterrows():
        assert row["n_participants"] == 2  # Both P1 and P2 in each condition

    # Verify: GIVE_WITH should have longer mean dwell times than HUG_WITH
    give_mean = condition_df[condition_df["condition_name"] == "GIVE_WITH"]["mean_dwell_time_ms"].iloc[0]
    hug_mean = condition_df[condition_df["condition_name"] == "HUG_WITH"]["mean_dwell_time_ms"].iloc[0]
    assert give_mean > hug_mean  # GIVE_WITH dwell times are longer in our sample data

    # Verify: AOI summary
    aoi_csv = ar4_output_dir / "aoi_summary.csv"
    assert aoi_csv.exists()

    # Verify: Figures were generated
    condition_fig = ar4_output_dir / "dwell_time_by_condition.png"
    assert condition_fig.exists()


def test_ar4_calculate_participant_dwell_times():
    """Test participant dwell time calculation with filtering."""
    data = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 500.0,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 300.0,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 200.0,
                "trial_number": 2,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 50.0,  # Below minimum, should be filtered
                "trial_number": 2,
            },
        ]
    )

    result = ar4.calculate_participant_dwell_times(data, min_dwell_time_ms=100)

    # Verify: P1 GIVE_WITH should average 500 and 300 = 400 ms
    p1_give = result[(result["participant_id"] == "P1") & (result["condition_name"] == "GIVE_WITH")]
    assert len(p1_give) == 1
    assert pytest.approx(p1_give.iloc[0]["mean_dwell_time_ms"], rel=1e-6) == 400.0
    assert p1_give.iloc[0]["gaze_fixation_count"] == 2

    # Verify: P1 HUG_WITH should only have 200 ms (50 ms filtered out)
    p1_hug = result[(result["participant_id"] == "P1") & (result["condition_name"] == "HUG_WITH")]
    assert len(p1_hug) == 1
    assert pytest.approx(p1_hug.iloc[0]["mean_dwell_time_ms"], rel=1e-6) == 200.0
    assert p1_hug.iloc[0]["gaze_fixation_count"] == 1


def test_ar4_summarize_by_condition():
    """Test condition-level summarization."""
    participant_means = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "mean_dwell_time_ms": 400.0,
                "gaze_fixation_count": 2,
            },
            {
                "participant_id": "P2",
                "condition_name": "GIVE_WITH",
                "mean_dwell_time_ms": 500.0,
                "gaze_fixation_count": 2,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG_WITH",
                "mean_dwell_time_ms": 200.0,
                "gaze_fixation_count": 1,
            },
            {
                "participant_id": "P2",
                "condition_name": "HUG_WITH",
                "mean_dwell_time_ms": 225.0,
                "gaze_fixation_count": 2,
            },
        ]
    )

    result = ar4.summarize_by_condition(participant_means)

    # Verify: Both conditions present
    assert set(result["condition_name"]) == {"GIVE_WITH", "HUG_WITH"}

    # Verify: GIVE_WITH mean = (400 + 500) / 2 = 450
    give_row = result[result["condition_name"] == "GIVE_WITH"].iloc[0]
    assert pytest.approx(give_row["mean_dwell_time_ms"], rel=1e-6) == 450.0
    assert give_row["n_participants"] == 2

    # Verify: HUG_WITH mean = (200 + 225) / 2 = 212.5
    hug_row = result[result["condition_name"] == "HUG_WITH"].iloc[0]
    assert pytest.approx(hug_row["mean_dwell_time_ms"], rel=1e-6) == 212.5
    assert hug_row["n_participants"] == 2


def test_ar4_empty_gaze_fixations(tmp_path: Path):
    """Test AR-4 analysis with empty gaze fixations file."""
    # Setup: Create empty gaze fixations file
    processed_dir = tmp_path / "data" / "processed"
    gaze_fixations_path = processed_dir / "gaze_fixations_child.csv"

    processed_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["gaze_duration_ms", "participant_id", "condition_name"]).to_csv(gaze_fixations_path, index=False)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    # Execute: Run AR-4 analysis
    result = ar4.run(config=config)

    # Verify: Analysis returns empty metadata
    assert result["report_id"] == "AR-4"
    assert result["html_path"] == ""
    assert result["pdf_path"] == ""


def test_ar4_missing_gaze_fixations_file(tmp_path: Path):
    """Test AR-4 analysis when gaze fixations file is missing."""
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    # Note: NOT creating the gaze_fixations file

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
    }

    # Execute: Run AR-4 analysis
    result = ar4.run(config=config)

    # Verify: Analysis returns empty metadata when file is missing
    assert result["report_id"] == "AR-4"
    assert result["html_path"] == ""
    assert result["pdf_path"] == ""


def test_ar4_aoi_analysis(tmp_path: Path):
    """Test AOI-specific dwell time analysis."""
    # Setup: Create sample data with different AOIs
    processed_dir = tmp_path / "data" / "processed"
    gaze_fixations_path = processed_dir / "gaze_fixations_child.csv"

    data = pd.DataFrame(
        [
            # Multiple toy_present gazes in GIVE_WITH
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 500.0,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 600.0,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 550.0,
                "trial_number": 1,
            },
            # Fewer man_face gazes
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 300.0,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 350.0,
                "trial_number": 1,
            },
        ]
    )

    processed_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(gaze_fixations_path, index=False)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar4_dwell_times": {
                "dwell_time": {"min_dwell_time_ms": 100},
                "aoi_analysis": {"min_gaze_fixations_per_aoi": 2},
            },
        },
    }

    # Execute: Run AR-4 analysis
    result = ar4.run(config=config)

    # Verify: AOI summary was generated
    ar4_output_dir = results_dir / "AR4_Dwell_Times"
    aoi_csv = ar4_output_dir / "aoi_summary.csv"
    assert aoi_csv.exists()

    aoi_df = pd.read_csv(aoi_csv)
    assert not aoi_df.empty
    assert "aoi_category" in aoi_df.columns
    assert "mean_dwell_time_ms" in aoi_df.columns

    # Verify: toy_present should have mean of (500 + 600 + 550) / 3 = 550 ms
    toy_row = aoi_df[aoi_df["aoi_category"] == "toy_present"]
    if not toy_row.empty:
        assert pytest.approx(toy_row.iloc[0]["mean_dwell_time_ms"], rel=1e-6) == 550.0
