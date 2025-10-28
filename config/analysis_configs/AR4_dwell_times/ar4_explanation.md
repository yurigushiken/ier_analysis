# AR4 Analysis: Understanding Dwell Time on Areas of Interest

## What is the Research Question (RQ)?

While **AR1** measures *how much* time infants look at toys, **AR4** asks a more detailed question:

**"How long do infants' individual gaze fixations last when looking at different areas of interest (AOIs)? Does fixation duration differ by condition or AOI type?"**

This is about the **quality** of looking, not just the quantity. Longer dwell times suggest deeper processing or greater interest.

---

## What Does AR4 Measure? (Key Concept: Dwell Time)

**Dwell time** = The duration of a single, uninterrupted gaze fixation on an AOI

### Key Distinction from AR1:

| Measure | AR1 | AR4 |
|---------|-----|-----|
| **Unit of analysis** | Total time per trial | Individual fixations |
| **What it measures** | Cumulative attention | Single-fixation duration |
| **Example** | "Looked at toy for 2 seconds total across 5 fixations" | "Each fixation on toy lasted 0.4 seconds on average" |

### Why Does Dwell Time Matter?

**Longer dwell times indicate:**
- 🧠 Deeper cognitive processing
- 🎯 Greater interest or salience
- 📊 More effortful encoding
- 🔍 Careful examination

**Shorter dwell times suggest:**
- 👀 Rapid scanning
- ⚡ Less engagement
- 🔄 Sampling strategy
- 📱 Distraction or disinterest

---

## How This Analysis Works

### Core Calculation:

For each gaze fixation (remember: 3+ consecutive frames on same AOI):

```
Dwell Time (ms) = Fixation Duration in milliseconds
```

Then aggregate by:
1. **Participant + Condition**: Average dwell time per participant in each condition
2. **Participant + Condition + AOI**: Average dwell time per participant per condition per AOI type
3. **Condition-level**: Overall averages across all participants

---

## What Do the Results Show?

### Typical AR4 Output Structure:

#### 1. **Mean Dwell Times by Condition**

Example results:

| Condition | Mean Dwell (ms) | SD | N Participants | N Fixations |
|-----------|-----------------|-----|----------------|-------------|
| GIVE_WITH | 425.3 | 156.8 | 46 | 1,847 |
| HUG_WITH | 398.2 | 142.1 | 46 | 1,652 |

**Interpretation:**
- On average, fixations last ~400ms (about 0.4 seconds)
- GIVE_WITH has slightly longer dwells than HUG_WITH
- High SD indicates substantial individual variation

#### 2. **Dwell Times by AOI Category**

| AOI | GIVE_WITH (ms) | HUG_WITH (ms) | Difference |
|-----|----------------|---------------|------------|
| Toy | 458.3 | 412.5 | +45.8 |
| Man Face | 402.1 | 395.8 | +6.3 |
| Woman Face | 415.7 | 408.3 | +7.4 |
| Man Body | 380.2 | 375.1 | +5.1 |

**Interpretation:**
- Infants fixate longest on the toy in GIVE conditions
- Face fixations are intermediate duration
- Body fixations are shortest
- Pattern suggests toy is most engaging in GIVE events

---

## Understanding the Statistics in AR4

### Statistical Tests Used

AR4 uses **Linear Mixed Models (LMM)** or **Generalized Linear Mixed Models (GLMM)**:

#### Why Mixed Models?

Mixed models handle:
- **Multiple observations per participant** (many fixations per person)
- **Repeated measures** (same participant across conditions)
- **Random effects** (individual baseline differences)
- **Fixed effects** (condition, AOI type)

#### Model Structure (Typical):

```
Dwell Time ~ Condition + (1|Participant)
```

**Translation:**
- **Dwell Time**: The outcome (how long fixations last)
- **Condition**: Fixed effect (GIVE vs HUG)
- **(1|Participant)**: Random intercept (each person has their own baseline)

### Key Statistical Outputs

#### 1. Fixed Effects Table

| Effect | Estimate | SE | t-value | p-value |
|--------|----------|----|---------|---------|
| Intercept | 415.2 | 18.3 | 22.68 | <.001 |
| Condition [HUG_WITH] | -27.1 | 12.4 | -2.18 | .031 |

