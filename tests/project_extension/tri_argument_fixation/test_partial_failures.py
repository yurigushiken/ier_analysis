import pandas as pd
import pytest

from project_extension.analyses.tri_argument_fixation import pipeline


def _sample_fixations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            # Trial p1-t1 sees man + toy only -> Recipient_Object
            {
                "participant_id": "p1",
                "participant_type": "infant",
                "participant_age_months": 8,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "man_face",
                "gaze_start_frame": 10,
                "gaze_end_frame": 20,
            },
            {
                "participant_id": "p1",
                "participant_type": "infant",
                "participant_age_months": 8,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "toy_present",
                "gaze_start_frame": 30,
                "gaze_end_frame": 40,
            },
            # Trial p2-t1 sees woman only -> Woman_Only
            {
                "participant_id": "p2",
                "participant_type": "infant",
                "participant_age_months": 8,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "woman_face",
                "gaze_start_frame": 15,
                "gaze_end_frame": 25,
            },
            # Trial p3-t1 sees nothing -> Other
            {
                "participant_id": "p3",
                "participant_type": "adult",
                "participant_age_months": 300,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "screen_nonAOI",
                "gaze_start_frame": 5,
                "gaze_end_frame": 50,
            },
            # Successful trial should be ignored
            {
                "participant_id": "p4",
                "participant_type": "adult",
                "participant_age_months": 300,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "woman_face",
                "gaze_start_frame": 5,
                "gaze_end_frame": 10,
            },
            {
                "participant_id": "p4",
                "participant_type": "adult",
                "participant_age_months": 300,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "man_face",
                "gaze_start_frame": 12,
                "gaze_end_frame": 18,
            },
            {
                "participant_id": "p4",
                "participant_type": "adult",
                "participant_age_months": 300,
                "trial_number": 1,
                "condition": "gw",
                "aoi_category": "toy_present",
                "gaze_start_frame": 20,
                "gaze_end_frame": 25,
            },
        ]
    )


def _trial_results() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "participant_type": "infant",
                "participant_age_months": 8,
                "tri_argument_success": 0,
                "cohort": "infant",
            },
            {
                "participant_id": "p2",
                "trial_number": 1,
                "condition": "gw",
                "participant_type": "infant",
                "participant_age_months": 8,
                "tri_argument_success": 0,
                "cohort": "infant",
            },
            {
                "participant_id": "p3",
                "trial_number": 1,
                "condition": "gw",
                "participant_type": "adult",
                "participant_age_months": 300,
                "tri_argument_success": 0,
                "cohort": "adult",
            },
            {
                "participant_id": "p4",
                "trial_number": 1,
                "condition": "gw",
                "participant_type": "adult",
                "participant_age_months": 300,
                "tri_argument_success": 1,
                "cohort": "adult",
            },
        ]
    )


AOI_GROUPS = {
    "man": ["man_face"],
    "woman": ["woman_face"],
    "toy": ["toy_present"],
}

COHORTS = [
    {"label": "infant", "min_months": 7, "max_months": 12},
    {"label": "adult", "min_months": 216, "max_months": 600},
]


def test_classify_event_structure_assigns_categories():
    events = pipeline.classify_event_structure(
        _sample_fixations(),
        _trial_results(),
        aoi_groups=AOI_GROUPS,
        condition_codes=["gw"],
        frame_window={"start": 0, "end": 200},
    )
    categories = (
        events.sort_values(["participant_id"]).reset_index(drop=True)["event_category"].tolist()
    )
    assert categories == ["Man_Toy", "Woman_Only", "Other", "Full_Trifecta"]


def test_event_structure_summary_counts_percentages():
    events = pipeline.classify_event_structure(
        _sample_fixations(),
        _trial_results(),
        aoi_groups=AOI_GROUPS,
        condition_codes=["gw"],
        frame_window={"start": 0, "end": 200},
    )
    summary = pipeline.summarize_event_structure(events, COHORTS)
    infant_rows = summary[summary["cohort"] == "infant"]
    assert infant_rows["count"].sum() == 2
    recip_rate = infant_rows.loc[infant_rows["event_category"] == "Man_Toy", "percentage"].iloc[0]
    assert recip_rate == pytest.approx(50.0)
    adult_rows = summary[summary["cohort"] == "adult"]
    assert adult_rows["count"].sum() == 2
    trifecta_pct = adult_rows.loc[adult_rows["event_category"] == "Full_Trifecta", "percentage"].iloc[0]
    assert trifecta_pct == pytest.approx(50.0)

