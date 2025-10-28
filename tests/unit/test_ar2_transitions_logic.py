from __future__ import annotations

import pandas as pd
import pytest

from src.analysis import ar2_transitions


def _build_fixations(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "participant_id",
            "trial_number",
            "condition_name",
            "gaze_onset_time",
            "gaze_duration_ms",
            "aoi_category",
            "age_months",
            "age_group",
        ],
    )


def test_collapse_repeated_aois_removes_duplicates():
    df = _build_fixations(
        [
            ("p1", 1, "A", 0.0, 150, "man_face", 8, "8-month-olds"),
            ("p1", 1, "A", 0.1, 150, "man_face", 8, "8-month-olds"),
            ("p1", 1, "A", 0.2, 150, "toy_present", 8, "8-month-olds"),
        ]
    )

    collapsed = ar2_transitions._collapse_repeated_aois(df)
    assert list(collapsed["aoi_category"]) == ["man_face", "toy_present"]


def test_compute_transitions_skips_identical_successive_fixations():
    df = _build_fixations(
        [
            ("p1", 1, "A", 0.0, 150, "man_face", 8, "8-month-olds"),
            ("p1", 1, "A", 0.1, 150, "man_face", 8, "8-month-olds"),
            ("p1", 1, "A", 0.2, 150, "toy_present", 8, "8-month-olds"),
            ("p1", 1, "A", 0.3, 150, "woman_face", 8, "8-month-olds"),
        ]
    )

    collapsed = ar2_transitions._collapse_repeated_aois(df)
    transitions = ar2_transitions._compute_transitions(collapsed)

    assert list(transitions[["from_aoi", "to_aoi"]].itertuples(index=False, name=None)) == [
        ("man_face", "toy_present"),
        ("toy_present", "woman_face"),
    ]


def test_aggregate_probabilities_returns_mean_and_sem(tmp_path):
    df = pd.DataFrame(
        [
            ("p1", "A", "man_face", "toy_present", 4),
            ("p1", "A", "man_face", "woman_face", 1),
            ("p2", "A", "man_face", "toy_present", 2),
            ("p2", "A", "man_face", "woman_face", 2),
        ],
        columns=["participant_id", "condition_name", "from_aoi", "to_aoi", "count"],
    )

    participant_probs, summary = ar2_transitions._aggregate_probabilities(df)

    assert not participant_probs.empty
    row = summary[(summary["condition_name"] == "A") & (summary["from_aoi"] == "man_face") & (summary["to_aoi"] == "toy_present")]
    assert pytest.approx(row["mean_probability"].iloc[0], rel=1e-3) == 0.6
