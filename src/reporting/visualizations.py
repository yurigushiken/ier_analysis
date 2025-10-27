"""Visualization utilities for reporting modules."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def bar_plot(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    hue: str | None = None,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    output_path: Path | str | None = None,
    figsize: tuple[float, float] = (8, 6),
    rotate_labels: int = 0,
) -> Path | None:
    """Create a bar plot with optional grouped bars and rotated labels.
    
    Parameters
    ----------
    data : pd.DataFrame
        Data containing x and y columns
    x : str
        Column name for x-axis categories
    y : str
        Column name for y-axis values
    hue : str, optional
        Column name for grouping (creates grouped bars)
    title : str, optional
        Plot title
    xlabel : str, optional
        X-axis label (defaults to x column name)
    ylabel : str, optional
        Y-axis label (defaults to y column name)
    output_path : Path | str, optional
        Path to save figure
    figsize : tuple[float, float], default=(8, 6)
        Figure size in inches (width, height)
    rotate_labels : int, default=0
        Rotation angle for x-axis labels (0, 45, 90, etc.)
    
    Returns
    -------
    Path | None
        Path to saved figure, or None if not saved
    """
    plt.figure(figsize=figsize)
    
    if hue:
        categories = data[x].unique()
        hue_levels = data[hue].unique()
        width = 0.8 / len(hue_levels)
        for idx, level in enumerate(hue_levels):
            subset = data[data[hue] == level]
            positions = [i + idx * width for i in range(len(categories))]
            plt.bar(positions, subset[y], width=width, label=str(level))
        plt.xticks(
            [i + width * (len(hue_levels) - 1) / 2 for i in range(len(categories))],
            categories,
            rotation=rotate_labels,
            ha="right" if rotate_labels > 0 else "center"
        )
        plt.legend()
    else:
        plt.bar(data[x], data[y])
        if rotate_labels > 0:
            plt.xticks(rotation=rotate_labels, ha="right")

    plt.title(title or "", fontsize=14, pad=15)
    plt.ylabel(ylabel or y, fontsize=12)
    plt.xlabel(xlabel or x, fontsize=12)
    plt.tight_layout()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()
        return path

    return None


def line_plot(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    hue: str | None = None,
    title: str | None = None,
    ylabel: str | None = None,
    output_path: Path | str | None = None,
) -> Path | None:
    plt.figure(figsize=(8, 6))
    if hue:
        for level, subset in data.groupby(hue):
            plt.plot(subset[x], subset[y], marker="o", label=str(level))
        plt.legend()
    else:
        plt.plot(data[x], data[y], marker="o")

    plt.title(title or "")
    plt.ylabel(ylabel or y)
    plt.xlabel(x)
    plt.tight_layout()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    return None


def directed_graph(
    transitions: Mapping[tuple[str, str], float],
    node_durations: Mapping[str, float],
    *,
    title: str | None = None,
    output_path: Path | str | None = None,
) -> Path | None:
    graph = nx.DiGraph()
    for (source, target), weight in transitions.items():
        graph.add_edge(source, target, weight=weight)

    for node, duration in node_durations.items():
        graph.add_node(node, duration=duration)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, seed=42)
    node_sizes = [node_durations.get(node, 0.1) * 1000 for node in graph.nodes]
    nx.draw_networkx_nodes(graph, pos, node_size=node_sizes, node_color="#1f77b4", alpha=0.8)
    nx.draw_networkx_labels(graph, pos)

    edge_weights = [graph[u][v]["weight"] for u, v in graph.edges]
    nx.draw_networkx_edges(graph, pos, arrows=True, width=[max(weight, 0.1) * 5 for weight in edge_weights])
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels={(u, v): f"{data['weight']:.2f}" for u, v, data in graph.edges(data=True)},
    )

    plt.title(title or "")
    plt.axis("off")
    plt.tight_layout()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    return None


def line_plot_with_error_bars(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    hue: str | None = None,
    error_col: str = "sem",
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    output_path: Path | str | None = None,
) -> Path | None:
    """
    Create a line plot with error bars for developmental trajectory visualization.

    Args:
        data: DataFrame with data to plot
        x: Column name for x-axis (e.g., age_months)
        y: Column name for y-axis (e.g., mean)
        hue: Optional column for grouping lines (e.g., condition_name)
        error_col: Column name for error bars (default: "sem")
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        output_path: Path to save figure

    Returns:
        Path to saved figure, or None if not saved
    """
    plt.figure(figsize=(10, 7))

    if hue:
        hue_levels = data[hue].unique()
        cmap = plt.cm.get_cmap("tab10")
        colors = [cmap(i) for i in range(len(hue_levels))]

        for idx, level in enumerate(hue_levels):
            subset = data[data[hue] == level].sort_values(x)

            # Plot line with markers
            plt.plot(
                subset[x],
                subset[y],
                marker="o",
                label=str(level),
                color=colors[idx],
                linewidth=2,
                markersize=8,
            )

            # Add error bars if error_col exists
            if error_col in subset.columns:
                plt.fill_between(
                    subset[x],
                    subset[y] - subset[error_col],
                    subset[y] + subset[error_col],
                    alpha=0.2,
                    color=colors[idx],
                )

        plt.legend(loc="best", frameon=True, shadow=True)
    else:
        subset = data.sort_values(x)
        plt.plot(subset[x], subset[y], marker="o", linewidth=2, markersize=8)

        if error_col in subset.columns:
            plt.fill_between(
                subset[x],
                subset[y] - subset[error_col],
                subset[y] + subset[error_col],
                alpha=0.2,
            )

    plt.title(title or "", fontsize=14, fontweight="bold")
    plt.ylabel(ylabel or y, fontsize=12)
    plt.xlabel(xlabel or x, fontsize=12)
    plt.grid(True, alpha=0.3, linestyle="--")
    plt.tight_layout()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()
        return path

    return None


__all__ = ["bar_plot", "line_plot", "line_plot_with_error_bars", "directed_graph"]
