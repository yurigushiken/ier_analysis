# AR5 Developmental Trajectory Analysis - Configuration Directory

## Overview

This directory contains configuration files for **AR5 Developmental Trajectory Analysis**, which tests whether experimental condition effects change with infant age using Age × Condition interaction models.

**Research Question**: Do condition effects (e.g., GIVE vs HUG) change with infant age? Is there an Age × Condition interaction suggesting that developmental timing matters for event comprehension?

---

## File Structure

```
AR5_developmental_trajectories/
├── ar5_config.yaml          ← Base config (shared methodology)
├── ar5_explanation.md       ← Scientific documentation & interpretation (TO BE CREATED)
├── ar5_gw_vs_hw.yaml       ← Variant: GIVE_WITH vs HUG_WITH developmental trajectory
└── README.md               ← This file (configuration guide)
```

---

## Configuration System

### Base Config (`ar5_config.yaml`)

Controls **how developmental trajectories are modeled** (methodology shared across all variants):

**Age Modeling Settings:**
- `use_continuous_age`: Whether to use continuous age (in months) vs categorical age groups
- `test_nonlinear`: Whether to test for quadratic age effects (acceleration/deceleration)

**Statistical Settings:**
- `primary_test`: Statistical method (linear_mixed_model)
- `test_interaction`: Whether to test Age × Condition interaction (core AR5 question)
- `calculate_effect_size`: Whether to compute effect sizes
- `report_aic_bic`: Whether to report model fit statistics
- `check_residuals`: Whether to check assumption violations
- `compare_models`: Whether to compare nested models for ANOVA-like table

**Dependent Variables:**
- `dependent_variables`: Which metrics to model as function of age and condition
  - `proportion_primary_aois`: Default - proportion looking at faces + toy
  - `social_triplet_rate`: Alternative - age effects on social coordination
  - `mean_dwell_time`: Alternative - age effects on processing depth

**Visualization:**
- `plot_type`: Type of interaction plot
- `generate_interaction_plot`: Whether to create Age × Condition plot
- `show_regression_line`: Whether to show fitted model predictions
- `show_confidence_band`: Whether to show CI around predictions

**Edit this file when**: You want to change the modeling approach for ALL variants (e.g., add quadratic age terms, change dependent variable)

---

### Variant Configs (`ar5_*.yaml`)

Controls **what to compare** (specific analysis parameters):

**Key Variant Settings:**
- `variant_key`: Unique identifier for this variant
- `variant_label`: Human-readable label for reports
- `target_conditions`: Which conditions to compare (must have exactly 2 for interaction)
- `cohorts`: Which participant groups to include (typically infants + adults)

**Edit these when**: You want to test Age × Condition interaction for different event comparisons (e.g., GIVE_WITH vs GIVE_WITHOUT)

---

## Creating a New Variant

### Example: Create `ar5_gw_vs_gwo.yaml` (GIVE_WITH vs GIVE_WITHOUT developmental)

**Step 1**: Copy an existing variant as template
```bash
cp ar5_gw_vs_hw.yaml ar5_gw_vs_gwo.yaml
```

**Step 2**: Edit the key identifying fields
```yaml
variant_key: "ar5_gw_vs_gwo"
variant_label: "AR-5: GIVE_WITH vs GIVE_WITHOUT"
analysis_name: "AR-5: Developmental Trajectory"
description: "Age x Condition analysis: Does toy presence effect change with age?"

# Which conditions to compare (exactly 2 for interaction)
target_conditions:
  - "GIVE_WITH"
  - "GIVE_WITHOUT"

# Cohorts: Include infants to get age range + adults as mature baseline
cohorts:
  - key: "infant"
    label: "Infant Cohort"
    data_path: "data/processed/gaze_fixations_child.csv"
    participant_filters:
      participant_type: ["infant"]
  - key: "adult"
    label: "Adult Control Cohort"
    data_path: "data/processed/gaze_fixations_adult.csv"
    participant_filters:
      participant_type: ["adult"]
```

**Step 3**: Run the analysis
```bash
conda activate ier_analysis

# Set environment variable to choose variant (optional if it's the default)
export IER_AR5_CONFIG="AR5_developmental_trajectories/ar5_gw_vs_gwo"    # Linux/Mac
# OR
$env:IER_AR5_CONFIG="AR5_developmental_trajectories/ar5_gw_vs_gwo"     # Windows PowerShell

python -m src.analysis.ar5_development

# Clean up
unset IER_AR5_CONFIG           # Linux/Mac
Remove-Item Env:IER_AR5_CONFIG # Windows PowerShell
```

**Output**: Results saved to `results/AR5_Developmental_Trajectories/ar5_gw_vs_gwo/`

---

## Configuration Options Reference

### Base Config Options

#### `age_modeling.use_continuous_age`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Use continuous age in months (e.g., 7, 8, 9, ...) rather than categorical groups
- **Recommendation**: Keep as `true` for maximum statistical power
- **When to use false**: If you want discrete age group comparisons (e.g., "younger" vs "older")

