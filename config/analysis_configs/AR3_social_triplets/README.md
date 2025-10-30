# AR3 Social Gaze Triplets - Configuration Directory

## Overview

This directory contains configuration files for **AR3 Social Gaze Triplet Analysis**, which detects and analyzes systematic face-object-face gaze sequences that demonstrate social-cognitive integration in infants.

**Research Question**: Do infants produce systematic gaze sequences that connect both actors and the object (person₁ → toy → person₂), demonstrating joint attention and event understanding?

---

## File Structure

```
AR3_social_triplets/
├── ar3_config.yaml          ← Base config (shared methodology)
├── ar3_explanation.md       ← Scientific documentation & interpretation
├── ar3_gw_vs_hw.yaml       ← Variant: GIVE_WITH vs HUG_WITH
├── ar3_gw_vs_gwo.yaml      ← Variant: GIVE_WITH vs GIVE_WITHOUT
├── ar3_give_vs_hug.yaml    ← Variant: Alternative GIVE vs HUG comparison
└── README.md               ← This file (configuration guide)
```

---

## Configuration System

### Base Config (`ar3_config.yaml`)

Controls **how triplets are detected** (methodology shared across all variants):

**Triplet Detection Settings:**
- `valid_patterns`: Which 3-gaze sequences count as triplets
- `max_gap_frames`: How many empty frames allowed between consecutive gazes
- `require_consecutive`: Mode for gap tolerance ("gap_tolerant" or "strict")
- `toy_absent_mapping`: How to handle WITHOUT conditions (toy_location substitution)
- `summary_age_mode`: How to group age data ("child_vs_adult" or "detailed")

**Statistical Settings:**
- `primary_test`: Statistical method (glmm_poisson)
- `glmm_formula`: Model specification with random effects
- `check_overdispersion`: Whether to detect overdispersion issues
- `overdispersion_threshold`: Threshold for warning (default: 1.5)

**Reporting & Output:**
- Export options for triplet data, summaries, and visualizations
- What sections to include in reports

**Edit this file when**: You want to change the triplet detection algorithm for ALL variants (e.g., allow 3 frames gap instead of 2, or add new triplet patterns)

---

### Variant Configs (`ar3_*.yaml`)

Controls **what to compare** (specific analysis parameters):

**Key Variant Settings:**
- `variant_key`: Unique identifier for this variant
- `variant_label`: Human-readable label for reports
- `conditions.include`: Which experimental conditions to compare
- `segments.include`: Which event segments to analyze (e.g., "interaction")
- `cohorts`: Which participant groups to include (infants, adults)

**Edit these when**: You want to run a different comparison (e.g., HUG_WITH vs HUG_WITHOUT) or analyze different cohorts

---

## Creating a New Variant

### Example: Create `ar3_hw_vs_hwo.yaml` (HUG_WITH vs HUG_WITHOUT)

**Step 1**: Copy an existing variant as template
```bash
cp ar3_gw_vs_gwo.yaml ar3_hw_vs_hwo.yaml
```

**Step 2**: Edit the key identifying fields
```yaml
variant_key: "ar3_hw_vs_hwo"
variant_label: "HUG_WITH vs HUG_WITHOUT"
analysis_name: "AR-3: Social Gaze Triplets"
description: "Compare triplets in HUG events with vs without toy present"
report_title: "AR-3: HUG_WITH vs HUG_WITHOUT"

conditions:
  include:
    - "HUG_WITH"
    - "HUG_WITHOUT"

segments:
  include:
    - "interaction"

cohorts:
  - key: "infant"
    label: "Infant"
    data_path: "data/processed/gaze_fixations_child.csv"
    include_in_reports: true
    participant_filters:
      participant_type: ["infant"]
  - key: "adult"
    label: "Adult"
    data_path: "data/processed/gaze_fixations_adult.csv"
    include_in_reports: true
    participant_filters:
      participant_type: ["adult"]
```

