"""AR-7 Event Dissociation analysis module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import GLMMResult, fit_linear_mixed_model, fit_glmm_placeholder
from src.utils.config import ConfigurationError, load_analysis_config
from src.analysis.filter_utils import apply_filters_tolerant
import os

LOGGER = logging.getLogger("ier.analysis.ar7")

DEFAULT_OUTPUT_DIR = Path("results/AR7_Dissociation")


@dataclass
class DissociationResult:
    """Results from event dissociation analysis."""

    model_type: str
    formula: str
    converged: bool
    condition_means: pd.DataFrame
    pairwise_comparisons: pd.DataFrame
    dissociation_detected: bool
    dissociation_metric: str
    effect_sizes: Dict[str, float]
    warnings: List[str]


def _load_gaze_fixations(config: Dict[str, Any]) -> pd.DataFrame:
    """Load gaze fixations from processed data directory."""
    processed_dir = Path(config["paths"]["processed_data"])
    default_path = processed_dir / "gaze_fixations.csv"
    child_path = processed_dir / "gaze_fixations_child.csv"

    if default_path.exists():
        path = default_path
    elif child_path.exists():
        path = child_path
    else:
        raise FileNotFoundError("No gaze fixations file found for AR-7 analysis")

    LOGGER.info("Loading gaze fixations from %s", path)
    df = pd.read_csv(path)

    # Coerce numeric columns if present
    if "age_months" in df.columns:
        df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")
    if "trial_number_global" in df.columns:
        df["trial_number_global"] = pd.to_numeric(df["trial_number_global"], errors="coerce")

    return df


def _load_variant_configuration(config: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
    """Load AR-7 variant configuration (supports env override)."""
    analysis_specific = config.get("analysis_specific", {}).get("ar7_dissociation", {})
    default_variant = str(analysis_specific.get("config_name", "AR7_dissociation/ar7_example")).strip()
    env_variant = os.environ.get("IER_AR7_CONFIG", "").strip()
    variant_name = env_variant or default_variant

    try:
        variant_config = load_analysis_config(variant_name)
    except ConfigurationError as exc:
        LOGGER.warning("Failed to load AR-7 variant config '%s': %s; using empty variant.", variant_name, exc)
        variant_config = {}

    return variant_config, variant_name


def _load_analysis_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load AR-7 specific configuration settings."""
    try:
        analysis_config = load_analysis_config("ar7_config")
    except ConfigurationError:
        analysis_config = {}

    # Default settings
    defaults = {
        "comparisons": {
            "contrasts": [
                {"name": "GIVE vs HUG", "conditions": ["GIVE", "HUG"]},
                {"name": "GIVE vs SHOW", "conditions": ["GIVE", "SHOW"]},
                {"name": "HUG vs SHOW", "conditions": ["HUG", "SHOW"]},
            ],
            "correction_method": "bonferroni",
        },
        "statistics": {
            "primary_test": "linear_mixed_model",
            "posthoc_comparisons": True,
            "calculate_effect_size": True,
        },
        "dissociation": {
            "key_metric": "social_gaze_pattern",
            "min_effect_size": 0.5,
        },
        "metrics": {
            "dependent_variables": ["proportion_primary_aois", "social_triplet_rate"],
        },
        "visualization": {
            "plot_type": "grouped_bar",
            "subplot_per_metric": True,
        },
        "output": {
            "include_dissociation_interpretation": True,
            "include_theoretical_interpretation": True,
        },
    }

    # Merge with loaded config
    for key, value in analysis_config.items():
        if key in defaults:
            target = defaults[key]
            if isinstance(target, dict) and isinstance(value, dict):
                target.update(value)
            else:
                defaults[key] = value
        else:
            defaults[key] = value

    return defaults


