from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.preprocessing.master_log_generator import generate_master_log

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
CONTRACT_PATH = PROJECT_ROOT / "specs" / "001-infant-event-analysis" / "contracts" / "raw_data_schema.json"


def test_generate_master_log(tmp_path: Path):
    output = tmp_path / "gaze_fixations.csv"
    df = generate_master_log(
        raw_directories=[FIXTURE_DIR],
        contract_path=CONTRACT_PATH,
        output_path=output,
    )

    assert not df.empty
    assert "gaze_duration_frames" in df.columns
    assert output.exists()


def test_generate_master_log_condition_mapping(monkeypatch):
    config = {
        "condition_mapping": {"gw": "GIVE_WITH"},
        "age_groups": {
            "infant": [
                {"label": "8-month-olds", "min_months": 7, "max_months": 9},
            ],
            "adult_threshold_months": 216,
        },
    }

    result = generate_master_log(
        raw_directories=[FIXTURE_DIR],
        contract_path=CONTRACT_PATH,
        config=config,
    )

    assert result.iloc[0]["condition_name"] == "GIVE_WITH"
    assert result.iloc[0]["age_group"] == "8-month-olds"
