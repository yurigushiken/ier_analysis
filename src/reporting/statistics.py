"""Statistical utilities for reporting modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

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
    params: Optional[pd.Series] = None
    pvalues: Optional[pd.Series] = None
    conf_int: Optional[pd.DataFrame] = None
    aic: Optional[float] = None
    bic: Optional[float] = None
    effect_sizes: Optional[pd.DataFrame] = None
    dispersion: Optional[float] = None


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
    pooled_std = np.sqrt(
        ((x1.size - 1) * np.var(x1, ddof=1) + (x2.size - 1) * np.var(x2, ddof=1)) / (x1.size + x2.size - 2)
    )
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
        params=None,
        pvalues=None,
        conf_int=None,
        aic=None,
        bic=None,
        effect_sizes=None,
        dispersion=None,
    )


def fit_linear_mixed_model(
    formula: str,
    data: pd.DataFrame,
    *,
    groups_column: str,
    re_formula: str | None = "1",
    method: str = "lbfgs",
) -> GLMMResult:
    """Fit a linear mixed effects model using statsmodels.

    Parameters
    ----------
    formula : str
        Patsy-style formula specifying fixed effects.
    data : pd.DataFrame
        Dataset containing dependent variable, predictors, and grouping column.
    groups_column : str
        Column name defining grouping structure (random intercepts).
    re_formula : str | None, default="1"
        Formula for random effects; set to None for simple random intercept.
    method : str, default="lbfgs"
        Optimisation method passed to statsmodels MixedLM.fit.

    Returns
    -------
    GLMMResult
        Encapsulates convergence info, summary text, and warnings if any.
    """

    warnings: list[str] = []

    if groups_column not in data.columns:
        return GLMMResult(
            model_name="LinearMixedModel",
            converged=False,
            summary=f"Grouping column '{groups_column}' not found in dataset.",
            warnings=[f"Missing grouping column: {groups_column}"],
        )

    try:
        from statsmodels.formula.api import mixedlm

        model = mixedlm(
            formula,
            data=data,
            groups=data[groups_column],
            re_formula=re_formula,
        )
        fit = model.fit(method=method, reml=False)
        converged = bool(getattr(fit, "converged", False))
        summary_text = str(fit.summary())
        if not converged:
            warnings.append("Mixed model did not converge; interpret cautiously.")
        params = getattr(fit, "params", None)
        params_series = pd.Series(params) if params is not None else None
        pvalues = getattr(fit, "pvalues", None)
        if pvalues is not None and params_series is not None:
            pvalues = pd.Series(pvalues, index=params_series.index)
        try:
            conf_int = fit.conf_int()
            if isinstance(conf_int, np.ndarray):
                conf_int = pd.DataFrame(conf_int, index=params_series.index, columns=["lower", "upper"])
        except Exception:  # pragma: no cover - defensive
            conf_int = None
        return GLMMResult(
            model_name="LinearMixedModel",
            converged=converged,
            summary=summary_text,
            warnings=warnings,
            params=params_series,
            pvalues=pvalues,
            conf_int=conf_int,
            aic=getattr(fit, "aic", None),
            bic=getattr(fit, "bic", None),
            dispersion=None,
        )
    except ImportError as exc:
        return GLMMResult(
            model_name="LinearMixedModel",
            converged=False,
            summary="statsmodels is required for linear mixed models.",
            warnings=[f"Install statsmodels to enable LMM fitting: {exc}"],
            params=None,
            pvalues=None,
            conf_int=None,
            aic=None,
            bic=None,
            effect_sizes=None,
            dispersion=None,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return GLMMResult(
            model_name="LinearMixedModel",
            converged=False,
            summary=f"Failed to fit linear mixed model: {exc}",
            warnings=[str(exc)],
            params=None,
            pvalues=None,
            conf_int=None,
            aic=None,
            bic=None,
            effect_sizes=None,
            dispersion=None,
        )


def fit_generalized_linear_mixed_model(
    formula: str,
    data: pd.DataFrame,
    *,
    groups_column: str,
    family: str = "poisson",
    offset_column: Optional[str] = None,
    vc_formula: Optional[Dict[str, str]] = None,
    method: str = "lbfgs",
    maxiter: int = 200,
) -> GLMMResult:
    """Fit a generalized linear mixed model with a random intercept.

    Parameters
    ----------
    formula : str
        Patsy-style formula describing fixed effects.
    data : pd.DataFrame
        Dataset used for fitting.
    groups_column : str
        Column containing grouping factor for random intercepts.
    family : str, default="poisson"
        Response distribution family ("poisson" or "negative_binomial").
    offset_column : str, optional
        Column name to use as log-offset.
    vc_formula : dict, optional
        Variance component specification passed to statsmodels GLMM.
    method : str, default="lbfgs"
        Optimizer used by statsmodels.
    maxiter : int, default=200
        Maximum iterations for optimizer.
    """

    if data.empty:
        return GLMMResult(
            model_name="GLMM",
            converged=False,
            summary="Insufficient data to fit GLMM (no rows provided).",
            warnings=["Provide at least one observation to fit the GLMM."],
        )

    if groups_column not in data.columns:
        return GLMMResult(
            model_name="GLMM",
            converged=False,
            summary=f"Grouping column '{groups_column}' not found in dataset.",
            warnings=[f"Missing grouping column: {groups_column}"],
        )

    warnings_list: list[str] = []

    try:
        import statsmodels.api as sm
        from statsmodels.genmod.generalized_linear_mixed_model import GeneralizedLinearMixedModel
        has_frequentist_glmm = True
    except ImportError:
        GeneralizedLinearMixedModel = None
        has_frequentist_glmm = False

    if not has_frequentist_glmm:
        try:
            from statsmodels.genmod.bayes_mixed_glm import PoissonBayesMixedGLM
        except ImportError as exc:
            return GLMMResult(
                model_name="GLMM",
                converged=False,
                summary="statsmodels is required for GLMM fitting but does not provide a compatible implementation.",
                warnings=[f"Install statsmodels>=0.14 with GLMM support: {exc}"],
            )
    else:
        try:
            from statsmodels.genmod.bayes_mixed_glm import PoissonBayesMixedGLM  # pragma: no cover - optional
        except ImportError:
            PoissonBayesMixedGLM = None  # type: ignore[assignment]

    family_name = (family or "poisson").lower()
    if family_name == "poisson":
        family_obj = sm.families.Poisson()
    elif family_name in {"neg-binomial", "negativebinomial", "negative_binomial"}:
        family_obj = sm.families.NegativeBinomial()
        family_name = "negative_binomial"
    else:
        return GLMMResult(
            model_name="GLMM",
            converged=False,
            summary=f"Unsupported GLMM family '{family}'.",
            warnings=["Supported families: poisson, negative_binomial."],
        )

    design = data.copy()
    design[groups_column] = design[groups_column].astype("category")

    offset = None
    if offset_column:
        if offset_column not in design.columns:
            return GLMMResult(
                model_name="GLMM",
                converged=False,
                summary=f"Offset column '{offset_column}' not found in dataset.",
                warnings=[f"Missing offset column: {offset_column}"],
            )
        offset = design[offset_column].astype(float)

    vc = vc_formula or {groups_column: f"0 + C({groups_column})"}

    if has_frequentist_glmm and GeneralizedLinearMixedModel is not None:  # pragma: no cover - optional path
        try:
            model = GeneralizedLinearMixedModel.from_formula(
                formula,
                design,
                vc_formula=vc,
                family=family_obj,
                offset=offset,
            )
            fit = model.fit(method=method, maxiter=maxiter)
            converged = bool(getattr(fit, "converged", False))
            if not converged:
                warnings_list.append("GLMM did not converge; interpret results with caution.")
            params_series = pd.Series(fit.params, index=model.exog_names)
            try:
                conf_int = fit.conf_int()
                if isinstance(conf_int, np.ndarray):
                    conf_int_df = pd.DataFrame(conf_int, index=model.exog_names, columns=["lower", "upper"])
                else:
                    conf_int_df = conf_int.loc[model.exog_names]
            except Exception:  # pragma: no cover - defensive
                conf_int_df = None
            pvalues_series = pd.Series(getattr(fit, "pvalues", np.nan), index=model.exog_names)
            dispersion = None
            try:
                if getattr(fit, "df_resid", 0) > 0:
                    dispersion = float(getattr(fit, "deviance", np.nan) / fit.df_resid)
            except Exception:  # pragma: no cover - defensive
                dispersion = None

            effect_df = None
            if params_series is not None:
                effect_df = pd.DataFrame(
                    {
                        "Term": params_series.index,
                        "Estimate": params_series.values,
                        "Rate Ratio": np.exp(params_series.values),
                    }
                )
                if conf_int_df is not None:
                    effect_df["RR 95% CI Lower"] = np.exp(conf_int_df.iloc[:, 0].values)
                    effect_df["RR 95% CI Upper"] = np.exp(conf_int_df.iloc[:, 1].values)
                if pvalues_series is not None:
                    effect_df["p-value"] = pvalues_series.values

            return GLMMResult(
                model_name=f"GLMM-{family_name}",
                converged=converged,
                summary=str(fit.summary()),
                warnings=warnings_list,
                params=params_series,
                pvalues=pvalues_series,
                conf_int=conf_int_df,
                aic=getattr(fit, "aic", None),
                bic=getattr(fit, "bic", None),
                dispersion=dispersion,
                effect_sizes=effect_df,
            )
        except Exception as exc:  # pragma: no cover - defensive
            warnings_list.append(f"Frequentist GLMM fitting failed: {exc}")

    if family_name != "poisson":
        warnings_list.append("Only Poisson GLMM is supported; falling back to PoissonBayesMixedGLM.")
        return GLMMResult(
            model_name=f"GLMM-{family_name}",
            converged=False,
            summary="Only Poisson GLMM is supported in the current statsmodels installation.",
            warnings=warnings_list,
        )

    if offset_column:
        warnings_list.append(
            f"Offset column '{offset_column}' ignored because PoissonBayesMixedGLM does not support offsets."
        )

    try:
        model = PoissonBayesMixedGLM.from_formula(
            formula,
            vc,
            design,
        )
        fit = model.fit_map()
    except Exception as exc:  # pragma: no cover - defensive
        warnings_list.append(f"Failed to fit PoissonBayesMixedGLM: {exc}")
        return GLMMResult(
            model_name="PoissonBayesMixedGLM",
            converged=False,
            summary=f"Failed to fit Poisson Bayes mixed GLM: {exc}",
            warnings=warnings_list,
        )

    params_series = pd.Series(fit.params[: len(model.exog_names)], index=model.exog_names)
    cov = fit.cov_params().iloc[: len(model.exog_names), : len(model.exog_names)]
    se = np.sqrt(np.diag(cov))
    from scipy import stats  # local import to avoid top-level dependency during docs build

    z_scores = np.divide(params_series.values, se, out=np.zeros_like(params_series.values), where=se > 0)
    pvalues_series = pd.Series(2 * stats.norm.sf(np.abs(z_scores)), index=params_series.index)
    conf_int_df = pd.DataFrame(
        {
            "lower": params_series.values - 1.96 * se,
            "upper": params_series.values + 1.96 * se,
        },
        index=params_series.index,
    )

    effect_df = pd.DataFrame(
        {
            "Term": params_series.index,
            "Estimate": params_series.values,
            "Rate Ratio": np.exp(params_series.values),
            "RR 95% CI Lower": np.exp(conf_int_df["lower"].values),
            "RR 95% CI Upper": np.exp(conf_int_df["upper"].values),
            "p-value": pvalues_series.values,
        }
    )

    return GLMMResult(
        model_name="PoissonBayesMixedGLM",
        converged=True,
        summary=str(fit.summary()),
        warnings=warnings_list,
        params=params_series,
        pvalues=pvalues_series,
        conf_int=conf_int_df,
        effect_sizes=effect_df,
    )


__all__ = [
    "SummaryStats",
    "GLMMResult",
    "summarize",
    "cohens_d",
    "t_test",
    "proportion",
    "fit_glmm_placeholder",
    "fit_linear_mixed_model",
    "fit_generalized_linear_mixed_model",
]
