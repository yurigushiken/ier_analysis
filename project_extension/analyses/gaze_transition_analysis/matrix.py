"""Aggregation utilities for transition matrices."""

from __future__ import annotations

from typing import Dict, List, Sequence

import pandas as pd


def assign_cohort(age: float, cohorts: List[Dict]) -> str | None:
    for cohort in cohorts:
        if cohort["min_months"] <= age <= cohort["max_months"]:
            return cohort["label"]
    return None


def build_transition_matrix(
    transitions_df: pd.DataFrame,
    *,
    cohorts: List[Dict],
    aoi_nodes: Sequence[str],
) -> pd.DataFrame:
    """Aggregate transitions per cohort returning long-form matrix data."""
    if transitions_df.empty:
        return pd.DataFrame(
            columns=["cohort", "from_aoi", "to_aoi", "mean_count"]
        )
    df = transitions_df.copy()
    df["cohort"] = df["participant_age_months"].apply(lambda age: assign_cohort(age, cohorts))
    df = df.dropna(subset=["cohort"])
    if df.empty:
        raise ValueError("All transitions were dropped after cohort assignment.")
    grouped = (
        df.groupby(["cohort", "from_aoi", "to_aoi"])["count"]
        .mean()
        .reset_index()
        .rename(columns={"count": "mean_count"})
    )
    # Ensure every cohort/from/to combination exists (fill zeros)
    records = []
    for cohort in [c["label"] for c in cohorts]:
        for from_aoi in aoi_nodes:
            for to_aoi in aoi_nodes:
                if from_aoi == to_aoi:
                    continue
                match = grouped[
                    (grouped["cohort"] == cohort)
                    & (grouped["from_aoi"] == from_aoi)
                    & (grouped["to_aoi"] == to_aoi)
                ]
                if match.empty:
                    records.append(
                        {
                            "cohort": cohort,
                            "from_aoi": from_aoi,
                            "to_aoi": to_aoi,
                            "mean_count": 0.0,
                        }
                    )
                else:
                    records.append(match.iloc[0].to_dict())
    return pd.DataFrame(records)

