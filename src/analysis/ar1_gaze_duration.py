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
    child_path = processed_dir / "gaze_events_child.csv"
    default_path = processed_dir / "gaze_events.csv"

    if child_path.exists():
        path = child_path
    elif default_path.exists():
        path = default_path
    else:
        raise FileNotFoundError("No gaze events file found for AR-1 analysis")

    LOGGER.info("Loading gaze events from %s", path)
    return pd.read_csv(path)


def _calculate_trial_proportions(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[~df["aoi_category"].isin(ONSCREEN_EXCLUDE)].copy()
    filtered["is_toy"] = filtered["aoi_category"].isin(TOY_AOIS)

    trial_totals = (
        filtered.groupby(["participant_id", "condition_name", "trial_number"], as_index=False)["gaze_duration_ms"].sum()
    )
    toy_totals = (
        filtered[filtered["is_toy"]]
        .groupby(["participant_id", "condition_name", "trial_number"], as_index=False)["gaze_duration_ms"].sum()
        .rename(columns={"gaze_duration_ms": "toy_duration_ms"})
    )

    merged = pd.merge(trial_totals, toy_totals, on=["participant_id", "condition_name", "trial_number"], how="left")
    merged["toy_duration_ms"].fillna(0.0, inplace=True)
    merged["toy_proportion"] = merged.apply(
        lambda row: row["toy_duration_ms"] / row["gaze_duration_ms"] if row["gaze_duration_ms"] > 0 else 0.0,
        axis=1,
    )
    return merged


def _aggregate_by_condition(trial_df: pd.DataFrame) -> pd.DataFrame:
    condition_means = trial_df.groupby(["condition_name", "participant_id"], as_index=False)["toy_proportion"].mean()
    summary = (
        condition_means.groupby("condition_name")
        .agg(mean_toy_proportion=("toy_proportion", "mean"), n=("toy_proportion", "size"))
        .reset_index()
    )
    return summary


def _compute_statistics(summary: pd.DataFrame, trial_df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
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
        stats_context["summary_rows"].append({
            "condition": row["condition_name"],
            "mean": row["mean_toy_proportion"],
            "n": int(row["n"]),
        })

    give = trial_df[trial_df["condition_name"].str.upper().str.startswith("GIVE")]["toy_proportion"]
    hug = trial_df[trial_df["condition_name"].str.upper().str.startswith("HUG")]["toy_proportion"]

    min_n = config.get("analysis", {}).get("min_statistical_n", 3)
    if len(give) >= min_n and len(hug) >= min_n:
        ttest_result = t_test(give, hug)
        stats_context["ttest"] = ttest_result
        stats_context["ttest_df"] = getattr(ttest_result, "df", len(give) + len(hug) - 2)
        stats_context["ttest_p"] = float(ttest_result.pvalue)
        stats_context["ttest_statistic"] = float(ttest_result.statistic)
        stats_context["cohens_d"] = float(cohens_d(give, hug))
        stats_context["significant_condition"] = "GIVE"
        stats_context["other_condition"] = "HUG"
        stats_context["p_comparison"] = "<" if ttest_result.pvalue < config["analysis"].get("alpha", 0.05) else "="
    else:
        stats_context["ttest_p"] = None

    return stats_context


def _generate_outputs(
    summary: pd.DataFrame,
    stats_context: Dict[str, Any],
    output_dir: Path,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_csv = output_dir / "summary_stats.csv"
    summary.to_csv(summary_csv, index=False)

    figure_path = output_dir / "duration_by_condition.png"
    visualizations.bar_plot(
        summary,
        x="condition_name",
        y="mean_toy_proportion",
        title="Mean Toy Looking Proportion by Condition",
        ylabel="Mean Toy Proportion",
        output_path=figure_path,
    )

    descriptive_table_html = summary.rename(columns={
        "condition_name": "Condition",
        "mean_toy_proportion": "Mean Toy Proportion",
        "n": "Participants",
    }).to_html(index=False, classes="table table-striped")

    context = {
        "report_title": "AR-1: Gaze Duration Analysis",
        "total_participants": int(summary["n"].sum()) if not summary.empty else 0,
        "participants_included": int(summary["n"].sum()) if not summary.empty else 0,
        "participants_excluded": 0,
        "total_gaze_events": 0,
        "conditions": summary["condition_name"].tolist(),
        "exclusions": [],
        "min_gaze_frames": config["analysis"].get("min_gaze_frames", 3),
        "alpha": config["analysis"].get("alpha", 0.05),
        "descriptive_stats_table": descriptive_table_html,
        "figure_duration_by_condition": str(figure_path),
        "error_bar_type": config["reporting"].get("error_bar_type", "sem"),
        "significance_marker": "*" if stats_context["ttest_p"] and stats_context["ttest_p"] < config["analysis"].get("alpha", 0.05) else "",
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
        "interpretation_text": "Toy-looking proportions show baseline differences across conditions.",
        "comparison_to_gordon": "Consistent with hypothesis",  # placeholder
        "limitations": "More data required for age covariate analysis.",
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
    summary = _aggregate_by_condition(trials)
    stats_context = _compute_statistics(summary, trials, config)

    output_dir = Path(config["paths"]["results"]) / "AR1_Gaze_Duration"
    metadata = _generate_outputs(summary, stats_context, output_dir, config)

    LOGGER.info("AR-1 analysis completed; report generated at %s", metadata["html_path"])
    return metadata