**Interpretation:**
- **Intercept**: Baseline dwell time (GIVE_WITH) is 415.2ms
- **Condition effect**: HUG_WITH has 27.1ms shorter dwells (significant, p=.031)

#### 2. Random Effects

```
Random Effect: Participant Intercept
  Variance: 2840.5
  SD: 53.3
```

**Interpretation:**
- Individual participants vary by ~53ms in their baseline dwell times
- This accounts for "some people look longer at everything" vs. "some scan quickly"

#### 3. Model Fit Statistics

- **AIC** (Akaike Information Criterion): Lower is better for model comparison
- **BIC** (Bayesian Information Criterion): Lower is better, penalizes complexity more
- **Log-Likelihood**: Higher (less negative) indicates better fit

---

## Important Methodological Details

### Filtering and Outlier Detection

AR4 includes sophisticated data cleaning:

#### 1. Minimum Dwell Time
```yaml
min_dwell_time_ms: 100
```
- Excludes very brief fixations (<100ms)
- Rationale: Too short to represent meaningful looking

#### 2. Maximum Dwell Time
```yaml
max_dwell_time_ms: 5000
```
- Excludes extremely long fixations (>5 seconds)
- Rationale: May represent tracker loss or off-task behavior

#### 3. Outlier Removal by Standard Deviation
```yaml
outlier_threshold_sd: 3.0
```
- Within each participant × condition, removes fixations >3 SD from mean
- Rationale: Extreme values may be measurement artifacts

### Why These Filters Matter

**Example without filtering:**
- One corrupted fixation: 45,000ms (45 seconds - clearly invalid)
- Would skew the mean dramatically
- Would reduce statistical power to detect real effects

**Example with filtering:**
- Removes that extreme value
- Retains valid data (100ms to 5000ms range)
- Cleaner, more reliable averages

---

## Visualizations in AR4

### 1. Dwell Time by Condition
- Bar chart with error bars (SEM or CI)
- Compares mean dwell across conditions
- Shows if one condition elicits longer looking

### 2. Dwell Time by AOI and Condition
- Grouped bar chart
- Shows which AOIs get longest fixations
- Can reveal interactions (e.g., toy dwell increases more in GIVE than HUG)

### 3. Distribution Plots
- Histograms or violin plots
- Shows the full distribution of dwell times
- Reveals whether data is normal or skewed

---

## Theoretical Implications

### What Longer Dwell Times Mean

If **GIVE_WITH has longer dwells than HUG_WITH**, this suggests:

1. **Deeper Processing Hypothesis**:
   - Infants spend more time processing each fixation in GIVE events
   - May reflect greater cognitive effort to understand the transfer action

2. **Interest/Engagement Hypothesis**:
   - GIVE events are more engaging
   - Infants are more captivated by the transfer of objects

3. **Encoding Hypothesis**:
   - More time needed to encode the toy as relevant argument
   - Longer fixations support memory formation

### What AOI-Specific Dwell Patterns Mean

If **toy dwells are longest**:
- Toy is most salient or interesting element
- Consistent with AR1 finding (infants look at toy more)
- Suggests both quantity (AR1) and quality (AR4) of toy attention

If **face dwells are intermediate**:
- Faces get moderate sustained attention
- Balance between gathering social info and monitoring other elements

If **body/hands dwells are shortest**:
- Bodies are scanned quickly
- May be peripheral to understanding the event
- Or: Information extracted more efficiently (less processing needed)

---

## AR4 vs. Other Analyses

### Comparison Table

| Analysis | Question | Metric | Example Finding |
|----------|----------|--------|-----------------|
| **AR1** | Where do they look? | Total duration | 20% of time on toy in GIVE |
| **AR2** | How do they scan? | Transition probability | 67% chance toy→face |
| **AR3** | Do they triangulate? | Triplet count | 0.06 triplets per trial |
| **AR4** | How long per fixation? | Dwell time (ms) | 425ms per fixation on toy |

**All four analyses together** provide a complete picture:
- **AR1**: Toy gets more total time in GIVE
- **AR2**: Toy is connected to faces via transitions
- **AR3**: Some infants make full person-toy-person sequences
- **AR4**: Individual toy fixations are longer in GIVE (deeper processing)

---

## Interpreting Your Results

### Example Scenario 1: Significant Condition Effect

**Result**: GIVE_WITH dwells (450ms) > HUG_WITH dwells (380ms), p < .01

