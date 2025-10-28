"""AR-3 Social Gaze Triplet analysis module."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.reporting.statistics import SummaryStats, summarize
from src.utils.config import ConfigurationError, load_analysis_config

LOGGER = logging.getLogger("ier.analysis.ar3")

OUTPUT_ROOT_DIR = Path("AR3")


TripletPattern = Tuple[str, str, str]


@dataclass
class TripletConfig:
    valid_patterns: List[TripletPattern]
    require_consecutive: bool = True
    max_gap_frames: Optional[int] = None
    alias_to_canonical: Dict[str, str] = field(default_factory=dict)


def _resolve_dataset_paths(variant_config: Mapping[str, Any], global_config: Mapping[str, Any]) -> List[Dict[str, Any]]:
    cohorts = variant_config.get("cohorts", [])
    if not cohorts:
        processed_dir = Path(global_config["paths"]["processed_data"])
        default_path = processed_dir / "gaze_fixations.csv"
        if not default_path.exists():
            raise FileNotFoundError("No cohorts defined and gaze_fixations.csv missing")
        return [
            {
                "key": "all",
                "label": "All Participants",
                "data_path": default_path,
                "include_in_reports": True,
                "participant_filters": {},
            }
        ]

    base_dir = Path(global_config.get("paths", {}).get("results", ".")).resolve().parent
    resolved: List[Dict[str, Any]] = []
    for cohort in cohorts:
        data_path = Path(cohort.get("data_path", "")).expanduser()
        if not data_path.is_absolute():
            data_path = (base_dir / data_path).resolve()
        resolved.append({**cohort, "data_path": data_path})
    return resolved


def _load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Gaze fixation dataset missing: {path}")
    return pd.read_csv(path)


def _apply_filters(df: pd.DataFrame, filters: Optional[Dict[str, Sequence[Any]]]) -> pd.DataFrame:
    if not filters:
        return df.copy()
    filtered = df.copy()
    for column, allowed in filters.items():
        if column not in filtered.columns:
            raise KeyError(f"Filter column '{column}' not found in gaze fixations data.")
        allowed_values = list(allowed)
        filtered = filtered[filtered[column].isin(allowed_values)]
    return filtered


def _apply_condition_segment_filters(df: pd.DataFrame, variant_config: Mapping[str, Any]) -> pd.DataFrame:
    result = df.copy()

    conditions_block = variant_config.get("conditions", {})
    include_conditions = conditions_block.get("include")
    if include_conditions:
        result = result[result["condition_name"].isin(include_conditions)]

    segments_block = variant_config.get("segments", {})
    include_segments = segments_block.get("include")
    exclude_segments = segments_block.get("exclude")
    if include_segments:
        result = result[result["segment"].isin(include_segments)]
    elif exclude_segments:
        result = result[~result["segment"].isin(exclude_segments)]

    return result


def _cohort_metadata(triplets: pd.DataFrame, counts: pd.DataFrame) -> Dict[str, Any]:
    participants = triplets["participant_id"].nunique() if not triplets.empty else 0
    conditions = triplets["condition_name"].unique().tolist() if not triplets.empty else []
    return {
        "n_triplets": int(triplets.shape[0]),
        "n_participants": int(participants),
        "conditions": conditions,
        "n_trials": int(counts[["participant_id", "trial_number"]].drop_duplicates().shape[0]) if not counts.empty else 0,
    }


def _load_variant_configuration(config: Mapping[str, Any]) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    try:
        base_config = load_analysis_config("ar3_config")
    except ConfigurationError:
        base_config = {}

    analysis_specific = config.get("analysis_specific", {}).get("ar3_social_triplets", {})
    default_variant = analysis_specific.get("config_name", "ar3/ar3_give_vs_hug")
    env_variant = os.environ.get("IER_AR3_CONFIG", "").strip()
    variant_name = env_variant or default_variant

    try:
        variant_config = load_analysis_config(variant_name)
    except ConfigurationError as exc:
        raise ConfigurationError(f"Failed to load AR-3 variant configuration '{variant_name}': {exc}") from exc

    return variant_config, variant_name, base_config


def _resolve_triplet_config(
    global_config: Mapping[str, Any],
    variant_config: Mapping[str, Any],
    base_config: Mapping[str, Any],
) -> TripletConfig:
    triplet_settings = variant_config.get("triplets") or base_config.get("triplet_definition", {})

    valid_patterns: List[TripletPattern] = []
    patterns_source = triplet_settings.get("valid_patterns") or base_config.get("triplet_definition", {}).get("valid_patterns", [])
    if not patterns_source:
        patterns_source = (
            global_config.get("analysis_specific", {})
            .get("ar3_social_triplets", {})
            .get("valid_patterns", [])
        )
    for pattern in patterns_source:
        if len(pattern) == 3:
            valid_patterns.append(tuple(pattern))

    if not valid_patterns:
        raise ConfigurationError("No valid triplet patterns defined for AR-3 analysis.")

    require_consecutive = bool(
        triplet_settings.get(
            "require_consecutive",
            base_config.get("triplet_definition", {}).get("require_consecutive", True),
        )
    )
    max_gap_frames = triplet_settings.get(
        "max_gap_frames",
        base_config.get("triplet_definition", {}).get("max_gap_frames"),
    )
    if max_gap_frames is not None:
        try:
            max_gap_frames = int(max_gap_frames)
        except (TypeError, ValueError):
            LOGGER.warning("Invalid max_gap_frames value %s; ignoring.", max_gap_frames)
            max_gap_frames = None

    toy_absent_mapping = triplet_settings.get("toy_absent_mapping", {})
    alias_to_canonical: Dict[str, str] = {}
    for canonical, alias in toy_absent_mapping.items():
        alias_to_canonical[str(alias)] = str(canonical)

    return TripletConfig(
        valid_patterns=valid_patterns,
        require_consecutive=require_consecutive,
        max_gap_frames=max_gap_frames,
        alias_to_canonical=alias_to_canonical,
    )


def detect_triplets(
    gaze_fixations: pd.DataFrame,
    valid_patterns: Sequence[TripletPattern],
    *,
    require_consecutive: bool = True,
    max_gap_frames: Optional[int] = None,
    alias_to_canonical: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """Identify social gaze triplets in the gaze fixations DataFrame."""

    columns = [
        "participant_id",
        "trial_number",
        "condition_name",
        "age_group",
        "pattern",
        "gaze_start_frame",
        "gaze_end_frame",
    ]

    if gaze_fixations.empty or not valid_patterns:
        return pd.DataFrame(columns=columns)

    valid_set = {tuple(pattern) for pattern in valid_patterns if len(pattern) == 3}
    records: List[Dict[str, Any]] = []

    sorted_events = gaze_fixations.sort_values(
        ["participant_id", "trial_number", "gaze_onset_time", "gaze_start_frame"],
        kind="stable",
    )

    for (participant_id, trial_number), trial_df in sorted_events.groupby(
        ["participant_id", "trial_number"], sort=False
    ):
        trial_df = trial_df.reset_index(drop=True)
        for idx in range(len(trial_df) - 2):
            window = trial_df.iloc[idx : idx + 3]
            categories = []
            for value in window["aoi_category"].tolist():
                canonical = alias_to_canonical.get(value, value) if alias_to_canonical else value
                categories.append(canonical)

            pattern = tuple(categories)
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
        return pd.DataFrame(columns=["participant_id", "trial_number", "condition_name", "age_group", "triplet_count"])

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
        return pd.DataFrame(columns=["age_group", "mean_triplets", "std_triplets", "sem_triplets", "n_participants"])

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


def compute_directional_bias(triplets: pd.DataFrame) -> pd.DataFrame:
    if triplets.empty:
        return pd.DataFrame(columns=["condition_name", "pattern", "count"])

    return (
        triplets.groupby(["condition_name", "pattern"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values(["condition_name", "pattern"])
    )


def compute_temporal_summary(triplets: pd.DataFrame) -> pd.DataFrame:
    if triplets.empty:
        return pd.DataFrame(columns=["condition_name", "first_occurrence", "subsequent_occurrences"])

    def _split_counts(group: pd.DataFrame) -> Tuple[int, int]:
        first_trials = (
            group.groupby("participant_id", as_index=False)["trial_number"]
            .min()
            .rename(columns={"trial_number": "first_trial"})
        )
        merged = group.merge(first_trials, on="participant_id", how="left")
        first_mask = merged["trial_number"] == merged["first_trial"]
        first_count = int(first_mask.sum())
        subsequent_count = int((~first_mask).sum())
        return first_count, subsequent_count

    records: List[Dict[str, Any]] = []
    for condition, condition_df in triplets.groupby("condition_name", sort=True):
        first, subsequent = _split_counts(condition_df)
        records.append(
            {
                "condition_name": condition,
                "first_occurrence": first,
                "subsequent_occurrences": subsequent,
            }
        )

    return pd.DataFrame(records)


def _series_summary(values: pd.Series) -> SummaryStats:
    try:
        return summarize(values.tolist())
    except ValueError:
        return SummaryStats(mean=float(np.mean(values)), std=0.0, sem=0.0, count=len(values))


def _build_overview_text(total_triplets: int) -> str:
    if total_triplets == 0:
        return (
            "No social gaze triplets were detected in the processed dataset. "
            "Review AOI labeling and gaze fixation definitions before interpreting results."
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
        f"Maximum of {config.max_gap_frames} frame gaps allowed between gazes."
        if config.max_gap_frames is not None
        else "No frame gap limit applied."
    )
    consecutive_desc = (
        "Triplets require consecutive gaze fixations."
        if config.require_consecutive
        else "Triplets may include non-consecutive gaze fixations."
    )
    return (
        f"Triplets were detected using the following valid patterns: {patterns}. " f"{consecutive_desc} {max_gap_desc}"
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
    variant_config: Mapping[str, Any],
    directional_bias: pd.DataFrame | None = None,
    temporal_summary: pd.DataFrame | None = None,
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

    if directional_bias is None:
        directional_bias = pd.DataFrame(columns=["condition_name", "pattern", "count"])
    if temporal_summary is None:
        temporal_summary = pd.DataFrame(columns=["condition_name", "first_occurrence", "subsequent_occurrences"])

    directional_csv = output_dir / "triplet_directional_bias.csv"
    directional_bias.to_csv(directional_csv, index=False)
    tables_to_save.append(directional_csv)

    temporal_csv = output_dir / "triplet_temporal_summary.csv"
    temporal_summary.to_csv(temporal_csv, index=False)
    tables_to_save.append(temporal_csv)

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
    directional_table_html = directional_bias.to_html(index=False, classes="table table-striped")
    temporal_table_html = temporal_summary.to_html(index=False, classes="table table-striped")

    context = {
        "overview_text": _build_overview_text(int(triplets.shape[0])),
        "methods_text": _build_methods_text(config),
        "frequency_table": frequency_table_html,
        "age_group_table": age_table_html,
        "directional_bias_table": directional_table_html,
        "temporal_summary_table": temporal_table_html,
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
        variant_config, variant_name, base_config = _load_variant_configuration(config)
    except ConfigurationError as exc:
        LOGGER.warning("Skipping AR-3 analysis: %s", exc)
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "variant_key": None,
            "html_path": "",
            "pdf_path": "",
        }

    triplet_config = _resolve_triplet_config(config, variant_config, base_config)

    cohort_defs = _resolve_dataset_paths(variant_config, config)
    if not cohort_defs:
        LOGGER.warning("No cohorts resolved for AR-3 analysis")
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "variant_key": variant_config.get("variant_key"),
            "html_path": "",
            "pdf_path": "",
        }

    results_root = Path(config["paths"]["results"]) / OUTPUT_ROOT_DIR
    variant_key = variant_config.get("variant_key", Path(variant_name).stem)
    output_dir = results_root / variant_key

    resolved_any = False
    all_triplets: List[pd.DataFrame] = []
    all_counts: List[pd.DataFrame] = []
    for cohort in cohort_defs:
        data_path: Path = cohort["data_path"]
        try:
            dataset = _load_dataset(data_path)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping cohort %s: %s", cohort.get("key"), exc)
            continue

        resolved_any = True

        cohort_filters = cohort.get("participant_filters", {})
        filtered = _apply_filters(dataset, cohort_filters)
        filtered = _apply_condition_segment_filters(filtered, variant_config)

        if filtered.empty:
            LOGGER.info("Cohort %s yielded no gaze fixations after filtering", cohort.get("key"))
            continue

        triplets = detect_triplets(
            filtered,
            triplet_config.valid_patterns,
            require_consecutive=triplet_config.require_consecutive,
            max_gap_frames=triplet_config.max_gap_frames,
            alias_to_canonical=triplet_config.alias_to_canonical,
        )

        if triplets.empty:
            LOGGER.info("No triplets detected for cohort %s", cohort.get("key"))
            continue

        triplets["cohort_key"] = cohort.get("key")
        triplets["cohort_label"] = cohort.get("label")
        all_triplets.append(triplets)

        counts = count_triplets_per_trial(triplets)
        counts["cohort_key"] = cohort.get("key")
        counts["cohort_label"] = cohort.get("label")
        all_counts.append(counts)

    if not resolved_any:
        LOGGER.warning("No datasets found for AR-3 variant %s", variant_key)
        return {
            "report_id": "AR-3",
            "title": "Social Gaze Triplet Analysis",
            "variant_key": None,
            "html_path": "",
            "pdf_path": "",
            "message": "No datasets found",
        }

    if not all_triplets:
        LOGGER.warning("No social gaze triplets detected for variant %s", variant_key)
        output_dir.mkdir(parents=True, exist_ok=True)
        empty_triplets = pd.DataFrame(
            columns=[
                "participant_id",
                "trial_number",
                "condition_name",
                "age_group",
                "pattern",
                "gaze_start_frame",
                "gaze_end_frame",
            ]
        )
        empty_counts = pd.DataFrame(
            columns=["participant_id", "trial_number", "condition_name", "age_group", "triplet_count"]
        )
        empty_summary_condition = pd.DataFrame(
            columns=["condition_name", "mean_triplets", "std_triplets", "sem_triplets", "n_participants"]
        )
        empty_summary_age = pd.DataFrame(
            columns=["age_group", "mean_triplets", "std_triplets", "sem_triplets", "n_participants"]
        )
        metadata = _generate_outputs(
            output_dir=output_dir,
            triplets=empty_triplets,
            counts=empty_counts,
            summary_condition=empty_summary_condition,
            summary_age=empty_summary_age,
            config=triplet_config,
            global_config=config,
            variant_config=variant_config,
            directional_bias=pd.DataFrame(columns=["condition_name", "pattern", "count"]),
            temporal_summary=pd.DataFrame(columns=["condition_name", "first_occurrence", "subsequent_occurrences"]),
        )
        metadata.update(_cohort_metadata(empty_triplets, empty_counts))
        metadata["variant_key"] = variant_key
        return metadata

    triplets_concat = pd.concat(all_triplets, ignore_index=True)
    counts_concat = pd.concat(all_counts, ignore_index=True)

    summary_condition = summarize_by_condition(counts_concat)
    summary_age = summarize_by_age_group(counts_concat)
    directional_bias = compute_directional_bias(triplets_concat)
    temporal_summary = compute_temporal_summary(triplets_concat)

    metadata = _generate_outputs(
        output_dir=output_dir,
        triplets=triplets_concat,
        counts=counts_concat,
        summary_condition=summary_condition,
        summary_age=summary_age,
        config=triplet_config,
        global_config=config,
        variant_config=variant_config,
        directional_bias=directional_bias,
        temporal_summary=temporal_summary,
    )
    metadata.update(_cohort_metadata(triplets_concat, counts_concat))
    metadata["variant_key"] = variant_key

    LOGGER.info("AR-3 analysis completed for %s; report generated at %s", variant_key, metadata["html_path"])
    return metadata


__all__ = [
    "detect_triplets",
    "count_triplets_per_trial",
    "summarize_by_condition",
    "summarize_by_age_group",
    "run",
]
