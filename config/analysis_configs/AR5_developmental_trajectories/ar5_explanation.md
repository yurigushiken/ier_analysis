# AR5 Analysis: Understanding Developmental Trajectories of Event Comprehension

## What is the Research Question (RQ)?

While **AR1-AR4** ask whether infants show particular attention patterns (where they look, how they scan, how they coordinate, how deeply they process), **AR5** asks a fundamentally different question:

**"WHEN does event understanding develop? Does the ability to distinguish between relevant and incidental objects change with age?"**

Specifically: **Is there an Age × Condition interaction, meaning that the difference between conditions (e.g., GIVE vs HUG) grows larger or smaller as infants get older?**

### For GIVE_WITH vs HUG_WITH:

This analysis tests whether the toy-looking difference between GIVE and HUG events changes across the infant age range (typically 7-12 months).

**Three possible developmental patterns:**

1. **Early competence**: Even 7-month-olds distinguish GIVE from HUG (no interaction, main effect only)
2. **Emergent understanding**: Younger infants show no difference, but older infants do (significant interaction)
3. **Refinement with age**: All ages show the effect, but it gets stronger with development (significant interaction)

---

## What Does AR5 Measure? (Key Concept: Age × Condition Interaction)

An **interaction** occurs when the effect of one variable (Condition) depends on the level of another variable (Age).

### Understanding Interactions Visually:

**No Interaction (Parallel Lines)**:
```
Proportion Looking at Toy
    ^
0.25|           GIVE ●━━━━━━━●━━━━━━━●
    |
0.15|           HUG  ●━━━━━━━●━━━━━━━●
    |
    └──────────────────────────────────>
              7 mo    9 mo    11 mo
```
The GIVE-HUG difference is **constant** across ages → No interaction

**Significant Interaction (Non-Parallel Lines)**:
```
Proportion Looking at Toy
    ^
0.25|                       GIVE ●
    |                          ╱
0.20|              ●━━━━━━●╱
    |            ╱
0.15|    GIVE ●━
    |    HUG  ●━━━━━━●━━━━━━━●
    |
    └──────────────────────────────────>
              7 mo    9 mo    11 mo
```
The GIVE-HUG difference **grows** with age → Significant interaction

---

## How This Analysis Works

### Core Statistical Model:

AR5 uses a **Linear Mixed Model (LMM)** with the formula:

```
proportion_primary_aois ~ age_months + C(condition) + age_months:C(condition) + (1 | participant)
```

**Breaking this down:**

| Term | What it tests | Example interpretation |
|------|---------------|------------------------|
| `age_months` | **Main effect of age** | Do infants look more at primary AOIs as they get older? |
| `C(condition)` | **Main effect of condition** | Do GIVE and HUG differ on average across all ages? |
| `age_months:C(condition)` | **THE INTERACTION** | Does the GIVE-HUG difference change with age? |
| `(1 | participant)` | **Random intercept** | Accounts for individual baseline differences |

### What Gets Modeled?

**Dependent Variable (default)**: `proportion_primary_aois`
- Proportion of looking time spent on primary areas of interest (faces + toy)
- Same metric used in AR1, but now modeled as a function of both age AND condition

**Alternative dependent variables** (configurable):
- `social_triplet_rate`: Age effects on social coordination (AR3 metric)
- `mean_dwell_time`: Age effects on processing depth (AR4 metric)

---

## Understanding the Statistics in AR5

### The Three Key Effects to Examine:

#### 1. Main Effect of Age

**What it tests**: Does overall looking change with age, regardless of condition?

**Example result**:
```
age_months: β = 0.015, SE = 0.005, t = 3.0, p = .003
```

**Interpretation**:
- For every 1-month increase in age, proportion looking increases by 0.015 (1.5%)
- This is averaged across both GIVE and HUG conditions
- Significant main effect suggests general developmental maturation

**What it means theoretically**:
- Older infants may have better attention control
- Or greater interest in social events overall
- Or more efficient visual processing

#### 2. Main Effect of Condition

**What it tests**: Do conditions differ on average across all ages?

**Example result**:
```
C(condition)[HUG_WITH]: β = -0.087, SE = 0.024, t = -3.62, p < .001
```

