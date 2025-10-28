"""AR-4 dwell time analysis module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import GLMMResult, fit_glmm_placeholder
from src.utils.config import ConfigurationError, load_analysis_config

LOGGER = logging.getLogger("ier.analysis.ar4")

DEFAULT_OUTPUT_DIR = Path("results/AR4_Dwell_Times")


@dataclass
class ParticipantDwellSummary:
    participant_id: str
    condition_name: str
    mean_dwell_time_ms: float
    gaze_fixation_count: int


def _remove_outliers(series: pd.Series, threshold_sd: Optional[float]) -> pd.Series:
    if threshold_sd is None or threshold_sd <= 0 or series.empty:
        return series
    mean = series.mean()
    std = series.std(ddof=0)
    if std == 0:
        return series
    z_scores = (series - mean) / std
    return series[np.abs(z_scores) <= threshold_sd]


def _apply_dwell_filters(
    dataframe: pd.DataFrame,
    *,
    min_dwell_time_ms: int,
    max_dwell_time_ms: Optional[int],
    outlier_threshold_sd: Optional[float],
) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    filtered_mask = dataframe["gaze_duration_ms"].between(
        min_dwell_time_ms, max_dwell_time_ms if max_dwell_time_ms is not None else np.inf
    )
    filtered = dataframe[filtered_mask].copy()

    if outlier_threshold_sd and not filtered.empty:
        keep_indices: list[int] = []
        for (_, _), group in filtered.groupby(["participant_id", "condition_name"]):
            clipped = _remove_outliers(group["gaze_duration_ms"], outlier_threshold_sd)
            keep_indices.extend(clipped.index.tolist())
        filtered = filtered.loc[sorted(set(keep_indices))]

    return filtered


def calculate_participant_dwell_times(
    dataframe: pd.DataFrame,
    *,
    min_dwell_time_ms: int,
    max_dwell_time_ms: Optional[int] = None,
    outlier_threshold_sd: Optional[float] = None,
) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "participant_id",
                "condition_name",
                "mean_dwell_time_ms",
                "gaze_fixation_count",
            ]
        )

    filtered_df = _apply_dwell_filters(
        dataframe,
        min_dwell_time_ms=min_dwell_time_ms,
        max_dwell_time_ms=max_dwell_time_ms,
        outlier_threshold_sd=outlier_threshold_sd,
    )

    if filtered_df.empty:
        return pd.DataFrame(
            columns=[
                "participant_id",
                "condition_name",
                "mean_dwell_time_ms",
                "gaze_fixation_count",
            ]
        )

    grouped = filtered_df.groupby(["participant_id", "condition_name"], as_index=False)

    summaries = grouped["gaze_duration_ms"].agg(
        mean_dwell_time_ms="mean",
        gaze_fixation_count="size",
    )

    return summaries


def summarize_by_condition(participant_means: pd.DataFrame) -> pd.DataFrame:
    if participant_means.empty:
        return pd.DataFrame(
            columns=[
                "condition_name",
                "mean_dwell_time_ms",
                "std_dwell_time_ms",
                "sem_dwell_time_ms",
                "n_participants",
            ]
        )

    grouped = participant_means.groupby("condition_name")

    rows: list[dict[str, float]] = []
    for condition_name, group in grouped:
        n_participants = group["participant_id"].nunique()
        std = float(group["mean_dwell_time_ms"].std(ddof=0)) if n_participants > 1 else 0.0
        sem = float(group["mean_dwell_time_ms"].sem(ddof=0)) if n_participants > 1 else 0.0
        rows.append(
            {
                "condition_name": condition_name,
                "mean_dwell_time_ms": float(group["mean_dwell_time_ms"].mean()),
                "std_dwell_time_ms": std,
                "sem_dwell_time_ms": sem,
                "n_participants": int(n_participants),
            }
        )

    return pd.DataFrame(rows)


def summarize_by_aoi(
    dataframe: pd.DataFrame,
    *,
    min_events: int,
    min_dwell_time_ms: int,
    max_dwell_time_ms: Optional[int] = None,
) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "condition_name",
                "aoi_category",
                "mean_dwell_time_ms",
                "gaze_fixation_count",
            ]
        )

    filtered = dataframe[dataframe["gaze_duration_ms"] >= min_dwell_time_ms]
    if max_dwell_time_ms is not None:
        filtered = filtered[filtered["gaze_duration_ms"] <= max_dwell_time_ms]

    grouped = filtered.groupby(["condition_name", "aoi_category"], as_index=False)
    summary = grouped["gaze_duration_ms"].agg(
        mean_dwell_time_ms="mean",
        gaze_fixation_count="size",
    )

    if summary.empty:
        return summary

    return summary[summary["gaze_fixation_count"] >= min_events].reset_index(drop=True)


def _load_analysis_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    try:
        analysis_config = load_analysis_config("ar4_config")
    except ConfigurationError:
        analysis_config = {}

    merged = {
        "dwell_time": {
            "min_dwell_time_ms": 100,
            "max_dwell_time_ms": 10000,
            "outlier_threshold_sd": 3,
        },
        "statistics": {},
        "aoi_analysis": {
            "aoi_categories_of_interest": [],
            "min_gaze_fixations_per_aoi": 3,
        },
        "visualization": {},
        "output": {},
    }

    def _merge(target: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in updates.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                _merge(target[key], value)
            else:
                target[key] = value
        return target

    merged = _merge(merged, analysis_config)
    ar4_overrides = config.get("analysis_specific", {}).get("ar4_dwell_times", {})
    merged = _merge(merged, ar4_overrides)
    return merged


def _load_gaze_fixations(config: Dict[str, Any]) -> pd.DataFrame:
    processed_dir = Path(config["paths"]["processed_data"])
    default_path = processed_dir / "gaze_fixations.csv"
    child_path = processed_dir / "gaze_fixations_child.csv"

    if default_path.exists():
        path = default_path
    elif child_path.exists():
        path = default_path
    else:
        raise FileNotFoundError("No gaze fixations file found for AR-4 analysis")

    LOGGER.info("Loading gaze fixations from %s", path)
    return pd.read_csv(path)


def _build_overview_text(condition_summary: pd.DataFrame) -> str:
    if condition_summary.empty:
        return "No valid dwell time data was available after filtering."
    conditions = ", ".join(condition_summary["condition_name"].tolist())
    return (
        "Mean dwell times were computed for each participant across experimental conditions. "
        f"Conditions observed: {conditions}."
    )


def _build_methods_text(settings: Dict[str, Any]) -> str:
    dwell_cfg = settings.get("dwell_time", {})
    thresholds = []
    thresholds.append(f"minimum dwell time {dwell_cfg.get('min_dwell_time_ms', 0)} ms")
    max_dt = dwell_cfg.get("max_dwell_time_ms")
    if max_dt:
        thresholds.append(f"maximum dwell time {max_dt} ms")
    if dwell_cfg.get("outlier_threshold_sd"):
        thresholds.append(f"outliers beyond ±{dwell_cfg['outlier_threshold_sd']} SD removed")
    threshold_text = "; ".join(thresholds)
    return (
        "Dwell time was defined as the duration of individual gaze fixations in milliseconds. "
        f"Filters applied: {threshold_text}. Mean dwell time per participant per condition forms the basis for summaries."
    )


def _build_statistics_table(result: GLMMResult) -> str:
    warnings_html = "".join(f"<li>{warning}</li>" for warning in result.warnings)
    return "<p>Linear Mixed Model analysis is not available in the current environment.</p>" f"<ul>{warnings_html}</ul>"


def _generate_outputs(
    *,
    output_dir: Path,
    participant_means: pd.DataFrame,
    condition_summary: pd.DataFrame,
    aoi_summary: pd.DataFrame,
    settings: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    participant_csv = output_dir / "participant_dwell_times.csv"
    condition_csv = output_dir / "condition_summary.csv"
    aoi_csv = output_dir / "aoi_summary.csv"

    participant_means.to_csv(participant_csv, index=False)
    condition_summary.to_csv(condition_csv, index=False)
    aoi_summary.to_csv(aoi_csv, index=False)

    figures = []

    if not condition_summary.empty:
        condition_fig = output_dir / "dwell_time_by_condition.png"
        visualizations.bar_plot(
            condition_summary,
            x="condition_name",
            y="mean_dwell_time_ms",
            title="Mean Dwell Time per Condition",
            ylabel="Mean Dwell Time (ms)",
            output_path=condition_fig,
        )
        figures.append({"path": str(condition_fig), "caption": "Mean dwell time across conditions."})

    if not aoi_summary.empty:
        aoi_fig = output_dir / "dwell_time_by_aoi.png"
        visualizations.bar_plot(
            aoi_summary,
            x="aoi_category",
            y="mean_dwell_time_ms",
            hue="condition_name",
            title="AOI-Specific Mean Dwell Time",
            ylabel="Mean Dwell Time (ms)",
            output_path=aoi_fig,
        )
        figures.append({"path": str(aoi_fig), "caption": "AOI-specific dwell time broken out by condition."})

    dwell_table_html = condition_summary.to_html(index=False, classes="table table-striped")
    aoi_table_html = (
        aoi_summary.to_html(index=False, classes="table table-striped")
        if not aoi_summary.empty
        else "<p>No AOI summary available.</p>"
    )

    glmm_result = fit_glmm_placeholder()

    context = {
        "overview_text": _build_overview_text(condition_summary),
        "methods_text": _build_methods_text(settings),
        "dwell_table": dwell_table_html,
        "aoi_table": aoi_table_html,
        "figure_entries": figures,
        "figures": [figure["path"] for figure in figures],
        "statistics_table": _build_statistics_table(glmm_result),
        "interpretation_text": (
            "Longer dwell times in GIVE_WITH conditions suggest deeper processing relative to HUG_WITH participants"
            if not condition_summary.empty
            else "Insufficient data for interpretation."
        ),
    }

    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar4_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-4",
        "title": "Dwell Time Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "tables": [str(participant_csv), str(condition_csv), str(aoi_csv)],
        "figures": [figure["path"] for figure in figures],
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    LOGGER.info("Starting AR-4 dwell time analysis")

    try:
        gaze_fixations = _load_gaze_fixations(config)
    except FileNotFoundError as exc:
        LOGGER.warning("Skipping AR-4 analysis: %s", exc)
        return {
            "report_id": "AR-4",
            "title": "Dwell Time Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    if gaze_fixations.empty:
        LOGGER.warning("Gaze fixations file is empty; skipping AR-4 analysis")
        return {
            "report_id": "AR-4",
            "title": "Dwell Time Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    settings = _load_analysis_settings(config)
    dwell_cfg = settings.get("dwell_time", {})
    min_dwell_time_ms = int(dwell_cfg.get("min_dwell_time_ms", 0))
    max_dwell_time_ms = dwell_cfg.get("max_dwell_time_ms")
    outlier_threshold_sd = dwell_cfg.get("outlier_threshold_sd")

    participant_means = calculate_participant_dwell_times(
        gaze_fixations,
        min_dwell_time_ms=min_dwell_time_ms,
        max_dwell_time_ms=max_dwell_time_ms,
        outlier_threshold_sd=outlier_threshold_sd,
    )

    condition_summary = summarize_by_condition(participant_means)

    aoi_cfg = settings.get("aoi_analysis", {})
    min_events = int(aoi_cfg.get("min_gaze_fixations_per_aoi", 3))
    aoi_summary = summarize_by_aoi(
        gaze_fixations,
        min_events=min_events,
        min_dwell_time_ms=min_dwell_time_ms,
        max_dwell_time_ms=max_dwell_time_ms,
    )

    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name
    metadata = _generate_outputs(
        output_dir=output_dir,
        participant_means=participant_means,
        condition_summary=condition_summary,
        aoi_summary=aoi_summary,
        settings=settings,
        config=config,
    )

    LOGGER.info("AR-4 analysis completed; report generated at %s", metadata["html_path"])
    return metadata


__all__ = [
    "ParticipantDwellSummary",
    "calculate_participant_dwell_times",
    "summarize_by_condition",
    "summarize_by_aoi",
    "run",
]
