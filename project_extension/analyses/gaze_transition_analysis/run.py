"""CLI entry point for the gaze transition analysis."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml

if __package__ in (None, ""):
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from project_extension.analyses.gaze_transition_analysis import loader, matrix, transitions, visuals, strategy
else:
    from . import loader, matrix, transitions, visuals, strategy


def run_analysis(config_path: Path) -> None:
    config = _load_config(config_path)
    output_root = _determine_output_root(config, config_path)
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    reports_dir = output_root / "reports"
    for folder in (tables_dir, figures_dir, reports_dir):
        folder.mkdir(parents=True, exist_ok=True)

    condition_codes = config.get("condition_codes") or ["gw"]
    aoi_nodes = config["aoi_nodes"]
    cohorts = config["cohorts"]

    fixations = loader.load_fixations(
        Path(config.get("input_fixations")) if config.get("input_fixations") else None,
        condition_codes=condition_codes,
    )
    transitions_df = transitions.compute_transitions(fixations, aoi_nodes=aoi_nodes)
    wide_counts = transitions.to_wide_counts(transitions_df, aoi_nodes=aoi_nodes)
    wide_counts.to_csv(tables_dir / f"{config_path.stem}_transition_counts.csv", index=False)

    matrix_df = matrix.build_transition_matrix(
        transitions_df,
        cohorts=cohorts,
        aoi_nodes=aoi_nodes,
    )
    matrix_df.to_csv(tables_dir / f"{config_path.stem}_transition_matrix.csv", index=False)

    visuals.plot_heatmap(
        matrix_df,
        aoi_nodes=aoi_nodes,
        cohorts=[c["label"] for c in cohorts],
        figure_path=figures_dir / f"{config_path.stem}_transition_heatmap.png",
        title=f"\"{_condition_label(condition_codes)}\" - Transition frequencies",
    )

    strategy_df = strategy.compute_strategy_proportions(transitions_df)
    strategy_df.to_csv(tables_dir / f"{config_path.stem}_strategy_proportions.csv", index=False)
    strategy_summary = strategy.build_strategy_summary(strategy_df, cohorts=cohorts)
    strategy_summary.to_csv(tables_dir / f"{config_path.stem}_strategy_summary.csv", index=False)
    gee_results = strategy.run_strategy_gee(
        strategy_df,
        cohorts=cohorts,
        reports_dir=reports_dir,
        filename_prefix=config_path.stem,
    )
    annotations = strategy.build_significance_annotations(
        gee_results,
        reference=cohorts[0]["label"],
        cohort_order=[c["label"] for c in cohorts],
    )
    visuals.plot_strategy_bars(
        strategy_summary,
        figure_path=figures_dir / f"{config_path.stem}_gaze_strategy_comparison.png",
        title=f"\"{_condition_label(condition_codes)}\" - Strategy proportions",
        cohorts_order=[c["label"] for c in cohorts],
        annotations=annotations,
    )
    trend = strategy.run_linear_trend_test(
        strategy_df,
        infant_cohorts=[c for c in cohorts if "Adults" not in c["label"]],
        reports_dir=reports_dir,
        filename_prefix=config_path.stem,
    )
    visuals.plot_linear_trend(
        strategy_summary,
        trend,
        figure_path=figures_dir / f"{config_path.stem}_linear_trend_plot.png",
    )
    _write_strategy_summary(
        strategy_summary,
        gee_results,
        trend,
        reports_dir / f"{config_path.stem}_strategy_summary.txt",
    )

    _write_text_report(
        transitions_df,
        matrix_df,
        reports_dir / f"{config_path.stem}_transition_summary.txt",
        condition_codes,
    )


def _load_config(config_path: Path) -> Dict:
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data


def _determine_output_root(config: Dict, config_path: Path) -> Path:
    configured = config.get("output_dir")
    if configured:
        return Path(configured).expanduser().resolve()
    return (config_path.parent / config_path.stem).resolve()


def _condition_label(codes: List[str]) -> str:
    mapping = {
        "gw": "Give",
        "sw": "Show",
        "gwo": "Give (no toy)",
        "swo": "Show (no toy)",
    }
    first = codes[0].lower() if codes else ""
    return mapping.get(first, first.upper() or "Condition")


def _write_text_report(
    transitions_df: pd.DataFrame,
    matrix_df: pd.DataFrame,
    output_path: Path,
    condition_codes: List[str],
) -> None:
    total_transitions = int(transitions_df["count"].sum()) if not transitions_df.empty else 0
    lines = [
        f"Condition: {_condition_label(condition_codes)}",
        f"Total transitions counted: {total_transitions}",
        "",
        "Top cohort transition pairs:",
    ]
    if not matrix_df.empty:
        for cohort, cohort_df in matrix_df.groupby("cohort"):
            lines.append(f"{cohort}:")
            top = (
                cohort_df.sort_values("mean_count", ascending=False)
                .head(5)
                .reset_index(drop=True)
            )
            for row in top.itertuples():
                lines.append(
                    f"  {row.from_aoi} -> {row.to_aoi}: mean {row.mean_count:.2f}"
                )
            lines.append("")
    else:
        lines.append("No transitions available.")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_strategy_summary(summary_df: pd.DataFrame, gee_df: pd.DataFrame, trend: Dict[str, float] | None, output_path: Path) -> None:
    lines = ["Cohort,Social_Verification,Object_Face,Mechanical"]
    if summary_df.empty:
        lines.append("N/A,N/A,N/A,N/A")
    else:
        for row in summary_df.itertuples():
            lines.append(
                f"{row.cohort},{row.social_verification_mean:.3f},{row.object_face_linking_mean:.3f},{row.mechanical_tracking_mean:.3f}"
            )
    lines.append("")
    lines.append("Cohort,GEE_coef,GEE_pvalue")
    if gee_df is None or gee_df.empty:
        lines.append("N/A,N/A,N/A")
    else:
        for row in gee_df.itertuples():
            lines.append(f"{row.cohort},{row.coef:.3f},{row.pvalue}")
    if trend:
        lines.append("")
        lines.append(
            f"Linear trend coef={trend.get('coef', 0):.3f}, p={trend.get('pvalue')}"
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run gaze transition analysis.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("project_extension/analyses/gaze_transition_analysis/config.yaml"),
        help="YAML config path.",
    )
    args = parser.parse_args()
    run_analysis(args.config.expanduser().resolve())


if __name__ == "__main__":
    main()