**Interpretation**:
- HUG_WITH has 0.087 (8.7%) lower proportion looking than GIVE_WITH (the reference level)
- This is the average difference across all ages
- Significant main effect confirms conditions differ overall

**What it means theoretically**:
- Replicates AR1 findings: GIVE gets more attention than HUG
- But this is the average effect—interaction tells us if it varies by age

#### 3. Age × Condition Interaction (THE CRITICAL TEST)

**What it tests**: Does the condition effect change with age?

**Example result (Significant Interaction)**:
```
age_months:C(condition)[HUG_WITH]: β = -0.012, SE = 0.005, t = -2.4, p = .018
```

**Interpretation**:
- The GIVE-HUG difference increases by 0.012 (1.2%) for each month of age
- At 7 months: GIVE-HUG difference might be 5%
- At 12 months: GIVE-HUG difference might be 11% (5 months × 1.2% = 6% growth → 11% total)
- **Conclusion**: Event structure understanding emerges or strengthens with development

**Example result (Non-Significant Interaction)**:
```
age_months:C(condition)[HUG_WITH]: β = -0.003, SE = 0.006, t = -0.5, p = .62
```

**Interpretation**:
- The GIVE-HUG difference stays relatively constant across ages
- Younger infants already show the distinction
- **Conclusion**: Event structure understanding is present throughout the 7-12 month range

---

## What Do the Results Tell Us?

### Scenario 1: Significant Interaction + Significant Main Effects

**Statistical Pattern**:
- Main effect of age: p < .05
- Main effect of condition: p < .05
- Age × Condition interaction: p < .05

**Interpretation**:
✅ **Developmental emergence or refinement**
- Both conditions show age-related increases
- But the conditions diverge with age (non-parallel trajectories)
- Event comprehension is age-dependent

**Example**:
- 7 months: GIVE (15%) vs HUG (14%) → barely different
- 12 months: GIVE (25%) vs HUG (15%) → clearly different
- **Conclusion**: Event structure understanding develops between 7-12 months

**Theoretical Implication**:
This would suggest that verb-argument structure understanding is NOT fully present at 7 months but emerges during the first year of life, possibly linked to crawling onset, joint attention development, or language exposure.

---

### Scenario 2: Significant Main Effects, Non-Significant Interaction

**Statistical Pattern**:
- Main effect of age: p < .05
- Main effect of condition: p < .05
- Age × Condition interaction: p > .05

**Interpretation**:
✅ **Early competence with general maturation**
- Both conditions increase with age (parallel trajectories)
- GIVE-HUG difference is constant across ages
- Event comprehension is present early but overall attention improves

**Example**:
- 7 months: GIVE (12%) vs HUG (8%) → 4% difference
- 12 months: GIVE (22%) vs HUG (18%) → 4% difference
- **Conclusion**: Event structure understanding is present at 7 months; general attention matures

**Theoretical Implication**:
This would suggest that verb-argument structure understanding is an **early-emerging competence**, present even in 7-month-olds, but expressed more robustly with age due to general improvements in attention, visual processing, or engagement.

---

### Scenario 3: Significant Condition Effect Only

**Statistical Pattern**:
- Main effect of age: p > .05
- Main effect of condition: p < .05
- Age × Condition interaction: p > .05

**Interpretation**:
✅ **Stable early competence**
- No overall age-related change
- GIVE-HUG difference is stable across ages
- Event comprehension is robust throughout age range

**Example**:
- 7 months: GIVE (18%) vs HUG (12%) → 6% difference
- 12 months: GIVE (19%) vs HUG (13%) → 6% difference
- **Conclusion**: Event structure understanding is stable across 7-12 months

**Theoretical Implication**:
This would suggest verb-argument structure understanding is a **foundational cognitive ability** present throughout infancy, not dependent on age-related maturation within this range. The competence might emerge before 7 months.

---

### Scenario 4: No Significant Effects

**Statistical Pattern**:
- Main effect of age: p > .05
- Main effect of condition: p > .05
- Age × Condition interaction: p > .05

**Interpretation**:
❌ **No evidence for condition discrimination**
- No difference between GIVE and HUG at any age
- Contradicts AR1 findings

