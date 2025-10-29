"""Small utilities for applying participant_filters from YAML in a tolerant way.

The repository uses simple membership filters in many AR modules; YAML can contain
numbers as strings ("7" / "7.0") or numeric literals. These helpers coerce and
compare in a forgiving way so filters don't drop rows unexpectedly.
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional

import pandas as pd
import numpy as np


def _as_number(x: Any) -> Any:
    try:
        return pd.to_numeric(x)
    except Exception:
        return np.nan


def apply_filters_tolerant(df: pd.DataFrame, filters: Optional[dict]) -> pd.DataFrame:
    """Apply simple equality membership filters with tolerant casting.

    Behaviour:
    - If filters is falsy, returns a copy of df.
    - For each (column -> allowed_values) pair, we attempt to match rows where the
      column value equals any allowed value. Matching is attempted both as numeric
      comparison (when possible) and as case-insensitive string comparison.
    - Unknown columns raise KeyError to keep existing checks explicit.
    """
    if not filters:
        return df.copy()

    out = df.copy()
    for column, allowed in filters.items():
        if column not in out.columns:
            raise KeyError(f"Filter column '{column}' not found in gaze fixations data.")

        if isinstance(allowed, (list, tuple, set)):
            allowed_values: List[Any] = list(allowed)
        else:
            allowed_values = [allowed]

        # Prepare sets for string and numeric matching
        allowed_str = {str(v).strip().lower() for v in allowed_values}
        allowed_nums = set()
        for v in allowed_values:
            num = _as_number(v)
            if not pd.isna(num):
                # use numpy scalar if possible
                try:
                    allowed_nums.add(float(num))
                except Exception:
                    pass

        series = out[column]

        if pd.api.types.is_numeric_dtype(series):
            # numeric column: prefer numeric matching but also allow string matches
            series_num = pd.to_numeric(series, errors="coerce")
            mask_num = series_num.isin(allowed_nums) if allowed_nums else pd.Series(False, index=series.index)
            mask_str = series.astype(str).str.strip().str.lower().isin(allowed_str)
            mask = mask_num | mask_str
        else:
            # non-numeric column: try string matching, but also coerce column to numeric
            mask_str = series.astype(str).str.strip().str.lower().isin(allowed_str)
            series_num = pd.to_numeric(series.astype(str), errors="coerce")
            mask_num = series_num.isin(allowed_nums) if allowed_nums else pd.Series(False, index=series.index)
            mask = mask_str | mask_num

        out = out[mask]

    return out
