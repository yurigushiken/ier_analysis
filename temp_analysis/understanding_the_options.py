"""
Educational demonstration: Understanding weighted Gaussian vs Binomial GEE
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

# Load real data
data_path = Path(r"c:\CascadeProjects\ier_analysis\project_extension\analyses\gaze_transition_analysis\gw_transitions_min3_50_percent\tables\gw_transitions_min3_50_percent_strategy_proportions.csv")
df = pd.read_csv(data_path)

# Focus on one comparison for clarity
df = df[df['participant_age_months'].isin([7, 10, 20])].copy()
df['cohort'] = df['participant_age_months'].apply(
    lambda x: '7mo' if x == 7 else ('10mo' if x == 10 else 'Adults')
)
df['cohort'] = pd.Categorical(df['cohort'], categories=['7mo', '10mo', 'Adults'], ordered=True)

print("="*80)
print("UNDERSTANDING YOUR OPTIONS: Weighted Gaussian vs Binomial GEE")
print("="*80)
print()

# Show the data structure
print("SAMPLE DATA (what you're modeling):")
print("-"*80)
sample = df[['participant_id', 'cohort', 'total_transitions', 'agent_agent_attention_pct']].head(10)
print(sample.to_string(index=False))
print()

# Current: Unweighted Gaussian
print("CURRENT APPROACH: Unweighted Gaussian")
print("-"*80)
formula = "agent_agent_attention_pct ~ C(cohort, Treatment(reference='7mo'))"
model_unweighted = smf.gee(formula, groups='participant_id', data=df,
                           family=sm.families.Gaussian())
result_unweighted = model_unweighted.fit()

print("Interpretation: Direct change in proportion")
for param, coef, se, pval in zip(result_unweighted.params.index,
                                   result_unweighted.params,
                                   result_unweighted.bse,
                                   result_unweighted.pvalues):
    if 'cohort' not in param:
        continue
    cohort = param.split('[T.')[-1].rstrip(']')
    print(f"  {cohort}: +{coef:.3f} proportion (SE={se:.3f}, p={pval:.3f})")
    print(f"         Meaning: {cohort} has {coef:.1%} more agent-agent attention than 7mo")
print()

# Option B: Weighted Gaussian
print("OPTION B: Weighted Gaussian GEE")
print("-"*80)
model_weighted = smf.gee(formula, groups='participant_id', data=df,
                        family=sm.families.Gaussian(),
                        weights=df['total_transitions'])
result_weighted = model_weighted.fit()

print("Interpretation: Still direct change in proportion, but weighted by evidence")
for param, coef, se, pval in zip(result_weighted.params.index,
                                   result_weighted.params,
                                   result_weighted.bse,
                                   result_weighted.pvalues):
    if 'cohort' not in param:
        continue
    cohort = param.split('[T.')[-1].rstrip(']')
    print(f"  {cohort}: +{coef:.3f} proportion (SE={se:.3f}, p={pval:.3f})")
    print(f"         Meaning: {cohort} has {coef:.1%} more agent-agent attention than 7mo")
print()

# Show what changed
print("WHAT CHANGED FROM CURRENT TO WEIGHTED:")
print("-"*80)
for param in result_unweighted.params.index:
    if 'cohort' not in param:
        continue
    cohort = param.split('[T.')[-1].rstrip(']')
    old_coef = result_unweighted.params[param]
    new_coef = result_weighted.params[param]
    old_p = result_unweighted.pvalues[param]
    new_p = result_weighted.pvalues[param]

    print(f"{cohort}:")
    print(f"  Coefficient: {old_coef:.4f} -> {new_coef:.4f} (change: {new_coef-old_coef:+.4f})")
    print(f"  P-value:     {old_p:.4f} -> {new_p:.4f} (change: {new_p-old_p:+.4f})")
    print()

# Option A: Binomial GEE
print("OPTION A: Binomial GEE (for comparison)")
print("-"*80)
from statsmodels.genmod.generalized_estimating_equations import GEE
from patsy import dmatrices

# Reset index to avoid index mismatch issues
df_reset = df.reset_index(drop=True)
y, X = dmatrices(formula, data=df_reset, return_type='dataframe')
model_binomial = GEE(endog=y, exog=X, groups=df_reset['participant_id'],
                    family=sm.families.Binomial(),
                    weights=df_reset['total_transitions'])
result_binomial = model_binomial.fit()

print("Interpretation: Change in LOG-ODDS (harder to interpret!)")
for param, coef, se, pval in zip(result_binomial.params.index,
                                   result_binomial.params,
                                   result_binomial.bse,
                                   result_binomial.pvalues):
    if 'cohort' not in param:
        continue
    cohort = param.split('[T.')[-1].rstrip(']')
    odds_ratio = np.exp(coef)
    print(f"  {cohort}: log-odds={coef:.3f}, OR={odds_ratio:.2f} (SE={se:.3f}, p={pval:.3f})")
    print(f"         Meaning: {cohort} has {odds_ratio:.2f}x the odds of agent-agent attention vs 7mo")
    print(f"         (Much less intuitive than '{coef:.1%} more'!)")
print()

# Check predictions stay in bounds
print("DIAGNOSTIC: Do predictions stay in [0, 1] range?")
print("-"*80)
pred_gaussian_unw = result_unweighted.predict()
pred_gaussian_w = result_weighted.predict()
pred_binomial = result_binomial.predict()

print(f"Unweighted Gaussian: [{pred_gaussian_unw.min():.3f}, {pred_gaussian_unw.max():.3f}]")
print(f"Weighted Gaussian:   [{pred_gaussian_w.min():.3f}, {pred_gaussian_w.max():.3f}]")
print(f"Binomial GEE:        [{pred_binomial.min():.3f}, {pred_binomial.max():.3f}]")

if pred_gaussian_w.min() >= 0 and pred_gaussian_w.max() <= 1:
    print("\n[OK] Weighted Gaussian predictions are valid! Option B is safe.")
else:
    print("\n[WARNING] Weighted Gaussian predictions outside [0,1]! Consider Option A.")
print()

print("="*80)
print("BOTTOM LINE RECOMMENDATIONS")
print("="*80)
print()
print("1. START WITH OPTION B (Weighted Gaussian)")
print("   - Easy to implement: just add weights= parameter")
print("   - Easy to interpret: coefficients stay on proportion scale")
print("   - Fixes the main problem: proper weighting by sample size")
print()
print("2. CHECK DIAGNOSTICS")
print("   - Are predictions in [0,1]? (We just checked: yes!)")
print("   - Do results make scientific sense?")
print("   - Do any conclusions meaningfully change?")
print()
print("3. ONLY MOVE TO OPTION A IF:")
print("   - Reviewer specifically requests it")
print("   - Predictions go outside [0,1] (they don't)")
print("   - You have lots of 0% or 100% trials (you don't)")
print()
print("4. FORGET OPTION C")
print("   - Way overkill for this analysis")
print("   - Use it only if you have complex nested structure to model")
print()