#### `age_modeling.test_nonlinear`
- **Type**: Boolean
- **Default**: `false`
- **Purpose**: Add quadratic age term to test for non-linear developmental trajectories
- **Use case**: When development might accelerate or decelerate (not just linear growth)
- **Model change**: From `outcome ~ age` to `outcome ~ age + age²`
- **Interpretation**: Positive quadratic = accelerating development; negative = decelerating

#### `statistics.test_interaction`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Test the Age × Condition interaction term (THE CORE AR5 QUESTION)
- **Interpretation**:
  - Significant interaction → condition effect changes with age
  - Non-significant → condition effect stable across age range

#### `statistics.compare_models`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Compare nested models to generate ANOVA-like table
- **How it works**: Fits multiple models and uses likelihood ratio tests
  - Model 1: Age only
  - Model 2: Age + Condition
  - Model 3: Age × Condition (interaction)

#### `metrics.dependent_variables`
- **Type**: List of strings
- **Default**: `["proportion_primary_aois"]`
- **Purpose**: Which outcome measures to model as function of age
- **Options**:
  - `"proportion_primary_aois"`: Proportion looking at faces + toy (default)
  - `"social_triplet_rate"`: Triplet production rate (requires AR3 analysis first)
  - `"mean_dwell_time"`: Average fixation duration (requires AR4 analysis first)
- **Note**: Currently only first DV is used; multi-DV support is future enhancement

#### `visualization.plot_type`
- **Type**: String
- **Default**: `"line_with_error_bars"`
- **Purpose**: Type of interaction plot to generate
- **Options**: `"line_with_error_bars"`, `"line"`, `"scatter"`

#### `visualization.show_regression_line`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Whether to overlay fitted model predictions on interaction plot
- **Use case**: Shows the LMM prediction alongside raw data

#### `visualization.show_confidence_band`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Whether to show confidence band around regression line
- **Use case**: Visualizes uncertainty in model predictions

---

### Variant Config Options

#### `target_conditions`
- **Type**: List of exactly 2 strings
- **Required**: Yes
- **Purpose**: Which two conditions to compare in Age × Condition interaction
- **Example**: `["GIVE_WITH", "HUG_WITH"]`
- **Note**: Must be exactly 2 conditions for interaction interpretation to make sense
- **Valid values**: Any condition codes from your data

#### `cohorts`
- **Type**: List of cohort definitions
- **Required**: Yes
- **Purpose**: Define which participant groups to include
- **Typical structure**: Include infants (for age range) + adults (as mature baseline)
- **Structure**:
  ```yaml
  - key: "infant"
    label: "Infant Cohort"
    data_path: "data/processed/gaze_fixations_child.csv"
    participant_filters:
      participant_type: ["infant"]
      # Note: No age filtering - include all infant ages for trajectory
  - key: "adult"
    label: "Adult Control Cohort"
    data_path: "data/processed/gaze_fixations_adult.csv"
    participant_filters:
      participant_type: ["adult"]
  ```

**Important**: Don't filter by `age_months` in cohorts for AR5 - you want the full age range to test developmental trajectories!

---

## Running AR5 Analysis

### Default Variant
```bash
conda activate ier_analysis
python -m src.analysis.ar5_development
```
Uses the default variant specified in code (falls back to `AR5_developmental_trajectories/ar5_example` if no config specified)

### Specific Variant
```bash
conda activate ier_analysis

# Set environment variable to choose variant
export IER_AR5_CONFIG="AR5_developmental_trajectories/ar5_gw_vs_hw"    # Linux/Mac
# OR
$env:IER_AR5_CONFIG="AR5_developmental_trajectories/ar5_gw_vs_hw"     # Windows PowerShell

python -m src.analysis.ar5_development

# Clean up
unset IER_AR5_CONFIG           # Linux/Mac
Remove-Item Env:IER_AR5_CONFIG # Windows PowerShell
```

### Batch Run All Variants
```bash
conda activate ier_analysis
python scripts/run_ar5_variants.py  # If this script exists
```

---

## Outputs

Each AR5 variant generates:

```
results/AR5_Developmental_Trajectories/<variant_key>/
├── report.html                                 # Interactive web report
├── report.pdf                                  # Printable report (if PDF enabled)
├── proportion_primary_aois_by_age_condition.csv  # Raw data for plotting
├── proportion_primary_aois_summary.csv         # Age group summaries
├── proportion_primary_aois_coefficients.csv    # LMM coefficients
├── proportion_primary_aois_anova.csv           # ANOVA table (if compare_models: true)
└── proportion_primary_aois_age_by_condition.png # Interaction plot
```

---

## Interpreting Results

### Significant Age × Condition Interaction

**What it means**: The condition effect **changes** with age

**Example**:
- At 7 months: No difference between GIVE and HUG
- At 12 months: Large difference between GIVE and HUG
- **Interpretation**: Event structure understanding **develops** between 7-12 months

**Interaction plot shape**: Lines are **not parallel**

