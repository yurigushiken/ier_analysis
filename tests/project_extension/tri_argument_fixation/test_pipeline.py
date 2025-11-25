import pandas as pd
import pytest

from project_extension.analyses.tri_argument_fixation import pipeline


@pytest.fixture
def sample_fixations() -> pd.DataFrame:
    """Synthetic fixation rows that mimic the CSV schema."""
    return pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "participant_type": "infant",
                "participant_age_months": 9,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "giver_face",
                "gaze_start_frame": 5,
                "gaze_end_frame": 10,
            },
            {
                "participant_id": "p1",
                "participant_type": "infant",
                "participant_age_months": 9,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "recipient_face",
                "gaze_start_frame": 12,
                "gaze_end_frame": 20,
            },
            {
                "participant_id": "p1",
                "participant_type": "infant",
                "participant_age_months": 9,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "toy_present",
                "gaze_start_frame": 30,
                "gaze_end_frame": 35,
            },
            {
                "participant_id": "p2",
                "participant_type": "adult",
                "participant_age_months": 360,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "giver_face",
                "gaze_start_frame": 5,
                "gaze_end_frame": 9,
            },
        ]
    )


def test_compute_trial_metrics_flags_success(sample_fixations):
    aoi_groups = {
        "giver": ["giver_face"],
        "recipient": ["recipient_face"],
        "object": ["toy_present"],
    }
    result = pipeline.compute_trial_metrics(
        sample_fixations,
        aoi_groups=aoi_groups,
        condition_codes=["gw"],
        frame_window={"start": 0, "end": 40},
    )
    assert "tri_argument_success" in result.columns
    p1_row = result[result["participant_id"] == "p1"].iloc[0]
    assert bool(p1_row["tri_argument_success"]) is True


def test_filter_by_min_trials_drops_participants():
    trial_df = pd.DataFrame(
        {
            "participant_id": ["p1", "p1", "p2"],
            "trial_number": [1, 2, 1],
            "tri_argument_success": [True, False, True],
        }
    )
    filtered = pipeline.filter_by_min_trials(trial_df, min_trials=2)
    assert set(filtered["participant_id"]) == {"p1"}


def test_summarize_by_cohort_preserves_order():
    trial_df = pd.DataFrame(
        {
            "participant_id": ["p1", "p2", "p3"],
            "cohort": ["infant", "adult", "infant"],
            "trial_number": [1, 2, 3],
            "tri_argument_success": [True, False, True],
        }
    )
    cohorts = [
        {"label": "infant", "min_months": 7, "max_months": 12},
        {"label": "adult", "min_months": 216, "max_months": 600},
    ]
    summary = pipeline.summarize_by_cohort(trial_df, cohorts)
    assert list(summary["cohort"]) == ["infant", "adult"]
    assert summary.loc[summary["cohort"] == "infant", "success_rate"].iloc[0] == pytest.approx(1.0)

