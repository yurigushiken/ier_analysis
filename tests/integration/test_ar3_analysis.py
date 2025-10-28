"""Integration test for AR-3 Social Triplet Analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar3_social_triplets as ar3


def _create_sample_gaze_fixations(output_path: Path) -> pd.DataFrame:
    """Create sample gaze fixations data with triplet patterns."""
    data = pd.DataFrame(
        [
            # Participant P1, Trial 1 - GIVE_WITH condition
            # Pattern: man_face -> toy_present -> woman_face (valid triplet)
            {
                "gaze_fixation_id": 1,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "interaction",
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
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
                "segment": "interaction",
                "aoi_category": "toy_present",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_fixation_id": 3,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "interaction",
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
                "gaze_fixation_id": 4,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "interaction",
                "aoi_category": "woman_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
            },
            {
                "gaze_fixation_id": 5,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "interaction",
                "aoi_category": "toy_present",
                "gaze_start_frame": 4,
                "gaze_end_frame": 6,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.1,
                "gaze_offset_time": 0.2,
            },
            {
                "gaze_fixation_id": 6,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 2,
                "condition": "hw",
                "condition_name": "HUG_WITH",
                "segment": "interaction",
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
                "gaze_fixation_id": 7,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "interaction",
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
            },
            {
                "gaze_fixation_id": 8,
                "participant_id": "P2",
                "participant_type": "infant",
                "age_months": 12,
                "age_group": "12-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "interaction",
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
    """Fail-first: AR-3 should honor variant configs and export directional summaries."""

    processed_dir = tmp_path / "data" / "processed"
    gaze_fixations_path = processed_dir / "gaze_fixations_child.csv"
    _create_sample_gaze_fixations(gaze_fixations_path)

    results_dir = tmp_path / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar3_social_triplets": {
                "config_name": "AR3_social_triplets/ar3_give_vs_hug",
            },
        },
    }
    # Point variant cohort paths to the temporary processed dataset by overriding env var
    variant_path = Path("config/analysis_configs/AR3_social_triplets/ar3_give_vs_hug.yaml")
    original_yaml = variant_path.read_text(encoding="utf-8")
    updated_yaml = original_yaml.replace("data/processed/gaze_fixations_child.csv", str(gaze_fixations_path).replace("\\", "/"))
    updated_yaml = updated_yaml.replace("data/processed/gaze_fixations_adult.csv", str(gaze_fixations_path).replace("\\", "/"))
    temp_variant_path = tmp_path / "config" / "analysis_configs" / "ar3" / "ar3_variant.yaml"
    temp_variant_path.parent.mkdir(parents=True, exist_ok=True)
    temp_variant_path.write_text(updated_yaml, encoding="utf-8")

    monkeypatch_env = pytest.MonkeyPatch()
    monkeypatch_env.setenv("IER_AR3_CONFIG", str(temp_variant_path.resolve()))

    result = ar3.run(config=config)
    monkeypatch_env.undo()

    variant_output_dir = results_dir / "AR3_social_triplets" / "ar3_give_vs_hug"

    # Fail-first expectations: variant metadata and directory structure
    assert result["report_id"] == "AR-3"
    assert result["title"] == "Social Gaze Triplet Analysis"
    assert result.get("variant_key") == "ar3_give_vs_hug"
    assert Path(result["html_path"]).parent == variant_output_dir
    assert not result["pdf_path"]

    assert variant_output_dir.exists()

    triplets_csv = variant_output_dir / "triplets_detected.csv"
    counts_csv = variant_output_dir / "triplet_counts_by_trial.csv"
    summary_condition_csv = variant_output_dir / "triplet_summary_by_condition.csv"
    summary_age_csv = variant_output_dir / "triplet_summary_by_age_group.csv"
    directional_bias_csv = variant_output_dir / "triplet_directional_bias.csv"
    temporal_summary_csv = variant_output_dir / "triplet_temporal_summary.csv"

    for required in [
        triplets_csv,
        counts_csv,
        summary_condition_csv,
        summary_age_csv,
        directional_bias_csv,
        temporal_summary_csv,
    ]:
        assert required.exists(), f"Expected export missing: {required}"

    triplets_df = pd.read_csv(triplets_csv)
    assert set(triplets_df["pattern"].unique()) == {
        "man_face>toy_present>woman_face",
        "woman_face>toy_present>man_face",
    }

    summary_condition_df = pd.read_csv(summary_condition_csv)
    assert set(summary_condition_df["condition_name"]) == {"GIVE_WITH", "HUG_WITH"}

    directional_df = pd.read_csv(directional_bias_csv)
    assert {"pattern", "condition_name", "count"}.issubset(directional_df.columns)
    assert {
        "man_face>toy_present>woman_face",
        "woman_face>toy_present>man_face",
    }.issubset(set(directional_df["pattern"]))

    temporal_df = pd.read_csv(temporal_summary_csv)
    assert {"condition_name", "first_occurrence", "subsequent_occurrences"}.issubset(
        temporal_df.columns
    )


def test_ar3_detect_triplets_with_valid_patterns():
    """Test triplet detection with sample data."""
    gaze_fixations = pd.DataFrame(
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

    triplets = ar3.detect_triplets(gaze_fixations, valid_patterns, require_consecutive=True)

    assert len(triplets) == 1
    assert triplets.iloc[0]["pattern"] == "man_face>toy_present>woman_face"
    assert triplets.iloc[0]["participant_id"] == "P1"
    assert triplets.iloc[0]["trial_number"] == 1


def test_ar3_no_triplets_detected(tmp_path: Path):
    """Test AR-3 analysis when no triplets are detected."""
    # Setup: Create gaze fixations with no valid triplet patterns
    processed_dir = tmp_path / "data" / "processed"
    gaze_fixations_path = processed_dir / "gaze_fixations_child.csv"

    data = pd.DataFrame(
        [
            {
                "gaze_fixation_id": 1,
                "participant_id": "P1",
                "participant_type": "infant",
                "age_months": 8,
                "age_group": "8-month-olds",
                "trial_number": 1,
                "condition": "gw",
                "condition_name": "GIVE_WITH",
                "segment": "interaction",
                "aoi_category": "man_face",
                "gaze_start_frame": 1,
                "gaze_end_frame": 3,
                "gaze_duration_frames": 3,
                "gaze_duration_ms": 100.0,
                "gaze_onset_time": 0.0,
                "gaze_offset_time": 0.1,
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
                "segment": "interaction",
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
    data.to_csv(gaze_fixations_path, index=False)

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

    variant_path = Path("config/analysis_configs/AR3_social_triplets/ar3_give_vs_hug.yaml")
    original_yaml = variant_path.read_text(encoding="utf-8")
    updated_yaml = (
        original_yaml
        .replace("data/processed/gaze_fixations_child.csv", str(gaze_fixations_path).replace("\\", "/"))
        .replace("data/processed/gaze_fixations_adult.csv", str(gaze_fixations_path).replace("\\", "/"))
    )
    temp_variant_path = tmp_path / "config" / "analysis_configs" / "ar3" / "ar3_variant.yaml"
    temp_variant_path.parent.mkdir(parents=True, exist_ok=True)
    temp_variant_path.write_text(updated_yaml, encoding="utf-8")

    monkeypatch_env = pytest.MonkeyPatch()
    monkeypatch_env.setenv("IER_AR3_CONFIG", str(temp_variant_path.resolve()))

    # Execute: Run AR-3 analysis
    result = ar3.run(config=config)
    monkeypatch_env.undo()

    # Verify: Analysis completes even with no triplets
    assert result["report_id"] == "AR-3"
    html_path = Path(result["html_path"])
    assert html_path.exists()

    # Verify: Empty triplets CSV still created
    ar3_output_dir = Path(result["html_path"]).parent
    triplets_csv = ar3_output_dir / "triplets_detected.csv"
    assert triplets_csv.exists()
    triplets_df = pd.read_csv(triplets_csv)
    assert len(triplets_df) == 0  # No triplets detected


def test_ar3_missing_gaze_fixations_file(tmp_path: Path):
    """Test AR-3 analysis when gaze fixations file is missing."""
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
    assert result.get("variant_key") is None




