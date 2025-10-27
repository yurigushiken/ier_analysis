"""Raw CSV loading facilities with structural validation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from src.utils.config import load_config
from src.utils.validation import DataValidationError, load_contract, validate_dataframe_against_contract

LOGGER = logging.getLogger("ier.preprocessing.csv_loader")


def discover_csv_files(directory: Path | str, *, pattern: str = "*.csv") -> List[Path]:
    base_path = Path(directory).resolve()
    if not base_path.exists() or not base_path.is_dir():
        raise FileNotFoundError(f"CSV directory not found: {base_path}")
    files = sorted(base_path.glob(pattern))
    return [path for path in files if path.is_file()]


def load_csv_files(
    directories: Iterable[Path | str],
    *,
    contract_path: Path | str,
    config: Optional[dict] = None,
) -> pd.DataFrame:
    cfg = config or load_config()
    concat_frames: List[pd.DataFrame] = []
    contract = load_contract(contract_path)

    for directory in directories:
        files = discover_csv_files(directory)
        if not files:
            LOGGER.warning("No CSV files discovered in %s", directory)
        for csv_path in files:
            LOGGER.info("Loading raw CSV: %s", csv_path)
            frame = pd.read_csv(csv_path)
            try:
                validate_dataframe_against_contract(frame, contract, strict_columns=False)
            except DataValidationError as exc:
                LOGGER.error("Validation failed for %s: %s", csv_path, exc)
                raise
            frame["source_file"] = str(csv_path)
            concat_frames.append(frame)

    if not concat_frames:
        raise FileNotFoundError("No CSV files loaded from provided directories")

    combined = pd.concat(concat_frames, ignore_index=True)
    LOGGER.info("Loaded %d records from %d files", len(combined), len(concat_frames))
    return combined


__all__ = ["discover_csv_files", "load_csv_files"]
