"""CLI runner for the latency-to-toy analysis."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import pandas as pd
import yaml

if __package__ in (None, ""):
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from project_extension.analyses.latency_to_toy import calculator, stats, visuals
else:
    from . import calculator, stats, visuals


def run_analysis(config_path: Path) -> None:
    """Execute the latency-to-toy analysis for the provided config."""
    config = _load_config(config_path)
    config_name = config_path.stem
    output_root = _determine_output_root(config, config_path)
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    reports_dir = output_root / "reports"
    for directory in (tables_dir, figures_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    fixations = _load_fixations(config)
    condition_codes = config.get("condition_codes") or []
    if condition_codes:
        fixations = fixations[fixations["condition"].isin(condition_codes)].copy()

    window = config["window"]
    latencies = calculator.compute_latencies(
        fixations,
        window_start=window["start_frame"],
        window_end=window["end_frame"],
        toy_aois=config.get("toy_aois") or ["toy_present"],
    )
    if latencies.empty:
        raise ValueError("No latency measurements were found for the configured window/AOIs.")

    cohorts = config["cohorts"]
    summary = calculator.summarize_by_cohort(latencies, cohorts=cohorts)
    summary_path = tables_dir / f"{config_name}_latency_stats.csv"
    summary.to_csv(summary_path, index=False)

    per_trial_path = tables_dir / f"{config_name}_latency_trials.csv"
    latencies.to_csv(per_trial_path, index=False)

    gee_results, gee_report = stats.run_adult_reference_gee(latencies, cohorts=cohorts)
    adult_vs_infant = stats.summarize_adult_vs_infant(
        latencies,
        infant_cohorts=[c for c in cohorts if c["max_months"] <= 11],
        cohorts=cohorts,
    )

    report_lines = [gee_report, ""]
    if adult_vs_infant:
        report_lines.extend(
            [
                "Adult vs. Infant comparison (frames):",
                f"Infant mean: {adult_vs_infant['infant_mean_frames']:.2f} (n={adult_vs_infant['infant_trials']})",
                f"Adult mean: {adult_vs_infant['adult_mean_frames']:.2f} (n={adult_vs_infant['adult_trials']})",
            ]
        )
    reports_dir.joinpath(f"{config_name}_latency_stats_adult_ref.txt").write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    bar_title = (
        '"Give with toy" – Latency to fixation on toy\n'
        "starting from frame 30 (begin toy forward motion)"
    )
    forest_title = (
        '"Give with toy" – Latency to fixation on toy\n'
        "starting from frame 30 (begin toy forward motion)\n"
        "differences relative to Adults"
    )
    visuals.plot_latency_bar(
        summary,
        figure_path=figures_dir / f"{config_name}_latency_to_toy_bar.png",
        title=bar_title,
        cohort_order=[c["label"] for c in cohorts],
        gee_results=gee_results,
        reference_label=_find_adult_label(cohorts),
    )
    visuals.plot_latency_forest(
        gee_results,
        cohort_order=[c["label"] for c in cohorts],
        reference_label=_find_adult_label(cohorts),
        figure_path=figures_dir / f"{config_name}_latency_forest_plot.png",
        title=forest_title,
    )


def _load_fixations(config: Dict) -> pd.DataFrame:
    root = Path(config["input_threshold_dir"]).expanduser().resolve()
    csv_path = root / config.get("input_filename", "gaze_fixations_combined_min3.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Gaze fixation file not found: {csv_path}")
    return pd.read_csv(csv_path)


def _determine_output_root(config: Dict, config_path: Path) -> Path:
    configured = config.get("output_dir")
    if configured:
        return Path(configured).expanduser().resolve()
    return (config_path.parent / config_path.stem).resolve()


def _find_adult_label(cohorts: List[Dict[str, int]]) -> str:
    for cohort in cohorts:
        if "adult" in cohort["label"].lower():
            return cohort["label"]
    return cohorts[-1]["label"]


def _load_config(config_path: Path) -> Dict:
    with config_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run latency-to-toy timing analysis.")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to a latency-to-toy YAML configuration.",
    )
    args = parser.parse_args()
    run_analysis(args.config.expanduser().resolve())


if __name__ == "__main__":
    main()