**Interpretation**:
- ✅ Infants process GIVE events more deeply (longer per fixation)
- ✅ Complements AR1 (they look more AND look longer per fixation)
- ✅ Supports verb-argument structure: Relevant events get qualitatively different attention

### Example Scenario 2: No Condition Effect, But AOI × Condition Interaction

**Result**:
- Overall dwell: GIVE (400ms) ≈ HUG (395ms), p = .45
- But toy dwell: GIVE (480ms) > HUG (350ms), p < .001
- Face dwell: GIVE (390ms) ≈ HUG (385ms), p = .62

**Interpretation**:
- ✅ Overall looking depth similar across conditions
- ✅ BUT: Toy-specific dwells are much longer in GIVE
- ✅ This is a more **specific** effect than overall condition differences
- ✅ Supports selective processing: Longer dwells only where it matters (toy in GIVE)

### Example Scenario 3: High Individual Variability

**Result**:
- Mean dwell: 400ms
- Random effect SD: 80ms
- Some participants average 250ms, others 550ms

**Interpretation**:
- ⚠️ Substantial individual differences in looking style
- Some infants are "quick scanners," others are "slow processors"
- ✅ This is normal and interesting
- ✅ May relate to temperament, attention control, or processing speed
- ✅ LMM appropriately accounts for this via random effects

---

## Limitations and Considerations

### 1. Dwell Time Isn't Always Better

**Longer ≠ always better:**
- Very long dwells might indicate **confusion** rather than deep processing
- Quick dwells might indicate **efficient processing**, not lack of interest
- Context matters!

### 2. Fixation Definition Matters

AR4 uses the same fixation definition as AR1:
- **Fixation** = 3+ consecutive frames on same AOI
- At 30 fps: Minimum fixation = 100ms

Different definitions would yield different dwell times.

### 3. Multiple Comparisons

If testing many AOIs × many conditions:
- Risk of false positives increases
- Consider correction (e.g., Bonferroni) or focus on planned comparisons
- LMM partially addresses this via modeling the structure

---

## Advanced: Understanding the LMM Output

### Sample LMM Summary:

```
Linear Mixed Model Fit by REML
Formula: dwell_time_ms ~ condition_name + (1 | participant_id)

Fixed Effects:
                        Estimate  Std.Error  t-value  p-value
(Intercept)              425.18      19.34    21.99   <.0001
condition_name[HUG_WITH] -32.45      14.12    -2.30    .0226

Random Effects:
  Groups          Name        Variance   Std.Dev
  participant_id  (Intercept)  2956.3     54.37
  Residual                    18430.2    135.76

Number of observations: 3499
Number of groups (participant_id): 46

AIC: 48562.3
BIC: 48589.1
```

### How to Read This:

**Fixed Effects:**
- Baseline (GIVE_WITH): 425.18ms average dwell
- HUG_WITH effect: -32.45ms difference (shorter dwells)
- t = -2.30, p = .023 → **Significant** difference

**Random Effects:**
- Participant variance: 2956.3 → SD = 54.37ms
  - Participants vary by about 54ms in their baseline dwells
- Residual variance: 18430.2 → SD = 135.76ms
  - Individual fixations vary by about 136ms within participants

**Interpretation:**
- There's more variation **within** people (136ms) than **between** people (54ms)
- This is typical: Each person's fixations vary a lot trial-to-trial
- The participant random effect still improves the model by accounting for individual baselines

---

## The Bottom Line

**AR4 reveals the quality of looking** by measuring how long each individual fixation lasts. Longer dwell times suggest deeper processing, greater interest, or more effortful encoding.

Combined with AR1 (quantity), AR2 (scanning patterns), and AR3 (social coordination), AR4 completes a comprehensive picture of infant visual attention during event observation.

**Key insight**: It's not just *how much* infants look (AR1) but *how long each look lasts* (AR4) that tells us about cognitive processing depth!

---

## Connection to Gordon (2003)

Gordon's original work showed infants look longer (total time) at relevant objects. AR4 extends this by showing:
- Not just **more looking**, but **deeper looking** (longer per fixation)
- This suggests **qualitative differences** in processing, not just quantitative
- Provides finer-grained evidence for verb-argument structure understanding

The combination of high-resolution eye-tracking (AR1-AR4) reveals mechanisms Gordon couldn't access with overall looking time measures!
