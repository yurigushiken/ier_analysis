"""Tri-argument fixation analysis runner."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.backends.backend_pdf import PdfPages
import statsmodels.api as sm
import statsmodels.formula.api as smf


def run_analysis(config_path: Path) -> None:
    """Entry point for the tri-argument fixation analysis."""
    config = _load_config(config_path)
    output_root = _determine_output_root(config, config_path)
    reports_dir = output_root / "reports"
    figures_dir = output_root / "figures"
    tables_dir = output_root / "tables"
    for directory in (reports_dir, figures_dir, tables_dir):
        directory.mkdir(parents=True, exist_ok=True)

    df = _load_fixations(config)
    if df.empty:
        raise ValueError("No gaze fixation data available for the configured conditions.")

    trial_results = _compute_trial_metrics(
        df,
        aoi_groups=config["aoi_groups"],
        condition_codes=config["condition_codes"],
        frame_window=config.get("frame_window"),
    )
    trial_results = _filter_by_min_trials(
        trial_results, min_trials=config.get("min_trials_per_participant", 1)
    )
    trial_results["cohort"] = trial_results["participant_age_months"].apply(
        lambda age: _assign_cohort(age, config["cohorts"])
    )
    trial_results = trial_results.dropna(subset=["cohort"])
    if trial_results.empty:
        raise ValueError("All trials were filtered out after cohort assignment.")

    summary = _summarize_by_cohort(trial_results, config["cohorts"])
    summary_path = tables_dir / "tri_argument_summary.csv"
    summary.to_csv(summary_path, index=False)

    figure_path = figures_dir / "tri_argument_success.png"
    window = config.get("frame_window")
    base_title = config.get("plot_title") or f"{', '.join(config['condition_codes']).upper()} tri-argument fixation coverage by cohort"
    if window:
        chart_title = f"{base_title} (frames {window['start']}-{window['end']})"
    else:
        chart_title = base_title

    stats_summary = _run_gee_analysis(trial_results, reports_dir, config)
    _plot_success(
        summary,
        figure_path,
        title=chart_title,
        stats_summary=stats_summary,
        reference_label=(config.get("gee", {}) or {}).get("reference_cohort"),
    )

    if stats_summary is not None:
        forest_path = figures_dir / "forest_plot_odds_ratios.png"
        _plot_forest(
            stats_summary,
            forest_path,
            title=f"{base_title} - Odds ratios vs {(config.get('gee', {}) or {}).get('reference_cohort', 'reference cohort')}",
            reference_label=(config.get("gee", {}) or {}).get("reference_cohort"),
        )

    trials_fig_path = figures_dir / "trials_per_participant.png"
    _plot_trials_per_participant(
        trial_results,
        trials_fig_path,
        cohorts=config["cohorts"],
    )

    report_config = config.get("report", {})
    _write_text_report(summary, report_config, reports_dir)
    _write_html_report(summary, report_config, reports_dir, figure_path.relative_to(output_root))
    _write_pdf_report(summary, report_config, reports_dir, figure_path)


def _load_config(config_path: Path) -> Dict:
    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    return config


def _determine_output_root(config: Dict, config_path: Path) -> Path:
    configured = config.get("output_dir")
    if configured:
        return Path(configured).expanduser().resolve()
    config_stem = config_path.stem
    parent = config_path.parent
    if parent.name == "configs":
        analysis_root = parent.parent
    else:
        analysis_root = parent
    return (analysis_root / config_stem).resolve()


def _load_fixations(config: Dict) -> pd.DataFrame:
    threshold_dir = Path(config["input_threshold_dir"]).expanduser().resolve()
    filename = config.get("input_filename", "gaze_fixations_combined_min4.csv")
    input_path = threshold_dir / filename
    if not input_path.exists():
        raise FileNotFoundError(f"Gaze fixation file not found: {input_path}")
    return pd.read_csv(input_path)


def _compute_trial_metrics(
    df: pd.DataFrame,
    *,
    aoi_groups: Dict[str, List[str]],
    condition_codes: List[str],
    frame_window: Optional[Dict[str, int]] = None,
) -> pd.DataFrame:
    filtered = df[df["condition"].isin(condition_codes)].copy()
    if frame_window:
        start = frame_window["start"]
        end = frame_window["end"]
        filtered = filtered[
            (filtered["gaze_end_frame"] >= start) & (filtered["gaze_start_frame"] <= end)
        ].copy()
    grouped = filtered.groupby(["participant_id", "trial_number", "condition"], sort=False)

    rows: List[Dict[str, object]] = []
    for (participant_id, trial_number, condition), trial_df in grouped:
        row = trial_df.iloc[0]
        rows.append(
            {
                "participant_id": participant_id,
                "trial_number": trial_number,
                "condition": condition,
                "participant_type": row["participant_type"],
                "participant_age_months": row["participant_age_months"],
                "tri_argument_success": _has_all_aoi(trial_df, aoi_groups),
            }
        )
    return pd.DataFrame(rows)


def _has_all_aoi(trial_df: pd.DataFrame, aoi_groups: Dict[str, List[str]]) -> bool:
    for aois in aoi_groups.values():
        if not trial_df["aoi_category"].isin(aois).any():
            return False
    return True


def _filter_by_min_trials(trial_df: pd.DataFrame, *, min_trials: int) -> pd.DataFrame:
    if min_trials <= 1:
        return trial_df
    counts = trial_df.groupby("participant_id")["trial_number"].nunique()
    eligible = counts[counts >= min_trials].index
    return trial_df[trial_df["participant_id"].isin(eligible)].copy()


def _assign_cohort(age_months: float, cohorts: List[Dict[str, object]]) -> Optional[str]:
    for cohort in cohorts:
        if cohort["min_months"] <= age_months <= cohort["max_months"]:
            return cohort["label"]
    return None


def _summarize_by_cohort(trial_df: pd.DataFrame, cohorts: List[Dict[str, object]]) -> pd.DataFrame:
    summary = (
        trial_df.groupby("cohort")
        .agg(
            participants=("participant_id", "nunique"),
            total_trials=("trial_number", "count"),
            successful_trials=("tri_argument_success", "sum"),
        )
        .reset_index()
    )
    summary["success_rate"] = summary["successful_trials"] / summary["total_trials"]
    cohort_order = [c["label"] for c in cohorts]
    summary["cohort"] = pd.Categorical(summary["cohort"], categories=cohort_order, ordered=True)
    summary = summary.sort_values("cohort").reset_index(drop=True)
    return summary


def _plot_success(
    summary: pd.DataFrame,
    figure_path: Path,
    *,
    title: str,
    stats_summary: Optional[pd.DataFrame] = None,
    reference_label: Optional[str] = None,
) -> None:
    plt.figure(figsize=(8, 4))
    ax = plt.gca()
    x_pos = range(len(summary))
    ax.bar(x_pos, summary["success_rate"] * 100, color="#4C72B0")
    ax.set_ylabel("Tri-argument coverage (%)")
    ax.set_xlabel("Cohort")
    ax.set_ylim(0, 100)
    ax.set_title(title)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(summary["cohort"], rotation=30, ha="right")
    for idx, rate in enumerate(summary["success_rate"]):
        ax.text(idx, rate * 100 + 1, f"{rate * 100:.1f}%", ha="center", va="bottom", fontsize=8)

    if stats_summary is not None and reference_label is not None:
        bars = summary["success_rate"] * 100
        idx_map = {cohort: i for i, cohort in enumerate(summary["cohort"])}
        ref_idx = idx_map.get(reference_label)
        if ref_idx is not None:
            bump_tracker: Dict[tuple, float] = {}
            for _, row in stats_summary.iterrows():
                cohort = row["cohort"]
                if cohort == reference_label:
                    continue
                label = _format_significance(row["pvalue"])
                other_idx = idx_map.get(cohort)
                if not label or other_idx is None:
                    continue
                base_height = max(bars.iloc[ref_idx], bars.iloc[other_idx])
                key = (min(ref_idx, other_idx), max(ref_idx, other_idx))
                bump = bump_tracker.get(key, 0.0)
                y = base_height + 5 + bump
                ax.plot([ref_idx, ref_idx, other_idx, other_idx], [y, y + 2, y + 2, y], color="black", linewidth=1)
                ax.text((ref_idx + other_idx) / 2, y + 2.5, label, ha="center", va="bottom", fontsize=10)
                bump_tracker[key] = bump + 6

    if stats_summary is not None and reference_label is not None:
        footnote = f"* p < 0.05, ** p < 0.01, *** p < 0.001 vs {reference_label}"
        plt.subplots_adjust(bottom=0.2)
        ax.text(0.5, -0.18, footnote, transform=ax.transAxes, ha="center", va="top", fontsize=9)
    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(figure_path)
    plt.close()


def _plot_trials_per_participant(
    trial_results: pd.DataFrame,
    figure_path: Path,
    *,
    cohorts: List[Dict[str, object]],
) -> None:
    if trial_results.empty:
        return

    cohort_order = [c["label"] for c in cohorts]
    counts = (
        trial_results.groupby("participant_id")
        .agg(trial_count=("trial_number", "nunique"), cohort=("cohort", lambda x: x.iloc[0]))
        .reset_index()
    )
    counts["cohort"] = pd.Categorical(counts["cohort"], categories=cohort_order, ordered=True)
    counts = counts.sort_values(["cohort", "participant_id"])

    plt.figure(figsize=(max(8, len(counts) * 0.35), 4))
    colors = plt.cm.tab20.colors
    color_map = {label: colors[i % len(colors)] for i, label in enumerate(cohort_order)}
    bar_colors = [color_map.get(cohort, "#4C72B0") for cohort in counts["cohort"]]

    ax = plt.gca()
    ax.bar(range(len(counts)), counts["trial_count"], color=bar_colors)
    ax.set_ylabel("Valid trials")
    ax.set_xlabel("Participant")
    ax.set_title("Trials contributed per participant")
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts["participant_id"], rotation=60, ha="right", fontsize=8)
    legend_handles = [
        plt.Line2D([0], [0], color=color_map[label], lw=6, label=label)
        for label in cohort_order
        if label in counts["cohort"].values
    ]
    if legend_handles:
        ax.legend(handles=legend_handles, title="Cohort", bbox_to_anchor=(1.02, 1), loc="upper left")

    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(figure_path)
    plt.close()


def _write_text_report(summary: pd.DataFrame, report_cfg: Dict, reports_dir: Path) -> None:
    lines = [
        f"Research Question: {report_cfg.get('research_question', '')}",
        f"Hypothesis: {report_cfg.get('hypothesis', '')}",
        f"Prediction: {report_cfg.get('prediction', '')}",
        "",
        "Results:",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"- {row['cohort']}: {row['successful_trials']}/{row['total_trials']} "
            f"trials ({row['success_rate']*100:.1f}% coverage, "
            f"{int(row['participants'])} participants)"
        )
    report_path = reports_dir / "tri_argument_report.txt"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _write_html_report(summary: pd.DataFrame, report_cfg: Dict, reports_dir: Path, figure_rel_path: Path) -> None:
    table_html = summary.to_html(index=False, float_format=lambda x: f"{x:.2f}")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Tri-Argument Fixation Analysis</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    h1 {{ margin-bottom: 0; }}
    p {{ max-width: 800px; }}
    table {{ border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem 1rem; text-align: center; }}
  </style>
</head>
<body>
  <h1>Tri-Argument Fixation Analysis</h1>
  <p><strong>Research Question:</strong> {report_cfg.get("research_question", "")}</p>
  <p><strong>Hypothesis:</strong> {report_cfg.get("hypothesis", "")}</p>
  <p><strong>Prediction:</strong> {report_cfg.get("prediction", "")}</p>
  <h2>Results</h2>
  {table_html}
  <h2>Visualization</h2>
  <img src="../{figure_rel_path.as_posix()}" alt="Tri-argument coverage chart" width="600"/>
</body>
</html>
"""
    html_path = reports_dir / "tri_argument_report.html"
    html_path.write_text(html, encoding="utf-8")


