"""Unit tests for AR-5 Developmental Trajectory Analysis."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analysis import ar5_development as ar5


def _sample_gaze_fixations_with_age() -> pd.DataFrame:
    """Create sample gaze fixations with age variation."""
    return pd.DataFrame(
        [
            # Younger infant (8 months)
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_duration_ms": 400.0,
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_duration_ms": 300.0,
                "gaze_onset_time": 0.4,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 300.0,
                "gaze_onset_time": 0.7,
            },
            # Older infant (12 months)
            {
                "participant_id": "P2",
                "age_months": 12,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_duration_ms": 600.0,
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P2",
                "age_months": 12,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "woman_face",
                "gaze_duration_ms": 350.0,
                "gaze_onset_time": 0.6,
            },
            {
                "participant_id": "P2",
                "age_months": 12,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 50.0,
                "gaze_onset_time": 0.95,
            },
            # Same participants, HUG condition
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "HUG_WITH",
                "trial_number": 2,
                "aoi_category": "toy_present",
                "gaze_duration_ms": 200.0,
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "HUG_WITH",
                "trial_number": 2,
                "aoi_category": "man_body",
                "gaze_duration_ms": 600.0,
                "gaze_onset_time": 0.2,
            },
            {
                "participant_id": "P2",
                "age_months": 12,
                "condition_name": "HUG_WITH",
                "trial_number": 2,
                "aoi_category": "toy_present",
                "gaze_duration_ms": 250.0,
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P2",
                "age_months": 12,
                "condition_name": "HUG_WITH",
                "trial_number": 2,
                "aoi_category": "woman_body",
                "gaze_duration_ms": 550.0,
                "gaze_onset_time": 0.25,
            },
        ]
    )


def test_calculate_proportion_primary_aois():
    """Test calculation of proportion looking at primary AOIs."""
    gaze_fixations = _sample_gaze_fixations_with_age()

    result = ar5.calculate_proportion_primary_aois(gaze_fixations)

    # Verify result structure
    assert not result.empty
    assert set(result.columns) >= {
        "participant_id",
        "age_months",
        "condition_name",
        "proportion_primary_aois",
    }

    # Verify P1 GIVE_WITH: toy + man_face = 700ms / 1000ms = 0.7
    p1_give = result[(result["participant_id"] == "P1") & (result["condition_name"] == "GIVE_WITH")]
    assert len(p1_give) == 1
    assert pytest.approx(p1_give.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.7

    # Verify P2 GIVE_WITH: toy + woman_face = 950ms / 1000ms = 0.95
    p2_give = result[(result["participant_id"] == "P2") & (result["condition_name"] == "GIVE_WITH")]
    assert len(p2_give) == 1
    assert pytest.approx(p2_give.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.95

    # Verify P1 HUG_WITH: toy = 200ms / 800ms = 0.25
    p1_hug = result[(result["participant_id"] == "P1") & (result["condition_name"] == "HUG_WITH")]
    assert len(p1_hug) == 1
    assert pytest.approx(p1_hug.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.25

    # Verify ages are preserved
    assert p1_give.iloc[0]["age_months"] == 8
    assert p2_give.iloc[0]["age_months"] == 12


def test_calculate_proportion_primary_aois_empty_data():
    """Test proportion calculation with empty data."""
    empty_df = pd.DataFrame()
    result = ar5.calculate_proportion_primary_aois(empty_df)

    assert result.empty
    assert "proportion_primary_aois" in result.columns


def test_calculate_social_triplet_rate():
    """Test calculation of social gaze triplet rate."""
    gaze_fixations = pd.DataFrame(
        [
            # Valid triplet: man_face -> toy_present -> woman_face
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_onset_time": 0.0,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_onset_time": 0.2,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "woman_face",
                "gaze_onset_time": 0.4,
            },
            # Second valid triplet in same trial
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "woman_face",
                "gaze_onset_time": 0.6,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "toy_present",
                "gaze_onset_time": 0.8,
            },
            {
                "participant_id": "P1",
                "age_months": 8,
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "aoi_category": "man_face",
                "gaze_onset_time": 1.0,
            },
        ]
    )

    result = ar5.calculate_social_triplet_rate(gaze_fixations)

    assert not result.empty
    assert set(result.columns) >= {
        "participant_id",
        "age_months",
        "condition_name",
        "social_triplet_rate",
    }

    # Should find 2 triplets (mean rate = 2.0)
    assert len(result) == 1
    assert result.iloc[0]["social_triplet_rate"] == 2.0


def test_fit_developmental_model():
    """Test developmental model fitting."""
    data = pd.DataFrame(
        [
            {"participant_id": "P1", "age_months": 8, "condition_name": "GIVE", "proportion_primary_aois": 0.5},
            {"participant_id": "P2", "age_months": 9, "condition_name": "GIVE", "proportion_primary_aois": 0.55},
            {"participant_id": "P3", "age_months": 10, "condition_name": "GIVE", "proportion_primary_aois": 0.6},
            {"participant_id": "P1", "age_months": 8, "condition_name": "HUG", "proportion_primary_aois": 0.3},
            {"participant_id": "P2", "age_months": 9, "condition_name": "HUG", "proportion_primary_aois": 0.32},
            {"participant_id": "P3", "age_months": 10, "condition_name": "HUG", "proportion_primary_aois": 0.34},
        ]
    )

    result = ar5.fit_developmental_model(data, "proportion_primary_aois", test_nonlinear=True)

    # Verify result structure
    assert isinstance(result, ar5.DevelopmentalModelResult)
    assert result.converged
    assert not result.coefficients.empty
    assert "Intercept" in result.coefficients["term"].values
    assert "age_months" in result.coefficients["term"].values
    assert "condition" in result.coefficients["term"].values
    assert "age_months:condition" in result.coefficients["term"].values

    # Verify ANOVA table
    assert result.anova_table is not None
    assert not result.anova_table.empty

    # Verify model fit statistics
    assert result.r_squared >= 0.0
    assert result.r_squared <= 1.0


def test_fit_developmental_model_empty_data():
    """Test model fitting with empty data."""
    empty_df = pd.DataFrame()
    result = ar5.fit_developmental_model(empty_df, "proportion_primary_aois")

    assert not result.converged
    assert result.coefficients.empty
    assert len(result.warnings) > 0


def test_summarize_by_age_group():
    """Test age group summarization."""
    data = pd.DataFrame(
        [
            {"age_months": 8, "condition_name": "GIVE", "proportion_primary_aois": 0.5},
            {"age_months": 8, "condition_name": "GIVE", "proportion_primary_aois": 0.6},
            {"age_months": 12, "condition_name": "GIVE", "proportion_primary_aois": 0.7},
            {"age_months": 12, "condition_name": "GIVE", "proportion_primary_aois": 0.8},
            {"age_months": 8, "condition_name": "HUG", "proportion_primary_aois": 0.3},
            {"age_months": 12, "condition_name": "HUG", "proportion_primary_aois": 0.4},
        ]
    )

    result = ar5.summarize_by_age_group(data, "proportion_primary_aois")

    assert not result.empty
    assert set(result.columns) >= {"age_months", "condition_name", "mean", "sem", "n"}

    # Verify 8-month GIVE mean = (0.5 + 0.6) / 2 = 0.55
    age8_give = result[(result["age_months"] == 8) & (result["condition_name"] == "GIVE")]
    assert len(age8_give) == 1
    assert pytest.approx(age8_give.iloc[0]["mean"], rel=1e-6) == 0.55
    assert age8_give.iloc[0]["n"] == 2

    # Verify 12-month GIVE mean = (0.7 + 0.8) / 2 = 0.75
    age12_give = result[(result["age_months"] == 12) & (result["condition_name"] == "GIVE")]
    assert len(age12_give) == 1
    assert pytest.approx(age12_give.iloc[0]["mean"], rel=1e-6) == 0.75
    assert age12_give.iloc[0]["n"] == 2


def test_summarize_by_age_group_empty():
    """Test summarization with empty data."""
    empty_df = pd.DataFrame()
    result = ar5.summarize_by_age_group(empty_df, "proportion_primary_aois")

    assert result.empty
    assert "mean" in result.columns
