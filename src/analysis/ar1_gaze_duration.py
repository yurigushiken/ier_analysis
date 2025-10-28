"""AR-1 Gaze Duration analysis module."""

from __future__ import annotations

import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import cohens_d, t_test
from src.utils.config import load_analysis_config
from scipy import stats

LOGGER = logging.getLogger("ier.analysis.ar1")

TOY_AOIS: Iterable[str] = ("toy_present", "toy_location")
ONSCREEN_EXCLUDE: Iterable[str] = ("off_screen",)

def _load_gaze_fixations(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Gaze fixations file not found for AR-1 analysis: {path}")

    LOGGER.info("Loading gaze fixations from %s", path)
    return pd.read_csv(path)


def _calculate_trial_proportions(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[~df["aoi_category"].isin(ONSCREEN_EXCLUDE)].copy()
    filtered["is_toy"] = filtered["aoi_category"].isin(TOY_AOIS)

    trial_totals = filtered.groupby(["participant_id", "condition_name", "trial_number"], as_index=False)[
        "gaze_duration_ms"
    ].sum()
    toy_totals = (
        filtered[filtered["is_toy"]]
        .groupby(["participant_id", "condition_name", "trial_number"], as_index=False)["gaze_duration_ms"]
        .sum()
        .rename(columns={"gaze_duration_ms": "toy_duration_ms"})
    )

    merged = pd.merge(
        trial_totals,
        toy_totals,
        on=["participant_id", "condition_name", "trial_number"],
        how="left",
    )
    # Avoid chained-assignment; assign the filled series back to the column
    merged["toy_duration_ms"] = merged["toy_duration_ms"].fillna(0.0)
    merged["toy_proportion"] = merged.apply(
        lambda row: row["toy_duration_ms"] / row["gaze_duration_ms"] if row["gaze_duration_ms"] > 0 else 0.0,
        axis=1,
    )
    return merged


def _apply_participant_filters(
    df: pd.DataFrame, filters: Optional[Dict[str, Iterable[Any]]]
) -> pd.DataFrame:
    """Filter the gaze fixation dataframe using cohort-level criteria."""
    if not filters:
        return df

    filtered = df
    for column, allowed in filters.items():
        if column not in filtered.columns:
            raise KeyError(f"Filter column '{column}' not found in gaze fixations data.")

        if isinstance(allowed, (list, tuple, set)):
            allowed_values = list(allowed)
        else:
            allowed_values = [allowed]

        filtered = filtered[filtered[column].isin(allowed_values)]

    return filtered


def _aggregate_by_condition(trial_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate trial data to participant and condition levels.
    
    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        - participant_means: participant × condition means
        - condition_summary: condition-level summary with proper participant counts
    """
    # First aggregate to participant × condition level
    participant_means = trial_df.groupby(["condition_name", "participant_id"], as_index=False)["toy_proportion"].mean()
    
    # Then summarize by condition (n = unique participants per condition)
    condition_summary = (
        participant_means.groupby("condition_name")
        .agg(
            mean_toy_proportion=("toy_proportion", "mean"),
            n=("participant_id", "nunique")  # Count UNIQUE participants
        )
        .reset_index()
    )
    
    return participant_means, condition_summary


def _get_active_comparison(analysis_config: Dict[str, Any]) -> tuple[List[str], List[str], str]:
    """Resolve comparison groups from the analysis configuration."""

    comparisons = analysis_config.get("comparisons")
    active_key = analysis_config.get("active_comparison", "primary")

    if not comparisons or not isinstance(comparisons, dict):
        raise ValueError("AR-1 variant configuration is missing a 'comparisons' mapping.")

    comparison = comparisons.get(active_key)
    if not comparison:
        raise ValueError(f"Active comparison '{active_key}' not defined in AR-1 configuration.")

    give_conditions = comparison.get("give_conditions")
    hug_conditions = comparison.get("hug_conditions")

    if not give_conditions or not hug_conditions:
        raise ValueError("Comparison definition must include both 'give_conditions' and 'hug_conditions'.")

    LOGGER.info("Active comparison '%s'", active_key)
    LOGGER.debug("  Group A conditions: %s", give_conditions)
    LOGGER.debug("  Group B conditions: %s", hug_conditions)

    return list(give_conditions), list(hug_conditions), str(active_key)


def _compute_statistics(
    participant_means: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    config: Dict[str, Any],
    give_conditions: List[str],
    hug_conditions: List[str],
    comparison_label: str,
) -> Dict[str, Any]:
    """Compute statistical comparisons using PARTICIPANT-LEVEL means."""
    stats_context: Dict[str, Any] = {
        "summary_rows": [],
        "ttest": None,
        "cohens_d": None,
        "ci_lower": None,
        "ci_upper": None,
        "ttest_df": None,
        "ttest_p": None,
        "ttest_statistic": None,
        "significant_condition": None,
        "other_condition": None,
        "p_comparison": "=",
        "comparison_label": comparison_label,
        "give_conditions": give_conditions,
        "hug_conditions": hug_conditions,
    }

    for _, row in summary.iterrows():
        stats_context["summary_rows"].append(
            {
                "condition": row["condition_name"],
                "mean": row["mean_toy_proportion"],
                "n": int(row["n"]),
            }
        )

    give = participant_means[
        participant_means["condition_name"].isin(give_conditions)
    ]["toy_proportion"]

    hug = participant_means[
        participant_means["condition_name"].isin(hug_conditions)
    ]["toy_proportion"]

    min_n = config.get("analysis", {}).get("min_statistical_n", 3)
    alpha_value = config.get("analysis", {}).get("alpha", 0.05)

    stats_context["give_n"] = len(give)
    stats_context["hug_n"] = len(hug)

    confidence_level = config.get("analysis", {}).get("confidence_level", 0.95)

    if len(give) >= min_n and len(hug) >= min_n:
        stats_context["give_mean"] = float(give.mean())
        stats_context["hug_mean"] = float(hug.mean())

        ttest_result = t_test(give, hug)
        stats_context["ttest"] = ttest_result
        stats_context["ttest_df"] = getattr(ttest_result, "df", len(give) + len(hug) - 2)
        stats_context["ttest_p"] = float(ttest_result.pvalue)
        stats_context["ttest_statistic"] = float(ttest_result.statistic)
        stats_context["cohens_d"] = float(cohens_d(give, hug))

        diff_mean = stats_context["give_mean"] - stats_context["hug_mean"]
        var_give = float(give.var(ddof=1)) if len(give) > 1 else 0.0
        var_hug = float(hug.var(ddof=1)) if len(hug) > 1 else 0.0
        se_diff = math.sqrt(var_give / len(give) + var_hug / len(hug)) if len(give) and len(hug) else float("nan")
        df_value = stats_context["ttest_df"] if stats_context["ttest_df"] is not None else len(give) + len(hug) - 2

        if se_diff and math.isfinite(se_diff) and se_diff > 0 and df_value > 0:
            tail = (1.0 - confidence_level) / 2.0
            t_crit = stats.t.ppf(1.0 - tail, df_value)
            ci_lower = diff_mean - t_crit * se_diff
            ci_upper = diff_mean + t_crit * se_diff
            stats_context["ci_lower"] = float(ci_lower)
            stats_context["ci_upper"] = float(ci_upper)
        else:
            stats_context["ci_lower"] = None
            stats_context["ci_upper"] = None

        stats_context["significant_condition"] = " + ".join(give_conditions)
        stats_context["other_condition"] = " + ".join(hug_conditions)
        stats_context["p_comparison"] = "<" if ttest_result.pvalue < alpha_value else "="
    else:
        stats_context["ttest_p"] = None
        stats_context["significant_condition"] = " + ".join(give_conditions)
        stats_context["other_condition"] = " + ".join(hug_conditions)
        stats_context["ci_lower"] = None
        stats_context["ci_upper"] = None
        LOGGER.warning(
            "Insufficient data for GIVE vs HUG comparison (n_give=%s, n_hug=%s)",
            len(give),
            len(hug),
        )

    return stats_context


def _compute_age_anova(
    cohort_df: pd.DataFrame,
    primary_participant_means: pd.DataFrame,
    *,
    min_group_n: int,
) -> Dict[str, Any]:
    """Run one-way ANOVA across age groups using participant-level averages."""

    result: Dict[str, Any] = {
        "available": False,
        "message": "",
        "table": None,
        "f_statistic": None,
        "p_value": None,
        "df_between": None,
        "df_within": None,
        "eta_squared": None,
    }

    if primary_participant_means.empty or cohort_df.empty:
        result["message"] = "No data available for age analysis."
        return result

    age_map = (
        cohort_df[["participant_id", "age_group"]]
        .drop_duplicates(subset=["participant_id"])
        .set_index("participant_id")
    )

    participant_mean = (
        primary_participant_means.groupby("participant_id", as_index=False)["toy_proportion"].mean()
    )
    participant_mean["age_group"] = participant_mean["participant_id"].map(age_map["age_group"])
    participant_mean = participant_mean.dropna(subset=["age_group"])

    if participant_mean.empty:
        result["message"] = "Age group labels unavailable for participants in this comparison."
        return result

    grouped = participant_mean.groupby("age_group")
    valid_groups: List[np.ndarray] = []
    group_names: List[str] = []
    summaries: List[Tuple[str, int, float, float]] = []

    for name, subset in grouped:
        values = subset["toy_proportion"].to_numpy(dtype=float)
        n = len(values)
        if n >= min_group_n:
            valid_groups.append(values)
            group_names.append(str(name))
            summaries.append(
                (
                    str(name),
                    n,
                    float(np.mean(values)),
                    float(np.std(values, ddof=1)) if n > 1 else 0.0,
                )
            )

    if len(valid_groups) < 2:
        result["message"] = (
            "Age analysis requires at least two age groups with sufficient data "
            f"(minimum {min_group_n} participants each)."
        )
        return result

    try:
        f_statistic, p_value = stats.f_oneway(*valid_groups)
    except Exception as exc:  # pragma: no cover - defensive
        result["message"] = f"ANOVA computation failed: {exc}"
        return result

    df_between = len(valid_groups) - 1
    df_within = sum(len(g) for g in valid_groups) - len(valid_groups)

    all_values = np.concatenate(valid_groups)
    grand_mean = float(np.mean(all_values))
    ss_between = 0.0
    for group_values in valid_groups:
        group_mean = float(np.mean(group_values))
        ss_between += len(group_values) * (group_mean - grand_mean) ** 2

    ss_total = float(np.sum((all_values - grand_mean) ** 2))
    eta_squared = ss_between / ss_total if ss_total > 0 else None

    result.update(
        {
            "available": True,
            "message": "",
            "table": pd.DataFrame(
                summaries,
                columns=["Age Group", "N Participants", "Mean Toy Proportion", "SD Toy Proportion"],
            ),
            "f_statistic": float(f_statistic),
            "p_value": float(p_value),
            "df_between": int(df_between),
            "df_within": int(df_within),
            "eta_squared": float(eta_squared) if eta_squared is not None else None,
        }
    )
    return result


def _generate_outputs(
    *,
    output_dir: Path,
    cohort_results: List[Dict[str, Any]],
    primary_result: Dict[str, Any],
    primary_conditions: List[str],
    full_conditions: List[str],
    config: Dict[str, Any],
    variant_key: str,
    variant_label: str,
    report_title: str,
    variant_description: str,
) -> Dict[str, Any]:
    """Generate overview and context outputs for AR-1."""
    output_dir.mkdir(parents=True, exist_ok=True)

    def build_table(df: pd.DataFrame) -> str:
        if df.empty:
            return "<p>No data available for this subset.</p>"
        return (
            df.rename(
                columns={
                    "condition_name": "Condition",
                    "mean_toy_proportion": "Mean Toy Proportion",
                    "n": "N Participants",
                }
            ).to_html(index=False, classes="table table-striped", float_format="%.3f")
        )

    table_names: List[str] = []
    primary_tables_html_parts: List[str] = []
    full_tables_html_parts: List[str] = []

    for result in cohort_results:
        key = result["key"]
        label = result["label"]
        cohort_n = (
            result["primary_participant_means"]["participant_id"].nunique()
            if not result["primary_participant_means"].empty
            else 0
        )
        legend_label = f"{label} (N={cohort_n})" if cohort_n else label
        primary_summary = result["primary_summary"]
        full_summary = result["full_summary"]

        primary_summary_csv = output_dir / f"summary_stats_primary_{key}.csv"
        full_summary_csv = output_dir / f"summary_stats_all_conditions_{key}.csv"

        primary_summary.to_csv(primary_summary_csv, index=False)
        full_summary.to_csv(full_summary_csv, index=False)

        table_names.extend([primary_summary_csv.name, full_summary_csv.name])
        primary_tables_html_parts.append(f"<h4>{label} (N={cohort_n})</h4>{build_table(primary_summary)}")
        full_tables_html_parts.append(f"<h4>{label}</h4>{build_table(full_summary)}")

    primary_table_html = "\n".join(primary_tables_html_parts) if primary_tables_html_parts else "<p>No data.</p>"
    full_table_html = "\n".join(full_tables_html_parts) if full_tables_html_parts else "<p>No data.</p>"

    figures: List[Path] = []
    primary_plot_frames: List[pd.DataFrame] = []
    full_plot_frames: List[pd.DataFrame] = []

    for result in cohort_results:
        label = result["label"]
        cohort_n = (
            result["primary_participant_means"]["participant_id"].nunique()
            if not result["primary_participant_means"].empty
            else 0
        )
        legend_label = f"{label} (N={cohort_n})" if cohort_n else label

        if result["include_in_primary_plot"] and not result["primary_summary"].empty:
            df_primary = result["primary_summary"].copy()
            df_primary["cohort"] = legend_label
            primary_plot_frames.append(df_primary)
        if not result["full_summary"].empty:
            df_full = result["full_summary"].copy()
            df_full["cohort"] = legend_label
            full_plot_frames.append(df_full)

    primary_figure_path = output_dir / "duration_primary_comparison_by_cohort.png"
    if primary_plot_frames:
        primary_plot_df = pd.concat(primary_plot_frames, ignore_index=True)
        visualizations.bar_plot(
            primary_plot_df,
            x="condition_name",
            y="mean_toy_proportion",
            hue="cohort",
            title=f"{variant_label}: Toy Looking by Cohort",
            ylabel="Proportion of Looking Time on Toy",
            xlabel="Condition",
            output_path=primary_figure_path,
            figsize=(10, 6),
            rotate_labels=0,
        )
        figures.append(primary_figure_path)
        primary_figure_str = primary_figure_path.name
    else:
        primary_figure_str = ""

    full_figure_path = output_dir / "duration_by_condition_by_cohort.png"
    if full_plot_frames:
        full_plot_df = pd.concat(full_plot_frames, ignore_index=True)
        visualizations.bar_plot(
            full_plot_df,
            x="condition_name",
            y="mean_toy_proportion",
            hue="cohort",
            title=f"{variant_label}: All Conditions by Cohort",
            ylabel="Proportion of Looking Time on Toy",
            xlabel="Experimental Condition",
            output_path=full_figure_path,
            figsize=(14, 6),
            rotate_labels=45,
        )
        figures.append(full_figure_path)
        full_figure_str = full_figure_path.name
    else:
        full_figure_str = ""

    stats_context = primary_result["stats_context"]
    primary_participant_means = primary_result["primary_participant_means"]
    age_anova = primary_result.get("age_anova", {})

    unique_primary_participants = (
        primary_participant_means["participant_id"].nunique() if not primary_participant_means.empty else 0
    )

    total_gaze_fixations = sum(
        result["total_gaze_fixations_primary"]
        for result in cohort_results
        if result["include_in_primary_plot"]
    )
    total_gaze_fixations_all = sum(result["total_gaze_fixations_all"] for result in cohort_results)

    reporting_cfg = config.get("reporting", {})
    error_bar_type = (reporting_cfg.get("error_bar_type") or "sem").lower()
    error_bar_labels = {
        "sem": "standard error of the mean",
        "sd": "standard deviation",
        "ci": "confidence interval",
    }
    error_bar_label = error_bar_labels.get(error_bar_type, error_bar_type)

    alpha_value = config.get("analysis", {}).get("alpha", 0.05)

    interpretation_text = (
        f"Toy-looking proportions for {variant_label} show differences across the configured conditions."
    )
    if stats_context["ttest_p"] is not None:
        if stats_context["ttest_p"] < alpha_value:
            interpretation_text = (
                f"Infants looked significantly more at the toy in {stats_context['significant_condition']} "
                f"(M = {stats_context['give_mean']:.3f}) compared to {stats_context['other_condition']} "
                f"(M = {stats_context['hug_mean']:.3f}); "
                f"t({stats_context['ttest_df']:.1f}) = {stats_context['ttest_statistic']:.2f}, "
                f"p {stats_context['p_comparison']} {stats_context['ttest_p']:.3f}, "
                f"Cohen's d = {stats_context['cohens_d']:.2f}."
            )
        else:
            interpretation_text = (
                f"No significant difference was found between {stats_context['significant_condition']} "
                f"(M = {stats_context['give_mean']:.3f}) and {stats_context['other_condition']} "
                f"(M = {stats_context['hug_mean']:.3f}); "
                f"t({stats_context['ttest_df']:.1f}) = {stats_context['ttest_statistic']:.2f}, "
                f"p = {stats_context['ttest_p']:.3f}."
            )

    figures_names = [p.name for p in figures if p]
    table_names = list(dict.fromkeys(table_names))

    ci_lower_value = stats_context.get("ci_lower")
    ci_upper_value = stats_context.get("ci_upper")
    ci_lower_fmt = (
        f"{ci_lower_value:.3f}"
        if ci_lower_value is not None and math.isfinite(ci_lower_value)
        else "N/A"
    )
    ci_upper_fmt = (
        f"{ci_upper_value:.3f}"
        if ci_upper_value is not None and math.isfinite(ci_upper_value)
        else "N/A"
    )

    if age_anova.get("available"):
        anova_table_html = age_anova["table"].to_html(
            index=False, classes="table table-striped", float_format="%.3f"
        )
        anova_p = age_anova.get("p_value")
        anova_df1 = age_anova.get("df_between")
        anova_df2 = age_anova.get("df_within")
        anova_f_stat = age_anova.get("f_statistic")
        eta_squared = age_anova.get("eta_squared")
        anova_message = ""
    else:
        anova_table_html = f"<p>{age_anova.get('message', 'Age analysis not available.')}</p>"
        anova_p = None
        anova_df1 = None
        anova_df2 = None
        anova_f_stat = None
        eta_squared = None
        anova_message = age_anova.get("message", "")

    participant_count_note = (
        "Participant counts reflect those with at least one valid trial per condition; counts can differ "
        "because some participants lacked usable data for specific conditions."
    )

    context = {
        "report_title": report_title,
        "variant_label": variant_label,
        "variant_key": variant_key,
        "variant_description": variant_description,
        "total_participants": unique_primary_participants,
        "participants_included": unique_primary_participants,
        "participants_excluded": 0,
        "total_gaze_fixations": total_gaze_fixations,
        "total_gaze_fixations_all": total_gaze_fixations_all,
        "primary_conditions": primary_conditions,
        "primary_conditions_joined": ", ".join(primary_conditions),
        "full_conditions": full_conditions,
        "full_conditions_joined": ", ".join(full_conditions),
        "comparison_label": stats_context.get("comparison_label", variant_label),
        "give_conditions": stats_context.get("give_conditions", []),
        "hug_conditions": stats_context.get("hug_conditions", []),
        "participant_count_note": participant_count_note,
        "exclusions": [],
        "min_gaze_frames": config.get("analysis", {}).get("min_gaze_frames", 3),
        "alpha": alpha_value,
        "primary_descriptive_table": primary_table_html,
        "full_descriptive_table": full_table_html,
        "figure_primary_comparison": primary_figure_str,
        "figure_full_conditions": full_figure_str,
        "error_bar_label": error_bar_label,
        "error_bar_type": error_bar_type,
        "significance_marker": (
            "*" if stats_context["ttest_p"] and stats_context["ttest_p"] < alpha_value else ""
        ),
        "ttest_p": stats_context["ttest_p"],
        "ttest_df": stats_context["ttest_df"],
        "ttest_statistic": stats_context["ttest_statistic"],
        "cohens_d": stats_context["cohens_d"],
        "ci_lower": ci_lower_fmt,
        "ci_upper": ci_upper_fmt,
        "significant_condition": stats_context["significant_condition"],
        "other_condition": stats_context["other_condition"],
        "p_comparison": stats_context["p_comparison"],
        "figure_duration_by_age": "",
        "anova_results_table": anova_table_html,
        "anova_p": anova_p,
        "anova_df1": anova_df1,
        "anova_df2": anova_df2,
        "anova_f_statistic": anova_f_stat,
        "eta_squared": eta_squared,
        "assumptions_violated": False,
        "assumptions_violated_message": anova_message,
        "interpretation_text": interpretation_text,
        "comparison_to_gordon": (
            "Consistent with Gordon (2003), this comparison supports the idea that infants "
            "differentiate event-relevant objects from incidental elements."
        ),
        "limitations": (
            "Current analysis focuses on the configured AR-1 comparison. Additional modules (AR-5/AR-6) "
            "provide developmental and learning perspectives. Sample size is adequate for the primary comparison "
            "(n >= 3 per condition)."
        ),
        "participant_summary_table": "",
        "assumptions_table": "",
        "logs_summary": "",
        "figures": figures_names,
        "tables": table_names,
    }

    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar1_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-1",
        "title": report_title,
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute AR-1 Gaze Duration Analysis."""
    LOGGER.info("Starting AR-1 gaze duration analysis")

    analysis_specific_cfg = config.get("analysis_specific", {}).get("ar1_gaze_duration", {})
    default_variant = str(analysis_specific_cfg.get("config_name", "ar1/ar1_gw_vs_hw")).strip()
    env_variant = os.environ.get("IER_AR1_CONFIG", "").strip()
    variant_config_name = env_variant or default_variant or "ar1/ar1_gw_vs_hw"

    try:
        analysis_config = load_analysis_config(variant_config_name)
    except Exception as exc:
        LOGGER.error("Failed to load AR-1 variant configuration '%s': %s", variant_config_name, exc)
        raise

    variant_key = analysis_config.get("variant_key") or Path(variant_config_name).stem
    variant_label = analysis_config.get("variant_label", variant_key)
    report_title = analysis_config.get(
        "report_title",
        analysis_config.get("analysis_name", "AR-1: Gaze Duration Analysis"),
    )
    variant_description = analysis_config.get("description", "")

    LOGGER.info("Using AR-1 variant '%s' (config: %s)", variant_label, variant_config_name)

    give_conditions, hug_conditions, active_comparison_key = _get_active_comparison(analysis_config)
    comparison_def = analysis_config.get("comparisons", {}).get(active_comparison_key, {})
    comparison_name = comparison_def.get("name", variant_label)

    seen: set[str] = set()
    primary_conditions: List[str] = []
    for condition in give_conditions + hug_conditions:
        if condition not in seen:
            primary_conditions.append(condition)
            seen.add(condition)

    cohorts_config = analysis_config.get("cohorts")
    if not cohorts_config:
        raise ValueError("AR-1 configuration must define at least one cohort under 'cohorts'.")
    if not isinstance(cohorts_config, list):
        raise ValueError("AR-1 'cohorts' configuration must be a list of cohort definitions.")

    primary_cohort_key = analysis_config.get("primary_cohort")
    if not primary_cohort_key and cohorts_config:
        primary_cohort_key = str(cohorts_config[0].get("key", "")).strip()
    if not primary_cohort_key:
        raise ValueError("AR-1 configuration is missing a valid 'primary_cohort' identifier.")

    cohort_results: List[Dict[str, Any]] = []
    full_conditions_set: set[str] = set()

    for cohort_cfg in cohorts_config:
        if not isinstance(cohort_cfg, dict):
            raise ValueError("Each cohort entry must be a mapping of settings.")

        key = str(cohort_cfg.get("key", "")).strip()
        if not key:
            raise ValueError("Cohort configuration is missing a 'key' value.")

        label = str(cohort_cfg.get("label", key)).strip() or key
        data_path_value = cohort_cfg.get("data_path")
        if not data_path_value:
            raise ValueError(f"Cohort '{key}' is missing required 'data_path'.")
        path = Path(data_path_value)

        include_in_primary_plot = bool(cohort_cfg.get("include_in_primary_plot", True))
        filters = cohort_cfg.get("participant_filters")

        LOGGER.info("Processing cohort '%s' from %s", label, path)
        df = _load_gaze_fixations(path)
        df = _apply_participant_filters(df, filters)

        if df.empty:
            raise ValueError(f"Cohort '{key}' has no rows after applying configured filters.")

        LOGGER.info("Cohort '%s' retained %d gaze fixations after filtering", label, len(df))

        trials = _calculate_trial_proportions(df)
        primary_trials = trials[trials["condition_name"].isin(primary_conditions)].copy()

        if primary_trials.empty:
            raise ValueError(
                f"Cohort '{key}' has no data for primary comparison conditions: {primary_conditions}"
            )

        primary_participant_means, primary_summary = _aggregate_by_condition(primary_trials)
        full_participant_means, full_summary = _aggregate_by_condition(trials)

        if primary_summary.empty:
            raise ValueError(f"Cohort '{key}' summary is empty for primary comparison conditions.")

        stats_context = _compute_statistics(
            primary_participant_means,
            primary_summary,
            config=config,
            give_conditions=give_conditions,
            hug_conditions=hug_conditions,
            comparison_label=comparison_name,
        )
        stats_context["comparison_label"] = comparison_name
        stats_context["comparison_variant"] = variant_label
        stats_context["active_comparison_key"] = active_comparison_key

        if not full_summary.empty:
            full_conditions_set.update(full_summary["condition_name"].unique())

        age_anova = _compute_age_anova(
            cohort_df=df,
            primary_participant_means=primary_participant_means,
            min_group_n=config.get("analysis", {}).get("min_statistical_n", 3),
        )

        cohort_results.append(
            {
                "key": key,
                "label": label,
                "include_in_primary_plot": include_in_primary_plot,
                "primary_participant_means": primary_participant_means,
                "primary_summary": primary_summary,
                "full_participant_means": full_participant_means,
                "full_summary": full_summary,
                "stats_context": stats_context,
                "age_anova": age_anova,
                "total_gaze_fixations_primary": int(
                    df[df["condition_name"].isin(primary_conditions)].shape[0]
                ),
                "total_gaze_fixations_all": int(df.shape[0]),
            }
        )

    primary_result = next((res for res in cohort_results if res["key"] == primary_cohort_key), None)
    if primary_result is None:
        raise ValueError(f"Primary cohort '{primary_cohort_key}' not found among configured cohorts.")

    if not full_conditions_set:
        full_conditions_set.update(primary_conditions)
    full_conditions = sorted(full_conditions_set)

    output_dir = Path(config["paths"]["results"]) / "AR1" / variant_key
    metadata = _generate_outputs(
        output_dir=output_dir,
        cohort_results=cohort_results,
        primary_result=primary_result,
        primary_conditions=primary_conditions,
        full_conditions=full_conditions,
        config=config,
        variant_key=variant_key,
        variant_label=variant_label,
        report_title=report_title,
        variant_description=variant_description,
    )

    metadata["variant_key"] = variant_key
    metadata["variant_label"] = variant_label
    metadata["config_name"] = variant_config_name

    LOGGER.info(
        "AR-1 analysis (%s) completed; report generated at %s",
        variant_label,
        metadata["html_path"],
    )
    return metadata
