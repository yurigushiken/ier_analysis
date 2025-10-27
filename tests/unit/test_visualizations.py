from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.reporting.visualizations import bar_plot, directed_graph, line_plot, line_plot_with_error_bars


def test_bar_plot_creates_file(tmp_path: Path):
    data = pd.DataFrame({"condition": ["A", "B"], "value": [1.0, 2.0]})
    output = tmp_path / "bar.png"
    result = bar_plot(data, x="condition", y="value", output_path=output)
    assert result == output
    assert output.exists()


def test_line_plot_creates_file(tmp_path: Path):
    data = pd.DataFrame({"trial": [1, 2, 3], "value": [0.1, 0.2, 0.3]})
    output = tmp_path / "line.png"
    result = line_plot(data, x="trial", y="value", output_path=output)
    assert result == output
    assert output.exists()


def test_directed_graph_creates_file(tmp_path: Path):
    transitions = {("A", "B"): 0.5, ("B", "C"): 0.3}
    durations = {"A": 1.0, "B": 2.0, "C": 1.5}
    output = tmp_path / "graph.png"
    result = directed_graph(transitions, durations, output_path=output)
    assert result == output
    assert output.exists()


def test_line_plot_with_error_bars_creates_file(tmp_path: Path):
    """Test line plot with error bars for developmental trajectories."""
    data = pd.DataFrame({
        "age_months": [8, 10, 12, 8, 10, 12],
        "condition_name": ["GIVE", "GIVE", "GIVE", "HUG", "HUG", "HUG"],
        "mean": [0.5, 0.55, 0.6, 0.3, 0.32, 0.35],
        "sem": [0.05, 0.04, 0.06, 0.03, 0.04, 0.05],
    })
    output = tmp_path / "dev_trajectory.png"
    result = line_plot_with_error_bars(
        data,
        x="age_months",
        y="mean",
        hue="condition_name",
        error_col="sem",
        title="Developmental Trajectory",
        xlabel="Age (months)",
        ylabel="Proportion",
        output_path=output,
    )
    assert result == output
    assert output.exists()


def test_line_plot_with_error_bars_without_hue(tmp_path: Path):
    """Test line plot with error bars without grouping variable."""
    data = pd.DataFrame({
        "trial": [1, 2, 3, 4],
        "mean": [0.6, 0.55, 0.52, 0.5],
        "sem": [0.05, 0.04, 0.04, 0.03],
    })
    output = tmp_path / "habituation.png"
    result = line_plot_with_error_bars(
        data,
        x="trial",
        y="mean",
        error_col="sem",
        output_path=output,
    )
    assert result == output
    assert output.exists()


def test_bar_plot_with_hue(tmp_path: Path):
    """Test bar plot with grouping variable."""
    data = pd.DataFrame({
        "aoi": ["toy", "face", "toy", "face"],
        "condition": ["GIVE", "GIVE", "HUG", "HUG"],
        "value": [0.5, 0.3, 0.4, 0.4],
    })
    output = tmp_path / "grouped_bar.png"
    result = bar_plot(data, x="aoi", y="value", hue="condition", output_path=output)
    assert result == output
    assert output.exists()


def test_visualizations_return_none_without_output_path():
    """Test that visualizations return None when no output path specified."""
    data = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    result = bar_plot(data, x="x", y="y", output_path=None)
    assert result is None
