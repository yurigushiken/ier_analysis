from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.utils.validation import (
    DataValidationError,
    load_contract,
    validate_dataframe_against_contract,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = PROJECT_ROOT / "specs" / "001-infant-event-analysis"
CONTRACT_PATH = SPEC_DIR / "contracts" / "raw_data_schema.json"


def _build_valid_dataframe() -> pd.DataFrame:
    data = {
        "Participant": ["Eight-0101-947"],
        "Frame Number": [1],
        "Time": ["00:00:00:001"],
        "What": ["man"],
        "Where": ["face"],
        "Onset": [0.0],
        "Offset": [0.033],
        "Blue Dot Center": ["(123.4, 567.8)"],
        "event_verified": ["gw"],
        "frame_count_event": [1],
        "trial_number": [1],
        "trial_number_global": [1],
        "frame_count_trial_number": [1],
        "segment": ["approach"],
        "frame_count_segment": [1],
        "participant_type": ["infant"],
        "participant_age_months": [8],
        "participant_age_years": [0.67],
    }
    return pd.DataFrame(data)


def test_raw_csv_contract_accepts_valid_dataframe():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()

    validate_dataframe_against_contract(df, contract)


def test_raw_csv_contract_rejects_missing_required_columns():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe().drop(columns=["Where"])

    with pytest.raises(DataValidationError):
        validate_dataframe_against_contract(df, contract)