**Possible explanations**:
- Sample size too small for AR5's more complex model
- High individual variability masks effects
- Need different dependent variable
- Artifact of data filtering or modeling choices

---

## Model Comparison and ANOVA Table

### Understanding Nested Model Comparisons

AR5 fits multiple models and compares them:

| Model | Formula | What it tests |
|-------|---------|---------------|
| **Model 1** | `outcome ~ age_months + (1│participant)` | Age effect only |
| **Model 2** | `outcome ~ age_months + C(condition) + (1│participant)` | + Condition main effect |
| **Model 3** | `outcome ~ age_months + C(condition) + age:C(condition) + (1│participant)` | + Interaction |

### ANOVA Table Interpretation

**Example ANOVA output**:

| Model | AIC | BIC | logLik | Deviance | χ² | Df | p-value |
|-------|-----|-----|--------|----------|-------|-----|---------|
| 1 (Age) | 245.3 | 256.1 | -118.6 | 237.3 | — | — | — |
| 2 (+ Condition) | 238.5 | 252.8 | -114.2 | 228.5 | 8.8 | 1 | .003 |
| 3 (+ Interaction) | 234.1 | 251.9 | -111.0 | 222.1 | 6.4 | 1 | .011 |

**How to read this**:

**Model 2 vs Model 1**:
- χ²(1) = 8.8, p = .003
- Adding Condition significantly improves fit
- **Conclusion**: Condition matters

**Model 3 vs Model 2**:
- χ²(1) = 6.4, p = .011
- Adding the interaction significantly improves fit
- **Conclusion**: Interaction is real; age moderates condition effect

**AIC/BIC values**:
- Lower is better
- Model 3 has lowest AIC (234.1) → best fit
- Model 3 has lowest BIC (251.9) → best fit considering complexity
- **Conclusion**: Interaction model is the best representation of the data

---

## Important Methodological Details

### Continuous vs Categorical Age

**Default (Continuous)**:
```yaml
use_continuous_age: true
```
- Treats age as continuous (7, 8, 9, 10, 11, 12 months)
- Assumes linear relationship between age and outcome
- **Advantage**: More statistical power, tests for smooth developmental trajectories
- **Use when**: You have participants across multiple age points

**Alternative (Categorical)**:
```yaml
use_continuous_age: false
```
- Treats age as discrete groups (e.g., "7-8 months" vs "9-10 months" vs "11-12 months")
- No linearity assumption
- **Advantage**: Can detect non-monotonic patterns (e.g., U-shaped development)
- **Use when**: Theory predicts discrete developmental stages

---

### Testing for Nonlinear Trajectories

**Default (Linear)**:
```yaml
test_nonlinear: false
```
- Model: `outcome ~ age`
- Assumes straight-line relationship

**Quadratic Option**:
```yaml
test_nonlinear: true
```
- Model: `outcome ~ age + age²`
- Allows for curved developmental trajectories

**Example of when to use quadratic**:

**Accelerating development** (positive quadratic):
```
    ^
    |                        ●
    |                   ●╱
    |              ●╱
    |         ●╱
    |    ●●
    └──────────────────────>
         Age
```
Understanding starts slowly, then accelerates

**Decelerating development** (negative quadratic):
```
    ^
    |    ●━━━●━━━━●
    |  ╱
    | ●
    |●
    └──────────────────────>
         Age
```
Rapid early growth, then plateaus

---

## Visualizations in AR5

### 1. Age × Condition Interaction Plot

**What it shows**:
- X-axis: Age (months)
- Y-axis: Proportion looking at primary AOIs
- Separate lines for each condition (GIVE vs HUG)

**Key features**:
- **Data points**: Raw participant means
- **Fitted lines**: LMM predictions
- **Confidence bands**: Uncertainty around predictions
- **Parallelism**: Visual test for interaction
  - Parallel lines → no interaction
  - Diverging/converging lines → interaction present

**Example interpretation**:
If lines fan out (diverge) with age:
→ Interaction significant
→ Condition effect grows with development

---

### 2. Coefficient Plot

**What it shows**:
- Bar chart or dot plot of model coefficients
- Error bars represent standard errors or 95% CIs
- Highlights which effects are significant

**Key elements**:
- **Age coefficient**: Developmental slope
- **Condition coefficient**: Average condition difference
- **Interaction coefficient**: How slope differs by condition

