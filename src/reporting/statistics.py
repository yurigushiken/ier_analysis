"""Statistical utilities for reporting modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class SummaryStats:
    mean: float
    std: float
    sem: float
    count: int


@dataclass
class GLMMResult:
    model_name: str
    converged: bool
    summary: str
    warnings: list[str]


def summarize(data: Iterable[float]) -> SummaryStats:
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        raise ValueError("Cannot summarize empty data")
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    sem = float(stats.sem(arr)) if arr.size > 1 else 0.0
    return SummaryStats(mean=mean, std=std, sem=sem, count=int(arr.size))


def cohens_d(sample1: Iterable[float], sample2: Iterable[float]) -> float:
    x1 = np.asarray(list(sample1), dtype=float)
    x2 = np.asarray(list(sample2), dtype=float)
    if x1.size < 2 or x2.size < 2:
        raise ValueError("Each sample must contain at least two values")
    pooled_std = np.sqrt(((x1.size - 1) * np.var(x1, ddof=1) + (x2.size - 1) * np.var(x2, ddof=1)) / (x1.size + x2.size - 2))
    if pooled_std == 0:
        return 0.0
    return (float(np.mean(x1)) - float(np.mean(x2))) / float(pooled_std)


def t_test(sample1: Iterable[float], sample2: Iterable[float]) -> stats.ttest_indResult:
    x1 = np.asarray(list(sample1), dtype=float)
    x2 = np.asarray(list(sample2), dtype=float)
    return stats.ttest_ind(x1, x2, equal_var=False)


def proportion(dataframe: pd.DataFrame, column: str, condition: Optional[pd.Series] = None) -> float:
    series = dataframe[column]
    if condition is not None:
        series = series[condition]
    total = len(series)
    if total == 0:
        return 0.0
    return float(series.sum()) / float(total)


def fit_glmm_placeholder(*args, **kwargs) -> GLMMResult:
    return GLMMResult(
        model_name="GLMM-not-available",
        converged=False,
        summary="GLMM fitting skipped because statsmodels is not installed in this environment.",
        warnings=["Install statsmodels>=0.14 to enable GLMM analysis."],
    )


__all__ = [
    "SummaryStats",
    "GLMMResult",
    "summarize",
    "cohens_d",
    "t_test",
    "proportion",
    "fit_glmm_placeholder",
]
