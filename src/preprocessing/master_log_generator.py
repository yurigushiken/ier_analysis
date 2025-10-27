"""Master gaze event log generation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from src.preprocessing.aoi_mapper import map_what_where_to_aoi
from src.preprocessing.csv_loader import load_csv_files
from src.preprocessing.gaze_detector import detect_gaze_events
from src.utils.config import load_config


def generate_master_log(
    *,
    raw_directories: Iterable[Path | str],
    contract_path: Path | str,
    output_path: Path | str | None = None,
    config: Optional[dict] = None,
) -> pd.DataFrame:
    cfg = config or load_config()
    df = load_csv_files(raw_directories, contract_path=contract_path, config=cfg)

    df["condition_name"] = df["event_verified"].map(lambda code: _map_condition_name(code, cfg))
    df["aoi_category"] = df.apply(lambda row: map_what_where_to_aoi(row["What"], row["Where"], config=cfg), axis=1)
    df["age_group"] = df.apply(lambda row: _map_age_to_group(row["participant_age_months"], cfg), axis=1)
    gaze_events = detect_gaze_events(df)

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        gaze_events.to_csv(path, index=False)

    return gaze_events


def _map_age_to_group(age_months: int, config: dict) -> str:
    age_groups = config.get("age_groups", {}).get("infant", [])
    for group in age_groups:
        if group["min_months"] <= age_months <= group["max_months"]:
            return group["label"]
    return "adult" if age_months >= config.get("age_groups", {}).get("adult_threshold_months", 216) else "unknown"


def _map_condition_name(code: str, config: dict) -> str:
    mapping = config.get("condition_mapping", {})
    return mapping.get(code, code)


__all__ = ["generate_master_log"]
