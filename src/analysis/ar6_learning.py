"""AR-6 Trial-Order Effects (Learning/Habituation) analysis module."""

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

LOGGER = logging.getLogger("ier.analysis.ar6")

DEFAULT_OUTPUT_DIR = Path("results/AR6_Trial_Order")


@dataclass
class TrialOrderModelResult:
    """Results from trial-order effects modeling."""

    model_type: str
    formula: str
    converged: bool
    fixed_effects: pd.DataFrame
    random_effects_variance: Dict[str, float]
    r_squared_marginal: float  # Fixed effects only
    r_squared_conditional: float  # Fixed + random effects
    aic: float
    bic: float
    slope_coefficient: float
    slope_p_value: float
    slope_significant: bool
    interaction_coefficient: float  # Trial × Condition interaction
    interaction_p_value: float
    interaction_significant: bool
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
        raise FileNotFoundError("No gaze fixations file found for AR-6 analysis")

    LOGGER.info("Loading gaze fixations from %s", path)
    df = pd.read_csv(path)

    # Ensure numeric columns are numeric where appropriate
    if "age_months" in df.columns:
        df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")
    # if trial cumulative column exists ensure numeric
    if "trial_cumulative_by_event" in df.columns:
        df["trial_cumulative_by_event"] = pd.to_numeric(df["trial_cumulative_by_event"], errors="coerce")

    return df


