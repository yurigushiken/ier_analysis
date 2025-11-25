"""Strategy aggregation and statistics."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

FACE_AOIS = {"man_face", "woman_face"}
BODY_AOIS = {"man_body", "woman_body"}
TOY_AOIS = {"toy_present", "toy_location"}


def compute_strategy_proportions(transitions_df: pd.DataFrame) -> pd.DataFrame:
    """Return per-trial normalized strategy proportions."""
    if transitions_df.empty:
        return pd.DataFrame(
            columns=[
                "participant_id",
                "trial_number",
                "condition",
                "participant_age_months",
                "total_transitions",
                "social_verification_pct",
                "object_face_linking_pct",
                "mechanical_tracking_pct",
            ]
        )
    grouped = []
    for (participant_id, trial_number), trial_df in transitions_df.groupby(
        ["participant_id", "trial_number"], sort=False
    ):
        total = trial_df["count"].sum()
        if total == 0:
            continue
        counts = {
            "social_verification": 0.0,
            "object_face_linking": 0.0,
            "mechanical_tracking": 0.0,
        }
        for row in trial_df.itertuples():
            strategy_key = _categorize_transition(row.from_aoi, row.to_aoi)
            if strategy_key:
                counts[strategy_key] += row.count
        grouped.append(
            {
                "participant_id": participant_id,
                "trial_number": trial_number,
                "condition": trial_df["condition"].iloc[0],
                "participant_age_months": float(trial_df["participant_age_months"].iloc[0]),
                "total_transitions": total,
                "social_verification_pct": counts["social_verification"] / total,
                "object_face_linking_pct": counts["object_face_linking"] / total,
                "mechanical_tracking_pct": counts["mechanical_tracking"] / total,
            }
        )
    return pd.DataFrame(grouped)


def _categorize_transition(from_aoi: str, to_aoi: str) -> str | None:
    if {from_aoi, to_aoi} == {"man_face", "woman_face"}:
        return "social_verification"
    if (
        (from_aoi in FACE_AOIS and to_aoi in TOY_AOIS)
        or (to_aoi in FACE_AOIS and from_aoi in TOY_AOIS)
    ):
        return "object_face_linking"
    if (
        (from_aoi in BODY_AOIS and to_aoi in TOY_AOIS)
        or (to_aoi in BODY_AOIS and from_aoi in TOY_AOIS)
    ):
        return "mechanical_tracking"
    return None


def build_strategy_summary(
    proportions_df: pd.DataFrame,
    *,
    cohorts: List[Dict],
) -> pd.DataFrame:
    """Average strategy proportions per cohort."""
    if proportions_df.empty:
        return pd.DataFrame(
            columns=[
                "cohort",
                "social_verification_mean",
                "object_face_linking_mean",
                "mechanical_tracking_mean",
            ]
        )
    working = proportions_df.copy()
    working["cohort"] = working["participant_age_months"].apply(
        lambda age: _assign_cohort(age, cohorts)
    )
    working = working.dropna(subset=["cohort"])
    grouped = (
        working.groupby("cohort")
        .agg(
            social_verification_mean=("social_verification_pct", "mean"),
            object_face_linking_mean=("object_face_linking_pct", "mean"),
            mechanical_tracking_mean=("mechanical_tracking_pct", "mean"),
        )
        .reset_index()
    )
    return grouped


def _assign_cohort(age: float, cohorts: List[Dict]) -> str | None:
    for cohort in cohorts:
        if cohort["min_months"] <= age <= cohort["max_months"]:
            return cohort["label"]
    return None


def run_strategy_gee(
    proportions_df: pd.DataFrame,
    *,
    cohorts: List[Dict],
    reports_dir: Path,
    filename_prefix: str,
) -> pd.DataFrame:
    """Run GEE on social verification proportions."""
    if proportions_df.empty:
        raise ValueError("No strategy proportions available for GEE.")
    working = proportions_df.copy()
    working["cohort"] = working["participant_age_months"].apply(
        lambda age: _assign_cohort(age, cohorts)
    )
    working = working.dropna(subset=["cohort"])
    if working.empty:
        raise ValueError("Strategy GEE has no rows after cohort assignment.")
    reference = cohorts[0]["label"]
    working["cohort"] = pd.Categorical(
        working["cohort"],
        categories=[c["label"] for c in cohorts],
        ordered=True,
    )
    formula = f"social_verification_pct ~ C(cohort, Treatment(reference='{reference}'))"
    model = smf.gee(
        formula=formula,
        groups="participant_id",
        data=working,
        family=sm.families.Gaussian(),
    )
    try:
        result = model.fit()
        report_body = result.summary().as_text()
    except ValueError as exc:
        report_body = f"GEE failed to converge: {exc}"
        gee_path = reports_dir / f"{filename_prefix}_strategy_gee.txt"
        gee_path.write_text(report_body, encoding="utf-8")
        return pd.DataFrame([{"cohort": reference, "coef": 0.0, "pvalue": None}])

    report_lines = [
        "GEE results for social verification proportion",
        f"Reference cohort: {reference}",
        f"Participants: {working['participant_id'].nunique()}",
        f"Trials: {len(working)}",
        "",
        report_body,
    ]
    gee_path = reports_dir / f"{filename_prefix}_strategy_gee.txt"
    gee_path.write_text("\n".join(report_lines), encoding="utf-8")

    stats_rows = [{"cohort": reference, "coef": 0.0, "pvalue": None}]
    for cohort in working["cohort"].cat.categories[1:]:
        term = f"C(cohort, Treatment(reference='{reference}'))[T.{cohort}]"
        if term in result.params:
            stats_rows.append(
                {
                    "cohort": cohort,
                    "coef": result.params[term],
                    "pvalue": result.pvalues[term],
                }
            )
    return pd.DataFrame(stats_rows)


def run_linear_trend_test(
    proportions_df: pd.DataFrame,
    *,
    infant_cohorts: List[Dict],
    reports_dir: Path,
    filename_prefix: str,
) -> Dict[str, float]:
    """Run linear trend (age numeric) GEE on infant cohorts (7-11 months)."""
    working = proportions_df.copy()
    min_age = infant_cohorts[0]["min_months"]
    max_age = infant_cohorts[-1]["max_months"]
    working = working[
        (working["participant_age_months"] >= min_age)
        & (working["participant_age_months"] <= max_age)
    ].copy()
    if working.empty:
        return {}
    working["age_numeric"] = working["participant_age_months"]
    model = smf.gee(
        "social_verification_pct ~ age_numeric",
        groups="participant_id",
        data=working,
        family=sm.families.Gaussian(),
    )
    try:
        result = model.fit()
    except ValueError:
        return {}
    coef = float(result.params["age_numeric"])
    pvalue = float(result.pvalues["age_numeric"])
    lines = [
        "Linear Trend Test (Infants 7-11mo)",
        result.summary().as_text(),
    ]
    report_path = reports_dir / f"{filename_prefix}_linear_trend_results.txt"
    report_path.write_text("\n\n".join(lines), encoding="utf-8")
    return {"coef": coef, "pvalue": pvalue}
def build_significance_annotations(
    gee_results: pd.DataFrame,
    *,
    reference: str,
    cohort_order: Sequence[str],
) -> List[Dict[str, object]]:
    """Return significance annotations for plotting."""
    annotations = []
    if gee_results is None or gee_results.empty:
        return annotations
    order = {label: idx for idx, label in enumerate(cohort_order)}
    ref_idx = order.get(reference, 0)
    for row in gee_results.itertuples():
        if row.cohort == reference:
            continue
        to_idx = order.get(row.cohort)
        if to_idx is None or row.pvalue is None:
            continue
        label = _format_pvalue(row.pvalue)
        if not label:
            continue
        annotations.append(
            {
                "from_idx": ref_idx,
                "to_idx": to_idx,
                "label": label,
                "pvalue": row.pvalue,
            }
        )
    return annotations


def _format_pvalue(pvalue: float) -> str | None:
    if pvalue < 0.001:
        return "***"
    if pvalue < 0.01:
        return "**"
    if pvalue < 0.05:
        return "*"
    if pvalue < 0.1:
        return f"p={pvalue:.2f}"
    return None

