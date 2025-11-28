import pandas as pd
import pytest
from pathlib import Path

from project_extension.analyses.gaze_transition_analysis import transitions
from project_extension.analyses.gaze_transition_analysis import matrix


@pytest.fixture
def sample_fixations() -> pd.DataFrame:
    fixture_path = Path("tests/project_extension/fixtures/gaze_transition_sample.csv")
    return pd.read_csv(fixture_path)


def test_compute_transitions_counts(sample_fixations):
    nodes = ["man_face", "woman_face", "man_body", "woman_body", "toy_present"]
    result = transitions.compute_transitions(sample_fixations, aoi_nodes=nodes)
    p1_trial = result[(result["participant_id"] == "p1") & (result["trial_number"] == 1)]
    assert set(p1_trial[["from_aoi", "to_aoi"]].apply(tuple, axis=1)) == {
        ("man_face", "woman_face"),
        ("woman_face", "man_face"),
        ("man_face", "toy_present"),
    }
    counts = {
        (row.from_aoi, row.to_aoi): row.count for row in p1_trial.itertuples()
    }
    assert counts[("man_face", "woman_face")] == 1
    assert counts[("woman_face", "man_face")] == 1
    assert counts[("man_face", "toy_present")] == 1


def test_cohort_transition_matrix(sample_fixations):
    nodes = ["man_face", "woman_face", "man_body", "woman_body", "toy_present"]
    transitions_df = transitions.compute_transitions(sample_fixations, aoi_nodes=nodes)
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "10-month-olds", "min_months": 10, "max_months": 10},
    ]
    matrix_df = matrix.build_transition_matrix(
        transitions_df, cohorts=cohorts, aoi_nodes=nodes
    )
    seven = matrix_df[(matrix_df["cohort"] == "7-month-olds") & (matrix_df["from_aoi"] == "man_face") & (matrix_df["to_aoi"] == "woman_face")]
    assert seven["mean_count"].iloc[0] == pytest.approx(1.0)
    ten = matrix_df[(matrix_df["cohort"] == "10-month-olds") & (matrix_df["from_aoi"] == "woman_face") & (matrix_df["to_aoi"] == "man_body")]
    assert ten["mean_count"].iloc[0] == pytest.approx(1.0)


def test_transition_matrix_uses_participant_trial_denominator():
    transitions_df = pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "participant_age_months": 7,
                "condition": "gw",
                "from_aoi": "man_face",
                "to_aoi": "toy_present",
                "count": 2,
            },
            {
                "participant_id": "p2",
                "trial_number": 1,
                "participant_age_months": 7,
                "condition": "gw",
                "from_aoi": "man_face",
                "to_aoi": "toy_present",
                "count": 2,
            },
        ]
    )
    nodes = ["man_face", "toy_present"]
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
    ]

    matrix_df = matrix.build_transition_matrix(
        transitions_df, cohorts=cohorts, aoi_nodes=nodes
    )
    mean_value = matrix_df[
        (matrix_df["cohort"] == "7-month-olds")
        & (matrix_df["from_aoi"] == "man_face")
        & (matrix_df["to_aoi"] == "toy_present")
    ]["mean_count"].iloc[0]

    # Total transitions = 4, total participant-trial combos = 2 -> mean should be 2.
    assert mean_value == pytest.approx(2.0)