import pandas as pd
import pytest

from project_extension.analyses.tri_argument_fixation import stats as tri_stats


@pytest.fixture
def sample_trial_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant_id": ["p1", "p1", "p2", "p2", "p3", "p3", "p4", "p4"],
            "tri_argument_success": [1, 0, 1, 1, 0, 1, 0, 0],
            "cohort": ["infant", "infant", "infant", "infant", "adult", "adult", "adult", "adult"],
        }
    )


def test_run_gee_analysis_returns_stats(tmp_path, sample_trial_results):
    config = {
        "cohorts": [
            {"label": "infant", "min_months": 7, "max_months": 12},
            {"label": "adult", "min_months": 216, "max_months": 600},
        ],
        "gee": {"enabled": True, "reference_cohort": "infant"},
    }
    stats_summary = tri_stats.run_gee_analysis(sample_trial_results, tmp_path, config, filename_prefix="sample")
    assert stats_summary is not None
    assert list(stats_summary["cohort"]) == ["infant", "adult"]
    assert (tmp_path / "sample_gee_results.txt").exists()


def test_format_significance_labels():
    assert tri_stats.format_significance(0.0005) == "***"
    assert tri_stats.format_significance(0.005) == "**"
    assert tri_stats.format_significance(0.02) == "*"
    assert tri_stats.format_significance(0.2) is None


def test_run_success_linear_trend_requires_outputs(sample_trial_results):
    infant_cohorts = [
        {"label": "infant", "min_months": 7, "max_months": 11},
    ]
    stats, report = tri_stats.run_success_linear_trend(sample_trial_results, infant_cohorts=infant_cohorts)
    assert stats  # expect non-empty stats dict
    assert "coef" in stats
    assert "pvalue" in stats
    assert "linear trend" in report.lower()