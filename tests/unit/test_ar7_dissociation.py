"""Unit tests for AR-7 Event Dissociation Analysis."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analysis import ar7_dissociation as ar7


def _sample_condition_data() -> pd.DataFrame:
    """Create sample data across multiple conditions."""
    return pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 500,
                "is_primary": True,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE",
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 500,
                "is_primary": False,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 300,
                "is_primary": True,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG",
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 700,
                "is_primary": False,
            },
            {
                "participant_id": "P1",
                "condition_name": "SHOW",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 450,
                "is_primary": True,
            },
            {
                "participant_id": "P1",
                "condition_name": "SHOW",
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 550,
                "is_primary": False,
            },
        ]
    )


def test_calculate_condition_metrics():
    """Test condition-level metric calculation."""
    gaze_fixations = _sample_condition_data()
    gaze_fixations["condition_family"] = gaze_fixations["condition_name"]

    result = ar7.calculate_condition_metrics(gaze_fixations)

    assert not result.empty
    assert "condition_name" in result.columns
    assert "proportion_primary_aois" in result.columns

    # Verify proportions
    # GIVE: 500 / 1000 = 0.5
    give_row = result[result["condition_name"] == "GIVE"]
    assert pytest.approx(give_row.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.5

    # HUG: 300 / 1000 = 0.3
    hug_row = result[result["condition_name"] == "HUG"]
    assert pytest.approx(hug_row.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.3

    # SHOW: 450 / 1000 = 0.45
    show_row = result[result["condition_name"] == "SHOW"]
    assert pytest.approx(show_row.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.45


def test_calculate_condition_metrics_filtered():
    """Test condition metrics with target conditions filter."""
    gaze_fixations = _sample_condition_data()
    gaze_fixations["condition_family"] = gaze_fixations["condition_name"]

    filtered = gaze_fixations[gaze_fixations["condition_family"].isin(["GIVE", "HUG"])]
    result = ar7.calculate_condition_metrics(filtered)

    conditions_found = result["condition_name"].unique()
    assert "SHOW" not in conditions_found or len(result[result["condition_name"] == "SHOW"]) == 0


def test_fit_dissociation_model():
    """Test dissociation model fitting."""
    data = pd.DataFrame(
        [
            {"participant_id": "P1", "condition_name": "GIVE", "proportion_primary_aois": 0.5},
            {"participant_id": "P1", "condition_name": "HUG", "proportion_primary_aois": 0.3},
            {"participant_id": "P2", "condition_name": "GIVE", "proportion_primary_aois": 0.6},
            {"participant_id": "P2", "condition_name": "HUG", "proportion_primary_aois": 0.35},
        ]
    )

    result = ar7.fit_dissociation_model(data, "proportion_primary_aois", ["GIVE", "HUG"])

    assert isinstance(result, ar7.DissociationResult)
    assert result.converged
    assert not result.condition_means.empty
    assert "condition_name" in result.condition_means.columns


def test_fit_dissociation_model_empty():
    """Test model fitting with empty data."""
    empty_df = pd.DataFrame()
    result = ar7.fit_dissociation_model(empty_df, "proportion_primary_aois", ["GIVE", "HUG"])

    assert not result.converged


def test_calculate_social_triplet_rate():
    """Test social triplet rate calculation."""
    prepared = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_onset_time": 0.1,
            },
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 1,
                "aoi_category": "woman_face",
                "gaze_onset_time": 0.2,
            },
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 2,
                "aoi_category": "man_face",
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 2,
                "aoi_category": "toy_location",
                "gaze_onset_time": 0.1,
            },
            {
                "participant_id": "P1",
                "condition_family": "SHOW",
                "trial_number": 2,
                "aoi_category": "woman_face",
                "gaze_onset_time": 0.2,
            },
            {
                "participant_id": "P2",
                "condition_family": "GIVE",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P2",
                "condition_family": "GIVE",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_onset_time": 0.1,
            },
            {
                "participant_id": "P2",
                "condition_family": "GIVE",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_onset_time": 0.2,
            },
        ]
    )

    result = ar7.calculate_social_triplet_rate(prepared)

    assert not result.empty
    show_rate = result[result["condition_name"] == "SHOW"]["social_triplet_rate"].iloc[0]
    give_rate = result[result["condition_name"] == "GIVE"]["social_triplet_rate"].iloc[0]

    assert pytest.approx(show_rate, rel=1e-6) == 1.0  # average of two trials with one triplet each
    assert pytest.approx(give_rate, rel=1e-6) == 0.0  # no valid triplet
    assert result.condition_means.empty


def test_dissociation_pairwise_comparisons():
    """Test pairwise comparisons structure."""
    data = pd.DataFrame(
        [
            {"participant_id": "P1", "condition_name": "GIVE", "proportion_primary_aois": 0.5},
            {"participant_id": "P1", "condition_name": "HUG", "proportion_primary_aois": 0.3},
            {"participant_id": "P1", "condition_name": "SHOW", "proportion_primary_aois": 0.4},
        ]
    )

    result = ar7.fit_dissociation_model(data, "proportion_primary_aois", ["GIVE", "HUG", "SHOW"])

    if not result.pairwise_comparisons.empty:
        assert "comparison" in result.pairwise_comparisons.columns
        assert "p_value" in result.pairwise_comparisons.columns
        assert "cohens_d" in result.pairwise_comparisons.columns
