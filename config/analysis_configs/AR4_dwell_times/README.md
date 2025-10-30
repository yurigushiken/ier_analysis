# AR4 Dwell Time Analysis - Configuration Directory

## Overview

This directory contains configuration files for **AR4 Dwell Time Analysis**, which measures the duration of individual gaze fixations to understand the depth and quality of cognitive processing during event observation.

**Research Question**: How long do infants' individual gaze fixations last when looking at different areas of interest? Does fixation duration differ by condition or AOI type?

---

## File Structure

```
AR4_dwell_times/
├── ar4_config.yaml          ← Base config (shared methodology)
├── ar4_explanation.md       ← Scientific documentation & interpretation
├── ar4_gw_vs_gwo.yaml      ← Variant: GIVE_WITH vs GIVE_WITHOUT
└── README.md               ← This file (configuration guide)
```

---

## Configuration System

### Base Config (`ar4_config.yaml`)

Controls **how dwell times are filtered and analyzed** (methodology shared across all variants):

**Dwell Time Filtering:**
- `min_dwell_time_ms`: Minimum fixation duration to include (excludes noise)
- `max_dwell_time_ms`: Maximum fixation duration (excludes tracker loss)
- `outlier_threshold_sd`: Within-participant z-score threshold for outlier removal

**AOI Analysis:**
- `focus_categories`: Which AOI categories to prioritize in reports
- `support_categories`: Secondary AOIs for reference
- `min_gaze_fixations_per_aoi`: Minimum fixations required for AOI summary

**Statistical Settings:**
- `lmm_formula`: Linear Mixed Model specification
- `lmm_formula_by_aoi`: Optional interaction model testing AOI × Condition
- `min_participants_per_condition`: Minimum N for valid statistical tests

**Visualization & Reporting:**
- Colors, plot types, violin plots, age notes
- Export options for participant means, summaries, and AOI breakdowns

**Edit this file when**: You want to change filtering thresholds or analysis methodology for ALL variants (e.g., change minimum dwell time from 100ms to 150ms)

---

### Variant Configs (`ar4_*.yaml`)

Controls **what to compare** (specific analysis parameters):

**Key Variant Settings:**
- `variant_key`: Unique identifier for this variant
- `variant_label`: Human-readable label for reports
- `conditions.include`: Which experimental conditions to compare
- `segments.include`: Which event segments to analyze
- `cohorts`: Which participant groups and age ranges to include
- `primary_cohort`: Which cohort is the focus of analysis

**Variant-Specific Overrides:**
- Custom colors for conditions
- Whether to generate violin plots
- Whether to include age-specific notes
- AOI focus categories (if different from base)

**Edit these when**: You want to run a different comparison (e.g., GIVE_WITH vs HUG_WITH) or analyze different age groups

---

## Creating a New Variant

### Example: Create `ar4_gw_vs_hw.yaml` (GIVE_WITH vs HUG_WITH)

**Step 1**: Copy an existing variant as template
```bash
cp ar4_gw_vs_gwo.yaml ar4_gw_vs_hw.yaml
```

**Step 2**: Edit the key identifying fields
```yaml
variant_key: "ar4_gw_vs_hw"
variant_label: "GIVE_WITH vs HUG_WITH"
analysis_name: "AR-4: Dwell Time Analysis"
description: "Compare dwell time depth between GIVE and HUG events"
report_title: "AR-4: GIVE_WITH vs HUG_WITH"

conditions:
  include:
    - "GIVE_WITH"
    - "HUG_WITH"

segments:
  include:
    - "approach"
    - "interaction"

cohorts:
  - key: "month_8"
    label: "8-Month Infants"
    data_path: "data/processed/gaze_fixations_child.csv"
    include_in_report: true
    participant_filters:
      participant_type: ["infant"]
      age_months: [8]
  - key: "month_10"
    label: "10-Month Infants"
    data_path: "data/processed/gaze_fixations_child.csv"
    include_in_report: true
    participant_filters:
      participant_type: ["infant"]
      age_months: [10]
  - key: "adult"
    label: "Adult Control"
    data_path: "data/processed/gaze_fixations_adult.csv"
    include_in_report: false
    participant_filters:
      participant_type: ["adult"]

primary_cohort: "month_8"

visualization:
  colors:
    GIVE_WITH: "#e67e22"
    HUG_WITH: "#3498db"
  violin_plot: true

reporting:
  include_age_notes: true

output:
  generate_violin_plot: true
  include_violin_plot: true
```

**Step 3**: Run the analysis
```bash
conda activate ier_analysis

# Run directly with code
python -c "from src.utils.config import load_config; from src.analysis import ar4_dwell_times; cfg = load_config(overrides=['analysis_specific.ar4_dwell_times.config_name=AR4_dwell_times/ar4_gw_vs_hw']); ar4_dwell_times.run(config=cfg)"
```

