# Verification: Unweighted GEE in Gaze Transition Analysis

## Summary

**The claim is VERIFIED.** The gaze-transition analysis currently treats all trials equally regardless of how many transitions were observed, which biases both coefficient estimates and p-values.

## The Issue

### What the code does:

1. **[strategy.py:52-77](c:\CascadeProjects\ier_analysis\project_extension\analyses\gaze_transition_analysis\strategy.py#L52-L77)**: `compute_strategy_proportions` correctly computes proportions and stores `total_transitions` for each trial
2. **[strategy.py:203-209](c:\CascadeProjects\ier_analysis\project_extension\analyses\gaze_transition_analysis\strategy.py#L203-L209)**: `run_strategy_gee` fits an **unweighted** Gaussian GEE using only the raw proportions
3. The `total_transitions` column is stored but **never used** in the statistical model

### The statistical problem:

For binomial proportions, the theoretical variance is:
```
Var(p) = p(1-p) / n
```

Where `n` is the number of transitions. This means:
- A trial with 2 transitions has ~4.5x more variance than a trial with 9 transitions
- But the current GEE assumes **the same variance** for all trials
- This gives trials with few observations the same statistical weight as trials with many observations

## Data Analysis

Using the actual data from `gw_transitions_min3_50_percent`:

### Distribution of total_transitions:
- **149 trials** from 55 participants
- Range: 1-9 transitions per trial
- Mean: 3.8 transitions
- Distribution:
  - 1 transition: 12 trials (8%)
  - 2 transitions: 23 trials (15%)
  - 3 transitions: 37 trials (25%)
  - 4 transitions: 32 trials (21%)
  - 5+ transitions: 45 trials (30%)

**35 trials (23%) have only 1-2 transitions**, but they're weighted equally with trials that have 5-9 transitions.

## Impact on Results

Comparing three approaches on agent-agent attention strategy:

| Cohort | Current (unweighted) | Weighted Gaussian | Binomial GEE |
|--------|---------------------|-------------------|--------------|
| **8-month-olds** | coef=0.002, p=0.976 | coef=-0.029, p=0.600 | coef=-0.442, p=0.597 |
| **9-month-olds** | coef=0.069, p=0.166 | coef=0.075, p=0.193 | coef=0.709, p=0.256 |
| **10-month-olds** | coef=0.119, p=0.064 | coef=0.105, p=0.110 | coef=0.913, p=0.156 |
| **11-month-olds** | coef=0.114, p=0.116 | coef=0.125, p=0.098 | coef=1.039, p=0.121 |
| **Adults** | coef=0.195, p=0.006 | coef=0.180, p=0.017 | coef=1.340, p=0.037 |

### Key findings:

1. **Coefficient estimates change** when weighting is applied, though the direction of effects is generally preserved
2. **P-values shift** - some effects become weaker, some stronger
3. **10-month-olds**: p=0.064 (current) vs p=0.110 (weighted) - crosses the marginal significance threshold
4. **Adults**: p=0.006 (current) vs p=0.017 (weighted) - still significant but weaker

Note: Binomial coefficients are on logit scale, so they're not directly comparable to Gaussian coefficients.

## Recommendations

### Immediate fix (minimal change):
Add `weights=total_transitions` to the GEE calls in `run_strategy_gee` and `run_linear_trend_test`:

```python
model = smf.gee(
    formula=formula,
    groups="participant_id",
    data=working,
    family=sm.families.Gaussian(),
    weights=working['total_transitions'],  # ADD THIS
)
```

This gives trials with more transitions more influence in the model.

### Better fix (theoretically correct):
Use binomial family with proper weights for proportion data:

```python
from statsmodels.genmod.generalized_estimating_equations import GEE
from patsy import dmatrices

y, X = dmatrices(formula, data=working, return_type='dataframe')
model = GEE(
    endog=y,
    exog=X,
    groups=working['participant_id'],
    family=sm.families.Binomial(),
    weights=working['total_transitions'],
)
```

Note: Binomial GEE produces coefficients on the logit scale, which would require updates to interpretation and plotting code.

## How Results Will Change

Based on the analysis of one dataset (agent-agent attention in gw condition):

1. **Direction of effects**: Generally preserved
2. **Magnitude**: Modest changes in coefficient estimates (typically <20% for weighted Gaussian)
3. **P-values**: Can shift by 0.01-0.05, potentially affecting marginal findings
4. **Conclusions**: Major findings likely robust, but marginal effects (p≈0.05-0.10) may change

### Specific concerns:
- **10-month-olds** showed p=0.064 (marginally significant) with current method, but p=0.110 (not significant) with proper weighting
- This could affect interpretation of developmental trajectories

## Files to Update

If implementing the fix:

1. [strategy.py:203-209](c:\CascadeProjects\ier_analysis\project_extension\analyses\gaze_transition_analysis\strategy.py#L203-L209) - `run_strategy_gee`
2. [strategy.py:264-269](c:\CascadeProjects\ier_analysis\project_extension\analyses\gaze_transition_analysis\strategy.py#L264-L269) - `run_linear_trend_test`
3. All existing results would need to be regenerated
4. Any manuscripts/presentations would need to be updated

## Conclusion

The claim is **100% accurate**:
- ✅ `total_transitions` is stored but ignored
- ✅ Current GEE treats all trials equally
- ✅ This violates the assumption that uncertainty scales with sample size
- ✅ Results are biased, particularly for comparisons where cohorts differ in typical transition counts

The impact is **moderate** - major findings appear robust, but some marginal effects may change significance status with proper weighting.