def _load_variant_configuration(config: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
    """Load AR-6 variant configuration (supports env override)."""
    analysis_specific = config.get("analysis_specific", {}).get("ar6_trial_order", {})
    default_variant = str(analysis_specific.get("config_name", "AR6_trial_order/ar6_gw_vs_hw")).strip()
    env_variant = os.environ.get("IER_AR6_CONFIG", "").strip()
    variant_name = env_variant or default_variant

    try:
        variant_config = load_analysis_config(variant_name)
    except ConfigurationError as exc:
        LOGGER.warning("Failed to load AR-6 variant config '%s': %s; using empty variant.", variant_name, exc)
        variant_config = {}

    return variant_config, variant_name


def _load_analysis_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load AR-6 specific configuration settings."""
    try:
        analysis_config = load_analysis_config("AR6_trial_order/ar6_config")
    except ConfigurationError:
        analysis_config = {}

    # Default settings
    defaults = {
        "trial_analysis": {
            "trial_variable": "trial_number_global",
            "max_presentations": 5,
            "min_presentations_per_event": 2,
            "expected_pattern": "both",
        },
        "statistics": {
            "primary_test": "linear_mixed_model",
            "random_intercept": True,
            "random_slope": True,
            "test_slope_significance": True,
            "calculate_effect_size": True,
        },
        "metrics": {
            "dependent_variables": ["proportion_primary_aois"],
        },
        "visualization": {
            "plot_type": "line_with_regression",
            "show_individual_trajectories": True,
            "show_group_mean": True,
            "separate_by_condition": True,
        },
        "output": {
            "export_trial_data": True,
            "export_regression_coefficients": True,
            "include_learning_interpretation": True,
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


def calculate_trial_level_metric(
    gaze_fixations: pd.DataFrame,
    metric_name: str = "proportion_primary_aois",
) -> pd.DataFrame:
    """
    Calculate gaze metric per trial for trial-order analysis.

    For AR-6, we need trial-level data (not participant-level aggregates).
    """
    if gaze_fixations.empty:
        return pd.DataFrame(
            columns=["participant_id", "trial_number", "trial_number_global", "condition_name", metric_name]
        )

    # Exclude off-screen fixations from denominator
    aoi_lower = gaze_fixations["aoi_category"].astype(str).str.lower()
    gaze_fixations = gaze_fixations[aoi_lower != "off_screen"].copy()

    # Define primary AOIs (faces, toy present, toy location/anticipation)
    primary_aois = {"man_face", "woman_face", "toy_present", "toy_location"}
    gaze_fixations["is_primary"] = gaze_fixations["aoi_category"].isin(primary_aois)

    # Calculate proportion per trial
    grouped = gaze_fixations.groupby(["participant_id", "trial_number", "condition_name"], as_index=False)

    results = []
    for (participant, trial, condition), group in grouped:
        total_duration = group["gaze_duration_ms"].sum()
        primary_duration = group[group["is_primary"]]["gaze_duration_ms"].sum()

        if total_duration > 0:
            proportion = primary_duration / total_duration
        else:
            proportion = 0.0

        # Get trial_number_global if available
        trial_global = group["trial_number_global"].iloc[0] if "trial_number_global" in group.columns else trial

        results.append(
            {
                "participant_id": participant,
                "trial_number": trial,
                "trial_number_global": trial_global,
                "condition_name": condition,
                metric_name: float(proportion),
            }
        )

    return pd.DataFrame(results)


def add_trial_order_within_event(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add trial order within each event type for each participant.

    This creates a 'trial_order_within_event' column that tracks the 1st, 2nd, 3rd...
    presentation of each specific event type for each participant.
    """
    if data.empty:
        return data

    # Sort by participant and trial number
    data = data.sort_values(["participant_id", "trial_number"]).copy()

    # Create trial order within event type
    data["trial_order_within_event"] = data.groupby(["participant_id", "condition_name"]).cumcount() + 1

    return data


def fit_trial_order_model(
    data: pd.DataFrame,
    dependent_var: str,
    trial_variable: str = "trial_order_within_event",
) -> TrialOrderModelResult:
    """
    Fit trial-order effects model with random slopes.

    This is the gold standard for habituation/learning analysis.
    Uses placeholder until statsmodels LMM is fully integrated.
    """
    warnings: List[str] = []

    if data.empty:
        warnings.append("No data available for modeling")
        return TrialOrderModelResult(
            model_type="linear_mixed_model",
            formula="N/A",
            converged=False,
            fixed_effects=pd.DataFrame(),
            random_effects_variance={},
            r_squared_marginal=0.0,
            r_squared_conditional=0.0,
            aic=0.0,
            bic=0.0,
            slope_coefficient=0.0,
            slope_p_value=1.0,
            slope_significant=False,
            interaction_coefficient=0.0,
            interaction_p_value=1.0,
            interaction_significant=False,
            warnings=warnings,
        )

    # Basic checks
    n_participants = data["participant_id"].nunique()
    if n_participants < 5:
        warnings.append(f"Small sample size (n={n_participants}); interpret with caution")

    # Ensure trial variable exists
    if trial_variable not in data.columns:
        warnings.append(f"Trial variable '{trial_variable}' not found in data; attempting to fall back to 'trial_number_global'")
        if "trial_number_global" in data.columns:
            data[trial_variable] = data["trial_number_global"]
        else:
            warnings.append("No suitable trial variable found; modelling aborted")
            return TrialOrderModelResult(
                model_type="linear_mixed_model",
                formula="N/A",
                converged=False,
                fixed_effects=pd.DataFrame(),
                random_effects_variance={},
                r_squared_marginal=0.0,
                r_squared_conditional=0.0,
                aic=0.0,
                bic=0.0,
                slope_coefficient=0.0,
                slope_p_value=1.0,
                slope_significant=False,
                interaction_coefficient=0.0,
                interaction_p_value=1.0,
                interaction_significant=False,
                warnings=warnings,
            )

    # Prepare data for statsmodels
    working = data.copy()
    working["participant"] = working["participant_id"].astype(str)
    working["condition_name"] = working["condition_name"].astype(str)

    # Build formula from config-like defaults
    formula = f"{dependent_var} ~ {trial_variable} * C(condition_name)"

    # Try full model with random slopes first
    glmm_res = fit_linear_mixed_model(formula, working, groups_column="participant", re_formula=f"1 + {trial_variable}")

    # If convergence fails, try simpler model with random intercept only
    if not glmm_res.converged:
        warnings.append("Random slopes model failed to converge; trying random intercept only")
        glmm_res = fit_linear_mixed_model(formula, working, groups_column="participant", re_formula="1")

    if not glmm_res.converged:
        warnings.extend(glmm_res.warnings or [])

    # Build fixed effects table if available
    fixed_df = pd.DataFrame()
    if glmm_res.params is not None:
        params = glmm_res.params
        pvals = glmm_res.pvalues if glmm_res.pvalues is not None else pd.Series(index=params.index, data=[np.nan] * len(params))

        # Extract standard errors from GLMMResult
        std_err = []
        z_vals = []

        if glmm_res.bse is not None:
            # Use standard errors directly from statsmodels
            for term in params.index:
                se = float(glmm_res.bse.get(term, np.nan))
                std_err.append(se)
                # Calculate z-value from estimate and SE
                est = float(params.get(term, np.nan))
                z_val = est / se if (not np.isnan(se) and se != 0) else np.nan
                z_vals.append(float(z_val))
        else:
            # Fallback: leave as NaN if bse not available
            for term in params.index:
                std_err.append(np.nan)
                z_vals.append(np.nan)

        fixed_df = pd.DataFrame(
            {
                "term": list(params.index),
                "estimate": list(params.values),
                "std_error": std_err,
                "z_value": z_vals,
                "p_value": [float(pvals.get(t, np.nan)) for t in params.index],
            }
        )

    # Random effects variance - cannot reliably extract from helper; leave empty or report warnings
    random_var = {}
    if glmm_res.aic is None and not glmm_res.converged:
        warnings.append("Model fit did not return AIC/BIC or converged state may be unreliable")

    # Extract slope coefficient for main trial term
    slope_term_candidates = [t for t in (glmm_res.params.index if glmm_res.params is not None else []) if trial_variable in t and ":" not in t]
    if slope_term_candidates:
        slope_term = slope_term_candidates[0]
        slope_coef = float(glmm_res.params[slope_term])
        slope_p = float(glmm_res.pvalues[slope_term]) if (glmm_res.pvalues is not None and slope_term in glmm_res.pvalues.index) else float(np.nan)
        slope_sig = (not np.isnan(slope_p)) and (slope_p < 0.05)
    else:
        slope_coef = 0.0
        slope_p = 1.0
        slope_sig = False

    # Extract interaction coefficient (Trial × Condition)
    interaction_term_candidates = [t for t in (glmm_res.params.index if glmm_res.params is not None else [])
                                    if trial_variable in t and "condition_name" in t and ":" in t]
    if interaction_term_candidates:
        interaction_term = interaction_term_candidates[0]
        interaction_coef = float(glmm_res.params[interaction_term])
        interaction_p = float(glmm_res.pvalues[interaction_term]) if (glmm_res.pvalues is not None and interaction_term in glmm_res.pvalues.index) else float(np.nan)
        interaction_sig = (not np.isnan(interaction_p)) and (interaction_p < 0.05)
    else:
        interaction_coef = 0.0
        interaction_p = 1.0
        interaction_sig = False

    # Compute individual participant slopes by fitting simple OLS per participant
    participant_slopes = []
    for pid, grp in working.groupby("participant"):
        grp = grp.dropna(subset=[dependent_var, trial_variable])
        if grp.shape[0] >= 2:
            try:
                x = grp[trial_variable].astype(float).values
                y = grp[dependent_var].astype(float).values
                coef = np.polyfit(x, y, 1)[0]
            except Exception:
                coef = float(np.nan)
        else:
            coef = float(np.nan)
        participant_slopes.append({"participant_id": pid, "slope": float(coef)})

    slopes_df = pd.DataFrame(participant_slopes)

    return TrialOrderModelResult(
        model_type="linear_mixed_model",
        formula=formula,
        converged=glmm_res.converged,
        fixed_effects=fixed_df,
        random_effects_variance=random_var,
        r_squared_marginal=0.0,
        r_squared_conditional=0.0,
        aic=float(glmm_res.aic) if glmm_res.aic is not None else 0.0,
        bic=float(glmm_res.bic) if glmm_res.bic is not None else 0.0,
        slope_coefficient=float(slope_coef),
        slope_p_value=float(slope_p) if not np.isnan(slope_p) else 1.0,
        slope_significant=bool(slope_sig),
        interaction_coefficient=float(interaction_coef),
        interaction_p_value=float(interaction_p) if not np.isnan(interaction_p) else 1.0,
        interaction_significant=bool(interaction_sig),
        warnings=warnings,
    )


def summarize_by_trial(data: pd.DataFrame, dependent_var: str, trial_variable: str) -> pd.DataFrame:
    """Summarize gaze metric by trial number and condition for visualization."""
    if data.empty:
        return pd.DataFrame(columns=[trial_variable, "condition_name", "mean", "sem", "n"])

    grouped = data.groupby([trial_variable, "condition_name"], as_index=False)

    results = []
    for (trial, condition), group in grouped:
        values = group[dependent_var].dropna()
        if len(values) > 0:
            results.append(
                {
                    trial_variable: int(trial),
                    "condition_name": condition,
                    "mean": float(values.mean()),
                    "sem": float(values.sem()) if len(values) > 1 else 0.0,
                    "n": int(len(values)),
                }
            )

    return pd.DataFrame(results)


def _build_overview_text(model_result: TrialOrderModelResult) -> str:
    """Generate overview text for the report."""
    # Main slope effect
    if model_result.slope_significant:
        direction = "decreasing" if model_result.slope_coefficient < 0 else "increasing"
        slope_text = (
            f"Trial-order effects analysis revealed a significant {direction} trend in looking behavior "
            f"across repeated presentations (slope = {model_result.slope_coefficient:.4f}, p = {model_result.slope_p_value:.3f}). "
        )
    else:
        slope_text = (
            f"Trial-order effects analysis found no significant overall change in looking behavior across "
            f"repeated presentations (slope = {model_result.slope_coefficient:.4f}, p = {model_result.slope_p_value:.3f}). "
        )

    # Interaction effect
    if model_result.interaction_significant:
        interaction_direction = "accelerated differently" if model_result.interaction_coefficient != 0 else "varied"
        interaction_text = (
            f"Importantly, the trial-order effect differed between conditions "
            f"(interaction coefficient = {model_result.interaction_coefficient:.4f}, p = {model_result.interaction_p_value:.3f}), "
            f"suggesting that learning or habituation rates varied by event type."
        )
    else:
        interaction_text = (
            f"The trial-order pattern did not differ significantly between conditions "
            f"(interaction p = {model_result.interaction_p_value:.3f}), indicating similar adaptation patterns across event types."
        )

    return slope_text + interaction_text


def _build_methods_text(settings: Dict[str, Any]) -> str:
    """Generate methods description."""
    trial_var = settings.get("trial_analysis", {}).get("trial_variable", "trial_number_global")
    has_random_slope = settings.get("statistics", {}).get("random_slope", True)

    random_effects_desc = (
        "random intercepts and random slopes for trial number" if has_random_slope else "random intercepts only"
    )

    return (
        f"Trial-order effects were analyzed using Linear Mixed Models (LMM) with {random_effects_desc} "
        f"for participants. The model tested whether {trial_var} predicted gaze patterns, "
        "indicating systematic learning or habituation across repeated presentations of the same event type. "
        "Random slopes allow each participant to have their own rate of change, which is essential "
        "for properly modeling individual differences in learning/habituation."
    )


def _build_statistics_table(model_result: TrialOrderModelResult) -> str:
    """Generate HTML statistics table."""
    if not model_result.fixed_effects.empty:
        fixed_html = model_result.fixed_effects.to_html(index=False, classes="table table-striped", float_format="%.4f")
    else:
        fixed_html = "<p>Fixed effects not available</p>"

    # Random effects variance table
    random_var_data = [{"Component": k, "Variance": v} for k, v in model_result.random_effects_variance.items()]
    if random_var_data:
        random_var_df = pd.DataFrame(random_var_data)
        random_html = random_var_df.to_html(index=False, classes="table table-striped", float_format="%.4f")
    else:
        random_html = "<p>Random effects not available</p>"

    model_fit_html = f"""
    <h4>Model Fit</h4>
    <ul>
        <li><strong>R² (marginal - fixed effects only):</strong> {model_result.r_squared_marginal:.3f}</li>
        <li><strong>R² (conditional - fixed + random):</strong> {model_result.r_squared_conditional:.3f}</li>
        <li><strong>AIC:</strong> {model_result.aic:.2f}</li>
        <li><strong>BIC:</strong> {model_result.bic:.2f}</li>
    </ul>
    """

    warnings_html = ""
    if model_result.warnings:
        warnings_list = "".join(f"<li>{warning}</li>" for warning in model_result.warnings)
        warnings_html = f'<div class="alert alert-warning"><h5>Warnings</h5><ul>{warnings_list}</ul></div>'

    return f"""
    <h3>Fixed Effects</h3>
    {fixed_html}

    <h3>Random Effects Variance Components</h3>
    {random_html}

    {model_fit_html}

    {warnings_html}
    """


def _generate_outputs(
    *,
    output_dir: Path,
    trial_data: pd.DataFrame,
    summary: pd.DataFrame,
    model_result: TrialOrderModelResult,
    dependent_var: str,
    trial_variable: str,
    settings: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate all AR-6 outputs: tables, figures, reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save data tables
    trial_csv = output_dir / f"{dependent_var}_by_trial.csv"
    trial_data.to_csv(trial_csv, index=False)

    summary_csv = output_dir / f"{dependent_var}_trial_summary.csv"
    summary.to_csv(summary_csv, index=False)

    if not model_result.fixed_effects.empty:
        coef_csv = output_dir / f"{dependent_var}_fixed_effects.csv"
        model_result.fixed_effects.to_csv(coef_csv, index=False)

    # Generate figures
    figures = []

    if not summary.empty:
        # Trial-order plot
        trial_fig = output_dir / f"{dependent_var}_by_trial.png"
        visualizations.line_plot_with_error_bars(
            summary,
            x=trial_variable,
            y="mean",
            hue="condition_name",
            title=f"Trial-Order Effects: {dependent_var.replace('_', ' ').title()}",
            xlabel="Trial Number",
            ylabel=dependent_var.replace("_", " ").title(),
            output_path=trial_fig,
        )
        # Use relative path from HTML file (in same directory as figure)
        figures.append(
            {
                "path": trial_fig.name,  # Just the filename, not full path
                "caption": f"Trial-order effects for {dependent_var}",
            }
        )

    # Build report context
    from datetime import datetime

    context = {
        # Base template required variables
        "report_title": "Trial-Order Effects Analysis",
        "analysis_name": "AR-6: Learning and Habituation",
        "analysis_id": "AR-6",
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pipeline_version": "1.0",
        "alpha": 0.05,
        "min_gaze_frames": 3,
        "error_bar_type": "SEM",

        # AR6-specific content
        "overview_text": _build_overview_text(model_result),
        "methods_text": _build_methods_text(settings),
        "regression_table": _build_statistics_table(model_result),
        "interpretation_text": (
            "Significant trial-order effects indicate learning or habituation. Negative slopes suggest "
            "adaptation/habituation (decreasing interest), while positive slopes suggest learning "
            "(increasing interest). The trial × condition interaction tests whether learning/habituation rates "
            "differ between event types (e.g., GIVE vs HUG). A significant interaction would indicate that "
            "infants adapt differently to different event structures."
        ),
        "learning_figures": figures,  # Template expects 'learning_figures'
        "figures": [fig["path"] for fig in figures],  # Already relative paths now
        "tables": [str(trial_csv), str(summary_csv)],
    }

    # Render report
    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar6_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-6",
        "title": "Trial-Order Effects Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "tables": [str(trial_csv), str(summary_csv)],
        "figures": [fig["path"] for fig in figures],
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    """Run AR-6 trial-order effects analysis."""
    LOGGER.info("Starting AR-6 trial-order effects analysis")

    # Load variant config (optional)
    variant_config, variant_name = _load_variant_configuration(config)
    variant_key = variant_config.get("variant_key", Path(variant_name).stem)
    variant_label = variant_config.get("variant_label", variant_key)

    settings = _load_analysis_settings(config)

    # Resolve cohorts if provided in variant; otherwise use processed gaze_fixations
    cohorts = variant_config.get("cohorts") if isinstance(variant_config, dict) else None
    cohort_frames: List[pd.DataFrame] = []

    if not cohorts:
        try:
            gf = _load_gaze_fixations(config)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping AR-6 analysis: %s", exc)
            return {"report_id": "AR-6", "title": "Trial-Order Effects Analysis", "html_path": "", "pdf_path": ""}

        if gf.empty:
            LOGGER.warning("Gaze fixations file is empty; skipping AR-6 analysis")
            return {"report_id": "AR-6", "title": "Trial-Order Effects Analysis", "html_path": "", "pdf_path": ""}

        cohort_frames.append(gf)
    else:
        processed_root_cfg = Path(config["paths"]["processed_data"])
        if processed_root_cfg.is_absolute():
            processed_root = processed_root_cfg.resolve()
        else:
            processed_root = (Path.cwd() / processed_root_cfg).resolve()
        project_root = Path.cwd()
        for cohort in cohorts:
            data_path = cohort.get("data_path")
            label = cohort.get("label", cohort.get("key", "cohort"))
            if not data_path:
                LOGGER.warning("Cohort '%s' missing data_path; skipping.", label)
                continue
            raw_path = Path(data_path)
            if raw_path.is_absolute():
                p = raw_path
            else:
                candidate = (project_root / raw_path).resolve()
                if candidate.exists():
                    p = candidate
                else:
                    p = (processed_root / raw_path).resolve()
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
            except Exception as exc:  # defensive
                LOGGER.warning("Cohort '%s' filter error: %s; skipping filters.", label, exc)

            if df.empty:
                LOGGER.info("Cohort '%s' has no data after filtering; skipping.", label)
                continue

            cohort_frames.append(df)

    if not cohort_frames:
        LOGGER.warning("No cohorts produced data for AR-6; skipping")
        return {"report_id": "AR-6", "title": "Trial-Order Effects Analysis", "html_path": "", "pdf_path": ""}

    gaze_fixations = pd.concat(cohort_frames, ignore_index=True)

    # Optional: restrict to target conditions if provided by variant
    target_conditions = None
    if isinstance(variant_config, dict):
        target_conditions = variant_config.get("target_conditions")
        if target_conditions and "condition_name" in gaze_fixations.columns:
            before_n = len(gaze_fixations)
            gaze_fixations = gaze_fixations[gaze_fixations["condition_name"].isin(list(target_conditions))].copy()
            LOGGER.info(
                "Filtered to target conditions %s (rows: %s -> %s)",
                list(target_conditions),
                before_n,
                len(gaze_fixations),
            )
        elif target_conditions:
            LOGGER.warning("target_conditions provided but 'condition_name' column not found; skipping filter")

    # Calculate trial-level metric
    dependent_var = "proportion_primary_aois"
    trial_data = calculate_trial_level_metric(gaze_fixations, dependent_var)
    if trial_data.empty:
        LOGGER.warning("No valid trial data for AR-6 analysis")
        return {"report_id": "AR-6", "title": "Trial-Order Effects Analysis", "html_path": "", "pdf_path": ""}

    # Add trial order within event
    trial_data = add_trial_order_within_event(trial_data)

    # Determine trial variable to use
    trial_variable = settings.get("trial_analysis", {}).get("trial_variable", "trial_order_within_event")
    if trial_variable not in trial_data.columns:
        # try fallbacks
        if "trial_number_global" in trial_data.columns:
            trial_data[trial_variable] = trial_data["trial_number_global"]

    # Fit trial-order model
    model_result = fit_trial_order_model(trial_data, dependent_var, trial_variable)

    # Compute participant-level slopes (simple OLS per participant)
    participant_slopes = []
    for pid, grp in trial_data.groupby("participant_id"):
        grp = grp.dropna(subset=[dependent_var, trial_variable])
        if grp.shape[0] >= 2:
            try:
                x = grp[trial_variable].astype(float).values
                y = grp[dependent_var].astype(float).values
                slope = float(np.polyfit(x, y, 1)[0])
            except Exception:
                slope = float(np.nan)
        else:
            slope = float(np.nan)
        participant_slopes.append({"participant_id": pid, "slope": slope})

    slopes_df = pd.DataFrame(participant_slopes)

    # Classify participants
    classify = variant_config.get("trial_order_effects", {}).get("classify_participants", True)
    slope_threshold = variant_config.get("trial_order_effects", {}).get("slope_threshold", 0.01)
    classifications = []
    if classify and not slopes_df.empty:
        for _, row in slopes_df.iterrows():
            s = row["slope"]
            if pd.isna(s):
                cls = "stable"
            elif s > slope_threshold:
                cls = "learner"
            elif s < -slope_threshold:
                cls = "adapter"
            else:
                cls = "stable"
            classifications.append({"participant_id": row["participant_id"], "slope": row["slope"], "classification": cls})
    classifications_df = pd.DataFrame(classifications)

    # Summarize by trial for visualization
    summary = summarize_by_trial(trial_data, dependent_var, trial_variable)

    # Generate outputs under variant-specific directory
    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name / variant_key
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save extra outputs
    slopes_csv = output_dir / f"{dependent_var}_participant_slopes.csv"
    slopes_df.to_csv(slopes_csv, index=False)
    if not classifications_df.empty:
        class_csv = output_dir / f"{dependent_var}_participant_classification.csv"
        classifications_df.to_csv(class_csv, index=False)

    metadata = _generate_outputs(
        output_dir=output_dir,
        trial_data=trial_data,
        summary=summary,
        model_result=model_result,
        dependent_var=dependent_var,
        trial_variable=trial_variable,
        settings=settings,
        config=config,
    )

    metadata["variant_key"] = variant_key
    metadata["variant_label"] = variant_label

    LOGGER.info("AR-6 analysis completed; report generated at %s", metadata.get("html_path"))
    return metadata


__all__ = [
    "TrialOrderModelResult",
    "calculate_trial_level_metric",
    "add_trial_order_within_event",
    "fit_trial_order_model",
    "summarize_by_trial",
    "run",
]
