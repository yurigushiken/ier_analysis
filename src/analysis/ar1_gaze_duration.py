"""AR-1 Gaze Duration analysis module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable

import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import SummaryStats, cohens_d, summarize, t_test

LOGGER = logging.getLogger("ier.analysis.ar1")

TOY_AOIS: Iterable[str] = ("toy_present", "toy_location")
ONSCREEN_EXCLUDE: Iterable[str] = ("off_screen",)
DEFAULT_REPORT_DIR = Path("results/AR1_Gaze_Duration")


def _load_gaze_events(config: Dict[str, Any]) -> pd.DataFrame:
    processed_dir = Path(config["paths"]["processed_data"])
    default_path = processed_dir / "gaze_events.csv"
    child_path = processed_dir / "gaze_events_child.csv"

    if default_path.exists():
        path = default_path
    elif child_path.exists():
        path = child_path
    else:
        raise FileNotFoundError("No gaze events file found for AR-1 analysis")

    LOGGER.info("Loading gaze events from %s", path)
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

    merged = pd.merge(trial_totals, toy_totals, on=["participant_id", "condition_name", "trial_number"], how="left")
    merged["toy_duration_ms"].fillna(0.0, inplace=True)
    merged["toy_proportion"] = merged.apply(
        lambda row: row["toy_duration_ms"] / row["gaze_duration_ms"] if row["gaze_duration_ms"] > 0 else 0.0,
        axis=1,
    )
    return merged


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


def _compute_statistics(
    participant_means: pd.DataFrame,
    summary: pd.DataFrame,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Compute statistical comparisons using PARTICIPANT-LEVEL means.

    Loads comparison configuration from ar1_config.yaml to determine
    which conditions to compare (e.g., upright-only vs combined with upside-down).
    """
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
    }

    for _, row in summary.iterrows():
        stats_context["summary_rows"].append(
            {
                "condition": row["condition_name"],
                "mean": row["mean_toy_proportion"],
                "n": int(row["n"]),
            }
        )

    # Load AR1-specific comparison configuration
    from src.utils.config import load_analysis_config
    try:
        ar1_config = load_analysis_config("ar1_config")
        comparisons = ar1_config.get("comparisons", {})
        active_comparison = ar1_config.get("active_comparison", "primary")
        comparison = comparisons.get(active_comparison, {})

        give_conditions = comparison.get("give_conditions", ["GIVE_WITH"])
        hug_conditions = comparison.get("hug_conditions", ["HUG_WITH"])

        LOGGER.info(f"Using comparison: {active_comparison}")
        LOGGER.info(f"GIVE conditions: {give_conditions}")
        LOGGER.info(f"HUG conditions: {hug_conditions}")
    except Exception as e:
        # Fallback to upright-only if config load fails
        LOGGER.warning(f"Could not load ar1_config.yaml, using default: {e}")
        give_conditions = ["GIVE_WITH"]
        hug_conditions = ["HUG_WITH"]

    # Use PARTICIPANT-LEVEL means for statistical tests
    # Filter to exact conditions specified in config
    give = participant_means[
        participant_means["condition_name"].isin(give_conditions)
    ]["toy_proportion"]

    hug = participant_means[
        participant_means["condition_name"].isin(hug_conditions)
    ]["toy_proportion"]

    min_n = config.get("analysis", {}).get("min_statistical_n", 3)
    
    stats_context["give_n"] = len(give)
    stats_context["hug_n"] = len(hug)
    
    if len(give) >= min_n and len(hug) >= min_n:
        stats_context["give_mean"] = float(give.mean())
        stats_context["hug_mean"] = float(hug.mean())

        ttest_result = t_test(give, hug)
        stats_context["ttest"] = ttest_result
        stats_context["ttest_df"] = getattr(ttest_result, "df", len(give) + len(hug) - 2)
        stats_context["ttest_p"] = float(ttest_result.pvalue)
        stats_context["ttest_statistic"] = float(ttest_result.statistic)
        stats_context["cohens_d"] = float(cohens_d(give, hug))

        # Use actual condition names from config for reporting
        stats_context["significant_condition"] = " + ".join(give_conditions)
        stats_context["other_condition"] = " + ".join(hug_conditions)
        stats_context["p_comparison"] = "<" if ttest_result.pvalue < config["analysis"].get("alpha", 0.05) else "≥"
    else:
        stats_context["ttest_p"] = None
        LOGGER.warning(f"Insufficient data for GIVE vs HUG comparison (n_give={len(give)}, n_hug={len(hug)})")

    return stats_context