**Step 3**: Run the analysis
```bash
conda activate ier_analysis
export IER_AR3_CONFIG="AR3_social_triplets/ar3_hw_vs_hwo"  # Linux/Mac
# OR
$env:IER_AR3_CONFIG="AR3_social_triplets/ar3_hw_vs_hwo"   # Windows PowerShell

python -m src.analysis.ar3_social_triplets
```

**Output**: Results saved to `results/AR3_social_triplets/ar3_hw_vs_hwo/`

---

## Configuration Options Reference

### Base Config Options

#### `triplet_definition.valid_patterns`
- **Type**: List of 3-element lists
- **Default**: `[["man_face", "toy_present", "woman_face"], ["woman_face", "toy_present", "man_face"]]`
- **Purpose**: Defines which gaze sequences count as social triplets
- **Note**: Both directions (man→toy→woman and woman→toy→man) are typically included

#### `triplet_definition.max_gap_frames`
- **Type**: Integer
- **Default**: `2`
- **Purpose**: Maximum empty frames allowed between consecutive gazes in a triplet
- **Example**: With value 2, sequence `man_face (frame 10) → [2 empty frames] → toy_present (frame 13) → woman_face (frame 14)` is valid

#### `triplet_definition.require_consecutive`
- **Type**: String or Boolean
- **Default**: `"gap_tolerant"`
- **Options**: `"strict"` (no gaps), `"gap_tolerant"` (use max_gap_frames)
- **Purpose**: Controls whether gazes must be strictly consecutive or gaps are allowed

#### `triplet_definition.toy_absent_mapping`
- **Type**: Dictionary
- **Default**: `{toy_present: "toy_location"}`
- **Purpose**: In WITHOUT conditions, maps canonical toy AOI to where toy would be located
- **Why**: Allows testing anticipatory looking even when toy is absent

#### `triplet_definition.summary_age_mode`
- **Type**: String
- **Default**: `"child_vs_adult"`
- **Options**: `"child_vs_adult"` (collapse all infant ages), `"detailed"` (each month separate)
- **Purpose**: Controls age grouping granularity in reports

#### `statistics.primary_test`
- **Type**: String
- **Default**: `"glmm_poisson"`
- **Purpose**: Which statistical test to use for comparing conditions

#### `statistics.check_overdispersion`
- **Type**: Boolean
- **Default**: `true`
- **Purpose**: Whether to detect and warn about overdispersion in Poisson models

---

### Variant Config Options

#### `conditions.include`
- **Type**: List of strings
- **Required**: Yes
- **Purpose**: Which experimental conditions to include in this comparison
- **Example**: `["GIVE_WITH", "HUG_WITH"]`
- **Valid values**: Any condition codes from your data (GIVE_WITH, GIVE_WITHOUT, HUG_WITH, HUG_WITHOUT, SHOW_WITH, etc.)

#### `segments.include`
- **Type**: List of strings
- **Required**: No (defaults to all segments)
- **Purpose**: Which event segments to analyze
- **Example**: `["interaction"]` - only analyze the interaction phase
- **Valid values**: `"approach"`, `"interaction"`, `"departure"`

#### `cohorts`
- **Type**: List of cohort definitions
- **Required**: Yes
- **Purpose**: Define which participant groups to analyze and how to filter them
- **Structure**:
  ```yaml
  - key: "infant"              # Unique identifier
    label: "Infant"            # Display name
    data_path: "data/processed/gaze_fixations_child.csv"
    include_in_reports: true   # Whether to include in final report
    participant_filters:       # How to filter this cohort
      participant_type: ["infant"]
  ```

---

## Running AR3 Analysis

### Default Variant
```bash
conda activate ier_analysis
python -m src.analysis.ar3_social_triplets
```
Uses the default variant specified in `config/pipeline_config.yaml` under `analysis_specific.ar3_social_triplets.config_name`

