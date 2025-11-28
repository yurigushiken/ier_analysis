import pandas as pd

from project_extension.analyses.tri_argument_fixation import latency_analysis


def test_compute_latency_metrics_subtracts_window_start():
    fixations = pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "gaze_start_frame": 40,
                "gaze_end_frame": 50,
                "aoi_category": "man_face",
            },
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "gaze_start_frame": 60,
                "gaze_end_frame": 70,
                "aoi_category": "woman_face",
            },
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "gaze_start_frame": 70,
                "gaze_end_frame": 80,
                "aoi_category": "toy_present",
            },
        ]
    )
    trial_results = pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "tri_argument_success": 1,
                "cohort": "7-month-olds",
                "participant_age_months": 7,
            }
        ]
    )
    aoi_groups = {
        "man": ["man_face"],
        "woman": ["woman_face"],
        "toy": ["toy_present"],
    }
    frame_window = {"start": 50, "end": 150}

    latency_df = latency_analysis.compute_latency_metrics(
        fixations,
        trial_results,
        aoi_groups=aoi_groups,
        condition_codes=["gw"],
        frame_window=frame_window,
    )

    assert not latency_df.empty
    # Expected latency is gaze_start_frame (70) minus window start (50) = 20 frames.
    assert latency_df["latency_frames"].iloc[0] == 20

