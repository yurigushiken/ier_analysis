"""Visualization helpers for transition matrices."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, List

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEFAULT_DPI = 300


def plot_heatmap(
    matrix_df: pd.DataFrame,
    *,
    aoi_nodes: Sequence[str],
    cohorts: Sequence[str],
    figure_path: Path,
    title: str,
) -> None:
    """Plot a cohort-stacked heatmap."""
    if matrix_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No transitions available", ha="center", va="center", fontsize=12)
        fig.savefig(figure_path, dpi=DEFAULT_DPI)
        plt.close(fig)
        return

    from_to = [(frm, to) for frm in aoi_nodes for to in aoi_nodes if frm != to]
    num_rows = len(cohorts)
    fig, axes = plt.subplots(num_rows, 1, figsize=(max(6, len(from_to) * 0.5), 3 * num_rows))
    if num_rows == 1:
        axes = [axes]

    for ax, cohort in zip(axes, cohorts):
        cohort_df = matrix_df[matrix_df["cohort"] == cohort]
        data = []
        labels = []
        for frm, to in from_to:
            row = cohort_df[
                (cohort_df["from_aoi"] == frm) & (cohort_df["to_aoi"] == to)
            ]
            value = row["mean_count"].iloc[0] if not row.empty else 0.0
            data.append(value)
            labels.append(f"{frm}\n→ {to}")
        ax.imshow(np.array([data]), aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=9)
        ax.set_yticks([])
        ax.set_ylabel(cohort, rotation=0, labelpad=40, fontsize=11)
    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=DEFAULT_DPI)
    plt.close(fig)


def plot_strategy_bars(
    summary_df: pd.DataFrame,
    *,
    figure_path: Path,
    title: str,
    cohorts_order: Sequence[str],
    annotations: Sequence[Dict[str, object]],
) -> None:
    """Render grouped bar chart for strategy proportions."""
    if summary_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No strategy data", ha="center", va="center", fontsize=12)
        fig.savefig(figure_path, dpi=DEFAULT_DPI)
        plt.close(fig)
        return
    strategies = [
        ("social_verification_mean", "Social Verification", "#1f77b4"),
        ("object_face_linking_mean", "Object-Face Linking", "#ff7f0e"),
        ("mechanical_tracking_mean", "Mechanical Tracking", "#2ca02c"),
    ]
    cohorts = cohorts_order
    summary_df = summary_df.copy()
    summary_df["cohort"] = pd.Categorical(summary_df["cohort"], categories=cohorts, ordered=True)
    summary_df = summary_df.sort_values("cohort")
    x = np.arange(len(cohorts))
    width = 0.25
    fig, ax = plt.subplots(figsize=(max(8, len(cohorts) * 1.2), 5))
    for idx, (col, label, color) in enumerate(strategies):
        ax.bar(
            x + (idx - 1) * width,
            summary_df[col],
            width=width,
            label=label,
            color=color,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(cohorts, rotation=30, ha="right")
    ax.set_ylabel("Mean proportion of transitions")
    ax.set_ylim(0, 1)
    ax.set_title(title)
    ax.legend()

    for ann in annotations:
        frm = ann["from_idx"]
        to = ann["to_idx"]
        y = max(summary_df.iloc[[frm, to]]["social_verification_mean"]) + 0.05
        ax.plot([x[frm], x[frm], x[to], x[to]], [y, y + 0.02, y + 0.02, y], color="black")
        ax.text((x[frm] + x[to]) / 2, y + 0.025, ann["label"], ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=DEFAULT_DPI)
    plt.close(fig)


def plot_linear_trend(
    summary_df: pd.DataFrame,
    trend_metrics: Dict[str, float] | None,
    *,
    figure_path: Path,
) -> None:
    if summary_df.empty or trend_metrics is None:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No data for linear trend", ha="center", va="center", fontsize=12)
        fig.savefig(figure_path, dpi=DEFAULT_DPI)
        plt.close(fig)
        return
    infants = summary_df[summary_df["cohort"].str.contains("month")]
    if infants.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No infant cohorts", ha="center", va="center", fontsize=12)
        fig.savefig(figure_path, dpi=DEFAULT_DPI)
        plt.close(fig)
        return
    x = infants["cohort"].str.extract(r"(\d+)").astype(int)[0]
    y = infants["social_verification_mean"]
    coef = trend_metrics.get("coef", 0)
    intercept = y.mean() - coef * x.mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, color="#1f77b4", label="Cohort mean")
    ax.plot(x, intercept + coef * x, color="#ff7f0e", label="Trend")
    ax.set_xlabel("Age (months)")
    ax.set_ylabel("Social Verification proportion")
    ax.set_ylim(0, 0.3)
    pvalue = trend_metrics.get("pvalue")
    ax.text(
        0.05,
        0.95,
        f"coef={coef:.3f}, p={pvalue}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
    )
    ax.legend()
    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=DEFAULT_DPI)
    plt.close(fig)