def _write_pdf_report(summary: pd.DataFrame, report_cfg: Dict, reports_dir: Path, figure_path: Path) -> None:
    pdf_path = reports_dir / "tri_argument_report.pdf"
    text_lines = [
        "Tri-Argument Fixation Analysis",
        "",
        f"Research Question: {report_cfg.get('research_question', '')}",
        f"Hypothesis: {report_cfg.get('hypothesis', '')}",
        f"Prediction: {report_cfg.get('prediction', '')}",
        "",
        "Results:",
    ]
    for _, row in summary.iterrows():
        text_lines.append(
            f"- {row['cohort']}: {row['successful_trials']}/{row['total_trials']} trials "
            f"({row['success_rate']*100:.1f}%)"
        )

    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")
        y = 0.95
        for line in text_lines:
            wrapped = textwrap.wrap(line, 80) or [""]
            for sub_line in wrapped:
                ax.text(0.05, y, sub_line, ha="left", va="top", fontsize=11)
                y -= 0.04
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig2, ax2 = plt.subplots(figsize=(8.27, 11.69))
        img = plt.imread(figure_path)
        ax2.imshow(img)
        ax2.axis("off")
        pdf.savefig(fig2, bbox_inches="tight")
        plt.close(fig2)


def _run_gee_analysis(trial_results: pd.DataFrame, reports_dir: Path, config: Dict) -> None:
    gee_cfg = config.get("gee", {})
    if not gee_cfg.get("enabled"):
        return

    cohorts = [c["label"] for c in config.get("cohorts", [])]
    if not cohorts:
        raise ValueError("Cohorts must be defined to run GEE analysis.")

    reference = gee_cfg.get("reference_cohort", cohorts[0])
    if reference not in cohorts:
        cohorts = [reference] + [label for label in cohorts if label != reference]
    else:
        cohorts = [reference] + [label for label in cohorts if label != reference]

    data = trial_results[trial_results["cohort"].isin(cohorts)].copy()
    if data.empty:
        raise ValueError("No data available for GEE after cohort filtering.")

    data["tri_argument_success"] = data["tri_argument_success"].astype(int)
    data["cohort"] = pd.Categorical(data["cohort"], categories=cohorts, ordered=True)

    formula = f"tri_argument_success ~ C(cohort, Treatment(reference='{reference}'))"
    model = smf.gee(formula, groups="participant_id", data=data, family=sm.families.Binomial())
    result = model.fit()

    coef = result.params
    bse = result.bse
    z = coef / bse
    pvalues = result.pvalues
    ci = result.conf_int()

    trials_per_participant = data.groupby("participant_id").size()
    success_count = int(data["tri_argument_success"].sum())
    failure_count = int(len(data) - success_count)

    qic_attr = getattr(result, "qic", None)
    qic_value = None
    if callable(qic_attr):
        try:
            qic_value = qic_attr()
        except Exception:
            qic_value = None
    elif isinstance(qic_attr, (int, float)):
        qic_value = qic_attr
    elif isinstance(qic_attr, (tuple, list, np.ndarray)) and len(qic_attr) > 0:
        qic_value = qic_attr[0]
        while isinstance(qic_value, (tuple, list, np.ndarray)) and len(qic_value) > 0:
            qic_value = qic_value[0]

    if qic_value is not None:
        try:
            qic_display = f"{float(qic_value):.3f}"
        except Exception:
            qic_display = str(qic_value)
    else:
        qic_display = "unavailable"

    rows = [
        "GEE (Binomial, logit link) results",
        "Descriptive statistics:",
        f"  Trials per participant - min: {trials_per_participant.min()}, max: {trials_per_participant.max()}, mean: {trials_per_participant.mean():.2f}",
        f"  Class balance - successes: {success_count}, failures: {failure_count}",
        "",
        f"Observations: {len(data)}",
        f"Participants: {data['participant_id'].nunique()}",
        "",
        "Model diagnostics:",
        f"  QIC: {qic_display}",
        f"  Scale parameter: {result.scale:.3f}",
        f"  Covariance type: {getattr(result, 'cov_type', 'robust')}",
    ]
    cov_struct = getattr(result.model, "cov_struct", None)
    if cov_struct is not None and hasattr(cov_struct, "dep_params") and cov_struct.dep_params is not None:
        rows.append(f"  Working correlation parameter: {cov_struct.dep_params}")
    else:
        rows.append("  Working correlation parameter: not estimated (independence)")
    rows.append("")
    rows.append("Coefficient Summary (reference cohort: {})".format(reference))
    header = f"{'Term':<30}{'Coef':>10}{'Std Err':>12}{'z':>10}{'P>|z|':>10}{'[0.025':>12}{'0.975]':>12}"
    rows.append(header)
    for term in coef.index:
        rows.append(
            f"{term:<30}{coef[term]:>10.4f}{bse[term]:>12.4f}{z[term]:>10.3f}{pvalues[term]:>10.4f}"
            f"{ci.loc[term, 0]:>12.4f}{ci.loc[term, 1]:>12.4f}"
        )

    report_path = reports_dir / "gee_results.txt"
    report_path.write_text("\n".join(rows), encoding="utf-8")

    stats_rows = [{"cohort": reference, "coef": 0.0, "pvalue": None, "ci_low": 0.0, "ci_high": 0.0}]
    for cohort in cohorts[1:]:
        term = f"C(cohort, Treatment(reference='{reference}'))[T.{cohort}]"
        if term in coef.index:
            stats_rows.append(
                {
                    "cohort": cohort,
                    "coef": coef[term],
                    "pvalue": pvalues[term],
                    "ci_low": ci.loc[term, 0],
                    "ci_high": ci.loc[term, 1],
                }
            )

    return pd.DataFrame(stats_rows)


