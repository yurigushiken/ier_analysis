"""AR-4 dwell time analysis module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import GLMMResult, fit_linear_mixed_model
from src.utils.config import ConfigurationError, load_analysis_config

LOGGER = logging.getLogger("ier.analysis.ar4")

DEFAULT_OUTPUT_DIR = Path("results/AR4_dwell_times")

EXCLUDE_AOIS: Iterable[str] = ("screen_nonAOI", "off_screen")


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
    include_aoi: bool = False,
    valid_aoi_categories: Optional[Iterable[str]] = None,
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

    working = dataframe.copy()

    has_aoi = "aoi_category" in working.columns
    if has_aoi:
        working = working[~working["aoi_category"].isin(EXCLUDE_AOIS)]

        if valid_aoi_categories is not None:
            allowed = {str(item) for item in valid_aoi_categories}
            working = working[working["aoi_category"].isin(allowed)]

    include_aoi = include_aoi and has_aoi

    if include_aoi:
        if not has_aoi:
            raise KeyError("AR-4 analysis requires 'aoi_category' column when include_aoi=True")

    filtered_df = _apply_dwell_filters(
        working,
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

    group_keys = ["participant_id", "condition_name"]
    if include_aoi:
        group_keys.append("aoi_category")

    grouped = filtered_df.groupby(group_keys, as_index=False)

    summaries = grouped["gaze_duration_ms"].agg(
        mean_dwell_time_ms="mean",
        total_dwell_time_ms="sum",
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
    allowed_categories: Optional[Iterable[str]] = None,
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

    if allowed_categories is not None:
        allowed = {str(item) for item in allowed_categories}
        filtered = filtered[filtered["aoi_category"].isin(allowed)]

    grouped = filtered.groupby(["condition_name", "aoi_category"], as_index=False)
    summary = grouped["gaze_duration_ms"].agg(
        mean_dwell_time_ms="mean",
        gaze_fixation_count="size",
    )

    if summary.empty:
        return summary

    return summary[summary["gaze_fixation_count"] >= min_events].reset_index(drop=True)


def _load_analysis_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    base_config: Dict[str, Any]
    try:
        base_config = load_analysis_config("AR4_dwell_times/ar4_config")
    except ConfigurationError:
        base_config = {}

    analysis_specific = config.get("analysis_specific", {}).get("ar4_dwell_times", {})
    variant_name = analysis_specific.get("config_name", "AR4_dwell_times/ar4_gw_vs_gwo")

    try:
        variant_config = load_analysis_config(variant_name)
    except ConfigurationError as exc:
        raise ConfigurationError(f"Failed to load AR-4 variant configuration '{variant_name}': {exc}") from exc

    def _merge(target: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in updates.items():
            if isinstance(target.get(key), dict) and isinstance(value, dict):
                _merge(target[key], value)
            else:
                target[key] = value
        return target

    merged: Dict[str, Any] = {
        "variant_name": variant_name,
        "recording": {},
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

    _merge(merged, base_config)
    _merge(merged, variant_config)
    _merge(merged, analysis_specific)
    return merged


def _resolve_dataset(path_value: str, processed_root: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path

    if path.parts and path.parts[0] == "data":
        repo_root = processed_root.parent.parent
        return (repo_root / path).resolve()

    return (processed_root / path).resolve()


def _load_gaze_fixations(config: Dict[str, Any], cohort_cfg: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    processed_root = Path(config["paths"]["processed_data"]).resolve()
    data_path_value = cohort_cfg.get("data_path")
    if not data_path_value:
        raise ValueError("Cohort configuration requires 'data_path'")

    raw_path = _resolve_dataset(data_path_value, processed_root)
    if not raw_path.exists():
        raise FileNotFoundError(f"Cohort dataset missing: {raw_path}")

    LOGGER.info("Loading cohort data from %s", raw_path)
    df = pd.read_csv(raw_path)
    metadata = {
        "path": raw_path,
        "label": cohort_cfg.get("label", cohort_cfg.get("key", "cohort")),
    }
    return df, metadata


def _build_overview_text(condition_summary: pd.DataFrame, *, cohort_labels: Iterable[str]) -> str:
    if condition_summary.empty:
        return "No valid dwell time data was available after filtering."
    conditions = ", ".join(condition_summary["condition_name"].tolist())
    return (
        "Mean dwell times were computed for each participant across experimental conditions. "
        f"Conditions observed: {conditions}. Cohorts analysed: {', '.join(cohort_labels)}."
    )


def _build_methods_text(settings: Dict[str, Any], *, segments: Iterable[str]) -> str:
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
        f"Segments analysed: {', '.join(segments)}. Filters applied: {threshold_text}. "
        "Mean dwell time per participant per condition forms the basis for summaries."
    )


def _build_statistics_table(result: GLMMResult) -> str:
    if result.converged and result.summary:
        warnings_html = "".join(f"<li>{warning}</li>" for warning in result.warnings)
        return (
            "<section class=\"statistics\">"
            f"<pre>{result.summary}</pre>"
            f"<ul>{warnings_html}</ul>"
            "</section>"
        )

    message = (
        "Linear mixed model fitting was skipped because statsmodels is not installed. "
        "Install statsmodels>=0.14 to enable this section."
    )
    extra_warnings = "".join(f"<li>{warning}</li>" for warning in result.warnings)
    return (
        "<section class=\"statistics warning\">"
        f"<p>{message}</p>"
        f"<ul>{extra_warnings}</ul>"
        "</section>"
    )


def _generate_outputs(
    *,
    output_dir: Path,
    participant_means: pd.DataFrame,
    condition_summary: pd.DataFrame,
    aoi_summary: pd.DataFrame,
    settings: Dict[str, Any],
    config: Dict[str, Any],
    cohort_labels: Iterable[str],
    recording: Dict[str, Any],
    statistics_result: GLMMResult,
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

        if settings.get("output", {}).get("include_violin_plot"):
            violin_fig = output_dir / "dwell_time_by_condition_violin.png"
            visualizations.violin_plot(
                condition_summary,
                x="condition_name",
                y="mean_dwell_time_ms",
                title="Dwell Time Distribution per Condition",
                output_path=violin_fig,
            )
            figures.append({"path": str(violin_fig), "caption": "Distribution of dwell times across conditions."})

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

        if settings.get("output", {}).get("include_violin_plot"):
            aoi_violin = output_dir / "dwell_time_by_aoi_violin.png"
            visualizations.violin_plot(
                aoi_summary,
                x="aoi_category",
                y="mean_dwell_time_ms",
                hue="condition_name",
                title="Dwell Time Distribution per AOI",
                output_path=aoi_violin,
            )
            figures.append({"path": str(aoi_violin), "caption": "Distribution of dwell times per AOI."})

    dwell_table_html = condition_summary.to_html(index=False, classes="table table-striped")
    aoi_table_html = (
        aoi_summary.to_html(index=False, classes="table table-striped")
        if not aoi_summary.empty
        else "<p>No AOI summary available.</p>"
    )

    context = {
        "overview_text": _build_overview_text(condition_summary, cohort_labels=cohort_labels),
        "methods_text": _build_methods_text(settings, segments=settings.get("segments", [])),
        "dwell_table": dwell_table_html,
        "aoi_table": aoi_table_html,
        "figure_entries": figures,
        "figures": [figure["path"] for figure in figures],
        "recording": recording,
        "statistics_table": _build_statistics_table(statistics_result),
        "interpretation_text": (
            "Longer dwell times in GIVE conditions suggest deeper processing relative to HUG conditions."
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

    settings = _load_analysis_settings(config)
    dwell_cfg = settings.get("dwell_time", {})
    min_dwell_time_ms = int(dwell_cfg.get("min_dwell_time_ms", 0))
    max_dwell_time_ms = dwell_cfg.get("max_dwell_time_ms")
    outlier_threshold_sd = dwell_cfg.get("outlier_threshold_sd")
    cohorts_cfg = settings.get("cohorts", [])
    if not cohorts_cfg:
        raise ValueError("AR-4 configuration must define at least one cohort.")

    include_segments = settings.get("segments", {}).get("include", [])

    all_participant_means: list[pd.DataFrame] = []
    cohort_labels: list[str] = []
    all_raw: list[pd.DataFrame] = []
    cohort_results: list[pd.DataFrame] = []

    for cohort_cfg in cohorts_cfg:
        try:
            gaze_fixations, metadata = _load_gaze_fixations(config, cohort_cfg)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping cohort due to missing data: %s", exc)
            continue

        filters = cohort_cfg.get("participant_filters")
        if filters:
            for column, allowed in filters.items():
                if column not in gaze_fixations.columns:
                    LOGGER.debug("Cohort %s missing column %s; skipping filter", metadata["label"], column)
                    continue
                values = allowed if isinstance(allowed, (list, tuple, set)) else [allowed]
                gaze_fixations = gaze_fixations[gaze_fixations[column].isin(values)]

        if include_segments and "segment" in gaze_fixations.columns:
            gaze_fixations = gaze_fixations[gaze_fixations["segment"].isin(include_segments)]

        if gaze_fixations.empty:
            LOGGER.warning("Cohort %s has no data after filtering; skipping", metadata["label"])
            continue

        cohort_labels.append(str(metadata["label"]))
        all_raw.append(gaze_fixations.assign(cohort=metadata["label"]))

        participant_means = calculate_participant_dwell_times(
            gaze_fixations,
            min_dwell_time_ms=min_dwell_time_ms,
            max_dwell_time_ms=max_dwell_time_ms,
            outlier_threshold_sd=outlier_threshold_sd,
            include_aoi=True,
            valid_aoi_categories=settings.get("aoi_analysis", {}).get("focus_categories"),
        )
        participant_means["cohort"] = metadata["label"]
        all_participant_means.append(
            participant_means[["participant_id", "condition_name", "mean_dwell_time_ms", "gaze_fixation_count", "aoi_category"]]
        )
        cohort_results.append(participant_means.assign(cohort=metadata["label"]))

    if not all_participant_means:
        LOGGER.warning("No cohorts produced valid data; skipping AR-4 analysis")
        return {
            "report_id": "AR-4",
            "title": "Dwell Time Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    combined_participant_means = pd.concat(all_participant_means, ignore_index=True)

    per_participant = (
        combined_participant_means.groupby(["participant_id", "condition_name"], as_index=False)[
            "mean_dwell_time_ms"
        ]
        .mean()
    )

    condition_summary = summarize_by_condition(per_participant)

    aoi_cfg = settings.get("aoi_analysis", {})
    min_events = int(aoi_cfg.get("min_gaze_fixations_per_aoi", 3))
    combined_raw = pd.concat(all_raw, ignore_index=True)
    aoi_summary = summarize_by_aoi(
        combined_raw,
        min_events=min_events,
        min_dwell_time_ms=min_dwell_time_ms,
        max_dwell_time_ms=max_dwell_time_ms,
        allowed_categories=aoi_cfg.get("focus_categories"),
    )

    # Statistical modelling
    statistics_result = fit_linear_mixed_model(
        formula=settings.get("statistics", {}).get("lmm_formula", "mean_dwell_time_ms ~ condition_name"),
        data=per_participant.rename(columns={"participant_id": "participant"}),
        groups_column="participant",
    )

    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name
    metadata = _generate_outputs(
        output_dir=output_dir,
        participant_means=combined_participant_means,
        condition_summary=condition_summary,
        aoi_summary=aoi_summary,
        settings=settings,
        config=config,
        cohort_labels=cohort_labels,
        recording=settings.get("recording", {}),
        statistics_result=statistics_result,
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
