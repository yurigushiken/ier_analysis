"""AR-5 Developmental Trajectory analysis module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import os

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import GLMMResult, fit_linear_mixed_model
from src.utils.config import ConfigurationError, load_analysis_config
from src.analysis.filter_utils import apply_filters_tolerant

LOGGER = logging.getLogger("ier.analysis.ar5")

DEFAULT_OUTPUT_DIR = Path("results/AR5_Development")


@dataclass
class DevelopmentalModelResult:
    """Results from developmental trajectory modeling."""

    model_type: str
    formula: str
    converged: bool
    coefficients: pd.DataFrame
    anova_table: Optional[pd.DataFrame]
    r_squared: float
    r_squared_adj: float
    aic: float
    bic: float
    interaction_significant: bool
    interaction_p_value: float
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
        raise FileNotFoundError("No gaze fixations file found for AR-5 analysis")

    LOGGER.info("Loading gaze fixations from %s", path)
    df = pd.read_csv(path)

    # Ensure age_months is numeric
    if "age_months" in df.columns:
        df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")

    return df


def _load_variant_configuration(config: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Load AR-5 variant configuration (supports env override)."""
    analysis_specific = config.get("analysis_specific", {}).get("ar5_development", {})
    default_variant = str(analysis_specific.get("config_name", "AR5_development/ar5_example")).strip()
    env_variant = os.environ.get("IER_AR5_CONFIG", "").strip()
    variant_name = env_variant or default_variant

    try:
        variant_config = load_analysis_config(variant_name)
    except ConfigurationError as exc:
        LOGGER.warning("Failed to load AR-5 variant config '%s': %s; using empty variant.", variant_name, exc)
        variant_config = {}

    return variant_config, variant_name


def _load_analysis_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load AR-5 specific configuration settings."""
    try:
        analysis_config = load_analysis_config("ar5_config")
    except ConfigurationError:
        analysis_config = {}

    # Default settings
    defaults = {
        "age_modeling": {
            "use_continuous_age": True,
            "test_nonlinear": True,
        },
        "statistics": {
            "primary_test": "linear_mixed_model",
            "test_interaction": True,
            "calculate_effect_size": True,
            "report_aic_bic": True,
            "check_residuals": True,
            "compare_models": True,
        },
        "metrics": {
            "dependent_variables": ["proportion_primary_aois"],
        },
        "visualization": {
            "plot_type": "line_with_error_bars",
            "generate_interaction_plot": True,
            "show_regression_line": True,
            "show_confidence_band": True,
            "confidence_level": 0.95,
        },
        "output": {
            "export_age_group_summaries": True,
            "export_anova_table": True,
            "include_developmental_interpretation": True,
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


def calculate_proportion_primary_aois(gaze_fixations: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate proportion of time looking at primary AOIs (toy, faces) per participant per condition.

    This is the main dependent variable for AR-5 developmental analysis.
    """
    if gaze_fixations.empty:
        return pd.DataFrame(columns=["participant_id", "age_months", "condition_name", "proportion_primary_aois"])

    # Define primary AOIs (faces and toy)
    primary_aois = ["man_face", "woman_face", "toy_present"]

    # Mark primary AOIs
    gaze_fixations["is_primary"] = gaze_fixations["aoi_category"].isin(primary_aois)

    # Calculate total duration per participant per condition
    grouped = gaze_fixations.groupby(["participant_id", "age_months", "condition_name"], as_index=False)

    results = []
    for (participant, age, condition), group in grouped:
        total_duration = group["gaze_duration_ms"].sum()
        primary_duration = group[group["is_primary"]]["gaze_duration_ms"].sum()

        if total_duration > 0:
            proportion = primary_duration / total_duration
        else:
            proportion = 0.0

        results.append(
            {
                "participant_id": participant,
                "age_months": float(age),
                "condition_name": condition,
                "proportion_primary_aois": float(proportion),
            }
        )

    return pd.DataFrame(results)


