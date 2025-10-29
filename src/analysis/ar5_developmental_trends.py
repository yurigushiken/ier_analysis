"""AR-5 Developmental Trends analysis (scaffold).

This is a minimal, safe scaffold that mirrors existing AR modules' patterns.
It reads a variant config, resolves cohorts, applies participant filters
with tolerant casting, computes per-participant focus proportions for a set of
focus AOIs, aggregates by age (months or age_group), writes CSV summaries,
renders a simple report, and returns report metadata.

This scaffold is intentionally conservative: it logs warnings and skips
missing cohorts rather than raising, and it produces empty CSV placeholders
when no data is available. Extend this with richer statistics & plotting
as needed for AR-5 feature work.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report
from src.utils.config import load_analysis_config

LOGGER = logging.getLogger("ier.analysis.ar5")

OUTPUT_ROOT = Path("AR5_developmental_trends")


def _load_variant_configuration(config: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    analysis_specific = config.get("analysis_specific", {}).get("ar5_developmental_trends", {})
    default_variant = str(analysis_specific.get("config_name", "AR5_developmental_trends/ar5_example")).strip()
    env_variant = __import__("os").environ.get("IER_AR5_CONFIG", "").strip()
    variant_name = env_variant or default_variant

    variant_config = load_analysis_config(variant_name)
    return variant_config, variant_name


def _resolve_dataset_paths(variant_config: Dict[str, Any], global_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    cohorts = variant_config.get("cohorts", [])
    if not cohorts:
        processed_dir = Path(global_config["paths"]["processed_data"]) if "paths" in global_config else Path("data/processed")
        default_path = processed_dir / "gaze_fixations_child.csv"
        if default_path.exists():
            return [{"key": "all", "label": "All Participants", "data_path": default_path, "include_in_reports": True, "participant_filters": {}}]
        return []

    base_dir = Path(global_config.get("paths", {}).get("results", ".")).resolve().parent
    resolved: List[Dict[str, Any]] = []
    for cohort in cohorts:
        data_path = Path(cohort.get("data_path", "")).expanduser()
        if not data_path.is_absolute():
            data_path = (base_dir / data_path).resolve()
        resolved.append({**cohort, "data_path": data_path})
    return resolved


def _load_gaze_fixations(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Gaze fixations file not found: {path}")
    return pd.read_csv(path)


def _attempt_cast_allowed(column: pd.Series, allowed_values: Iterable[Any]) -> List[Any]:
    # Try to coerce allowed_values to the dtype of `column` for reliable .isin
    allowed = list(allowed_values) if allowed_values is not None else []
    if not allowed:
        return allowed
    try:
        if pd.api.types.is_integer_dtype(column.dtype):
            return [int(x) for x in allowed]
        if pd.api.types.is_float_dtype(column.dtype):
            return [float(x) for x in allowed]
    except Exception:
        pass
    # Fallback: compare as strings
    return [str(x) for x in allowed]


def _apply_participant_filters(df: pd.DataFrame, filters: Optional[Dict[str, Iterable[Any]]]) -> pd.DataFrame:
    if not filters:
        return df
    filtered = df.copy()
    for column, allowed in filters.items():
        if column not in filtered.columns:
            LOGGER.warning("Filter column '%s' not present in dataset; skipping this filter", column)
            continue
        allowed_cast = _attempt_cast_allowed(filtered[column], allowed)
        filtered = filtered[filtered[column].isin(allowed_cast)]
    return filtered


def _compute_participant_focus_proportions(df: pd.DataFrame, focus_aois: Iterable[str]) -> pd.DataFrame:
    # Expects columns: participant_id, gaze_duration_ms, aoi_category, age_months, age_group
    if df.empty:
        return pd.DataFrame(columns=["participant_id", "age_months", "age_group", "focus_duration_ms", "total_duration_ms", "focus_proportion"])

    working = df.copy()
    # Treat missing gaze_duration_ms as zero-safe
    working["gaze_duration_ms"] = pd.to_numeric(working.get("gaze_duration_ms", pd.Series(0)), errors="coerce").fillna(0.0)
    working["is_focus"] = working.get("aoi_category", "").isin(set(focus_aois))

    totals = (
        working.groupby(["participant_id"], as_index=False)["gaze_duration_ms"].sum().rename(columns={"gaze_duration_ms": "total_duration_ms"})
    )
    focus = (
        working[working["is_focus"]]
        .groupby(["participant_id"], as_index=False)["gaze_duration_ms"]
        .sum()
        .rename(columns={"gaze_duration_ms": "focus_duration_ms"})
    )

    merged = totals.merge(focus, on="participant_id", how="left")
    merged["focus_duration_ms"] = merged["focus_duration_ms"].fillna(0.0)
    merged["focus_proportion"] = merged.apply(lambda r: r["focus_duration_ms"] / r["total_duration_ms"] if r["total_duration_ms"] > 0 else 0.0, axis=1)

    # bring in age info (prefer age_months then age_group)
    age_map = df[["participant_id", "age_months", "age_group"]].drop_duplicates(subset=["participant_id"]).set_index("participant_id")
    merged["age_months"] = merged["participant_id"].map(age_map["age_months"]) if "age_months" in age_map.columns else pd.NA
    merged["age_group"] = merged["participant_id"].map(age_map["age_group"]) if "age_group" in age_map.columns else pd.NA

    return merged


def _summarize_by_age(participant_df: pd.DataFrame, mode: str = "detailed") -> pd.DataFrame:
    if participant_df.empty:
        return pd.DataFrame(columns=["age_label", "mean_focus_proportion", "std", "sem", "n_participants"])

    if mode == "by_months":
        grouping = participant_df.groupby("age_months")
        rows = []
        for age, grp in grouping:
            vals = grp["focus_proportion"].dropna().astype(float)
            n = len(vals)
            rows.append({"age_label": int(age) if not pd.isna(age) else "unknown", "mean_focus_proportion": float(vals.mean()) if n else 0.0, "std": float(vals.std(ddof=1)) if n>1 else 0.0, "sem": float(vals.sem(ddof=1)) if n>1 else 0.0, "n_participants": int(n)})
        return pd.DataFrame(rows).sort_values("age_label")

    if mode == "child_vs_adult":
        df = participant_df.copy()
        df["age_label"] = df["age_group"].apply(lambda v: "adult" if str(v).lower() == "adult" else "child")
    else:
        df = participant_df.copy()
        df["age_label"] = df["age_group"].fillna("unknown")

    grouped = df.groupby("age_label")
    rows = []
    for label, grp in grouped:
        vals = grp["focus_proportion"].dropna().astype(float)
        n = len(vals)
        rows.append({"age_label": label, "mean_focus_proportion": float(vals.mean()) if n else 0.0, "std": float(vals.std(ddof=1)) if n>1 else 0.0, "sem": float(vals.sem(ddof=1)) if n>1 else 0.0, "n_participants": int(n)})
    return pd.DataFrame(rows).sort_values("age_label")


def _generate_outputs(*, output_dir: Path, participant_df: pd.DataFrame, age_summary: pd.DataFrame, variant_config: Dict[str, Any], variant_key: str) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    participant_csv = output_dir / "participant_focus_proportions.csv"
    age_csv = output_dir / "age_summary.csv"
    participant_df.to_csv(participant_csv, index=False)
    age_summary.to_csv(age_csv, index=False)

    figures = []
    if not age_summary.empty:
        fig_path = output_dir / "focus_by_age.png"
        # If age_label numeric, prefer line plot; otherwise bar
        try:
            if pd.api.types.is_integer_dtype(age_summary["age_label"]):
                visualizations.line_plot(age_summary, x="age_label", y="mean_focus_proportion", title="Mean Focus Proportion by Age (months)", ylabel="Mean Focus Proportion", output_path=fig_path)
            else:
                visualizations.bar_plot(age_summary, x="age_label", y="mean_focus_proportion", title="Mean Focus Proportion by Age Group", ylabel="Mean Focus Proportion", output_path=fig_path)
            figures.append(str(fig_path))
        except Exception as exc:
            LOGGER.warning("Failed to render age figure: %s", exc)

    context = {
        "report_title": variant_config.get("report_title", "AR-5: Developmental Trends"),
        "variant_label": variant_config.get("variant_label", variant_key),
        "variant_key": variant_key,
        "participant_table": str(participant_csv.name),
        "age_summary_table": str(age_csv.name),
        "figures": figures,
    }

    html_path = output_dir / "report.html"
    render_report(template_name="ar5_template.html" if True else "ar1_template.html", context=context, output_html=html_path, output_pdf=None)

    return {"report_id": "AR-5", "title": context["report_title"], "html_path": str(html_path), "csvs": [str(participant_csv), str(age_csv)], "figures": figures}


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    LOGGER.info("Starting AR-5 developmental trends (scaffold)")
    try:
        variant_config, variant_name = _load_variant_configuration(config)
    except Exception as exc:
        LOGGER.warning("Failed to load AR-5 variant configuration: %s", exc)
        return {"report_id": "AR-5", "title": "AR-5", "html_path": "", "message": "Configuration load failed"}

    variant_key = variant_config.get("variant_key", Path(variant_name).stem)
    focus_aois = variant_config.get("analysis", {}).get("aoi_focus", ["toy_present"]) or ["toy_present"]
    age_mode = variant_config.get("analysis", {}).get("age_summary_mode", "detailed")

    cohort_defs = _resolve_dataset_paths(variant_config, config)
    if not cohort_defs:
        LOGGER.warning("No cohorts resolved for AR-5 variant %s", variant_key)
        return {"report_id": "AR-5", "title": "AR-5", "variant_key": variant_key, "html_path": "", "message": "No cohorts"}

    results_root = Path(config["paths"]["results"]) / OUTPUT_ROOT
    output_dir = results_root / variant_key

    all_participant_frames: List[pd.DataFrame] = []

    for cohort in cohort_defs:
        data_path: Path = cohort["data_path"]
        try:
            df = _load_gaze_fixations(data_path)
        except FileNotFoundError as exc:
            LOGGER.warning("Skipping cohort %s: %s", cohort.get("key"), exc)
            continue

        filters = cohort.get("participant_filters", {})
        df = _apply_participant_filters(df, filters)
        if df.empty:
            LOGGER.info("Cohort %s produced no rows after filtering; skipping.", cohort.get("key"))
            continue

        participant_props = _compute_participant_focus_proportions(df, focus_aois)
        if participant_props.empty:
            LOGGER.info("No participant-level data for cohort %s", cohort.get("key"))
            continue
        participant_props["cohort"] = cohort.get("key")
        all_participant_frames.append(participant_props)

    if not all_participant_frames:
        LOGGER.warning("No participant data found for any cohort in variant %s", variant_key)
        output_dir.mkdir(parents=True, exist_ok=True)
        # create empty placeholders
        pd.DataFrame().to_csv(output_dir / "participant_focus_proportions.csv", index=False)
        pd.DataFrame().to_csv(output_dir / "age_summary.csv", index=False)
        return {"report_id": "AR-5", "title": "AR-5", "html_path": "", "message": "No data"}

    all_participants = pd.concat(all_participant_frames, ignore_index=True)
    age_summary = _summarize_by_age(all_participants, mode=age_mode)

    metadata = _generate_outputs(output_dir=output_dir, participant_df=all_participants, age_summary=age_summary, variant_config=variant_config, variant_key=variant_key)
    metadata["variant_key"] = variant_key
    LOGGER.info("AR-5 scaffold completed; report at %s", metadata.get("html_path"))
    return metadata


__all__ = ["run"]
