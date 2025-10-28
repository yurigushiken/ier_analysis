# 📊 Data Exploration Insights & Statistical Mentorship

**Date**: 2025-10-26
**Purpose**: Understand actual data structure and refine statistical approach

---

## 🔍 What We Learned from Your Data

### 1. **Data Structure Overview**

**Files**: 36 child participant CSV files (infant data)

**File Size Range**: ~5,500 - 12,000 rows per participant
**Average**: ~7,800 rows per participant

**Columns** (19 total):
```
1. Participant          - ID (e.g., "Eight-0101-947")
2. Time                 - Timestamp
3. What                 - AOI object (e.g., "no", "man", "woman", "toy")
4. Where                - AOI location (e.g., "signal", "face", "body", "hands")
5. Onset                - Frame start time
6. Offset               - Frame end time
7. Blue Dot Center      - Gaze coordinates
8. event                - Trial/event ID
9. session_frame        - Frame number in session
10. trial_block_cumulative_order
11. trial_block_frame
12. trial_block_trial
13. trial_frame         - Frame number within trial
14. trial_cumulative_by_event
15. segment             - Event segment
16. segment_frame
17. participant_type    - "child" or "adult"
18. participant_age_months  - Age in months
19. participant_age_years   - Age in years
```

**Key Observation**: Each ROW is a single frame (≈30fps sampling rate based on timestamps)

---

### 2. **Nesting Structure (CRITICAL for Statistical Modeling)**

```
Participant (Level 3)
  └─ Trial/Event (Level 2)
      └─ Frame (Level 1)
```

**Example from one participant**:
- **Participant**: "Eight-0101-947" (8 months old)
- **Frames**: 8,350 frames total
- **Estimated trials**: ~10-15 trials (based on event column)
- **Frames per trial**: ~500-800 frames each

**Statistical Implication**:
✓ **This is CLASSIC hierarchical/nested data**
✓ **Frames within trials are NOT independent**
✓ **Trials within participants are NOT independent**
✓ **LMM/GLMM is MANDATORY, not optional**

---

### 3. **Age Distribution**

**From filenames**:
- Eight-months: 9 participants
- Nine-months: Several participants
- Eleven-months: 8 participants
- (More age groups likely in full dataset)

**Range**: Appears to span 8-14 months (typical for infant event representation research)

**Statistical Implication**:
✓ **Continuous age modeling is appropriate** (no need to bin into younger/older)
✓ **Sufficient age spread to test developmental effects**
✓ **Age × Condition interactions are testable**

---

### 4. **AOI Structure (What + Where combinations)**

**Sample observations**:
- "no,signal" → off-screen (infant looking away)
- "man,face" → looking at man's face
- "woman,face" → looking at woman's face
- "toy,other" → looking at toy

**Statistical Implication**:
✓ **Clear categorical AOI structure**
✓ **Multiple AOIs per trial → many gaze fixations per trial**
✓ **Repeated gaze fixations within trials → nested data**

---

## 📈 How This Impacts Our Statistical Plan

### ✅ **Confirmation: LMM/GLMM is the CORRECT Choice**

Based on the data structure, here's why LMM/GLMM is essential:

#### **Problem with Traditional Tests (t-tests, ANOVA)**:

1. **Independence Assumption Violated**:
   - Each participant has ~8,000 frames
   - These frames are clustered within ~10-15 trials
   - Trials are clustered within participants
   - **Violation severity**: MASSIVE

2. **Example of the Problem**:
   ```
   Traditional t-test assumes:
     - Participant 1: 1 independent observation
     - Participant 2: 1 independent observation
     - ...
     - Participant 36: 1 independent observation
     - Total N = 36

   Reality in our data:
     - Participant 1: 10 trials × 15 gaze fixations = 150 observations
     - Participant 2: 12 trials × 18 gaze fixations = 216 observations
     - ...
     - Total N = thousands of non-independent observations
   ```

