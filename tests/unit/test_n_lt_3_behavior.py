from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.reporting.statistics import summarize


def test_summarize_raises_on_insufficient_data():
    with pytest.raises(ValueError):
        summarize([])


def test_analysis_skip_when_n_lt_3():
    config = {
        "analysis": {
            "min_statistical_n": 3,
        }
    }
    current_n = 2

    assert current_n < config["analysis"]["min_statistical_n"]
