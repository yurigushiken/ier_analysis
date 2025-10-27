from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.reporting.statistics import SummaryStats, cohens_d, proportion, summarize, t_test


def test_summarize_basic_statistics():
    stats_result = summarize([1, 2, 3, 4])
    assert isinstance(stats_result, SummaryStats)
    assert pytest.approx(stats_result.mean, rel=1e-6) == 2.5
    assert stats_result.count == 4


def test_summarize_raises_on_empty():
    with pytest.raises(ValueError):
        summarize([])


def test_cohens_d_symmetry():
    d = cohens_d([1, 2, 3], [4, 5, 6])
    assert d < 0
    d_reverse = cohens_d([4, 5, 6], [1, 2, 3])
    assert pytest.approx(d_reverse, rel=1e-6) == -d


def test_t_test_returns_statistic():
    result = t_test([1, 2, 3], [3, 4, 5])
    assert hasattr(result, "statistic")
    assert hasattr(result, "pvalue")


def test_proportion_with_condition():
    df = pd.DataFrame({"value": [1, 0, 1, 1]})
    prop = proportion(df, "value")
    assert pytest.approx(prop, rel=1e-6) == 0.75

    condition = df["value"] == 1
    prop_conditioned = proportion(df, "value", condition=condition)
    assert pytest.approx(prop_conditioned, rel=1e-6) == 1.0


def test_summarize_single_value():
    """Test summarize with single value."""
    stats_result = summarize([5.0])
    assert stats_result.mean == 5.0
    assert stats_result.std == 0.0
    assert stats_result.sem == 0.0
    assert stats_result.count == 1


def test_cohens_d_zero_effect():
    """Test Cohen's d when samples are identical."""
    d = cohens_d([1, 2, 3], [1, 2, 3])
    assert pytest.approx(d, abs=1e-10) == 0.0


def test_cohens_d_raises_on_insufficient_data():
    """Test that Cohen's d raises error with insufficient data."""
    with pytest.raises(ValueError):
        cohens_d([1], [2, 3])
    
    with pytest.raises(ValueError):
        cohens_d([1, 2], [3])


def test_proportion_empty_dataframe():
    """Test proportion with empty dataframe."""
    df = pd.DataFrame({"value": []})
    prop = proportion(df, "value")
    assert prop == 0.0


def test_t_test_significant_difference():
    """Test t-test detects significant difference."""
    # Two clearly different samples
    sample1 = [1, 2, 3, 2, 1]
    sample2 = [10, 11, 12, 11, 10]
    result = t_test(sample1, sample2)
    assert result.pvalue < 0.001  # Highly significant


def test_t_test_no_difference():
    """Test t-test with no difference."""
    sample1 = [5, 5, 5, 5]
    sample2 = [5, 5, 5, 5]
    result = t_test(sample1, sample2)
    # p-value should be very close to 1 (or NaN if variance is 0)
    assert np.isnan(result.pvalue) or result.pvalue > 0.99
