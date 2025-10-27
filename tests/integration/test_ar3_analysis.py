"""Integration test for AR-3 Social Triplet Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar3_social_triplets as ar3


def _create_sample_gaze_events(output_path: Path) -> pd.DataFrame:
    """Create sample gaze events data with triplet patterns."""
    data = pd.DataFrame(
        [
            # Participant P1, Trial 1 - GIVE_WITH condition
            # Pattern: man_face -> toy_present -> woman_face (valid triplet)
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
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
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
                "aoi_category": "toy_present",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_event_id": 3,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "woman_face",
                "gaze_start_frame": 7,
                "gaze_end_frame": 9,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.2,
                "gaze_offset_time": 0.3,
            },
            # Participant P1, Trial 2 - HUG_WITH condition
            # Pattern: woman_face -> toy_present -> man_face (valid triplet, reverse order)
            {
                "gaze_event_id": 4,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "woman_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
            },
            {
                "gaze_event_id": 5,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "toy_present",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_event_id": 6,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "action",
                "aoi_category": "man_face",
                "gaze_start_frame": 7,
                "gaze_end_frame": 9,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.2,
                "gaze_offset_time": 0.3,
            },
            # Participant P2, Trial 1 - GIVE_WITH condition
            # Pattern with no triplet (just faces, no toy)
            {
                "gaze_event_id": 7,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
            },
            {
                "gaze_event_id": 8,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "action",
                "aoi_category": "woman_face",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
        ]
    )

    # Save to file for the analysis module to load
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    return data


def test_ar3_analysis_end_to_end(tmp_path: Path):
    """Test AR-3 analysis from gaze events to report generation."""
    # Setup: Create sample gaze events
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"
    _create_sample_gaze_events(gaze_events_path)

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
            "ar3_social_triplets": {
                "valid_patterns": [
                    ["man_face", "toy_present", "woman_face"],
                    ["woman_face", "toy_present", "man_face"],
                ],
            },
        },
    }

    # Execute: Run AR-3 analysis
    result = ar3.run(config=config)

    # Verify: Check metadata
    assert result["report_id"] == "AR-3"
    assert result["title"] == "Social Gaze Triplet Analysis"
    assert result["html_path"] != ""
    assert result["pdf_path"] != ""

    # Verify: Check output files exist
    ar3_output_dir = results_dir / "AR3_Social_Triplets"
    assert ar3_output_dir.exists()

    # Verify: HTML report exists
    html_path = Path(result["html_path"])
    assert html_path.exists()
    assert html_path.suffix == ".html"

    # Verify: CSV outputs exist
    triplets_csv = ar3_output_dir / "triplets_detected.csv"
    assert triplets_csv.exists()
    triplets_df = pd.read_csv(triplets_csv)

    # Expected: 2 triplets total (P1 has 2 triplets, P2 has 0)
    assert len(triplets_df) == 2

    # Verify: Triplet patterns are correct
    assert set(triplets_df["pattern"].unique()) == {
        "man_face>toy_present>woman_face",
        "woman_face>toy_present>man_face",
    }

    # Verify: Triplet counts by trial
    counts_csv = ar3_output_dir / "triplet_counts_by_trial.csv"
    assert counts_csv.exists()
    counts_df = pd.read_csv(counts_csv)
    assert len(counts_df) >= 2  # At least P1's two trials

    # Verify: Summary by condition
    summary_condition_csv = ar3_output_dir / "triplet_summary_by_condition.csv"
    assert summary_condition_csv.exists()
    summary_condition_df = pd.read_csv(summary_condition_csv)
    assert not summary_condition_df.empty
    assert "condition_name" in summary_condition_df.columns
    assert "mean_triplets" in summary_condition_df.columns

    # Verify: Summary by age group
    summary_age_csv = ar3_output_dir / "triplet_summary_by_age_group.csv"
    assert summary_age_csv.exists()

    # Verify: Figures were generated
    condition_fig = ar3_output_dir / "triplets_by_condition.png"
    age_fig = ar3_output_dir / "triplets_by_age_group.png"
    assert condition_fig.exists() or age_fig.exists()  # At least one figure


def test_ar3_detect_triplets_with_valid_patterns():
    """Test triplet detection with sample data."""
    gaze_events = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "trial_number": 1,
                "condition_name": "GIVE_WITH",
                "age_group": "8-month-olds",
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "trial_number": 1,
                "condition_name": "GIVE_WITH",
                "age_group": "8-month-olds",
                "aoi_category": "toy_present",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_onset_time": 0.1,
            },
            {
                "participant_id": "P1",
                "trial_number": 1,
                "condition_name": "GIVE_WITH",
                "age_group": "8-month-olds",
                "aoi_category": "woman_face",
                "gaze_start_frame": 7,
                "gaze_end_frame": 9,
                "gaze_onset_time": 0.2,
            },
        ]
    )

    valid_patterns = [("man_face", "toy_present", "woman_face")]

    triplets = ar3.detect_triplets(gaze_events, valid_patterns, require_consecutive=True)

    assert len(triplets) == 1
    assert triplets.iloc[0]["pattern"] == "man_face>toy_present>woman_face"
    assert triplets.iloc[0]["participant_id"] == "P1"
    assert triplets.iloc[0]["trial_number"] == 1


def test_ar3_no_triplets_detected(tmp_path: Path):
    """Test AR-3 analysis when no triplets are detected."""
    # Setup: Create gaze events with no valid triplet patterns
    processed_dir = tmp_path / "data" / "processed"
    gaze_events_path = processed_dir / "gaze_events_child.csv"

    data = pd.DataFrame(
        [
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
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
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
                "aoi_category": "woman_body",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
        ]
    )

    processed_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(gaze_events_path, index=False)

    # Setup: Create config
    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar3_social_triplets": {
                "valid_patterns": [
                    ["man_face", "toy_present", "woman_face"],
                ],
            },
        },
    }

    # Execute: Run AR-3 analysis
    result = ar3.run(config=config)

    # Verify: Analysis completes even with no triplets
    assert result["report_id"] == "AR-3"
    html_path = Path(result["html_path"])
    assert html_path.exists()

    # Verify: Empty triplets CSV still created
    ar3_output_dir = results_dir / "AR3_Social_Triplets"
    triplets_csv = ar3_output_dir / "triplets_detected.csv"
    assert triplets_csv.exists()
    triplets_df = pd.read_csv(triplets_csv)
    assert len(triplets_df) == 0  # No triplets detected


def test_ar3_missing_gaze_events_file(tmp_path: Path):
    """Test AR-3 analysis when gaze events file is missing."""
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    # Note: NOT creating the gaze_events file

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar3_social_triplets": {
                "valid_patterns": [["man_face", "toy_present", "woman_face"]],
            },
        },
    }

    # Execute: Run AR-3 analysis
    result = ar3.run(config=config)

    # Verify: Analysis returns empty metadata when file is missing
    assert result["report_id"] == "AR-3"
    assert result["html_path"] == ""
    assert result["pdf_path"] == ""