3. **Consequences of ignoring nesting**:
   - Standard errors are **underestimated** (too small)
   - p-values are **anti-conservative** (too many false positives)
   - **Type I error rate inflated** (claiming significance when there isn't)
   - **Scientific integrity compromised**

---

### ✅ **LMM Solution**

**Linear Mixed Model properly handles this**:

```python
# AR-1 Example: Gaze Duration
# Each row = one trial observation
model = MixedLM.from_formula(
    'proportion_core_event ~ condition + (1 | participant)',
    data=trial_data,
    groups='participant'
)
```

**What this does**:
- **Fixed effect** (`condition`): Tests population-level difference between GIVE vs HUG
- **Random effect** (`1 | participant`): Allows each infant to have their own baseline looking time
- **Correct standard errors**: Accounts for within-participant correlation
- **Proper inference**: p-values are accurate

---

## 🎯 Refined Statistical Approach for Each Analysis

### **AR-1: Gaze Duration**

**Data Structure**:
- **Unit of analysis**: Trial-level (aggregate frames within trial)
- **Nesting**: Trials within participants
- **Outcome**: Proportion of looking time to core event

**Model**:
```
proportion_core_event ~ condition + (1 | participant)
```

**Why LMM**:
- Multiple trials per participant (repeated measures)
- Some participants may have more trials than others (unbalanced)
- LMM handles both issues

---

### **AR-2: Gaze Transitions**

**Data Structure**:
- **Unit of analysis**: Transition events (gaze shift from AOI A to AOI B)
- **Nesting**: Transitions within trials within participants

**Current Plan**: Chi-squared test for independence

**Potential Enhancement**: GLMM with Poisson/Negative Binomial
```python
# Count transitions per trial
model = GLMM.from_formula(
    'transition_count ~ source_aoi * target_aoi + (1 | participant)',
    data=transition_data,
    family=Poisson()
)
```

**Why GLMM could be better**:
- Transitions are count data (0, 1, 2, 3...)
- Multiple trials per participant
- Can test specific transition patterns while accounting for nesting

---

### **AR-3: Social Gaze Triplets**

**Data Structure**:
- **Unit of analysis**: Trial-level triplet counts
- **Nesting**: Trials within participants
- **Outcome**: Count of social gaze triplets per trial (0, 1, 2, 3...)

**Model**: GLMM with Poisson or Negative Binomial
```
triplet_count ~ condition + offset(log(trial_duration)) + (1 | participant)
```

**Why GLMM** (not LMM):
- Triplet counts are **discrete** (0, 1, 2, 3...), not continuous
- Often have **many zeros** (some trials have no triplets)
- Poisson/Negative Binomial distributions are appropriate for counts
- **Offset** normalizes by trial duration (longer trials → more opportunities for triplets)

**Overdispersion Check**:
- If variance > mean → use Negative Binomial instead of Poisson
- We'll check this in the data

---

### **AR-4: Dwell Time**

**Data Structure**:
- **Unit of analysis**: Individual gaze fixations
- **Nesting**: Gaze fixations within trials within participants
- **Outcome**: Duration of each gaze fixation (continuous, milliseconds)

**Model**: LMM with nested random effects
```
dwell_time_ms ~ condition * aoi_category + (1 | participant) + (1 | participant:trial)
```

**Why this structure**:
- **Three levels of nesting**: Gaze fixations → Trials → Participants
- **Random intercept for participant**: Some infants dwell longer overall
- **Random intercept for participant:trial**: Some trials elicit longer dwells
- **Interaction**: Condition effect may differ by AOI

---

### **AR-5: Developmental Trajectory**

**Data Structure**:
- **Unit of analysis**: Trial-level
- **Predictors**: Continuous age (months), condition
- **Nesting**: Trials within participants

**Model**: LMM with continuous age
```
gaze_metric ~ age_months * condition + (1 | participant)
```

**Why continuous age**:
- Preserves full information (no binning into "younger" vs "older")
- Can test non-linear effects: `age_months + age_squared`
- More power than categorical age groups

**Age range in your data**: ~8-14 months
- **Good news**: Sufficient spread to detect developmental changes
- **Interpretation**: Can say "for each additional month of age, gaze duration increases by X ms"

---

### **AR-6: Learning/Habituation (MOST CRITICAL)**

**Data Structure**:
- **Unit of analysis**: Trial-level
- **Predictor**: Trial number (1, 2, 3, ..., 15)
- **Nesting**: Trials within participants
- **Outcome**: Gaze metric across trials

**Model**: LMM with **random slopes**
```
gaze_metric ~ trial_number * condition + (1 + trial_number | participant)
```

**Why random slopes are ESSENTIAL**:
- **Random intercept** (`1 | participant`): Each infant has their own baseline
- **Random slope** (`trial_number | participant`): Each infant has their own habituation rate
- **Interaction** (`trial_number:condition`): Tests if habituation differs by condition

**Example**:
- **Infant A**: Habituates quickly (steep negative slope)
- **Infant B**: Habituates slowly (shallow negative slope)
- **Infant C**: Doesn't habituate (slope near zero)
- **Random slope captures this individual variability**

**Without random slopes**:
- Assumes all infants habituate at the SAME rate
- Underestimates standard errors
- Inflates Type I error

**This is the GOLD STANDARD for habituation analysis!**

---

### **AR-7: Event Dissociation**

**Data Structure**:
- **Unit of analysis**: Trial-level
- **Conditions**: GIVE, GIVE-TO-SELF, HUG (3 levels)
- **Nesting**: Trials within participants

**Model**: LMM with planned contrasts
```
gaze_metric ~ condition + (1 | participant)
```

**Planned Contrasts**:
1. GIVE vs (GIVE-TO-SELF + HUG) / 2  → Tests if GIVE is special
2. GIVE vs GIVE-TO-SELF              → Tests ownership transfer understanding
3. GIVE-TO-SELF vs HUG               → Baseline comparison

---

## 🚨 Critical Warnings Based on Your Data

### **1. Do NOT Aggregate to Participant Means (for most analyses)**

**Wrong approach**:
```python
# ❌ BAD: Aggregate all trials to one mean per participant
participant_means = trial_data.groupby('participant')['gaze_metric'].mean()
t_test(participant_means[condition=='GIVE'], participant_means[condition=='HUG'])
```

**Problems**:
- Throws away trial-level information
- Loses power
- Can't handle missing trials
- Ignores within-participant variability

**Right approach**:
```python
# ✓ GOOD: Use all trial-level data in LMM
model = MixedLM.from_formula(
    'gaze_metric ~ condition + (1 | participant)',
    data=trial_data,  # Each row is a trial
    groups='participant'
)
```

---

### **2. Check for Overdispersion in Count Models (AR-3)**

**What is overdispersion**:
- Poisson assumes variance = mean
- Real data often has variance > mean (overdispersion)
- Example: Most trials have 0-1 triplets, but a few have 5-10

**How to check**:
```python
mean_triplets = triplet_counts.mean()
var_triplets = triplet_counts.var()
dispersion_ratio = var_triplets / mean_triplets

if dispersion_ratio > 1.5:
    print("Overdispersed - use Negative Binomial instead of Poisson")
```

---

### **3. Handle Zero-Inflation (if present)**

**Zero-inflation**: Excess zeros beyond what Poisson/Negative Binomial expects

**Example**:
- Many trials have ZERO social gaze triplets (infant never looked person → toy → person)
- A few trials have 1-3 triplets

**If zero-inflated**:
- Consider **Zero-Inflated Poisson (ZIP)** or **Zero-Inflated Negative Binomial (ZINB)**
- Separate process for "structural zeros" vs "sampling zeros"

**We'll check this during implementation**

---

## 📚 Recommended Next Steps

### **Phase 1: Exploratory Data Analysis (Before Implementation)**

1. **Load full dataset** (all 36 participants)
2. **Calculate descriptive statistics**:
   - Trials per participant (mean, range, distribution)
   - Age distribution (mean, range, spread)
   - Gaze fixations per trial
   - Social triplet counts distribution (check for zeros)
3. **Check data quality**:
   - Missing values
   - Outliers
   - Negative values (should be impossible)
4. **Visualize distributions**:
   - Histograms of outcome variables
   - Q-Q plots to assess normality (for LMM)
   - Count distributions (for GLMM)

---

### **Phase 2: Model Fitting**

1. **Start simple, build complexity**:
   ```python
   # Model 1: Intercept-only (baseline)
   model1 = MixedLM.from_formula('outcome ~ 1 + (1 | participant)', data)

   # Model 2: Add condition
   model2 = MixedLM.from_formula('outcome ~ condition + (1 | participant)', data)

   # Model 3: Add random slope (if justified)
   model3 = MixedLM.from_formula('outcome ~ condition + (1 + condition | participant)', data)

   # Compare models with AIC/BIC
   ```

2. **Check model assumptions**:
   - Residual normality (Q-Q plot)
   - Homoscedasticity (residuals vs fitted)
   - No influential outliers

3. **Report variance components**:
   - **ICC (Intraclass Correlation)**: How much variance is between-participants vs within-participants
   - **Random effects SD**: How much participants vary in their baselines/slopes

---

### **Phase 3: Interpretation & Reporting**

**For each analysis, report**:

1. **Fixed Effects**:
   - Coefficient (β)
   - Standard error
   - t-statistic or z-statistic
   - p-value
   - 95% Confidence interval
   - **Effect size** (Cohen's d or rate ratio)

2. **Random Effects**:
   - Participant variance (τ²)
   - Residual variance (σ²)
   - ICC = τ² / (τ² + σ²)

3. **Model Fit**:
   - AIC, BIC (for model comparison)
   - R² marginal (variance explained by fixed effects)
   - R² conditional (variance explained by fixed + random effects)

4. **Diagnostic Plots**:
   - Residual plots
   - Q-Q plot
   - Random effects distribution

---

## 🎓 Key Takeaways for Your Project

### **1. Your Data Structure DEMANDS LMM/GLMM**

The nested structure (frames → trials → participants) makes traditional tests inappropriate. This isn't a preference - it's a **statistical requirement** for valid inference.

### **2. Random Slopes for AR-6 are NON-NEGOTIABLE**

Habituation analysis with simple linear regression would be statistically invalid. Random slopes are essential.

### **3. Count Data (AR-3) Needs GLMM, Not LMM**

Social gaze triplets are counts (0, 1, 2, 3...), not continuous. Poisson or Negative Binomial GLMM is the right tool.

### **4. Continuous Age (AR-5) is Superior to Binning**

With age range 8-14 months, you have enough spread to model age continuously. Don't bin into "younger" vs "older" - you lose information and power.

### **5. Your Config Updates Are Excellent**

The YAML configs with LMM formulas are well-designed and will make implementation straightforward.

---

## 📖 Further Reading

**Essential Papers**:
1. **Barr et al. (2013)** - "Keep it maximal" for confirmatory hypothesis testing
2. **Baayen, Davidson & Bates (2008)** - Mixed-effects modeling with crossed random effects
3. **Mirman (2014)** - Growth curve analysis (great for AR-6 habituation)

**Tutorials**:
1. **Winter (2013)** - "Linear models and linear mixed effects models in R" (concepts apply to Python)
2. **Bates (2010)** - "lme4: Mixed-effects modeling with R" (concepts applicable to statsmodels)

---

## ✅ Conclusion

Your decision to switch to LMM/GLMM is **100% correct** given your data structure. The nested hierarchy (frames → trials → participants) with thousands of observations per participant makes this the **only statistically valid approach**.

The traditional methods (t-tests, ANOVA) would give you **incorrect p-values** and lead to **false conclusions**. LMM/GLMM provides:
- ✓ Correct standard errors
- ✓ Valid p-values
- ✓ Better power
- ✓ Handles missing data
- ✓ Models individual differences
- ✓ Aligns with modern standards in developmental psychology

**You're ready to proceed with implementation!**

---

**Questions to consider as you implement**:
1. Should we fit crossed random effects (participants × trials) for AR-4 dwell time?
2. Do we need zero-inflated models for AR-3 triplets?
3. Should we test random slopes for condition effects (not just intercepts)?
4. How should we handle participants with very few trials?

We can refine these during implementation based on actual model diagnostics.