def _plot_forest(stats_summary: pd.DataFrame, figure_path: Path, *, title: str, reference_label: Optional[str] = None) -> None:
    plot_df = stats_summary.copy()
    plot_df["odds_ratio"] = np.exp(plot_df["coef"])
    plot_df["ci_low_or"] = np.exp(plot_df["ci_low"])
    plot_df["ci_high_or"] = np.exp(plot_df["ci_high"])

    y_pos = np.arange(len(plot_df))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1)

    or_values = plot_df["odds_ratio"]
    err_low = or_values - plot_df["ci_low_or"]
    err_high = plot_df["ci_high_or"] - or_values

    ax.errorbar(or_values, y_pos, xerr=[err_low, err_high], fmt="o", color="#4C72B0", ecolor="#4C72B0", capsize=4)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["cohort"])
    ax.set_xlabel("Odds ratio vs reference")
    ax.set_title(title)
    ax.set_xscale("log")
    ax.set_xlim(left=0.1, right=max(plot_df["ci_high_or"].max() * 1.2, 1.5))
    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(figure_path)
    plt.close()


def _format_significance(pvalue: Optional[float]) -> Optional[str]:
    if pvalue is None:
        return None
    if pvalue < 0.001:
        return "***"
    if pvalue < 0.01:
        return "**"
    if pvalue < 0.05:
        return "*"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tri-argument fixation analysis.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("project_extension/analyses/tri_argument_fixation/config.yaml"),
        help="Path to analysis configuration YAML file.",
    )
    args = parser.parse_args()
    run_analysis(args.config.expanduser().resolve())


if __name__ == "__main__":
    main()



