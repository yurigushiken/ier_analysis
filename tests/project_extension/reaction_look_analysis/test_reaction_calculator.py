import pandas as pd
import pytest

from project_extension.analyses.time_window_look_analysis import calculator


def _make_fixations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "trial_number": 1,
                "condition": "sw",
                "participant_age_months": 7,
                "gaze_start_frame": 65,
                "gaze_end_frame": 75,
                "aoi_category": "man_face",
            },
            {
                "participant_id": "P2",
                "trial_number": 1,
                "condition": "sw",
                "participant_age_months": 10,
                "gaze_start_frame": 80,
                "gaze_end_frame": 85,
                "aoi_category": "man_face",
            },
            {
                "participant_id": "P3",
                "trial_number": 1,
                "condition": "sw",
                "participant_age_months": 9,
                "gaze_start_frame": 40,
                "gaze_end_frame": 60,
                "aoi_category": "man_face",
            },
            {
                "participant_id": "P3",
                "trial_number": 1,
                "condition": "sw",
                "participant_age_months": 9,
                "gaze_start_frame": 72,
                "gaze_end_frame": 74,
                "aoi_category": "woman_face",
            },
        ]
    )


def test_compute_reaction_flags_overlap_logic():
    df = _make_fixations()
    results = calculator.compute_reaction_flags(
        df,
        target_aoi="man_face",
        window_start=70,
        window_end=90,
        condition_codes=["sw"],
    )
    looked = dict(zip(results["participant_id"], results["looked_at_target"]))
    assert looked["P1"] == 1
    assert looked["P2"] == 1
    assert looked["P3"] == 0


def test_summarize_by_cohort_means():
    df = pd.DataFrame(
        [
            {"participant_age_months": 7, "looked_at_target": 1, "trial_number": 1},
            {"participant_age_months": 10, "looked_at_target": 0, "trial_number": 1},
        ]
    )
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "10-month-olds", "min_months": 10, "max_months": 10},
    ]
    summary = calculator.summarize_by_cohort(df, cohorts=cohorts)
    assert summary.loc[summary["cohort"] == "7-month-olds", "mean_looked"].iloc[0] == 1
    assert summary.loc[summary["cohort"] == "10-month-olds", "mean_looked"].iloc[0] == 0

