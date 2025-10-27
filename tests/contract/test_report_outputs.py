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
CONTRACT_PATH = SPEC_DIR / "contracts" / "report_schema.json"


def _build_valid_dataframe() -> pd.DataFrame:
    data = {
        "report_id": ["AR-1"],
        "analysis_type": ["Gaze Duration"],
        "generation_timestamp": ["2025-10-25T12:00:00Z"],
        "files": [
            {
                "html": {
                    "path": "results/AR1/report.html",
                    "exists": True,
                    "size_bytes": 1024,
                    "format": "HTML",
                },
                "pdf": {
                    "path": "results/AR1/report.pdf",
                    "exists": True,
                    "size_bytes": 2048,
                    "format": "PDF",
                },
                "figures": [
                    {
                        "path": "results/AR1/figures/duration.png",
                        "exists": True,
                        "format": "PNG",
                        "dpi": 300,
                        "figure_type": "bar_chart",
                        "description": "Duration by condition",
                    }
                ],
                "tables": [
                    {
                        "path": "results/AR1/tables/summary.csv",
                        "exists": True,
                        "format": "CSV",
                        "table_type": "summary_statistics",
                        "description": "Summary statistics",
                    }
                ],
            }
        ],
        "statistical_results": [
            {
                "tests_performed": [
                    {
                        "test_name": "mixed_effects_model",
                        "comparison": "GIVE vs HUG",
                        "statistic": 2.35,
                        "p_value": 0.02,
                        "effect_size": {"measure": "cohens_d", "value": 0.5},
                    }
                ]
            }
        ],
        "metadata": [
            {
                "data_source": "data/processed/gaze_events.csv",
                "config_version": "1.0.0",
                "participants_included": 40,
                "participants_excluded": 2,
                "exclusion_reasons": ["n < 3"],
            }
        ],
    }
    return pd.DataFrame(data)


def test_report_contract_accepts_valid_dataframe():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()

    validate_dataframe_against_contract(df, contract)


def test_report_contract_rejects_missing_file_entries():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()
    df.loc[0, "files"]["html"]["exists"] = False

    with pytest.raises(DataValidationError):
        validate_dataframe_against_contract(df, contract)


def test_report_contract_requires_statistical_results():
    contract = load_contract(CONTRACT_PATH)
    df = _build_valid_dataframe()
    df.loc[0, "statistical_results"] = {"tests_performed": []}

    with pytest.raises(DataValidationError):
        validate_dataframe_against_contract(df, contract)
