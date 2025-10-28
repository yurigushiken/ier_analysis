from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar4_dwell_times as ar4


def _sample_gaze_fixations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 500,
                "trial_number": 1,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 400,
                "trial_number": 2,
            },
            {
                "participant_id": "P1",
                "condition_name": "HUG_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 200,
                "trial_number": 1,
            },
            {
                "participant_id": "P2",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 600,
                "trial_number": 1,
            },
            {
                "participant_id": "P2",
                "condition_name": "HUG_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 100,
                "trial_number": 1,
            },
            {
                "participant_id": "P2",
                "condition_name": "HUG_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 150,
                "trial_number": 2,
            },
        ]
    )


def test_calculate_participant_dwell_times_groups_by_condition():
    df = _sample_gaze_fixations()
    participant_means = ar4.calculate_participant_dwell_times(
        df,
        min_dwell_time_ms=0,
        include_aoi=True,
    )

    assert set(participant_means.columns) >= {
        "participant_id",
        "condition_name",
        "mean_dwell_time_ms",
        "gaze_fixation_count",
    }

    lookup = {
        (row.participant_id, row.condition_name): row.mean_dwell_time_ms for row in participant_means.itertuples()
    }

    assert pytest.approx(lookup[("P1", "GIVE_WITH")], rel=1e-6) == 450.0
    assert pytest.approx(lookup[("P1", "HUG_WITH")], rel=1e-6) == 200.0
    assert pytest.approx(lookup[("P2", "GIVE_WITH")], rel=1e-6) == 600.0
    assert pytest.approx(lookup[("P2", "HUG_WITH")], rel=1e-6) == 125.0


def test_summarize_by_condition_averages_participant_means():
    participant_means = ar4.calculate_participant_dwell_times(_sample_gaze_fixations(), min_dwell_time_ms=0)
    summary = ar4.summarize_by_condition(participant_means)

    assert set(summary.columns) >= {"condition_name", "mean_dwell_time_ms", "n_participants"}

    summary_indexed = summary.set_index("condition_name")
    assert pytest.approx(summary_indexed.loc["GIVE_WITH", "mean_dwell_time_ms"], rel=1e-6) == 525.0
    assert pytest.approx(summary_indexed.loc["HUG_WITH", "mean_dwell_time_ms"], rel=1e-6) == 162.5
    assert int(summary_indexed.loc["GIVE_WITH", "n_participants"]) == 2
    assert int(summary_indexed.loc["HUG_WITH", "n_participants"]) == 2


def test_calculate_participant_dwell_times_filters_short_gazes():
    df = _sample_gaze_fixations()
    df_filtered = pd.concat(
        [
            df,
            pd.DataFrame(
                [
                    {
                        "participant_id": "P2",
                        "condition_name": "HUG_WITH",
                        "aoi_category": "man_face",
                        "gaze_duration_ms": 90,
                        "trial_number": 3,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    participant_means = ar4.calculate_participant_dwell_times(df_filtered, min_dwell_time_ms=100)
    lookup = {
        (row.participant_id, row.condition_name): row.mean_dwell_time_ms for row in participant_means.itertuples()
    }

    # The 90 ms gaze should be excluded, preserving the 125 ms mean from the baseline data.
    assert pytest.approx(lookup[("P2", "HUG_WITH")], rel=1e-6) == 125.0


def test_calculate_participant_dwell_times_includes_aoi_dimension():
    df = _sample_gaze_fixations()

    participant_means = ar4.calculate_participant_dwell_times(
        df,
        min_dwell_time_ms=0,
        include_aoi=True,
    )

    assert "aoi_category" in participant_means.columns
    assert set(participant_means["aoi_category"]) == {"man_face", "toy_present"}


def test_calculate_participant_dwell_times_excludes_screen_nonsignal():
    df = pd.concat(
        [
            _sample_gaze_fixations(),
            pd.DataFrame(
                [
                    {
                        "participant_id": "P3",
                        "condition_name": "GIVE_WITH",
                        "aoi_category": "screen_nonAOI",
                        "gaze_duration_ms": 1000,
                        "trial_number": 1,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    participant_means = ar4.calculate_participant_dwell_times(df, min_dwell_time_ms=0)

    if "aoi_category" in participant_means.columns:
        assert "screen_nonAOI" not in set(participant_means["aoi_category"])


def test_summarize_by_aoi_applies_min_event_threshold():
    participant_means = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 400.0,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "toy_present",
                "gaze_duration_ms": 420.0,
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "aoi_category": "man_face",
                "gaze_duration_ms": 300.0,
            },
        ]
    )

    result = ar4.summarize_by_aoi(
        participant_means,
        min_events=2,
        min_dwell_time_ms=0,
        max_dwell_time_ms=None,
    )

    categories = set(result["aoi_category"])
    assert "toy_present" in categories
    assert "man_face" not in categories


def test_load_gaze_fixations_prefers_child_file(tmp_path: Path):
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    child_path = processed_dir / "gaze_fixations_child.csv"
    child_df = _sample_gaze_fixations()
    child_df.to_csv(child_path, index=False)

    config = {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(tmp_path / "results"),
        }
    }

    cohort_cfg = {
        "key": "child",
        "label": "Child Cohort",
        "data_path": str(child_path),
    }

    loaded, metadata = ar4._load_gaze_fixations(config, cohort_cfg)  # type: ignore[attr-defined]

    assert not loaded.empty
    assert set(loaded.columns) >= {"participant_id", "aoi_category"}
    assert metadata["label"] == "Child Cohort"
