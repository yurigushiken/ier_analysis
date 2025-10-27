from __future__ import annotations

import pandas as pd
import pytest

from src.reporting.statistics import summarize, t_test


def _build_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "participant_id": ["P1", "P2", "P3", "P4"],
            "condition": ["GIVE", "GIVE", "HUG", "HUG"],
            "toy_proportion": [0.6, 0.65, 0.4, 0.45],
            "age_months": [8, 8, 9, 9],
        }
    )


def test_summarize_toy_proportion():
    df = _build_sample_dataframe()
    stats = summarize(df[df["condition"] == "GIVE"]["toy_proportion"])
    assert pytest.approx(stats.mean, rel=1e-6) == 0.625


def test_t_test_between_conditions():
    df = _build_sample_dataframe()
    give = df[df["condition"] == "GIVE"]["toy_proportion"]
    hug = df[df["condition"] == "HUG"]["toy_proportion"]
    result = t_test(give, hug)
    assert result.pvalue < 0.1


@pytest.mark.skip(reason="Age covariate path not implemented")
def test_age_covariate_optional_path():
    assert True
