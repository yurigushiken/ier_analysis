"""Unit tests for AR-6 Trial-Order Effects Analysis."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analysis import ar6_learning as ar6


def _sample_trial_data() -> pd.DataFrame:
    """Create sample trial-level data."""
    return pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "trial_number": 1,
                "trial_number_global": 1,
                "condition_name": "GIVE",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 500,
                "is_primary": True,
            },
            {
                "participant_id": "P1",
                "trial_number": 1,
                "trial_number_global": 1,
                "condition_name": "GIVE",
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 500,
                "is_primary": False,
            },
            {
                "participant_id": "P1",
                "trial_number": 2,
                "trial_number_global": 2,
                "condition_name": "GIVE",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 400,
                "is_primary": True,
            },
            {
                "participant_id": "P1",
                "trial_number": 2,
                "trial_number_global": 2,
                "condition_name": "GIVE",
                "aoi_category": "screen_nonAOI",
                "gaze_duration_ms": 600,
                "is_primary": False,
            },
        ]
    )


def test_calculate_trial_level_metric():
    """Test trial-level metric calculation."""
    gaze_fixations = _sample_trial_data()
    result = ar6.calculate_trial_level_metric(gaze_fixations, "proportion_primary_aois")

    assert not result.empty
    assert "proportion_primary_aois" in result.columns
    assert len(result) == 2  # Two trials

    # Trial 1: 500 / 1000 = 0.5
    trial1 = result[result["trial_number"] == 1]
    assert pytest.approx(trial1.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.5

    # Trial 2: 400 / 1000 = 0.4
    trial2 = result[result["trial_number"] == 2]
    assert pytest.approx(trial2.iloc[0]["proportion_primary_aois"], rel=1e-6) == 0.4


def test_add_trial_order_within_event():
    """Test adding trial order within event type."""
    data = pd.DataFrame(
        [
            {"participant_id": "P1", "trial_number": 1, "condition_name": "GIVE", "value": 0.5},
            {"participant_id": "P1", "trial_number": 2, "condition_name": "GIVE", "value": 0.4},
            {"participant_id": "P1", "trial_number": 3, "condition_name": "HUG", "value": 0.3},
            {"participant_id": "P1", "trial_number": 4, "condition_name": "GIVE", "value": 0.35},
        ]
    )

    result = ar6.add_trial_order_within_event(data)

    assert "trial_order_within_event" in result.columns

    # GIVE presentations should be 1, 2, 3
    give_trials = result[result["condition_name"] == "GIVE"]
    assert list(give_trials["trial_order_within_event"]) == [1, 2, 3]

    # HUG presentation should be 1
    hug_trials = result[result["condition_name"] == "HUG"]
    assert list(hug_trials["trial_order_within_event"]) == [1]


def test_fit_trial_order_model():
    """Test trial-order model fitting."""
    data = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "trial_order_within_event": 1,
                "condition_name": "GIVE",
                "proportion_primary_aois": 0.5,
            },
            {
                "participant_id": "P1",
                "trial_order_within_event": 2,
                "condition_name": "GIVE",
                "proportion_primary_aois": 0.45,
            },
            {
                "participant_id": "P1",
                "trial_order_within_event": 3,
                "condition_name": "GIVE",
                "proportion_primary_aois": 0.42,
            },
            {
                "participant_id": "P2",
                "trial_order_within_event": 1,
                "condition_name": "GIVE",
                "proportion_primary_aois": 0.6,
            },
            {
                "participant_id": "P2",
                "trial_order_within_event": 2,
                "condition_name": "GIVE",
                "proportion_primary_aois": 0.58,
            },
        ]
    )

    result = ar6.fit_trial_order_model(data, "proportion_primary_aois", "trial_order_within_event")

    assert isinstance(result, ar6.TrialOrderModelResult)
    assert result.converged
    assert not result.fixed_effects.empty
    assert "trial_order_within_event" in result.fixed_effects["term"].values


def test_summarize_by_trial():
    """Test trial summary calculation."""
    data = pd.DataFrame(
        [
            {"trial_order_within_event": 1, "condition_name": "GIVE", "proportion_primary_aois": 0.5},
            {"trial_order_within_event": 1, "condition_name": "GIVE", "proportion_primary_aois": 0.6},
            {"trial_order_within_event": 2, "condition_name": "GIVE", "proportion_primary_aois": 0.45},
            {"trial_order_within_event": 2, "condition_name": "GIVE", "proportion_primary_aois": 0.55},
        ]
    )

    result = ar6.summarize_by_trial(data, "proportion_primary_aois", "trial_order_within_event")

    assert not result.empty
    assert set(result.columns) >= {"trial_order_within_event", "condition_name", "mean", "sem", "n"}

    # Trial 1 mean should be 0.55
    trial1 = result[result["trial_order_within_event"] == 1]
    assert pytest.approx(trial1.iloc[0]["mean"], rel=1e-6) == 0.55
