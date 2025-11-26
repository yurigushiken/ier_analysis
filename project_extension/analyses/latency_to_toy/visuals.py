"""Plotting utilities for latency-to-toy analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_latency_bar(
    summary_df: pd.DataFrame,
    *,
    figure_path: Path,
    title: str,
    cohort_order: Sequence[str],
    gee_results: pd.DataFrame,
    reference_label: str,
) -> None:
    """Render latency bar chart with adult reference annotations."""
    if summary_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No latency data available", ha="center", va="center", fontsize=12)
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(figure_path, dpi=300)
        plt.close(fig)
        return

    ordered = sorted(cohort_order, key=lambda label: (0 if "adult" in label.lower() else 1, cohort_order.index(label)))
    working = summary_df.set_index("cohort").reindex(ordered).reset_index()
    working = working.dropna(subset=["mean_latency_frames"])
    positions = np.arange(len(working))
    values = working["mean_latency_frames"].to_numpy()

    colors = ["#f4a261" if cohort == reference_label else "#4C72B0" for cohort in working["cohort"]]
    fig, ax = plt.subplots(figsize=(max(7, len(working) * 1.1), 6))
    ax.bar(positions, values, color=colors)
    ax.set_xticks(positions)
    ax.set_xticklabels(working["cohort"], rotation=30, ha="right")
    ax.set_ylabel("Mean latency to toy (frames)")
    ax.set_xlabel("Cohort")
    ax.set_ylim(0, max(10, values.max() * 1.4))
    ax.set_title(title, pad=20)
    for idx, value in enumerate(values):
        ax.text(positions[idx], value + 0.02 * max(10, values.max()), f"{value:.1f}f", ha="center", va="bottom", fontsize=10)

    idx_map = {cohort: idx for idx, cohort in enumerate(working["cohort"])}
    ref_idx = idx_map.get(reference_label)
    if gee_results is not None and ref_idx is not None:
        text_height = max(2, 0.05 * max(10, values.max()))
        for row in gee_results.itertuples():
            if np.isnan(row.pvalue) or row.cohort == reference_label or row.pvalue >= 0.05:
                continue
            other_idx = idx_map.get(row.cohort)
            if other_idx is None:
                continue
            y = values[other_idx] + text_height
            label = "***" if row.pvalue < 0.001 else "**" if row.pvalue < 0.01 else "*"
            ax.text(
                positions[other_idx],
                y,
                label,
                ha="center",
                va="bottom",
                fontsize=12,
            )
    plt.subplots_adjust(top=0.84, bottom=0.2, left=0.12, right=0.95)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)


def plot_latency_forest(
    gee_results: pd.DataFrame,
    *,
    cohort_order: Sequence[str],
    reference_label: str,
    figure_path: Path,
    title: str,
) -> None:
    """Forest plot showing latency differences vs adults."""
    if gee_results is None or gee_results.empty:
        return
    working = gee_results.set_index("cohort").reindex(cohort_order).reset_index()
    y_pos = np.arange(len(working))
    fig, ax = plt.subplots(figsize=(6, max(4, len(working) * 0.6)))
    ax.axvline(0.0, color="#555555", linestyle="--")
    effects = working["coef"].fillna(0.0).to_numpy()
    ci_low = working["ci_low"].fillna(0.0).to_numpy()
    ci_high = working["ci_high"].fillna(0.0).to_numpy()
    line_color = "#1f77b4"
    ax.errorbar(
        effects,
        y_pos,
        xerr=[effects - ci_low, ci_high - effects],
        fmt="o",
        color=line_color,
        ecolor=line_color,
        capsize=4,
        linewidth=2,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(working["cohort"])
    ax.set_xlabel("Latency difference vs Adults (frames)")
    ax.set_title(title)
    finite_high = ci_high[np.isfinite(ci_high)]
    finite_low = ci_low[np.isfinite(ci_low)]
    max_range = max(abs(finite_low.min() if finite_low.size else -1), abs(finite_high.max() if finite_high.size else 1), 1)
    ax.set_xlim(left=-max_range * 1.3, right=max_range * 1.3)
    for idx, row in enumerate(gee_results.itertuples()):
        if np.isnan(row.pvalue) or row.pvalue >= 0.05:
            continue
        label = "***" if row.pvalue < 0.001 else "**" if row.pvalue < 0.01 else "*"
        ax.text(effects[idx], y_pos[idx] + 0.1, label, ha="center", va="bottom", fontsize=12)
    plt.subplots_adjust(top=0.78, bottom=0.12, left=0.2, right=0.95)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)