**Output**: Results saved to `results/AR4_dwell_times/report.html`

---

## Configuration Options Reference

### Base Config Options

#### `dwell_time.min_dwell_time_ms`
- **Type**: Integer
- **Default**: `100`
- **Purpose**: Minimum fixation duration in milliseconds to include in analysis
- **Rationale**: Fixations < 100ms are too brief to represent meaningful looking
- **Range**: Typically 75-150ms

#### `dwell_time.max_dwell_time_ms`
- **Type**: Integer
- **Default**: `10000` (10 seconds)
- **Purpose**: Maximum fixation duration to include
- **Rationale**: Extremely long fixations may represent tracker loss or off-task behavior
- **Range**: Typically 5000-15000ms

#### `dwell_time.outlier_threshold_sd`
- **Type**: Float
- **Default**: `3.0`
- **Purpose**: Z-score threshold for within-participant outlier removal
- **How it works**: For each participant × condition, removes fixations more than 3 SD from that participant's mean
- **Why within-participant**: Prevents removing normal long fixations from participants who generally fixate longer

#### `aoi_analysis.focus_categories`
- **Type**: List of strings
- **Default**: `["toy_present", "toy_location", "man_face", "woman_face"]`
- **Purpose**: Which AOI categories to prioritize in summaries and visualizations
- **Options**: Any valid AOI from your data

#### `aoi_analysis.min_gaze_fixations_per_aoi`
- **Type**: Integer
- **Default**: `3`
- **Purpose**: Minimum number of fixations required for an AOI to appear in AOI-specific summaries
- **Rationale**: Prevents unreliable means based on 1-2 fixations

#### `statistics.lmm_formula`
- **Type**: String
- **Default**: `"mean_dwell_time_ms ~ condition_name"`
- **Purpose**: Formula for Linear Mixed Model (participant-level analysis)
- **Note**: Random effect `(1 | participant)` is added automatically by the code

#### `statistics.lmm_formula_by_aoi`
- **Type**: String
- **Default**: `"mean_dwell_time_ms ~ condition_name * aoi_category"`
- **Purpose**: Alternative formula testing whether condition effect varies by AOI
- **When to use**: To test if dwell differences are specific to certain AOIs (e.g., only toy, not faces)

---

### Variant Config Options

#### `conditions.include`
- **Type**: List of strings
- **Required**: Yes
- **Purpose**: Which experimental conditions to include in this comparison
- **Example**: `["GIVE_WITH", "GIVE_WITHOUT"]`
- **Valid values**: Any condition codes from your data

#### `segments.include`
- **Type**: List of strings
- **Required**: No (defaults to all segments)
- **Purpose**: Which event segments to analyze
- **Example**: `["approach", "interaction"]` - analyze approach and interaction phases only
- **Valid values**: `"approach"`, `"interaction"`, `"departure"`

#### `cohorts`
- **Type**: List of cohort definitions
- **Required**: Yes
- **Purpose**: Define which participant groups to analyze
- **Age stratification**: Can define separate cohorts for each age month
- **Structure**:
  ```yaml
  - key: "month_8"                    # Unique identifier
    label: "8-Month Infants"          # Display name
    data_path: "data/processed/gaze_fixations_child.csv"
    include_in_report: true           # Whether to include in final report
    participant_filters:              # How to filter this cohort
      participant_type: ["infant"]
      age_months: [8]
  ```

#### `primary_cohort`
- **Type**: String
- **Required**: No
- **Purpose**: Which cohort is the primary focus (used for emphasis in reports)
- **Example**: `"month_8"`

#### `visualization.colors`
- **Type**: Dictionary
- **Required**: No
- **Purpose**: Custom colors for each condition in plots
- **Example**:
  ```yaml
  colors:
    GIVE_WITH: "#e67e22"      # Orange
    GIVE_WITHOUT: "#8e44ad"   # Purple
  ```

#### `visualization.violin_plot`
- **Type**: Boolean
- **Default**: Inherited from base (false)
- **Purpose**: Whether to generate violin plots showing distribution of dwell times
- **Use case**: Violin plots show the full distribution, not just means

#### `output.generate_violin_plot` and `output.include_violin_plot`
- **Type**: Boolean
- **Default**: Inherited from base
- **Purpose**: Control whether violin plots are generated and included in reports
- **Note**: Both must be true to include violin plots

---

## Running AR4 Analysis

### Default Variant
```bash
conda activate ier_analysis
python -c "from src.utils.config import load_config; from src.analysis import ar4_dwell_times; cfg = load_config(); ar4_dwell_times.run(config=cfg)"
```