---

## Comparison to Other Analyses

| Analysis | Research Question | Age Treatment | Output |
|----------|-------------------|---------------|--------|
| **AR1** | Where do infants look? | Age as grouping factor | Means by age group |
| **AR2** | How do infants scan? | Age as grouping factor | Transitions by age group |
| **AR3** | Do they triangulate socially? | Age as grouping factor | Triplet counts by age group |
| **AR4** | How deeply do they process? | Age as grouping factor | Dwell times by age group |
| **AR5** | When does understanding develop? | **Age as continuous predictor** | **Developmental trajectories** |

**Key difference**: AR1-AR4 treat age as a **category** (compare age groups). AR5 treats age as a **continuous variable** (model developmental change).

---

## Including Adults as Mature Baseline

### Why Include Adults?

AR5 configurations typically include both infant and adult cohorts:

```yaml
cohorts:
  - key: "infant"
    participant_filters:
      participant_type: ["infant"]
  - key: "adult"
    participant_filters:
      participant_type: ["adult"]
```

**Purpose**:
- Adults represent the "end state" of development
- Shows where the developmental trajectory is heading
- Validates that the task works and conditions differ in mature participants

**Interpretation**:
- If adults show a strong GIVE-HUG effect (e.g., 30% difference)
- And infants show a smaller but growing effect (e.g., 5% at 7 mo → 15% at 12 mo)
- **Conclusion**: Development continues beyond infancy toward adult-like competence

---

## Understanding Random Effects

### Why Random Intercepts?

The model includes `(1 | participant)`, which means:
- Each participant has their own baseline level
- Some infants are "high lookers" (look more at everything)
- Some infants are "low lookers" (look less at everything)
- Random effects account for this, isolating the age and condition effects

**Example**:
- Infant A: Baseline 30% looking (high looker)
- Infant B: Baseline 10% looking (low looker)
- Both show same GIVE-HUG difference (8%)
- Random intercept captures the 30% vs 10% baseline difference
- Fixed effects capture the 8% condition effect

**Technical note**:
```
Random Effect: Participant Intercept
  Variance: 0.012
  SD: 0.11
```
This tells you how much participants vary in their baselines (11% in this example).

---

## Limitations and Considerations

### 1. Sample Size Requirements

**Minimum recommendations**:
- At least **6 participants** per condition for stable LMM estimates
- At least **3 different age points** for continuous age modeling
- Broader age range (e.g., 7-12 months) gives more power than narrow range (e.g., 8-9 months)

**Warning signs**:
- "Singular fit" or "convergence failure" messages → model is overfitted
- Very wide confidence intervals → insufficient data
- Solution: Simplify model or collect more data

### 2. Linearity Assumption

**With continuous age**, the default model assumes:
- Straight-line relationship between age and outcome
- May not capture non-monotonic development

**Solutions**:
- Set `test_nonlinear: true` to add quadratic term
- Or use categorical age if theory predicts stages

### 3. Missing Age Range

**If your sample only has 8-month-olds**:
- Can't test age effects (no variance in age)
- AR5 will fail or warn

**Solution**:
- Collect data across broader age range
- Or use AR1-AR4 for age-group comparisons instead

### 4. Correlation Between Age and Other Variables

**Confounds**:
- If older infants had different testing conditions (e.g., different experimenter, different time of day)
- Age effect could be artifact

**Solution**:
- Randomize testing conditions across ages
- Control for potential confounds in model if measured

---

## Advanced Topics

### Testing Different Dependent Variables

AR5 can model any continuous outcome:

**Proportion looking (default)**:
```yaml
metrics:
  dependent_variables:
    - "proportion_primary_aois"
```

**Social coordination (AR3)**:
```yaml
metrics:
  dependent_variables:
    - "social_triplet_rate"
```
Tests: Does triplet production rate change with age differently for GIVE vs HUG?

**Processing depth (AR4)**:
```yaml
metrics:
  dependent_variables:
    - "mean_dwell_time"
```
Tests: Do dwell times change with age differently for GIVE vs HUG?

---

### Interpreting Effect Sizes