### Non-Significant Interaction

**What it means**: The condition effect is **stable** across age range

**Example**:
- At 7 months: GIVE > HUG by 10%
- At 12 months: GIVE > HUG by 12%
- **Interpretation**: Event structure understanding is **present throughout** age range studied

**Interaction plot shape**: Lines are **parallel**

### Significant Main Effect of Age

**What it means**: Overall performance changes with age (regardless of condition)

**Example**: Both GIVE and HUG looking increases from 7 to 12 months
**Interpretation**: General attention/processing maturation

### Significant Main Effect of Condition

**What it means**: Conditions differ overall (averaged across ages)

**Example**: GIVE > HUG across all ages
**Interpretation**: Event type matters, but doesn't interact with age

---

## Troubleshooting

### "No data available for modeling"
**Problem**: After filtering by target_conditions, no participants remain

**Solution**:
- Check that `target_conditions` values match condition names in your data
- Verify that data files specified in cohorts exist and have data
- Check participant_filters - are you being too restrictive?

### "Small sample size (n=X); model estimates may be unstable"
**Problem**: Warning about insufficient participants

**Solution**:
- This is a warning, not an error - analysis continues
- Consider combining age groups if you have very few per age
- Results should be interpreted cautiously with small N
- Minimum recommended: N ≥ 6 participants for stable LMM estimation

### "Random effects covariance is singular"
**Problem**: LMM convergence issue with random effects

**Solution**:
- Common with small samples or low between-participant variance
- Analysis continues but results may be less reliable
- Consider simplifying model or increasing sample size
- Check if variance components make sense in output

### "Interaction not significant (p > 0.05)"
**Problem**: Not really a problem! This is a valid finding

**Interpretation**:
- Condition effects are relatively stable across age range
- Doesn't mean no development - just that the condition **difference** doesn't change with age
- Both conditions might be increasing with age in parallel
- Check main effects: condition effect present but not age-varying

### Age range too narrow
**Problem**: Only testing 1-2 age months

**Solution**:
- AR5 works best with broader age ranges (e.g., 7-12 months)
- With narrow range, hard to detect developmental change
- Consider including more ages in cohort filters
- Or interpret results as age-specific snapshot rather than trajectory

---

## Related Documentation

- **Scientific interpretation**: `ar5_explanation.md` TO BE CREATED - will explain developmental theory
- **Code implementation**: See [`src/analysis/ar5_development.py`](../../src/analysis/ar5_development.py) for modeling algorithms
- **Spec requirements**: See [`(archive)/specs/001-infant-event-analysis/spec.md`](../../(archive)/specs/001-infant-event-analysis/spec.md) for original FR-029 to FR-033

---

## Tips for Creating Variants

### Event Structure Development
Test when infants start distinguishing event types:
```yaml
target_conditions: ["GIVE_WITH", "HUG_WITH"]
# Question: When do infants show GIVE > HUG pattern?
```

### Toy Presence Development
Test when infants notice toy absence:
```yaml
target_conditions: ["GIVE_WITH", "GIVE_WITHOUT"]
# Question: When do infants show WITH > WITHOUT pattern?
```

### Alternative Dependent Variables
Test different aspects of development (requires modifying base config):
```yaml
metrics:
  dependent_variables:
    - "social_triplet_rate"  # Development of social coordination
    # OR
    - "mean_dwell_time"      # Development of processing depth
```

### Including Adults
Always include adults as mature baseline:
```yaml
cohorts:
  - key: "infant"
    participant_filters:
      participant_type: ["infant"]
  - key: "adult"
    participant_filters:
      participant_type: ["adult"]
# Adults show you the "end state" of development
```

---

## Understanding AR5 vs Other Analyses

**AR1-AR4** answer: "Do conditions differ?" (main effects)

**AR5** answers: "Does the condition difference **change with age**?" (interaction)

**Example**:
- AR1 might show: GIVE > HUG (overall)
- AR5 tests: Is GIVE-HUG difference larger at 12 months than 7 months?

**Why this matters**: Tells you WHEN development occurs, not just THAT it occurs

---

## Statistical Model Details

### Basic Model (default)
```
proportion_primary_aois ~ age_months + C(condition) + age_months:C(condition) + (1 | participant)
```

**Terms**:
- `age_months`: Main effect of age (linear trajectory)
- `C(condition)`: Main effect of condition (categorical)
- `age_months:C(condition)`: **THE INTERACTION** (does condition effect vary with age?)
- `(1 | participant)`: Random intercepts (individual baselines)

### With Nonlinear Age (if `test_nonlinear: true`)
```
proportion_primary_aois ~ age_months + I(age_months^2) + C(condition) + age_months:C(condition) + (1 | participant)
```

**Added term**:
- `I(age_months^2)`: Quadratic age effect (curvature in development)

---

**Last Updated**: 2025-10-29
**Maintainer**: IER Analysis Team

**Note**: `ar5_explanation.md` not yet created - will contain detailed scientific interpretation of developmental trajectories and interaction effects.
