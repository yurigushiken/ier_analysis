import pandas as pd
import pytest

from project_extension.src import gaze_detector
from project_extension.src.aoi_mapper import AOI_MAPPING


@pytest.fixture
def simple_frame_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Participant": "Infant-001",
                "Frame Number": 1,
                "What": "man",
                "Where": "face",
                "Onset": 0.0,
                "Offset": 0.033,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 10,
                "event_verified": "gw",
                "segment": "approach",
                "frame_count_trial_number": 1,
            },
            {
                "Participant": "Infant-001",
                "Frame Number": 2,
                "What": "man",
                "Where": "face",
                "Onset": 0.033,
                "Offset": 0.066,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 10,
                "event_verified": "gw",
                "segment": "approach",
                "frame_count_trial_number": 2,
            },
            {
                "Participant": "Infant-001",
                "Frame Number": 3,
                "What": "man",
                "Where": "face",
                "Onset": 0.066,
                "Offset": 0.099,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 10,
                "event_verified": "gw",
                "segment": "approach",
                "frame_count_trial_number": 3,
            },
            {
                "Participant": "Infant-001",
                "Frame Number": 4,
                "What": "toy",
                "Where": "other",
                "Onset": 0.099,
                "Offset": 0.132,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 10,
                "event_verified": "gw",
                "segment": "interaction",
                "frame_count_trial_number": 4,
            },
        ]
    )


@pytest.fixture
def boundary_frame_df() -> pd.DataFrame:
    data = []
    # First event segment with high frame_count values
    for idx, frame_count in enumerate([138, 139, 140], start=0):
        data.append(
            {
                "Participant": "Eight-0101-1579",
                "Frame Number": 500 + idx,
                "What": "screen",
                "Where": "other",
                "Onset": 13.7 + idx * 0.0333,
                "Offset": 13.7333 + idx * 0.0333,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 8,
                "event_verified": "gwo",
                "segment": "departure",
                "frame_count_trial_number": frame_count,
            }
        )
    # Next event resets frame_count back to 1 but keeps same trial/event code
    for idx, frame_count in enumerate([1, 2, 3], start=0):
        data.append(
            {
                "Participant": "Eight-0101-1579",
                "Frame Number": 503 + idx,
                "What": "screen",
                "Where": "other",
                "Onset": 14.0 + idx * 0.0333,
                "Offset": 14.0333 + idx * 0.0333,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 8,
                "event_verified": "gwo",
                "segment": "approach",
                "frame_count_trial_number": frame_count,
            }
        )
    return pd.DataFrame(data)


def test_detect_fixations_enforces_min_frames(simple_frame_df: pd.DataFrame) -> None:
    result_three = gaze_detector.detect_fixations(simple_frame_df, min_frames=3)
    assert len(result_three) == 1
    assert set(result_three["aoi_category"].unique()) == {AOI_MAPPING[("man", "face")]}

    result_four = gaze_detector.detect_fixations(simple_frame_df, min_frames=4)
    assert result_four.empty


def test_detect_fixations_resets_when_frame_counter_drops(boundary_frame_df: pd.DataFrame) -> None:
    result = gaze_detector.detect_fixations(boundary_frame_df, min_frames=3)
    assert len(result) == 2
    assert list(result["gaze_start_frame"]) == [138, 1]
    assert list(result["gaze_end_frame"]) == [140, 3]
    assert all(result["gaze_duration_frames"] == 3)