**R² (Variance Explained)**:
```
R² = 0.42
```
- The model explains 42% of variance in looking proportions
- Remaining 58% is individual differences and noise

**R² Adjusted**:
```
R² adj = 0.38
```
- Adjusted for number of predictors
- Penalizes model complexity
- More conservative estimate

**What's a good R²?**:
- R² > 0.30: Good fit for developmental data
- R² > 0.50: Excellent fit
- R² < 0.20: Weak predictive power; high individual variability

**AIC/BIC (Model Comparison)**:
- Lower AIC/BIC = better model
- Compare models with vs without interaction
- Difference > 10 suggests strong evidence for better model

---

## The Bottom Line

**AR5 reveals the developmental timing of event comprehension** by testing whether condition effects change with age. This moves beyond asking "Do infants understand event structure?" (AR1-AR4) to asking **"When does this understanding emerge or strengthen?"** (AR5).

The **Age × Condition interaction** is the critical test:
- **Significant interaction** → Understanding develops or refines with age
- **Non-significant interaction** → Understanding is stable across the age range tested

Combined with AR1-AR4 (which show **what** patterns exist), AR5 tells you **when** those patterns emerge, providing a complete developmental picture.

---

## Connection to Broader Research Goals

### Why Developmental Trajectories Matter

Understanding **when** verb-argument structure comprehension emerges helps answer:

1. **Nature vs. nurture**: Is this ability innate or learned?
   - Early emergence (present at 7 months) → more likely innate
   - Later emergence (develops 7-12 months) → more likely learned

2. **Critical periods**: Are there sensitive windows for development?
   - Accelerating trajectory → rapid learning period
   - Linear trajectory → steady continuous growth

3. **Individual differences**: Do infants follow different developmental paths?
   - High random effect variance → substantial individual variation
   - Low random effect variance → universal developmental pattern

4. **Intervention timing**: When should we support language development?
   - If effect emerges at 9 months → interventions most effective before 9 months
   - If effect is stable → interventions can target broader age range

---

## Connection to Gordon (2003)

Gordon's original work showed that infants **around 12-13 months** could distinguish relevant from incidental objects. AR5 extends this by:

- Testing whether this competence is present **earlier** (7-8 months)
- Modeling the **continuous developmental trajectory** rather than testing a single age
- Quantifying **how much** the effect changes with each month of development
- Providing **statistical evidence** for when the transition occurs

If AR5 shows a significant Age × Condition interaction with the effect emerging around 9-10 months, this would **refine Gordon's timeline** with high-resolution eye-tracking and continuous age modeling.

---

## Practical Example: Interpreting Your Results

### Sample Output Interpretation:

**Model Coefficients**:
```
Fixed Effects:
  Intercept (GIVE_WITH at age = 0):    β = 0.05,  SE = 0.03,  p = .10
  age_months:                          β = 0.012, SE = 0.003, p < .001
  C(condition)[HUG_WITH]:              β = -0.08, SE = 0.02,  p < .001
  age_months:C(condition)[HUG_WITH]:   β = -0.008,SE = 0.004, p = .04
```

**Translation**:
1. **Intercept**: Not interpretable (age=0 is outside data range)
2. **age_months (β = 0.012, p < .001)**: Each month of age increases looking by 1.2% on average
3. **Condition (β = -0.08, p < .001)**: HUG_WITH has 8% lower looking than GIVE_WITH on average
4. **Interaction (β = -0.008, p = .04)**: The HUG disadvantage grows by 0.8% per month

**Visualization**:
- At 7 months: GIVE (14%) vs HUG (12%) → 2% difference
- At 12 months: GIVE (20%) vs HUG (14%) → 6% difference
- Lines are non-parallel → interaction confirmed

**Conclusion**:
✅ **Event structure understanding strengthens with development**
- Even 7-month-olds show a small GIVE-HUG distinction
- By 12 months, the distinction is three times larger
- Development is continuous and linear across this age range

**Theoretical Implication**:
This pattern suggests early-emerging but **refining competence**—infants have some verb-argument structure understanding at 7 months, but it becomes more robust with age, possibly due to increased language exposure, motor development (reaching/grasping), or improved attention control.

---

**Last Updated**: 2025-10-29
**Author**: Claude (IER Analysis Assistant)
**Status**: Complete

