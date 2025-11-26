import pandas as pd
import pytest

from project_extension.analyses.latency_to_toy import calculator


def _sample_fixations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            # Case A: pre-look spanning frame 30 -> latency 0
            {
                "participant_id": "P1",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 7,
                "gaze_start_frame": 25,
                "gaze_end_frame": 35,
                "aoi_category": "toy_present",
            },
            # Case B: fixation starts inside window -> latency 5
            {
                "participant_id": "P2",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 10,
                "gaze_start_frame": 35,
                "gaze_end_frame": 45,
                "aoi_category": "toy_present",
            },
            # Case C: no fixation inside window -> excluded
            {
                "participant_id": "P3",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 9,
                "gaze_start_frame": 10,
                "gaze_end_frame": 20,
                "aoi_category": "toy_present",
            },
            # Non-toy AOI should be ignored
            {
                "participant_id": "P2",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 10,
                "gaze_start_frame": 31,
                "gaze_end_frame": 32,
                "aoi_category": "man_face",
            },
        ]
    )


def test_compute_latencies_handles_prelook_and_reaction_cases():
    df = _sample_fixations()
    latencies = calculator.compute_latencies(
        df,
        window_start=30,
        window_end=80,
        toy_aois=["toy_present"],
    )
    assert set(latencies["participant_id"]) == {"P1", "P2"}
    p1_latency = latencies[latencies["participant_id"] == "P1"]["latency_frames"].iloc[0]
    p2_latency = latencies[latencies["participant_id"] == "P2"]["latency_frames"].iloc[0]
    assert p1_latency == 0
    assert p2_latency == 5


def test_summarize_by_cohort_requires_implementation():
    latencies = pd.DataFrame(
        [
            {"participant_age_months": 7, "latency_frames": 0},
            {"participant_age_months": 10, "latency_frames": 5},
        ]
    )
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "10-month-olds", "min_months": 10, "max_months": 10},
    ]
    summary = calculator.summarize_by_cohort(latencies, cohorts=cohorts)
    assert list(summary["cohort"]) == ["7-month-olds", "10-month-olds"]
    assert summary.loc[summary["cohort"] == "7-month-olds", "mean_latency_frames"].iloc[0] == 0