### Specific Variant
```bash
conda activate ier_analysis

# Set environment variable to choose variant
export IER_AR3_CONFIG="AR3_social_triplets/ar3_gw_vs_hw"    # Linux/Mac
# OR
$env:IER_AR3_CONFIG="AR3_social_triplets/ar3_gw_vs_hw"     # Windows PowerShell

python -m src.analysis.ar3_social_triplets

# Clean up
unset IER_AR3_CONFIG           # Linux/Mac
Remove-Item Env:IER_AR3_CONFIG # Windows PowerShell
```

### Batch Run All Variants
```bash
conda activate ier_analysis
python scripts/run_ar3_variants.py
```
Automatically runs all `ar3_*.yaml` files in this directory

---

## Outputs

Each AR3 variant generates:

```
results/AR3_social_triplets/<variant_key>/
├── report.html                      # Interactive web report
├── report.pdf                       # Printable report (if PDF enabled)
├── triplets_detected.csv            # All detected triplets with metadata
├── triplet_counts_per_trial.csv     # Counts per trial per participant
├── summary_by_condition.csv         # Aggregated statistics by condition
├── summary_by_age_group.csv         # Age-stratified summaries
├── directional_bias.csv             # Which pattern direction is more common
└── temporal_summaries.csv           # First vs subsequent occurrences
```

---

## Troubleshooting

### "No valid triplet patterns defined"
**Problem**: Base config missing or invalid triplet pattern specification

**Solution**:
- Verify `ar3_config.yaml` exists in this directory
- Check that `triplet_definition.valid_patterns` contains valid 3-element lists
- Each pattern must be exactly 3 AOI names

### "Variant configuration not found"
**Problem**: Specified variant file doesn't exist

**Solution**:
- Check filename: must match pattern `ar3_*.yaml`
- Verify path: `config/analysis_configs/AR3_social_triplets/ar3_your_variant.yaml`
- Use correct environment variable: `IER_AR3_CONFIG="AR3_social_triplets/ar3_your_variant"`

### "No triplets detected"
**Problem**: Either no data matches criteria, or detection parameters too strict

**Solution**:
- Check that data has the required AOIs (man_face, woman_face, toy_present)
- Try increasing `max_gap_frames` in base config to allow more tolerance
- Verify that participants have valid gaze fixations in the specified segments
- Check `segments.include` - are you limiting to segments that have data?

### "GLMM convergence failed"
**Problem**: Statistical model didn't converge (common with rare events like triplets)

**Solution**:
- This is expected with low triplet rates - analysis continues with descriptive statistics
- Consider combining age groups or conditions to increase sample size
- Review overdispersion warnings - may need Negative Binomial model (future enhancement)

---

## Related Documentation

- **Scientific interpretation**: See [`ar3_explanation.md`](./ar3_explanation.md) for understanding what triplets mean theoretically
- **Code implementation**: See [`src/analysis/ar3_social_triplets.py`](../../src/analysis/ar3_social_triplets.py) for detection algorithm
- **Spec requirements**: See [`(archive)/specs/001-infant-event-analysis/spec.md`](../../(archive)/specs/001-infant-event-analysis/spec.md) for original FR-018 to FR-023

---

## Tips for Creating Variants

### Quick Comparisons
Want to test different event types? Just change `conditions.include`:
- GIVE vs HUG: `["GIVE_WITH", "HUG_WITH"]`
- WITH vs WITHOUT: `["GIVE_WITH", "GIVE_WITHOUT"]`
- Three-way: `["GIVE_WITH", "HUG_WITH", "SHOW_WITH"]`

### Cohort Subsets
Want to analyze only specific age groups? Adjust `participant_filters`:
```yaml
cohorts:
  - key: "8_month"
    label: "8-Month Infants"
    participant_filters:
      participant_type: ["infant"]
      age_months: [8]
```

### Segment Focus
Want to analyze only certain phases? Change `segments.include`:
- Just interaction: `["interaction"]`
- Approach + interaction: `["approach", "interaction"]`
- Full event: `["approach", "interaction", "departure"]`

---

**Last Updated**: 2025-10-29
**Maintainer**: IER Analysis Team