### Specific Variant
```bash
conda activate ier_analysis
python -c "from src.utils.config import load_config; from src.analysis import ar4_dwell_times; cfg = load_config(overrides=['analysis_specific.ar4_dwell_times.config_name=AR4_dwell_times/ar4_gw_vs_gwo']); ar4_dwell_times.run(config=cfg)"
```

### Batch Run All Variants
```bash
conda activate ier_analysis
python scripts/run_ar4_variants.py
```

---

## Outputs

Each AR4 variant generates:

```
results/AR4_dwell_times/
├── report.html                      # Interactive web report
├── report.pdf                       # Printable report (if PDF enabled)
├── participant_dwell_times.csv      # Mean dwell per participant per condition
├── condition_summary.csv            # Aggregated statistics by condition
├── aoi_summary.csv                  # AOI-specific dwell times by condition
├── dwell_time_by_condition.png      # Bar chart of mean dwell by condition
├── dwell_time_by_aoi.png           # Grouped bar chart: AOI × Condition
├── dwell_time_by_condition_violin.png  # Optional: distribution plots
└── dwell_time_by_aoi_violin.png    # Optional: AOI-specific distributions
```

---

## Troubleshooting

### "No valid dwell time data available"
**Problem**: All fixations filtered out by min/max thresholds or outlier removal

**Solution**:
- Check if raw data has fixations in the expected duration range
- Try relaxing `max_dwell_time_ms` threshold (increase from 10000 to 15000)
- Try disabling outlier removal temporarily: set `outlier_threshold_sd: null` in base config
- Verify that conditions and segments specified exist in your data

### "Linear mixed model fitting failed"
**Problem**: Statistical model didn't converge or insufficient data

**Solution**:
- Check if you have at least 3 participants per condition (required minimum)
- Verify participant-level means exist (some participants might have no valid fixations)
- Look at warnings in output - may indicate singular covariance (expected with small N)
- Analysis continues with descriptive statistics even if LMM fails

### "Random effects covariance is singular"
**Problem**: Warning from statsmodels about model estimation

**Solution**:
- This is common with small sample sizes or low between-participant variability
- It's a warning, not an error - analysis continues
- Results may be less reliable; consider increasing sample size or combining age groups
- Check if variance components make sense in the output

### Very high or low dwell times
**Problem**: Mean dwell times seem unrealistic (e.g., < 50ms or > 5 seconds)

**Solution**:
- Check your data for issues (incorrect timestamps, frame rate problems)
- Verify min/max thresholds in base config are appropriate for your setup
- Check if outlier removal is working: look at `outlier_threshold_sd` setting
- Review filtered data: How many fixations were excluded?

---

## Related Documentation

- **Scientific interpretation**: See [`ar4_explanation.md`](./ar4_explanation.md) for understanding what dwell times reveal about cognitive processing
- **Code implementation**: See [`src/analysis/ar4_dwell_times.py`](../../src/analysis/ar4_dwell_times.py) for filtering and analysis algorithms
- **Spec requirements**: See [`(archive)/specs/001-infant-event-analysis/spec.md`](../../(archive)/specs/001-infant-event-analysis/spec.md) for original FR-024 to FR-028

---

## Tips for Creating Variants

### Quick Condition Comparisons
Test different event structures:
- **GIVE vs HUG**: Do transfer events elicit longer fixations?
  ```yaml
  conditions: ["GIVE_WITH", "HUG_WITH"]
  ```
- **WITH vs WITHOUT**: Does toy presence affect fixation depth?
  ```yaml
  conditions: ["GIVE_WITH", "GIVE_WITHOUT"]
  ```

### Age Stratification
Compare developmental changes:
```yaml
cohorts:
  - key: "younger"
    participant_filters:
      age_months: [7, 8, 9]
  - key: "older"
    participant_filters:
      age_months: [10, 11, 12]
```

### Segment-Specific Analysis
Focus on specific event phases:
- **Interaction only**: `segments: ["interaction"]`
- **Approach + interaction**: `segments: ["approach", "interaction"]`
- **Departure only**: `segments: ["departure"]` - test memory effects

### AOI-Specific Focus
If you only care about certain AOIs:
```yaml
aoi_analysis:
  focus_categories:
    - "toy_present"
    - "man_face"
    - "woman_face"
  # Exclude bodies, hands, etc.
```

---

## Understanding Dwell Time vs Gaze Duration (AR1)

**AR1 (Gaze Duration)** measures: *Total cumulative time* looking at an AOI per trial
- Example: 5 fixations on toy totaling 2000ms

**AR4 (Dwell Time)** measures: *Average duration of each individual fixation*
- Example: Those 5 fixations average 400ms each

**Key difference**:
- AR1 answers "How much total attention?"
- AR4 answers "How deeply do they process each look?"

Both are valuable and complement each other!

---

**Last Updated**: 2025-10-29
**Maintainer**: IER Analysis Team
