import pandas as pd
import pytest

from project_extension.analyses.gaze_transition_analysis import strategy


@pytest.fixture
def sample_transitions_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 7,
                "from_aoi": "man_face",
                "to_aoi": "woman_face",
                "count": 2,
            },
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 7,
                "from_aoi": "woman_face",
                "to_aoi": "toy_present",
                "count": 1,
            },
            {
                "participant_id": "p1",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 7,
                "from_aoi": "man_body",
                "to_aoi": "toy_present",
                "count": 1,
            },
            {
                "participant_id": "p2",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 10,
                "from_aoi": "man_face",
                "to_aoi": "woman_face",
                "count": 1,
            },
            {
                "participant_id": "p2",
                "trial_number": 1,
                "condition": "gw",
                "participant_age_months": 10,
                "from_aoi": "woman_face",
                "to_aoi": "toy_present",
                "count": 1,
            },
        ]
    )


def test_compute_strategy_proportions(sample_transitions_df):
    proportions = strategy.compute_strategy_proportions(sample_transitions_df)
    p1 = proportions[(proportions["participant_id"] == "p1") & (proportions["trial_number"] == 1)].iloc[0]
    assert pytest.approx(p1["social_verification_pct"]) == 2 / 4
    assert pytest.approx(p1["object_face_linking_pct"]) == 1 / 4
    assert pytest.approx(p1["mechanical_tracking_pct"]) == 1 / 4


def test_strategy_summary_and_gee(sample_transitions_df):
    cohorts = [
        {"label": "7-month-olds", "min_months": 7, "max_months": 7},
        {"label": "10-month-olds", "min_months": 10, "max_months": 10},
    ]
    proportions = strategy.compute_strategy_proportions(sample_transitions_df)
    summary = strategy.build_strategy_summary(proportions, cohorts=cohorts)
    seven = summary[summary["cohort"] == "7-month-olds"].iloc[0]
    assert pytest.approx(seven["social_verification_mean"]) == 0.5

    descriptive = strategy.build_strategy_descriptive_stats(proportions, cohorts=cohorts)
    assert set(descriptive["strategy"]) == {
        "Social Verification",
        "Object-Face Linking",
        "Mechanical Tracking",
    }

    results, report_text = strategy.run_strategy_gee(
        proportions,
        cohorts=cohorts,
        value_column="social_verification_pct",
        metric_label="Social Verification",
    )
    assert "cohort" in results.columns
    assert "GEE results for Social Verification" in report_text
    annotations = strategy.build_significance_annotations(results, reference="7-month-olds", cohort_order=[c["label"] for c in cohorts])
    assert isinstance(annotations, list)
    trend, trend_report = strategy.run_linear_trend_test(
        proportions,
        infant_cohorts=cohorts,
        value_column="social_verification_pct",
        metric_label="Social Verification",
    )
    assert isinstance(trend, dict)
    assert isinstance(trend_report, str) and trend_report

