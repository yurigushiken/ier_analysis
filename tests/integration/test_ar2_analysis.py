from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from src.analysis import ar2_transitions
from src.utils.config import load_config


def _make_fixation_rows(participant: str, age: int, condition: str) -> list[list[object]]:
    return [
        [participant, "infant" if age < 200 else "adult", age, f"{age}-group", 1, condition, condition, "interaction", "man_face", 0, 5, 5, 200, 0.0, 0.2],
        [participant, "infant" if age < 200 else "adult", age, f"{age}-group", 1, condition, condition, "interaction", "toy_present", 5, 10, 5, 200, 0.2, 0.4],
        [participant, "infant" if age < 200 else "adult", age, f"{age}-group", 1, condition, condition, "interaction", "woman_face", 10, 15, 5, 200, 0.4, 0.6],
        [participant, "infant" if age < 200 else "adult", age, f"{age}-group", 1, condition, condition, "interaction", "toy_present", 15, 20, 5, 200, 0.6, 0.8],
    ]


def _build_dataset(rows: list[list[object]]) -> pd.DataFrame:
    columns = [
        "participant_id",
        "participant_type",
        "age_months",
        "age_group",
        "trial_number",
        "condition",
        "condition_name",
        "segment",
        "aoi_category",
        "gaze_start_frame",
        "gaze_end_frame",
        "gaze_duration_frames",
        "gaze_duration_ms",
        "gaze_onset_time",
        "gaze_offset_time",
    ]
    return pd.DataFrame(rows, columns=columns)


@pytest.mark.parametrize("variant", ["AR2_gaze_transitions/ar2_gw_vs_gwo"])
def test_ar2_analysis_generates_expected_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variant: str) -> None:
    child_rows = (
        _make_fixation_rows("p7", 7, "GIVE_WITH")
        + _make_fixation_rows("p7", 7, "GIVE_WITHOUT")
        + _make_fixation_rows("p8", 8, "GIVE_WITH")
        + _make_fixation_rows("p8", 8, "GIVE_WITHOUT")
    )
    adult_rows = (
        _make_fixation_rows("a1", 216, "GIVE_WITH")
        + _make_fixation_rows("a1", 216, "GIVE_WITHOUT")
    )
    child_df = _build_dataset(child_rows)
    adult_df = _build_dataset(adult_rows)

    datasets: Dict[Path, pd.DataFrame] = {
        Path("data/processed/gaze_fixations_child.csv"): child_df,
        Path("data/processed/gaze_fixations_adult.csv"): adult_df,
    }

    monkeypatch.setattr(ar2_transitions, "_load_dataset", lambda path: datasets[path])

    overrides = [
        f"paths.results={tmp_path / 'results'}",
        f"analysis_specific.ar2_transitions.config_name={variant}",
    ]
    cfg = load_config(overrides=overrides)

    metadata = ar2_transitions.run(config=cfg)

    assert metadata["html_path"]
    report_path = Path(metadata["html_path"])
    assert report_path.exists()

    output_dir = report_path.parent
    figures_dir = output_dir / "figures"
    assert figures_dir.exists()

    generated_heatmaps = list(figures_dir.glob("*_heatmap_*"))
    generated_graphs = list(figures_dir.glob("*_graph_*"))
    # Expect at least one heatmap and directed graph
    assert generated_heatmaps
    assert generated_graphs
