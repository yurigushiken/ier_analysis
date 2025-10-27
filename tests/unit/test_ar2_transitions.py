from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _build_transition_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "from_aoi": ["toy_present", "toy_present", "woman_face", "woman_face"],
            "to_aoi": ["woman_face", "man_face", "toy_present", "toy_present"],
            "count": [10, 5, 8, 4],
            "condition": ["GIVE_WITH", "GIVE_WITH", "HUG_WITH", "HUG_WITH"],
        }
    )


def test_transition_probabilities_sum_to_one():
    df = _build_transition_dataframe()
    pivot = df.pivot_table(index="from_aoi", columns="to_aoi", values="count", aggfunc="sum", fill_value=0)
    probabilities = pivot.div(pivot.sum(axis=1), axis=0)
    sums = probabilities.sum(axis=1)
    assert np.allclose(sums.values, np.ones_like(sums.values))


@pytest.mark.skip(reason="MTC tests require AR-2 implementation")
def test_multiple_comparison_correction_placeholder():
    assert True
