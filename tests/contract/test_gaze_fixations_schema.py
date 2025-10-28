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
CONTRACT_PATH = SPEC_DIR / "contracts" / "gaze_fixations_schema.json"


def _build_valid_dataframe() -> pd.DataFrame:
    data = {
        "gaze_fixation_id": [1],
        "participant_id": ["Eight-0101-947"],
        "participant_type": ["infant"],
        "age_months": [8],
        "age_group": ["8-month-olds"],
        "trial_number": [1],
        "condition": ["gw"],
        "condition_name": ["GIVE_WITH"],
        "segment": ["approach"],
        "aoi_category": ["woman_face"],
        "gaze_start_frame": [10],
        "gaze_end_frame": [12],
        "gaze_duration_frames": [3],
        "gaze_duration_ms": [100.0],
        "gaze_onset_time": [1.0],
        "gaze_offset_time": [1.1],
    }
    return pd.DataFrame(data)


def test_gaze_fixations_contract_accepts_valid_dataframe():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()

    validate_dataframe_against_contract(df, contract)


def test_gaze_fixations_contract_rejects_invalid_aoi_category():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()
    df.loc[0, "aoi_category"] = "invalid_aoi"

    with pytest.raises(DataValidationError):
        validate_dataframe_against_contract(df, contract)


def test_gaze_fixations_contract_rejects_duration_shorter_than_three_frames():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()
    df.loc[0, "gaze_duration_frames"] = 2

    with pytest.raises(DataValidationError):
        validate_dataframe_against_contract(df, contract)
