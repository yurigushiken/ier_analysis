"""Validation utilities supporting pandera schemas and JSON contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

import pandas as pd
import pandera as pa
from pandas.api import types as ptypes


class DataValidationError(RuntimeError):
    """Raised when dataset validation fails."""


@dataclass(frozen=True)
class Contract:
    """Wrapper around a JSON contract document."""

    payload: Dict[str, Any]

    @classmethod
    def from_path(cls, path: Path | str) -> "Contract":
        contract_path = Path(path).resolve()
        try:
            content = contract_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise DataValidationError(f"Contract file not found: {contract_path}") from exc
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise DataValidationError(f"Invalid JSON contract at {contract_path}: {exc}") from exc
        return cls(payload=payload)

    def required_columns(self) -> Iterable[str]:
        definitions = self.payload.get("definitions", {})
        raw_record = definitions.get("RawFrameRecord", {})
        required = raw_record.get("required", [])
        return list(required)

    def column_definitions(self) -> Mapping[str, Mapping[str, Any]]:
        definitions = self.payload.get("definitions", {})
        raw_record = definitions.get("RawFrameRecord", {})
        properties = raw_record.get("properties", {})
        return properties if isinstance(properties, dict) else {}


def validate_with_schema(
    dataframe: pd.DataFrame,
    schema: pa.DataFrameSchema,
    *,
    lazy: bool = False,
) -> pd.DataFrame:
    """Validate a dataframe using a pandera schema, raising DataValidationError."""

    try:
        return schema.validate(dataframe, lazy=lazy)
    except pa.errors.SchemaErrors as exc:
        raise DataValidationError("Pandera schema validation failed") from exc
    except pa.errors.SchemaError as exc:
        raise DataValidationError("Pandera schema validation failed") from exc


_TYPE_CHECKS: Dict[str, Any] = {
    "integer": ptypes.is_integer_dtype,
    "number": ptypes.is_numeric_dtype,
    "string": lambda series: ptypes.is_object_dtype(series) or ptypes.is_string_dtype(series),
    "boolean": ptypes.is_bool_dtype,
}


def validate_dataframe_against_contract(
    dataframe: pd.DataFrame,
    contract: Contract | Dict[str, Any],
    *,
    strict_columns: bool = False,
) -> None:
    """Validate dataframe structure against a JSON contract definition."""

    contract_obj = contract if isinstance(contract, Contract) else Contract(payload=contract)
    required_columns = set(contract_obj.required_columns())
    column_defs = contract_obj.column_definitions()

    columns = set(dataframe.columns)
    missing_columns = required_columns - columns
    if missing_columns:
        raise DataValidationError(f"Missing required columns: {sorted(missing_columns)}")

    if strict_columns:
        extra = columns - set(column_defs.keys())
        if extra:
            raise DataValidationError(f"Unexpected columns present: {sorted(extra)}")

    for column in required_columns:
        if dataframe[column].isnull().any():
            raise DataValidationError(f"Column '{column}' contains null values but is required.")

    for column, definition in column_defs.items():
        if column not in dataframe.columns:
            continue
        expected_types = definition.get("type", [])
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if expected_types:
            _enforce_types(dataframe[column], column, expected_types)

        enum_values = definition.get("enum")
        if enum_values is not None:
            invalid_mask = ~dataframe[column].isin(enum_values)
            # Allow NaNs if column not required
            if invalid_mask.any():
                bad_values = sorted(set(map(str, dataframe[column][invalid_mask].dropna())))
                raise DataValidationError(f"Column '{column}' contains values not allowed by contract: {bad_values}")


def _enforce_types(series: pd.Series, column: str, expected_types: Iterable[str]) -> None:
    if "null" in expected_types and series.isnull().all():
        return

    for expected in expected_types:
        check = _TYPE_CHECKS.get(expected)
        if check is None:
            continue
        if check(series.dropna()):
            return
    raise DataValidationError(f"Column '{column}' does not match expected types {list(expected_types)}")


def load_contract(path: Path | str) -> Contract:
    """Convenience loader for contract documents."""

    return Contract.from_path(path)


__all__ = [
    "Contract",
    "DataValidationError",
    "load_contract",
    "validate_with_schema",
    "validate_dataframe_against_contract",
]
