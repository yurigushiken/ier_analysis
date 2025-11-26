"""Visualization helpers for transition matrices."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, List, Dict, Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import networkx as nx
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
    subtitle: str = "",
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
        positions = np.arange(len(labels)) + 0.5
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=9)
        ax.set_xlim(0, len(labels))
        ax.set_yticks([])
        ax.set_ylabel(cohort, rotation=0, labelpad=40, fontsize=11)
    full_title = title if not subtitle else f"{title}\n{subtitle}"
    fig.suptitle(full_title, fontsize=14)
    plt.subplots_adjust(top=0.8, bottom=0.2, left=0.12, right=0.95)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=DEFAULT_DPI)
    plt.close(fig)


NODE_LAYOUT = {
    "man_face": (-0.6, 0.8),
    "man_body": (-0.6, 0.4),
    "woman_face": (0.6, 0.8),
    "woman_body": (0.6, 0.4),
    "toy_present": (0.0, 0.5),
    "toy_location": (0.0, 0.6),
}


def plot_transition_networks(
    matrix_df: pd.DataFrame,
    *,
    cohorts: Sequence[str],
    aoi_nodes: Sequence[str],
    figures_dir: Path,
    filename_prefix: str,
    threshold: float = 0.02,
) -> None:
    """Draw network graphs per cohort showing transition probabilities."""
    if matrix_df.empty:
        return
    figures_dir.mkdir(parents=True, exist_ok=True)
    for cohort in cohorts:
        cohort_df = matrix_df[matrix_df["cohort"] == cohort]
        if cohort_df.empty:
            continue
        total = cohort_df["mean_count"].sum()
        if total <= 0:
            continue
        G = nx.DiGraph()
        for node in aoi_nodes:
            if node == "off_screen":
                continue
            G.add_node(node)
        for row in cohort_df.itertuples():
            if row.from_aoi == row.to_aoi:
                continue
            probability = row.mean_count / total
            if probability < threshold:
                continue
            G.add_edge(row.from_aoi, row.to_aoi, weight=probability)
        if not G.edges:
            continue
        positions = {node: NODE_LAYOUT.get(node, (0.0, 0.0)) for node in G.nodes}
        weights = [max(0.5, edge_data["weight"] * 10) for _, _, edge_data in G.edges(data=True)]
        fig, ax = plt.subplots(figsize=(6, 5))
        nx.draw_networkx_nodes(G, positions, node_color="#f4f1de", edgecolors="#333333", node_size=1200, ax=ax)
        nx.draw_networkx_labels(G, positions, font_size=10, font_weight="bold", ax=ax)
        nx.draw_networkx_edges(
            G,
            positions,
            arrowstyle="-|>",
            arrowsize=15,
            edge_color="#1d3557",
            width=weights,
            ax=ax,
        )
        edge_labels = {(u, v): f"{data['weight']*100:.1f}%" for u, v, data in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, positions, edge_labels=edge_labels, font_size=8, ax=ax)
        ax.set_title(f"{filename_prefix} - {cohort}")
        ax.axis("off")
        safe_label = cohort.lower().replace(" ", "_").replace("/", "_")
        fig.savefig(figures_dir / f"{filename_prefix}_network_{safe_label}.png", dpi=DEFAULT_DPI)
        plt.close(fig)


def plot_single_strategy_bars(
    summary_df: pd.DataFrame,
    *,
    value_column: str,
    label: str,
    figure_path: Path,
    title: str,
    cohorts_order: Sequence[str],
    color: str,
    annotations: Optional[Sequence[Dict[str, object]]] = None,
    reference_label: str | None = None,
) -> None:
    """Render a single-strategy bar chart with optional annotations."""
    if summary_df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.axis("off")
        ax.text(0.5, 0.5, "No strategy data", ha="center", va="center", fontsize=12)
        fig.savefig(figure_path, dpi=DEFAULT_DPI)
        plt.close(fig)
        return
    cohorts = list(cohorts_order)
    if reference_label and reference_label in cohorts:
        cohorts = [reference_label] + [c for c in cohorts if c != reference_label]
    reference_label = cohorts_order[0] if cohorts_order else None
    working = (
        summary_df.set_index("cohort")
        .reindex(cohorts)
        .reset_index()
        .rename(columns={"index": "cohort"})
    )
    x = np.arange(len(cohorts))
    values = working[value_column].fillna(0.0).to_numpy()

    reference_idx = next((i for i, cohort in enumerate(cohorts) if cohort == reference_label), None)
    fig, ax = plt.subplots(figsize=(max(6, len(cohorts) * 0.9), 4.8))
    bar_colors = [color] * len(cohorts)
    if reference_idx is not None:
        bar_colors[reference_idx] = "#f4a261"
    ax.bar(x, values, color=bar_colors, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(cohorts, rotation=30, ha="right")
    ax.set_ylabel("Mean proportion of transitions")
    ax.set_ylim(0, min(1.0, max(0.35, values.max() + 0.15)))
    ax.set_title(title)

    max_bar = values.max() if len(values) else 0
    if annotations:
        for ann in annotations:
            idx = ann["to_idx"]
            symbol = ann.get("label", "*")
            y = values[idx] + 0.03 * max(1.0, max_bar)
            ax.text(x[idx], y, symbol, ha="center", va="bottom", fontsize=11)

    plt.tight_layout()
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=DEFAULT_DPI)
    plt.close(fig)


def plot_linear_trend(
    summary_df: pd.DataFrame,
    trend_metrics: Dict[str, float] | None,
    *,
    figure_path: Path,
    value_column: str,
    label: str,
    title: str,
    y_axis_label: str | None = None,
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
    y = infants[value_column]
    coef = trend_metrics.get("coef", 0)
    intercept = y.mean() - coef * x.mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, color="#1f77b4", label="Cohort mean")
    ax.plot(x, intercept + coef * x, color="#ff7f0e", label="Trend")
    ax.set_xlabel("Age (months)")
    xticks = sorted(x.unique())
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(val) for val in xticks])
    axis_label = y_axis_label or f"{label} proportion"
    ax.set_ylabel(axis_label)
    upper = min(1.0, max(0.35, (y.max() if not y.empty else 0) + 0.1))
    ax.set_ylim(0, upper)
    ax.set_title(title)
    pvalue = trend_metrics.get("pvalue")
    ax.text(
        0.05,
        0.92,
        f"coef={coef:.3f}, p={pvalue:.3f}" if pvalue is not None else f"coef={coef:.3f}",
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

