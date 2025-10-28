"""
Fixed version of _compute_key_transition_stats with:
1. ASCII arrows instead of corrupted UTF-8
2. Variance and sample size validation before t-tests
"""

def _compute_key_transition_stats(
    participant_probs: pd.DataFrame,
    key_transitions: Sequence[Dict[str, Any]],
    conditions: Sequence[str],
) -> List[KeyTransitionResult]:
    """Compute statistical comparisons for key transitions between conditions.

    Validates sample size and variance before conducting t-tests to prevent
    invalid statistical inference.
    """
    results: List[KeyTransitionResult] = []
    if len(conditions) < 2 or participant_probs.empty:
        return results

    condition_a, condition_b = conditions[0], conditions[1]

    # Constants for statistical validity
    MIN_SAMPLE_SIZE = 2
    MIN_VARIANCE = 1e-10

    for spec in key_transitions:
        label = spec.get("label")
        from_spec = spec.get("from_aoi", spec.get("from"))
        to_spec = spec.get("to_aoi", spec.get("to"))

        from_a = _resolve_aoi_spec(from_spec, condition_a)
        to_a = _resolve_aoi_spec(to_spec, condition_a)
        from_b = _resolve_aoi_spec(from_spec, condition_b)
        to_b = _resolve_aoi_spec(to_spec, condition_b)

        if not from_a or not to_a or not from_b or not to_b:
            continue

        if not label:
            label = f"{from_a} -> {to_a}"

        group_a = participant_probs[
            (participant_probs["condition_name"] == condition_a)
            & (participant_probs["from_aoi"] == from_a)
            & (participant_probs["to_aoi"] == to_a)
        ]["probability"].dropna()

        group_b = participant_probs[
            (participant_probs["condition_name"] == condition_b)
            & (participant_probs["from_aoi"] == from_b)
            & (participant_probs["to_aoi"] == to_b)
        ]["probability"].dropna()

        condition_a_transition = f"{condition_a} ({from_a} -> {to_a})"
        condition_b_transition = f"{condition_b} ({from_b} -> {to_b})"

        # Check if groups are empty
        if group_a.empty or group_b.empty:
            results.append(
                KeyTransitionResult(
                    label=label,
                    condition_a=condition_a,
                    condition_a_transition=condition_a_transition,
                    condition_b=condition_b,
                    condition_b_transition=condition_b_transition,
                    mean_a=float(group_a.mean()) if not group_a.empty else float('nan'),
                    mean_b=float(group_b.mean()) if not group_b.empty else float('nan'),
                    t_stat=None,
                    p_value=None,
                    df=None,
                    ci_lower=None,
                    ci_upper=None,
                    cohens_d=None,
                    n_a=len(group_a),
                    n_b=len(group_b),
                    note="Insufficient data for statistical test",
                )
            )
            continue

        mean_a = float(group_a.mean())
        mean_b = float(group_b.mean())

        # Validate statistical requirements before conducting t-test
        var_a = group_a.var(ddof=1)
        var_b = group_b.var(ddof=1)

        insufficient_sample = len(group_a) < MIN_SAMPLE_SIZE or len(group_b) < MIN_SAMPLE_SIZE
        insufficient_variance = var_a <= MIN_VARIANCE or var_b <= MIN_VARIANCE

        if insufficient_sample or insufficient_variance:
            # Descriptive statistics only - cannot conduct valid inference
            results.append(
                KeyTransitionResult(
                    label=label,
                    condition_a=condition_a,
                    condition_a_transition=condition_a_transition,
                    condition_b=condition_b,
                    condition_b_transition=condition_b_transition,
                    mean_a=mean_a,
                    mean_b=mean_b,
                    t_stat=None,
                    p_value=None,
                    df=None,
                    ci_lower=None,
                    ci_upper=None,
                    cohens_d=None,
                    n_a=len(group_a),
                    n_b=len(group_b),
                    note="Descriptive only - insufficient variance or sample size",
                )
            )
            continue

        # Conduct Welch's t-test
        t_result = stats.ttest_ind(group_a, group_b, equal_var=False)
        t_stat = float(t_result.statistic)
        p_value = float(t_result.pvalue)

        # Compute Welch-Satterthwaite degrees of freedom
        df = ((var_a / len(group_a)) + (var_b / len(group_b))) ** 2
        df /= (
            (var_a ** 2) / ((len(group_a) ** 2) * (len(group_a) - 1))
            + (var_b ** 2) / ((len(group_b) ** 2) * (len(group_b) - 1))
        )

        # Compute 95% confidence interval for the difference
        diff = mean_a - mean_b
        se = math.sqrt(var_a / len(group_a) + var_b / len(group_b))
        if se and math.isfinite(se):
            df_for_ci = max(df, 1)
            t_crit = stats.t.ppf(0.975, df_for_ci)
            ci_lower = diff - t_crit * se
            ci_upper = diff + t_crit * se
        else:
            ci_lower = ci_upper = None

        # Compute Cohen's d effect size
        pooled_sd = math.sqrt(
            ((len(group_a) - 1) * var_a + (len(group_b) - 1) * var_b)
            / (len(group_a) + len(group_b) - 2)
        )
        cohens_d = diff / pooled_sd if pooled_sd else None

        results.append(
            KeyTransitionResult(
                label=label,
                condition_a=condition_a,
                condition_a_transition=condition_a_transition,
                condition_b=condition_b,
                condition_b_transition=condition_b_transition,
                mean_a=mean_a,
                mean_b=mean_b,
                t_stat=t_stat,
                p_value=p_value,
                df=df,
                ci_lower=ci_lower,
                ci_upper=ci_upper,
                cohens_d=cohens_d,
                n_a=len(group_a),
                n_b=len(group_b),
            )
        )

    return results
