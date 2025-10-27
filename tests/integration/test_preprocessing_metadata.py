from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("pandera")

from src.preprocessing.master_log_generator import generate_master_log
from src.utils.config import load_config


@pytest.mark.skip(reason="Requires full preprocessing setup and fixtures")
def test_metadata_preservation(tmp_path: Path):
    config = load_config()
    contract_path = Path("specs/001-infant-event-analysis/contracts/raw_data_schema.json")
    output_path = tmp_path / "gaze_events.csv"

    generate_master_log(
        raw_directories=[tmp_path],
        contract_path=contract_path,
        output_path=output_path,
        config=config,
    )

    df = pd.read_csv(output_path)
    expected_columns = {
        "participant_id",
        "participant_type",
        "age_months",
        "age_group",
        "trial_number",
        "condition",
        "condition_name",
        "segment",
        "aoi_category",
    }
    assert expected_columns.issubset(df.columns)