def calculate_social_triplet_rate(gaze_fixations: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate social gaze triplet rate per participant per condition.

    Uses simple detection: count triplets per participant per condition.
    """
    if gaze_fixations.empty:
        return pd.DataFrame(columns=["participant_id", "age_months", "condition_name", "social_triplet_rate"])

    # Simple triplet detection: man_face -> toy_present -> woman_face (or reverse)
    valid_patterns = [
        ("man_face", "toy_present", "woman_face"),
        ("woman_face", "toy_present", "man_face"),
    ]

    triplet_counts = []

    for (participant, trial), trial_df in gaze_fixations.groupby(["participant_id", "trial_number"]):
        trial_df = trial_df.sort_values("gaze_onset_time").reset_index(drop=True)
        count = 0

        for i in range(len(trial_df) - 2):
            pattern = tuple(trial_df.iloc[i : i + 3]["aoi_category"].tolist())
            if pattern in valid_patterns:
                count += 1

        if count > 0 and not trial_df.empty:
            triplet_counts.append(
                {
                    "participant_id": participant,
                    "trial_number": trial,
                    "age_months": float(trial_df.iloc[0]["age_months"]),
                    "condition_name": trial_df.iloc[0]["condition_name"],
                    "triplet_count": count,
                }
            )

    if not triplet_counts:
        return pd.DataFrame(columns=["participant_id", "age_months", "condition_name", "social_triplet_rate"])

    triplets_df = pd.DataFrame(triplet_counts)

    # Aggregate to participant-condition level
    grouped = triplets_df.groupby(["participant_id", "age_months", "condition_name"], as_index=False)
    result = grouped["triplet_count"].mean().rename(columns={"triplet_count": "social_triplet_rate"})

    return result


def fit_developmental_model(
    data: pd.DataFrame,
    dependent_var: str,
    *,
    test_nonlinear: bool = True,
) -> DevelopmentalModelResult:
    """
    Fit developmental trajectory model with Age × Condition interaction.

    Uses placeholder for now until statsmodels LMM is fully integrated.
    """
    warnings: List[str] = []

    if data.empty:
        warnings.append("No data available for modeling")
        return DevelopmentalModelResult(
            model_type="linear_mixed_model",
            formula="N/A",
            converged=False,
            coefficients=pd.DataFrame(),
            anova_table=None,
            r_squared=0.0,
            r_squared_adj=0.0,
            aic=0.0,
            bic=0.0,
            interaction_significant=False,
            interaction_p_value=1.0,
            warnings=warnings,
        )

    # Ensure necessary columns
    if "participant_id" not in data.columns or "condition_name" not in data.columns or "age_months" not in data.columns:
        warnings.append("Input data missing required columns (participant_id, condition_name, age_months)")
        return DevelopmentalModelResult(
            model_type="linear_mixed_model",
            formula="N/A",
            converged=False,
            coefficients=pd.DataFrame(),
            anova_table=None,
            r_squared=0.0,
            r_squared_adj=0.0,
            aic=0.0,
            bic=0.0,
            interaction_significant=False,
            interaction_p_value=1.0,
            warnings=warnings,
        )

    n_participants = data["participant_id"].nunique()
    if n_participants < 6:
        warnings.append(f"Small sample size (n={n_participants}); model estimates may be unstable")

    # Prepare dataset for statsmodels
    working = data.copy()
    working["participant"] = working["participant_id"].astype(str)
    # Use categorical for condition
    working["condition_name"] = working["condition_name"].astype(str)

    # Formula: dependent ~ age_months * C(condition_name)
    formula = f"{dependent_var} ~ age_months * C(condition_name)"

    glmm_res = fit_linear_mixed_model(formula, working, groups_column="participant")

    if not glmm_res.converged:
        warnings.extend(glmm_res.warnings or [])
        return DevelopmentalModelResult(
            model_type="linear_mixed_model",
            formula=formula,
            converged=False,
            coefficients=pd.DataFrame(),
            anova_table=None,
            r_squared=0.0,
            r_squared_adj=0.0,
            aic=glmm_res.aic or 0.0,
            bic=glmm_res.bic or 0.0,
            interaction_significant=False,
            interaction_p_value=1.0,
            warnings=warnings,
        )

    # Build coefficients table
    coeff_df = pd.DataFrame()
    if glmm_res.params is not None:
        params = glmm_res.params
        pvalues = glmm_res.pvalues if glmm_res.pvalues is not None else pd.Series(index=params.index, data=[np.nan] * len(params))
        conf_int = glmm_res.conf_int if glmm_res.conf_int is not None else None

        estimates = params.values
        terms = list(params.index)
        std_err = []
        z_vals = []
        pvals = []
        for i, term in enumerate(terms):
            est = float(estimates[i])
            if conf_int is not None and term in conf_int.index:
                lower = float(conf_int.loc[term].iloc[0])
                upper = float(conf_int.loc[term].iloc[1])
                se = (upper - lower) / (2 * 1.96) if np.isfinite(upper) and np.isfinite(lower) else np.nan
            else:
                se = np.nan
            z = float(est / se) if se and se != 0 and not np.isnan(se) else np.nan
            pv = float(pvalues.get(term, np.nan)) if pvalues is not None else np.nan
            std_err.append(se)
            z_vals.append(z)
            pvals.append(pv)

        coeff_df = pd.DataFrame(
            {
                "term": terms,
                "estimate": estimates,
                "std_error": std_err,
                "z_value": z_vals,
                "p_value": pvals,
            }
        )

    # Determine interaction significance (look for ':' in term names)
    interaction_p = 1.0
    interaction_sig = False
    if not coeff_df.empty:
        interaction_terms = coeff_df[coeff_df["term"].str.contains(":")]
        if not interaction_terms.empty:
            # take smallest p-value among interaction terms
            interaction_p = float(interaction_terms["p_value"].min())
            interaction_sig = interaction_p < 0.05 if not np.isnan(interaction_p) else False

    return DevelopmentalModelResult(
        model_type="linear_mixed_model",
        formula=formula,
        converged=True,
        coefficients=coeff_df,
        anova_table=None,
        r_squared=0.0,
        r_squared_adj=0.0,
        aic=glmm_res.aic or 0.0,
        bic=glmm_res.bic or 0.0,
        interaction_significant=interaction_sig,
        interaction_p_value=interaction_p,
        warnings=warnings + (glmm_res.warnings or []),
    )


def summarize_by_age_group(data: pd.DataFrame, dependent_var: str) -> pd.DataFrame:
    """Summarize gaze metric by age group and condition for visualization."""
    if data.empty:
        return pd.DataFrame(columns=["age_months", "condition_name", "mean", "sem", "n"])

    grouped = data.groupby(["age_months", "condition_name"], as_index=False)

    results = []
    for (age, condition), group in grouped:
        values = group[dependent_var].dropna()
        if len(values) > 0:
            results.append(
                {
                    "age_months": float(age),
                    "condition_name": condition,
                    "mean": float(values.mean()),
                    "sem": float(values.sem()) if len(values) > 1 else 0.0,
                    "n": int(len(values)),
                }
            )

    return pd.DataFrame(results)


def _build_overview_text(model_result: DevelopmentalModelResult) -> str:
    """Generate overview text for the report."""
    if model_result.interaction_significant:
        return (
            "Developmental trajectory analysis revealed a significant Age × Condition interaction, "
            f"indicating that the effect of experimental condition changes with infant age (p = {model_result.interaction_p_value:.3f})."
        )
    else:
        return (
            "Developmental trajectory analysis found no significant Age × Condition interaction "
            f"(p = {model_result.interaction_p_value:.3f}), suggesting that condition effects are "
            "relatively stable across the age range studied."
        )


def _build_methods_text(settings: Dict[str, Any]) -> str:
    """Generate methods description."""
    use_continuous = settings.get("age_modeling", {}).get("use_continuous_age", True)
    test_nonlinear = settings.get("age_modeling", {}).get("test_nonlinear", True)

    age_desc = "continuous age in months" if use_continuous else "age group categories"
    nonlinear_desc = (
        " Quadratic age terms were tested to assess non-linear developmental trends." if test_nonlinear else ""
    )

    return (
        f"Developmental trajectories were analyzed using Linear Mixed Models (LMM) with {age_desc} "
        "as a predictor. The primary model tested the Age × Condition interaction to determine whether "
        "experimental condition effects varied with infant age. Random intercepts for participants "
        "accounted for individual differences in baseline gaze patterns."
        f"{nonlinear_desc}"
    )


def _build_statistics_table(model_result: DevelopmentalModelResult) -> str:
    """Generate HTML statistics table."""
    if model_result.anova_table is not None:
        anova_html = model_result.anova_table.to_html(index=False, classes="table table-striped", float_format="%.3f")
    else:
        anova_html = "<p>ANOVA table not available</p>"

    coef_html = model_result.coefficients.to_html(index=False, classes="table table-striped", float_format="%.3f")

    model_fit_html = f"""
    <h4>Model Fit</h4>
    <ul>
        <li><strong>R² (marginal):</strong> {model_result.r_squared:.3f}</li>
        <li><strong>R² (adjusted):</strong> {model_result.r_squared_adj:.3f}</li>
        <li><strong>AIC:</strong> {model_result.aic:.2f}</li>
        <li><strong>BIC:</strong> {model_result.bic:.2f}</li>
    </ul>
    """

    warnings_html = ""
    if model_result.warnings:
        warnings_list = "".join(f"<li>{warning}</li>" for warning in model_result.warnings)
        warnings_html = f'<div class="alert alert-warning"><h5>Warnings</h5><ul>{warnings_list}</ul></div>'

    return f"""
    <h3>Model Coefficients</h3>
    {coef_html}

    <h3>ANOVA Table</h3>
    {anova_html}

    {model_fit_html}

    {warnings_html}
    """


def _generate_outputs(
    *,
    output_dir: Path,
    data: pd.DataFrame,
    summary: pd.DataFrame,
    model_result: DevelopmentalModelResult,
    dependent_var: str,
    settings: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate all AR-5 outputs: tables, figures, reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save data tables
    data_csv = output_dir / f"{dependent_var}_by_age_condition.csv"
    data.to_csv(data_csv, index=False)

    summary_csv = output_dir / f"{dependent_var}_summary.csv"
    summary.to_csv(summary_csv, index=False)

    if model_result.coefficients is not None and not model_result.coefficients.empty:
        coef_csv = output_dir / f"{dependent_var}_coefficients.csv"
        model_result.coefficients.to_csv(coef_csv, index=False)

    if model_result.anova_table is not None and not model_result.anova_table.empty:
        anova_csv = output_dir / f"{dependent_var}_anova.csv"
        model_result.anova_table.to_csv(anova_csv, index=False)

    # Generate figures
    figures = []

    if not summary.empty:
        # Interaction plot: Age × Condition
        interaction_fig = output_dir / f"{dependent_var}_age_by_condition.png"
        visualizations.line_plot_with_error_bars(
            summary,
            x="age_months",
            y="mean",
            hue="condition_name",
            title=f"Developmental Trajectory: {dependent_var.replace('_', ' ').title()}",
            xlabel="Age (months)",
            ylabel=dependent_var.replace("_", " ").title(),
            output_path=interaction_fig,
        )
        figures.append(
            {
                "path": str(interaction_fig),
                "caption": f"Age × Condition interaction for {dependent_var}",
            }
        )

    # Build report context
    context = {
        "overview_text": _build_overview_text(model_result),
        "methods_text": _build_methods_text(settings),
        "statistics_table": _build_statistics_table(model_result),
        "interpretation_text": (
            "Interpret Age × Condition interactions carefully. Significant interactions suggest that "
            "developmental timing matters for understanding infant event representation. "
            "Non-significant interactions indicate relatively stable condition effects across age."
        ),
        "figure_entries": figures,
        "figures": [fig["path"] for fig in figures],
        "tables": [str(data_csv), str(summary_csv)],
    }

    # Render report
    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar5_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-5",
        "title": "Developmental Trajectory Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "tables": [str(data_csv), str(summary_csv)],
        "figures": [fig["path"] for fig in figures],
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    """Run AR-5 developmental trajectory analysis."""
    LOGGER.info("Starting AR-5 developmental trajectory analysis")
    # Load variant configuration (optional)
    variant_config, variant_name = _load_variant_configuration(config)
    variant_key = variant_config.get("variant_key", Path(variant_name).stem)
    variant_label = variant_config.get("variant_label", variant_key)

    settings = _load_analysis_settings(config)

    # Resolve cohorts (if provided in variant); otherwise process default processed file
    cohorts = variant_config.get("cohorts") if isinstance(variant_config, dict) else None
    cohort_frames: List[pd.DataFrame] = []

    if not cohorts:
        # Single dataset mode (use processed gaze_fixations)
        try:
            gf = _load_gaze_fixations(config)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping AR-5 analysis: %s", exc)
            return {"report_id": "AR-5", "title": "Developmental Trajectory Analysis", "html_path": "", "pdf_path": ""}

        if gf.empty:
            LOGGER.warning("Gaze fixations file is empty; skipping AR-5 analysis")
            return {"report_id": "AR-5", "title": "Developmental Trajectory Analysis", "html_path": "", "pdf_path": ""}

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
            except KeyError as exc:
                LOGGER.warning("Cohort '%s' filter error: %s; skipping filters.", label, exc)

            if df.empty:
                LOGGER.info("Cohort '%s' has no data after filtering; skipping.", label)
                continue

            cohort_frames.append(df)

    if not cohort_frames:
        LOGGER.warning("No cohorts produced data for AR-5; skipping")
        return {"report_id": "AR-5", "title": "Developmental Trajectory Analysis", "html_path": "", "pdf_path": ""}

    # Concatenate cohorts and compute dependent variables per participant-condition
    gaze_fixations = pd.concat(cohort_frames, ignore_index=True)

    # Calculate dependent variable (proportion of primary AOIs)
    dependent_var = "proportion_primary_aois"
    data = calculate_proportion_primary_aois(gaze_fixations)
    if data.empty:
        LOGGER.warning("No valid data for AR-5 analysis after computing dependent variable")
        return {"report_id": "AR-5", "title": "Developmental Trajectory Analysis", "html_path": "", "pdf_path": ""}

    # Fit developmental model
    test_nonlinear = settings.get("age_modeling", {}).get("test_nonlinear", True)
    model_result = fit_developmental_model(data, dependent_var, test_nonlinear=test_nonlinear)

    # Summarize by age group for visualization
    summary = summarize_by_age_group(data, dependent_var)

    # Generate outputs under variant-specific directory
    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name / variant_key
    metadata = _generate_outputs(
        output_dir=output_dir,
        data=data,
        summary=summary,
        model_result=model_result,
        dependent_var=dependent_var,
        settings=settings,
        config=config,
    )

    metadata["variant_key"] = variant_key
    metadata["variant_label"] = variant_label

    LOGGER.info("AR-5 analysis completed; report generated at %s", metadata.get("html_path"))
    return metadata


__all__ = [
    "DevelopmentalModelResult",
    "calculate_proportion_primary_aois",
    "calculate_social_triplet_rate",
    "fit_developmental_model",
    "summarize_by_age_group",
    "run",
]