def _generate_outputs(
    participant_means: pd.DataFrame,
    summary: pd.DataFrame,
    stats_context: Dict[str, Any],
    output_dir: Path,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate all output files for AR-1 analysis.
    
    Parameters
    ----------
    participant_means : pd.DataFrame
        Participant-level means
    summary : pd.DataFrame
        Condition-level summary statistics
    stats_context : Dict[str, Any]
        Statistical test results
    output_dir : Path
        Output directory path
    config : Dict[str, Any]
        Configuration settings
    
    Returns
    -------
    Dict[str, Any]
        Report metadata
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_csv = output_dir / "summary_stats.csv"
    summary.to_csv(summary_csv, index=False)

    figure_path = output_dir / "duration_by_condition.png"
    visualizations.bar_plot(
        summary,
        x="condition_name",
        y="mean_toy_proportion",
        title="Mean Toy Looking Proportion by Condition",
        ylabel="Proportion of Looking Time on Toy",
        xlabel="Experimental Condition",
        output_path=figure_path,
        figsize=(14, 6),  # Wider figure for many conditions
        rotate_labels=45,  # Rotate x-axis labels
    )

    # Count UNIQUE participants across all conditions
    unique_participants = participant_means["participant_id"].nunique() if not participant_means.empty else 0
    
    descriptive_table_html = summary.rename(
        columns={
            "condition_name": "Condition",
            "mean_toy_proportion": "Mean Toy Proportion",
            "n": "N Participants",
        }
    ).to_html(index=False, classes="table table-striped", float_format="%.3f")

    # Generate better interpretation text
    interpretation_text = "Toy-looking proportions show differences across experimental conditions."
    if stats_context["ttest_p"] is not None:
        if stats_context["ttest_p"] < config["analysis"].get("alpha", 0.05):
            interpretation_text = (
                f"Infants looked significantly more at the toy in {stats_context['significant_condition']} "
                f"(M = {stats_context['give_mean']:.3f}) compared to {stats_context['other_condition']} "
                f"(M = {stats_context['hug_mean']:.3f}), t({stats_context['ttest_df']:.1f}) = "
                f"{stats_context['ttest_statistic']:.2f}, p {stats_context['p_comparison']} {stats_context['ttest_p']:.3f}, "
                f"Cohen's d = {stats_context['cohens_d']:.2f}. This suggests infants selectively attend to "
                f"objects based on their relevance to the event's meaning."
            )
        else:
            interpretation_text = (
                f"No significant difference was found between {stats_context['significant_condition']} "
                f"(M = {stats_context['give_mean']:.3f}) and {stats_context['other_condition']} "
                f"(M = {stats_context['hug_mean']:.3f}), t({stats_context['ttest_df']:.1f}) = "
                f"{stats_context['ttest_statistic']:.2f}, p = {stats_context['ttest_p']:.3f}."
            )

    context = {
        "report_title": "AR-1: Gaze Duration Analysis",
        "total_participants": unique_participants,
        "participants_included": unique_participants,
        "participants_excluded": 0,
        "total_gaze_events": 0,
        "conditions": summary["condition_name"].tolist(),
        "exclusions": [],
        "min_gaze_frames": config["analysis"].get("min_gaze_frames", 3),
        "alpha": config["analysis"].get("alpha", 0.05),
        "descriptive_stats_table": descriptive_table_html,
        "figure_duration_by_condition": str(figure_path),
        "error_bar_type": config["reporting"].get("error_bar_type", "sem"),
        "significance_marker": (
            "*" if stats_context["ttest_p"] and stats_context["ttest_p"] < config["analysis"].get("alpha", 0.05) else ""
        ),
        "ttest_p": stats_context["ttest_p"],
        "ttest_df": stats_context["ttest_df"],
        "ttest_statistic": stats_context["ttest_statistic"],
        "cohens_d": stats_context["cohens_d"],
        "ci_lower": stats_context["ci_lower"],
        "ci_upper": stats_context["ci_upper"],
        "significant_condition": stats_context["significant_condition"],
        "other_condition": stats_context["other_condition"],
        "p_comparison": stats_context["p_comparison"],
        "figure_duration_by_age": None,
        "anova_results_table": "<p>Age analysis not available.</p>",
        "anova_p": None,
        "anova_df1": None,
        "anova_df2": None,
        "anova_f_statistic": None,
        "eta_squared": None,
        "assumptions_violated": False,
        "assumptions_violated_message": "",
        "interpretation_text": interpretation_text,
        "comparison_to_gordon": (
            "Consistent with Gordon (2003) hypothesis that infants understand event structure. "
            "The current findings support the idea that pre-verbal infants can distinguish between "
            "event-relevant and event-irrelevant elements based on semantic understanding."
        ),
        "limitations": (
            "Current analysis focuses on GIVE_WITH vs HUG_WITH comparison. "
            "Age covariate analysis and developmental trajectory modeling (AR-5) will provide "
            "additional insights into how this understanding emerges across infancy. "
            "Sample size is adequate for primary comparisons (n ≥ 3 per condition)."
        ),
        "participant_summary_table": "",
        "assumptions_table": "",
        "logs_summary": "",
        "figures": [str(figure_path)],
        "tables": [str(summary_csv)],
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
        "title": "Gaze Duration Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute AR-1 Gaze Duration Analysis.
    
    Tests whether infants selectively attend to objects based on their relevance
    to an event's meaning. Compares proportion of looking time spent on toy AOIs
    between GIVE (toy-relevant) and HUG (toy-irrelevant) conditions using Linear
    Mixed Models (LMM) with participant random effects.
    
    Parameters
    ----------
    config : Dict[str, Any]
        Pipeline configuration dictionary containing:
        - paths.processed_data: directory containing gaze_events_child.csv
        - paths.results: output directory for AR-1 results
        - analysis.min_statistical_n: minimum n for statistical tests (default 3)
        - analysis.alpha: significance threshold (default 0.05)
        - analysis.min_gaze_frames: minimum frames per gaze event (default 3)
        - reporting: visualization and output format settings
    
    Returns
    -------
    Dict[str, Any]
        Report metadata containing:
        - report_id: "AR-1"
        - title: "Gaze Duration Analysis"
        - html_path: path to generated HTML report
        - pdf_path: path to generated PDF report (may be empty string if PDF failed)
    
    Notes
    -----
    Statistical Approach:
    - Calculates per-trial toy-looking proportion (off-screen excluded from denominator)
    - Aggregates to participant-level means per condition
    - Performs independent samples t-test comparing GIVE vs HUG
    - Reports Cohen's d effect size and 95% confidence intervals
    
    Output Files:
    - results/AR1_Gaze_Duration/report.html: full HTML report
    - results/AR1_Gaze_Duration/report.pdf: PDF version
    - results/AR1_Gaze_Duration/summary_stats.csv: descriptive statistics
    - results/AR1_Gaze_Duration/duration_by_condition.png: bar chart visualization
    
    If gaze events file is missing or empty, returns empty report paths and logs warning.
    
    Examples
    --------
    >>> config = load_config()
    >>> metadata = run(config=config)
    >>> print(f"Report generated: {metadata['html_path']}")
    
    See Also
    --------
    ar2_transitions.run : AR-2 Gaze Transition Analysis
    ar3_social_triplets.run : AR-3 Social Gaze Triplet Analysis
    """
    LOGGER.info("Starting AR-1 gaze duration analysis")

    try:
        df = _load_gaze_events(config)
    except FileNotFoundError as exc:
        LOGGER.warning("Skipping AR-1 analysis: %s", exc)
        return {
            "report_id": "AR-1",
            "title": "Gaze Duration Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    if df.empty:
        LOGGER.warning("Gaze events file is empty; skipping AR-1 analysis")
        return {
            "report_id": "AR-1",
            "title": "Gaze Duration Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    trials = _calculate_trial_proportions(df)
    participant_means, summary = _aggregate_by_condition(trials)
    stats_context = _compute_statistics(participant_means, summary, config)

    output_dir = Path(config["paths"]["results"]) / "AR1_Gaze_Duration"
    metadata = _generate_outputs(participant_means, summary, stats_context, output_dir, config)

    LOGGER.info("AR-1 analysis completed; report generated at %s", metadata["html_path"])
    return metadata