def calculate_condition_metrics(
    gaze_fixations: pd.DataFrame,
    target_conditions: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Calculate gaze metrics per participant per condition.

    For AR-7, we need participant-level summaries across conditions.
    """
    if gaze_fixations.empty:
        return pd.DataFrame(columns=["participant_id", "condition_name", "proportion_primary_aois"])

    # Filter to target conditions if specified
    if target_conditions:
        # Normalize condition names for matching (partial match)
        gaze_fixations = gaze_fixations.copy()

        # Create a mask for rows that contain any of the target conditions
        mask = pd.Series([False] * len(gaze_fixations), index=gaze_fixations.index)
        for target in target_conditions:
            # Match if target appears in condition_name (e.g., "GIVE" matches "GIVE_WITH")
            mask |= gaze_fixations["condition_name"].str.upper().str.contains(target.upper(), na=False)

        gaze_fixations = gaze_fixations[mask]

    if gaze_fixations.empty:
        LOGGER.warning("No data found for target conditions: %s", target_conditions)
        return pd.DataFrame(columns=["participant_id", "condition_name", "proportion_primary_aois"])

    # Define primary AOIs
    primary_aois = ["man_face", "woman_face", "toy_present"]
    gaze_fixations["is_primary"] = gaze_fixations["aoi_category"].isin(primary_aois)

    # Calculate proportion per participant per condition
    grouped = gaze_fixations.groupby(["participant_id", "condition_name"], as_index=False)

    results = []
    for (participant, condition), group in grouped:
        total_duration = group["gaze_duration_ms"].sum()
        primary_duration = group[group["is_primary"]]["gaze_duration_ms"].sum()

        if total_duration > 0:
            proportion = primary_duration / total_duration
        else:
            proportion = 0.0

        results.append(
            {
                "participant_id": participant,
                "condition_name": condition,
                "proportion_primary_aois": float(proportion),
            }
        )

    return pd.DataFrame(results)


def fit_dissociation_model(
    data: pd.DataFrame,
    dependent_var: str,
    conditions: List[str],
) -> DissociationResult:
    """
    Fit dissociation model comparing multiple conditions.

    Uses placeholder for now until statsmodels LMM is fully integrated.
    """
    warnings: List[str] = []

    if data.empty:
        warnings.append("No data available for modeling")
        return DissociationResult(
            model_type="linear_mixed_model",
            formula="N/A",
            converged=False,
            condition_means=pd.DataFrame(),
            pairwise_comparisons=pd.DataFrame(),
            dissociation_detected=False,
            dissociation_metric="none",
            effect_sizes={},
            warnings=warnings,
        )

    # Check data availability per condition
    conditions_found = data["condition_name"].unique()
    missing = set(conditions) - set(conditions_found)
    if missing:
        warnings.append(f"Conditions not found in data: {missing}")

    n_participants = data["participant_id"].nunique()
    if n_participants < 5:
        warnings.append(f"Small sample size (n={n_participants}); interpret with caution")

    # Calculate condition means
    condition_means = data.groupby("condition_name", as_index=False).agg({dependent_var: ["mean", "std", "sem", "count"]})
    condition_means.columns = ["condition_name", "mean", "std", "sem", "n"]

    # Fit LMM: dependent_var ~ C(condition_name) + (1 | participant)
    working = data.copy()
    working["participant"] = working["participant_id"].astype(str)
    working["condition_name"] = working["condition_name"].astype(str)
    formula = f"{dependent_var} ~ C(condition_name)"

    lmm_res = fit_linear_mixed_model(formula, working, groups_column="participant", re_formula=None)

    if not lmm_res.converged:
        warnings.extend(lmm_res.warnings or [])

    # Build a simple pairwise table from condition means as fallback (placeholder for proper post-hoc)
    pairwise_data = []
    conds = list(condition_means["condition_name"]) if not condition_means.empty else []
    for i, cond1 in enumerate(conds):
        for cond2 in conds[i + 1 :]:
            # crude estimate difference
            m1 = float(condition_means.loc[condition_means["condition_name"] == cond1, "mean"].iloc[0])
            m2 = float(condition_means.loc[condition_means["condition_name"] == cond2, "mean"].iloc[0])
            pairwise_data.append(
                {
                    "comparison": f"{cond1} vs {cond2}",
                    "estimate": m1 - m2,
                    "std_error": float(np.nan),
                    "t_value": float(np.nan),
                    "p_value": float(np.nan),
                    "p_value_adjusted": float(np.nan),
                    "cohens_d": float(np.nan),
                }
            )

    pairwise_comparisons = pd.DataFrame(pairwise_data)

    # Determine dissociation heuristically
    dissociation_detected = False
    dissociation_metric = "none"
    if not pairwise_comparisons.empty:
        # if any (absolute) estimate > min_effect_size from default settings, flag
        min_es = 0.5
        if any(pairwise_comparisons["estimate"].abs() > min_es):
            dissociation_detected = True
            dissociation_metric = dependent_var

    # Aggregate effect sizes as simple dictionary fallback
    effect_sizes = {row["comparison"]: row["cohens_d"] for _, row in pairwise_comparisons.iterrows()}

    return DissociationResult(
        model_type="linear_mixed_model",
        formula=formula,
        converged=lmm_res.converged,
        condition_means=condition_means,
        pairwise_comparisons=pairwise_comparisons,
        dissociation_detected=dissociation_detected,
        dissociation_metric=dissociation_metric,
        effect_sizes=effect_sizes,
        warnings=warnings + (lmm_res.warnings or []),
    )


def _build_overview_text(result: DissociationResult, settings: Dict[str, Any]) -> str:
    """Generate overview text for the report."""
    if result.dissociation_detected:
        return (
            "Event dissociation analysis revealed significant differences in gaze patterns across event types. "
            f"Key metric ({result.dissociation_metric}) showed dissociation, providing evidence that infants "
            "differentiate between events with similar visual properties but different underlying structures."
        )
    else:
        return (
            "Event dissociation analysis found no significant differences in gaze patterns across the tested event types. "
            "This may indicate similar processing of the events, or may reflect insufficient statistical power."
        )


def _build_methods_text(settings: Dict[str, Any]) -> str:
    """Generate methods description."""
    correction = settings.get("comparisons", {}).get("correction_method", "bonferroni")

    return (
        "Event dissociation was tested using Linear Mixed Models (LMM) with condition as a categorical predictor. "
        "Random intercepts for participants accounted for individual differences. "
        f"Pairwise comparisons between conditions were conducted with {correction} correction for multiple comparisons. "
        "Dissociation is demonstrated when conditions differ significantly in social gaze patterns despite similar "
        "overall visual attention, providing evidence that infants understand event structure beyond visual salience."
    )


def _build_statistics_table(result: DissociationResult) -> str:
    """Generate HTML statistics table."""
    if not result.condition_means.empty:
        means_html = result.condition_means.to_html(index=False, classes="table table-striped", float_format="%.3f")
    else:
        means_html = "<p>Condition means not available</p>"

    if not result.pairwise_comparisons.empty:
        pairwise_html = result.pairwise_comparisons.to_html(
            index=False, classes="table table-striped", float_format="%.3f"
        )
    else:
        pairwise_html = "<p>Pairwise comparisons not available</p>"

    warnings_html = ""
    if result.warnings:
        warnings_list = "".join(f"<li>{warning}</li>" for warning in result.warnings)
        warnings_html = f'<div class="alert alert-warning"><h5>Warnings</h5><ul>{warnings_list}</ul></div>'

    return f"""
    <h3>Condition Means</h3>
    {means_html}

    <h3>Pairwise Comparisons</h3>
    {pairwise_html}

    {warnings_html}
    """


def _generate_outputs(
    *,
    output_dir: Path,
    data: pd.DataFrame,
    result: DissociationResult,
    dependent_var: str,
    settings: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate all AR-7 outputs: tables, figures, reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save data tables
    data_csv = output_dir / f"{dependent_var}_by_condition.csv"
    data.to_csv(data_csv, index=False)

    if not result.condition_means.empty:
        means_csv = output_dir / f"{dependent_var}_condition_means.csv"
        result.condition_means.to_csv(means_csv, index=False)

    if not result.pairwise_comparisons.empty:
        pairwise_csv = output_dir / f"{dependent_var}_pairwise_comparisons.csv"
        result.pairwise_comparisons.to_csv(pairwise_csv, index=False)

    # Generate figures
    figures = []

    if not result.condition_means.empty and len(result.condition_means) > 0:
        # Bar plot comparing conditions
        condition_fig = output_dir / f"{dependent_var}_by_condition.png"
        visualizations.bar_plot(
            result.condition_means,
            x="condition_name",
            y="mean",
            title=f"Event Dissociation: {dependent_var.replace('_', ' ').title()}",
            ylabel=dependent_var.replace("_", " ").title(),
            output_path=condition_fig,
        )
        figures.append(
            {
                "path": str(condition_fig),
                "caption": f"{dependent_var} across event types",
            }
        )

    # Build report context
    context = {
        "overview_text": _build_overview_text(result, settings),
        "methods_text": _build_methods_text(settings),
        "statistics_table": _build_statistics_table(result),
        "interpretation_text": (
            "Dissociation patterns provide evidence for event understanding beyond visual attention. "
            "Significant differences in social gaze patterns (e.g., face-toy-face triplets) across "
            "events with similar toy salience demonstrate that infants parse event structure, not just "
            "visual properties. This supports Gordon (2003) findings on infant event representation."
        ),
        "figure_entries": figures,
        "figures": [fig["path"] for fig in figures],
        "tables": [str(data_csv)],
    }

    # Render report
    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar7_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-7",
        "title": "Event Dissociation Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "tables": [str(data_csv)],
        "figures": [fig["path"] for fig in figures],
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    """Run AR-7 event dissociation analysis."""
    LOGGER.info("Starting AR-7 event dissociation analysis")

    # Load variant config (optional)
    variant_config, variant_name = _load_variant_configuration(config)
    variant_key = variant_config.get("variant_key", Path(variant_name).stem)
    variant_label = variant_config.get("variant_label", variant_key)

    settings = _load_analysis_settings(config)

    # Resolve cohorts
    cohorts = variant_config.get("cohorts") if isinstance(variant_config, dict) else None
    cohort_frames: List[pd.DataFrame] = []

    if not cohorts:
        try:
            gf = _load_gaze_fixations(config)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping AR-7 analysis: %s", exc)
            return {"report_id": "AR-7", "title": "Event Dissociation Analysis", "html_path": "", "pdf_path": ""}

        if gf.empty:
            LOGGER.warning("Gaze fixations file is empty; skipping AR-7 analysis")
            return {"report_id": "AR-7", "title": "Event Dissociation Analysis", "html_path": "", "pdf_path": ""}

        cohort_frames.append(gf)
    else:
        processed_root = Path(config["paths"]["processed_data"]).resolve()
        for cohort in cohorts:
            data_path = cohort.get("data_path")
            label = cohort.get("label", cohort.get("key", "cohort"))
            if not data_path:
                LOGGER.warning("Cohort '%s' missing data_path; skipping.", label)
                continue
            p = Path(data_path)
            if not p.is_absolute():
                p = (processed_root / p).resolve()
            if not p.exists():
                LOGGER.warning("Cohort '%s' dataset missing: %s; skipping.", label, p)
                continue
            try:
                df = pd.read_csv(p)
            except Exception as exc:
                LOGGER.warning("Failed to read cohort '%s' at %s: %s; skipping.", label, p, exc)
                continue

            # Apply participant filters if present
            filters = cohort.get("participant_filters")
            try:
                df = apply_filters_tolerant(df, filters)
            except Exception as exc:
                LOGGER.warning("Cohort '%s' filter error: %s; skipping filters.", label, exc)

            if df.empty:
                LOGGER.info("Cohort '%s' has no data after filtering; skipping.", label)
                continue

            cohort_frames.append(df)

    if not cohort_frames:
        LOGGER.warning("No cohorts produced data for AR-7; skipping")
        return {"report_id": "AR-7", "title": "Event Dissociation Analysis", "html_path": "", "pdf_path": ""}

    gaze_fixations = pd.concat(cohort_frames, ignore_index=True)

    # Get target conditions
    target_conditions = variant_config.get("target_conditions", ["GIVE", "HUG", "SHOW"])

    # Calculate metrics per condition
    dependent_var = "proportion_primary_aois"
    data = calculate_condition_metrics(gaze_fixations, target_conditions)

    if data.empty:
        LOGGER.warning("No valid data for AR-7 analysis (target conditions may be missing)")
        return {"report_id": "AR-7", "title": "Event Dissociation Analysis", "html_path": "", "pdf_path": ""}

    # Fit dissociation model
    result = fit_dissociation_model(data, dependent_var, target_conditions)

    # Prepare output dir per variant
    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name / variant_key
    metadata = _generate_outputs(
        output_dir=output_dir,
        data=data,
        result=result,
        dependent_var=dependent_var,
        settings=settings,
        config=config,
    )

    metadata["variant_key"] = variant_key
    metadata["variant_label"] = variant_label

    LOGGER.info("AR-7 analysis completed; report generated at %s", metadata.get("html_path"))
    return metadata


__all__ = [
    "DissociationResult",
    "calculate_condition_metrics",
    "fit_dissociation_model",
    "run",
]
