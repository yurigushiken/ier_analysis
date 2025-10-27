from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.preprocessing.csv_loader import discover_csv_files, load_csv_files
from src.utils.validation import DataValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
CONTRACT_PATH = PROJECT_ROOT / "specs" / "001-infant-event-analysis" / "contracts" / "raw_data_schema.json"


@pytest.fixture
def sample_data_dir(tmp_path: Path) -> Path:
    fixture_file = FIXTURE_DIR / "sample_raw_data.csv"
    dest = tmp_path / "sample_raw_data.csv"
    dest.write_text(fixture_file.read_text(), encoding="utf-8")
    return tmp_path


def test_discover_csv_files(sample_data_dir: Path) -> None:
    files = discover_csv_files(sample_data_dir)
    assert len(files) == 1
    assert files[0].name == "sample_raw_data.csv"


def test_load_csv_files_validate_contract() -> None:
    df = load_csv_files([FIXTURE_DIR], contract_path=CONTRACT_PATH)
    assert not df.empty
    assert "source_file" in df.columns


def test_load_csv_files_rejects_invalid_contract(monkeypatch) -> None:
    def _invalid(*args, **kwargs):
        raise DataValidationError("invalid")

    monkeypatch.setattr("src.utils.validation.validate_dataframe_against_contract", _invalid)

    with pytest.raises(DataValidationError):
        load_csv_files([FIXTURE_DIR], contract_path=CONTRACT_PATH)
