"""AR-3 Social Gaze Triplet analysis module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import SummaryStats, summarize
from src.utils.config import ConfigurationError, load_analysis_config

LOGGER = logging.getLogger("ier.analysis.ar3")

DEFAULT_OUTPUT_DIR = Path("results/AR3_Social_Triplets")


TripletPattern = Tuple[str, str, str]


@dataclass
class TripletConfig:
    valid_patterns: List[TripletPattern]
    require_consecutive: bool = True
    max_gap_frames: Optional[int] = None


def _load_gaze_events(config: Mapping[str, Any]) -> pd.DataFrame:
    processed_dir = Path(config["paths"]["processed_data"])
    child_path = processed_dir / "gaze_events_child.csv"
    default_path = processed_dir / "gaze_events.csv"

    if child_path.exists():
        path = child_path
    elif default_path.exists():
        path = default_path
    else:
        raise FileNotFoundError("No gaze events file found for AR-3 analysis")

    LOGGER.info("Loading gaze events from %s", path)
    return pd.read_csv(path)


def _resolve_triplet_config(config: Mapping[str, Any]) -> TripletConfig:
    try:
        analysis_config = load_analysis_config("ar3_config")
    except ConfigurationError:
        analysis_config = {}

    triplet_settings = analysis_config.get("triplet_definition", {})

    valid_patterns: List[TripletPattern] = []
    for pattern in triplet_settings.get("valid_patterns", []):
        if len(pattern) == 3:
            valid_patterns.append(tuple(pattern))

    if not valid_patterns:
        fallback = config.get("analysis_specific", {}).get("ar3_social_triplets", {}).get("valid_patterns", [])
        valid_patterns = [tuple(pattern) for pattern in fallback if len(pattern) == 3]

    require_consecutive = bool(triplet_settings.get("require_consecutive", True))
    max_gap_frames = triplet_settings.get("max_gap_frames")
    if max_gap_frames is not None:
        try:
            max_gap_frames = int(max_gap_frames)
        except (TypeError, ValueError):
            LOGGER.warning("Invalid max_gap_frames value %s; ignoring.", max_gap_frames)
            max_gap_frames = None

    return TripletConfig(
        valid_patterns=valid_patterns,
        require_consecutive=require_consecutive,
        max_gap_frames=max_gap_frames,
    )


def detect_triplets(
    gaze_events: pd.DataFrame,
    valid_patterns: Sequence[TripletPattern],
    *,
    require_consecutive: bool = True,
    max_gap_frames: Optional[int] = None,
) -> pd.DataFrame:
    """Identify social gaze triplets in the gaze events DataFrame."""

    columns = [
        "participant_id",
        "trial_number",
        "condition_name",
        "age_group",
        "pattern",
        "gaze_start_frame",
        "gaze_end_frame",
    ]

    if gaze_events.empty or not valid_patterns:
        return pd.DataFrame(columns=columns)

    valid_set = {tuple(pattern) for pattern in valid_patterns if len(pattern) == 3}
    records: List[Dict[str, Any]] = []

    sorted_events = gaze_events.sort_values(
        ["participant_id", "trial_number", "gaze_onset_time", "gaze_start_frame"],
        kind="stable",
    )

    for (participant_id, trial_number), trial_df in sorted_events.groupby(
        ["participant_id", "trial_number"], sort=False
    ):
        trial_df = trial_df.reset_index(drop=True)
        for idx in range(len(trial_df) - 2):
            window = trial_df.iloc[idx : idx + 3]
            pattern = tuple(window["aoi_category"].tolist())
            if pattern not in valid_set:
                continue

            if require_consecutive:
                if pattern[0] == pattern[1] or pattern[1] == pattern[2]:
                    continue

            gap_first = _frame_gap(window.iloc[0], window.iloc[1])
            gap_second = _frame_gap(window.iloc[1], window.iloc[2])

            if require_consecutive and (gap_first > 0 or gap_second > 0):
                continue

            if max_gap_frames is not None:
                if gap_first > max_gap_frames or gap_second > max_gap_frames:
                    continue

            records.append(
                {
                    "participant_id": participant_id,
                    "trial_number": trial_number,
                    "condition_name": window.iloc[0]["condition_name"],
                    "age_group": window.iloc[0].get("age_group", "unknown"),
                    "pattern": ">".join(pattern),
                    "gaze_start_frame": int(window.iloc[0]["gaze_start_frame"]),
                    "gaze_end_frame": int(window.iloc[2]["gaze_end_frame"]),
                }
            )

    return pd.DataFrame.from_records(records, columns=columns)


def _frame_gap(first: pd.Series, second: pd.Series) -> int:
    end_frame = _safe_int(first.get("gaze_end_frame"))
    start_frame = _safe_int(second.get("gaze_start_frame"))
    if end_frame is None or start_frame is None:
        return 0
    return max(0, start_frame - end_frame - 1)


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def count_triplets_per_trial(triplets: pd.DataFrame) -> pd.DataFrame:
    if triplets.empty:
        return pd.DataFrame(
            columns=["participant_id", "trial_number", "condition_name", "age_group", "triplet_count"]
        )

    counts = (
        triplets.groupby(["participant_id", "trial_number", "condition_name", "age_group"], as_index=False)
        .size()
        .rename(columns={"size": "triplet_count"})
    )
    return counts


def summarize_by_condition(counts: pd.DataFrame) -> pd.DataFrame:
    if counts.empty:
        return pd.DataFrame(
            columns=["condition_name", "mean_triplets", "std_triplets", "sem_triplets", "n_participants"]
        )

    rows: List[Dict[str, Any]] = []
    for condition, condition_df in counts.groupby("condition_name", sort=True):
        stats = _series_summary(condition_df["triplet_count"])
        rows.append(
            {
                "condition_name": condition,
                "mean_triplets": stats.mean,
                "std_triplets": stats.std,
                "sem_triplets": stats.sem,
                "n_participants": int(condition_df["participant_id"].nunique()),
            }
        )

    return pd.DataFrame(rows)


def summarize_by_age_group(counts: pd.DataFrame) -> pd.DataFrame:
    if counts.empty:
        return pd.DataFrame(
            columns=["age_group", "mean_triplets", "std_triplets", "sem_triplets", "n_participants"]
        )

    rows: List[Dict[str, Any]] = []
    for age_group, age_df in counts.groupby("age_group", sort=True):
        stats = _series_summary(age_df["triplet_count"])
        rows.append(
            {
                "age_group": age_group,
                "mean_triplets": stats.mean,
                "std_triplets": stats.std,
                "sem_triplets": stats.sem,
                "n_participants": int(age_df["participant_id"].nunique()),
            }
        )

    return pd.DataFrame(rows)


def _series_summary(values: pd.Series) -> SummaryStats:
    try:
        return summarize(values.tolist())
    except ValueError:
        return SummaryStats(mean=float(np.mean(values)), std=0.0, sem=0.0, count=len(values))


def _build_overview_text(total_triplets: int) -> str:
    if total_triplets == 0:
        return (
            "No social gaze triplets were detected in the processed dataset. "
            "Review AOI labeling and gaze event definitions before interpreting results."
        )

    return (
        "This analysis quantifies social gaze coordination by detecting sequences where infants "
        "look from one actor's face to the toy and then to the other actor's face."
    )


def _build_statistics_table() -> str:
    return (
        "<p>GLMM statistical modeling for AR-3 is pending due to missing dependencies. "
        "Counts and descriptive summaries are reported for transparency.</p>"
    )


def _build_methods_text(config: TripletConfig) -> str:
    patterns = ", ".join([" → ".join(pattern) for pattern in config.valid_patterns]) or "No patterns defined"
    max_gap_desc = (
        f"Maximum of {config.max_gap_frames} frame gaps allowed between gazes." if config.max_gap_frames is not None else "No frame gap limit applied."
    )
    consecutive_desc = "Triplets require consecutive gaze events." if config.require_consecutive else "Triplets may include non-consecutive gaze events."
    return (
        f"Triplets were detected using the following valid patterns: {patterns}. "
        f"{consecutive_desc} {max_gap_desc}"
    )


def _generate_outputs(
    *,
    output_dir: Path,
    triplets: pd.DataFrame,
    counts: pd.DataFrame,
    summary_condition: pd.DataFrame,
    summary_age: pd.DataFrame,
    config: TripletConfig,
    global_config: Mapping[str, Any],
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    tables_to_save: List[Path] = []

    triplet_csv = output_dir / "triplets_detected.csv"
    triplets.to_csv(triplet_csv, index=False)
    tables_to_save.append(triplet_csv)

    counts_csv = output_dir / "triplet_counts_by_trial.csv"
    counts.to_csv(counts_csv, index=False)
    tables_to_save.append(counts_csv)

    summary_condition_csv = output_dir / "triplet_summary_by_condition.csv"
    summary_condition.to_csv(summary_condition_csv, index=False)
    tables_to_save.append(summary_condition_csv)

    summary_age_csv = output_dir / "triplet_summary_by_age_group.csv"
    summary_age.to_csv(summary_age_csv, index=False)
    tables_to_save.append(summary_age_csv)

    figure_contexts: List[Dict[str, str]] = []

    if not summary_condition.empty:
        condition_figure = output_dir / "triplets_by_condition.png"
        visualizations.bar_plot(
            summary_condition,
            x="condition_name",
            y="mean_triplets",
            title="Mean Social Gaze Triplets per Trial by Condition",
            ylabel="Mean Triplets per Trial",
            output_path=condition_figure,
        )
        figure_contexts.append(
            {
                "path": str(condition_figure),
                "caption": "Mean social gaze triplets per trial across experimental conditions.",
            }
        )

    if not summary_age.empty:
        age_figure = output_dir / "triplets_by_age_group.png"
        visualizations.bar_plot(
            summary_age,
            x="age_group",
            y="mean_triplets",
            title="Mean Social Gaze Triplets per Trial by Age Group",
            ylabel="Mean Triplets per Trial",
            output_path=age_figure,
        )
        figure_contexts.append(
            {
                "path": str(age_figure),
                "caption": "Mean social gaze triplets per trial across age groups.",
            }
        )

    frequency_table_html = summary_condition.to_html(index=False, classes="table table-striped")
    age_table_html = summary_age.to_html(index=False, classes="table table-striped")

    context = {
        "overview_text": _build_overview_text(int(triplets.shape[0])),
        "methods_text": _build_methods_text(config),
        "frequency_table": frequency_table_html,
        "age_group_table": age_table_html,
        "statistics_table": _build_statistics_table(),
        "interpretation_text": (
            "Interpret findings with caution until formal GLMM modeling is completed. "
            "Descriptive results can still highlight which conditions elicit coordinated social gaze."
        ),
        "figure_entries": figure_contexts,
        "figures": [entry["path"] for entry in figure_contexts],
        "tables": [str(path) for path in tables_to_save],
    }

    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"

    render_report(
        template_name="ar3_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )

    return {
        "report_id": "AR-3",
        "title": "Social Gaze Triplet Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    LOGGER.info("Starting AR-3 social triplet analysis")

    try:
        gaze_events = _load_gaze_events(config)
    except FileNotFoundError as exc:
        LOGGER.warning("Skipping AR-3 analysis: %s", exc)
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    if gaze_events.empty:
        LOGGER.warning("Gaze events file is empty; skipping AR-3 analysis")
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    triplet_config = _resolve_triplet_config(config)
    if not triplet_config.valid_patterns:
        LOGGER.warning("No valid triplet patterns defined; skipping AR-3 analysis")
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    triplets = detect_triplets(
        gaze_events,
        triplet_config.valid_patterns,
        require_consecutive=triplet_config.require_consecutive,
        max_gap_frames=triplet_config.max_gap_frames,
    )

    counts = count_triplets_per_trial(triplets)
    summary_condition = summarize_by_condition(counts)
    summary_age = summarize_by_age_group(counts)

    output_dir = Path(config["paths"]["results"]) / DEFAULT_OUTPUT_DIR.name

    if triplets.empty:
        LOGGER.warning("No social gaze triplets detected; generating descriptive report with zero counts")

    metadata = _generate_outputs(
        output_dir=output_dir,
        triplets=triplets,
        counts=counts,
        summary_condition=summary_condition,
        summary_age=summary_age,
        config=triplet_config,
        global_config=config,
    )

    LOGGER.info("AR-3 analysis completed; report generated at %s", metadata["html_path"])
    return metadata


__all__ = [
    "detect_triplets",
    "count_triplets_per_trial",
    "summarize_by_condition",
    "summarize_by_age_group",
    "run",
]

