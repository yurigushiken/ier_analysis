from __future__ import annotations

import pandas as pd
import pytest

from src.preprocessing.gaze_detector import detect_gaze_fixations


def _build_dataframe() -> pd.DataFrame:
    data = {
        "Participant": ["P1"] * 5,
        "participant_type": ["infant"] * 5,
        "participant_age_months": [8] * 5,
        "trial_number": [1] * 5,
        "event_verified": ["gw"] * 5,
        "segment": ["approach"] * 5,
        "What": ["man", "man", "man", "toy", "toy"],
        "Where": ["face", "face", "face", "other", "other"],
        "frame_count_trial_number": [1, 2, 3, 4, 5],
        "Onset": [0.0, 0.033, 0.066, 0.099, 0.132],
        "Offset": [0.033, 0.066, 0.099, 0.132, 0.165],
    }
    return pd.DataFrame(data)


def test_detect_gaze_fixations_identifies_sequences():
    df = _build_dataframe()
    events = detect_gaze_fixations(df)

    assert len(events) == 1
    event = events.iloc[0]
    assert event["aoi_category"] == "man_face"
    assert event["gaze_duration_frames"] == 3
    assert pytest.approx(event["gaze_duration_ms"], rel=1e-4) == 99.0


def test_detect_gaze_fixations_handles_short_sequences():
    df = _build_dataframe()
    df.loc[:, "What"] = ["man", "man", "toy", "toy", "toy"]
    df.loc[:, "Where"] = ["face", "face", "other", "other", "other"]

    events = detect_gaze_fixations(df)

    assert len(events) == 1
    event = events.iloc[0]
    assert event["aoi_category"] == "toy_present"
    assert event["gaze_duration_frames"] == 3


def test_detect_gaze_fixations_empty_dataframe():
    events = detect_gaze_fixations(pd.DataFrame())
    assert events.empty
