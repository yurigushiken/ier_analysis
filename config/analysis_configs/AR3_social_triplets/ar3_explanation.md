# AR3 Analysis: Understanding Social Gaze Coordination (Triplets)

## What is the Research Question (RQ)?

While **AR1** measures *where* infants look and **AR2** measures *how* they scan between areas, **AR3** asks:

**"Do infants coordinate their attention socially by looking between the two actors and the object in a systematic sequence?"**

Specifically: **Do infants produce "social gaze triplets" - sequences where they look from one person's face, to the toy, to the other person's face?**

### Example of a Social Gaze Triplet:

```
Woman's Face → Toy → Man's Face
```

This pattern suggests the infant is **socially triangulating** - connecting both people to the object, which is a sophisticated form of social cognition.

---

## What Does AR3 Measure? (Key Concept: Triplets)

A **social gaze triplet** is a specific sequence of three consecutive gaze fixations:

1. **First fixation**: One actor's face (man or woman)
2. **Second fixation**: The toy (present or at its location if absent)
3. **Third fixation**: The other actor's face

### Valid Triplet Patterns:

AR3 looks for two patterns:
- **Pattern A**: `man_face → toy_present → woman_face`
- **Pattern B**: `woman_face → toy_present → man_face`

### What Makes a Valid Triplet?

The analysis configuration determines what counts as valid:

- **Consecutive requirement**: Are the three gazes directly one after another, or can there be brief gaps?
- **Frame gaps allowed**: How many frames (if any) can separate the gazes?
- **No repeated AOIs**: The pattern can't be man→man→woman (same AOI twice in a row)

---

## What Do the Results Show?

### Key Findings (from ar3_gw_vs_hw):

**Overall Detection:**
- ✅ **25 triplets detected** across 245 trials
- ✅ **18 participants** showed at least one triplet (out of 123 total)
- ✅ Detection rate: ~15% of participants produced triplets

**By Condition:**

| Condition | Mean Triplets/Trial | N Participants | Total Triplets |
|-----------|---------------------|----------------|----------------|
| GIVE_WITH | 0.056 | 62 | 11 |
| HUG_WITH | 0.069 | 61 | 14 |

**Directional Patterns:**

| Pattern | GIVE_WITH | HUG_WITH | Total |
|---------|-----------|----------|-------|
| man_face → toy → woman_face | 6 | 6 | 12 |
| woman_face → toy → man_face | 5 | 8 | 13 |

**Both directions are roughly balanced**, suggesting infants don't have a systematic bias toward starting with one actor over the other.

---

## Understanding the Statistics in AR3

### Comprehensive Statistical Inference

AR3 provides both **descriptive statistics** (means, counts, frequencies) and **inferential statistics** via Generalized Linear Mixed Models (GLMMs):

#### Statistical Methods Implemented:

**1. Poisson GLMM with Random Effects**
- **Model specification**: `triplet_count ~ condition + (1 | participant)`
- **Fixed effect**: Experimental condition (e.g., GIVE_WITH vs HUG_WITH)
- **Random effect**: Random intercept per participant (accounts for individual differences)
- **Family**: Poisson distribution (appropriate for count data)
- **Offset**: Log of trial count per participant (accounts for varying exposure)

**2. Rate Ratios (Interpretable Effect Sizes)**
- **What they are**: Exponentiated Poisson coefficients
- **Interpretation**:
  - RR = 1.0: No difference between conditions
  - RR = 1.5: 50% higher triplet rate in condition B vs baseline
  - RR = 0.7: 30% lower triplet rate in condition B vs baseline
- **Example**: If GIVE_WITH is baseline and HUG_WITH has RR = 1.2, then HUG_WITH produces 20% more triplets

**3. Overdispersion Checking**
- **What it detects**: When variance exceeds the mean (common with count data)
- **Threshold**: Dispersion > 1.5 triggers warning
- **Action**: System recommends Negative Binomial GLMM if overdispersed
- **Why it matters**: Overdispersion violates Poisson assumptions, leading to underestimated standard errors

**4. Convergence Validation**
- **Checks**: Model must converge successfully before reporting results
- **Fallback**: If GLMM fails, descriptive statistics provided with explanatory note
- **Quality control**: Ensures only reliable statistical inference is reported

### Key Metrics Reported

#### 1. Descriptive Statistics

**Mean Triplets per Trial**
- **What it means**: Average number of triplets per trial for each condition
- **Interpretation**: Low values (0.05-0.07) indicate triplets are relatively uncommon but meaningful when they occur

**Directional Bias**
- **What it measures**: Which pattern (man→toy→woman vs. woman→toy→man) is more common
- **Interpretation**: Balanced counts suggest no systematic directional preference; infants scan bidirectionally

**Temporal Summary**
- **First occurrence**: How many triplets happened in each participant's first trial
- **Subsequent occurrences**: How many happened in later trials
- **Interpretation**: If triplets are more common in later trials, might suggest learning or familiarization

**Age Group Differences**
- **Compares**: Infants vs. adults (or different infant age groups)
- **From results**: Adults show higher rates (0.111) than children (0.049)
- **Interpretation**: Social gaze coordination develops with age/experience

#### 2. Inferential Statistics (GLMM Output)

**Rate Ratios with 95% Confidence Intervals**
- **Example**: RR = 1.35, 95% CI [0.98, 1.86]
- **Interpretation**: Condition B shows 35% higher triplet rate, but CI includes 1.0, so not statistically significant

**p-values**
- **Threshold**: p < 0.05 for statistical significance
- **Interpretation**: Probability of observing the data if no true condition effect exists
- **Note**: With low base rates, lack of significance doesn't mean no effect—may reflect limited statistical power

**AIC/BIC Model Fit Statistics**
- **What they measure**: Model quality balancing fit and complexity
- **Use**: Comparing alternative models (e.g., Poisson vs Negative Binomial)
- **Lower is better**: Smaller AIC/BIC indicates better model

### Understanding GLMM Results

**When the GLMM Converges:**

The report will show:
- **Rate ratios** comparing conditions
- **Confidence intervals** for rate ratios
- **p-values** testing null hypothesis of no condition effect
- **Model diagnostics** (AIC, BIC, dispersion)

**Example Interpretation:**

> *"The Poisson GLMM revealed that HUG_WITH trials produced 23% more social gaze triplets compared to GIVE_WITH trials (RR = 1.23, 95% CI [0.89, 1.71], p = 0.21). However, this difference was not statistically significant, and the wide confidence interval reflects substantial individual variability in triplet production."*

**When the GLMM Does Not Converge:**

If model fitting fails (e.g., insufficient data, numerical instability), the report provides:
- **Descriptive statistics only** (means, counts, SDs)
- **Explanation** of why inference was not possible
- **Recommendation** for interpretation (e.g., "interpret patterns cautiously")

### Why GLMMs for Triplet Counts?

**1. Count Data Structure**
- Triplets are discrete counts (0, 1, 2, ...), not continuous measurements
- Poisson distribution naturally models count data

**2. Participant-Level Dependencies**
- Each participant contributes multiple trials
- Random effects account for within-participant correlation
- Prevents pseudoreplication (inflated Type I error)

**3. Varying Exposure**
- Participants have different numbers of valid trials
- Offset term adjusts for this exposure variation
- Ensures fair comparison of triplet **rates**, not raw counts

**4. Zero-Inflation Handling**
- Most trials have 0 triplets (rare events)
- GLMM includes all trials (including zeros) in the model
- Properly estimates low base rates

---

## What This Tells Us (Theoretical Implications)

### The Significance of Social Gaze Triplets

When an infant produces a triplet, they're demonstrating:

1. **Social Awareness**: Recognizing that both people are important
2. **Object-Agent Integration**: Connecting the toy to both actors
3. **Sequential Planning**: Following a structured looking pattern
4. **Joint Attention**: Understanding the social triangle (person-object-person)

### Why Are Triplets Rare?

The low frequency (~6% of trials) doesn't mean the finding isn't important:

- **High cognitive demand**: Triplets require coordinating attention across three distinct locations
- **Brief time window**: Events last only seconds; producing 3+ sequential gazes is challenging
- **Alternative strategies**: Infants may understand the event without producing this specific pattern
- **Individual differences**: Some infants may be "tripleters," others may not use this strategy

### Comparison to AR1 and AR2

- **AR1** (Duration): Shows infants look at relevant objects more
- **AR2** (Transitions): Shows infants look back and forth between toy and people
- **AR3** (Triplets): Shows some infants make complete social triangulation sequences

AR3 represents the **most sophisticated level** of gaze coordination measured in this pipeline.

---

## How This Analysis Works Technically

From `ar3_social_triplets.py`:

### Step-by-Step Process:

1. **Load gaze fixations**: Read processed data with fixation sequences
2. **Apply filters**: Include only specified conditions and segments
3. **Sliding window detection**: For each trial, examine every 3-consecutive-gaze window
4. **Pattern matching**: Check if the window matches a valid triplet pattern
5. **Gap checking**: Verify frame gaps are within allowed limits
6. **No repetition**: Ensure no repeated AOIs (e.g., man→man→woman is invalid)
7. **Record triplets**: Save detected triplets with participant, trial, and frame info
8. **Aggregate**: Count triplets per trial, per participant, per condition

### Example Detection:

Given this gaze sequence in a trial:
```
Frame 44: woman_face
Frame 50: toy_present
Frame 70: man_face
Frame 91: screen_nonAOI
```

With `require_consecutive: true` and `max_gap_frames: 2`:
- Check frames 44→50: Gap = 50-44-1 = 5 frames (TOO BIG, would reject if strict)
- With `max_gap_frames: 2`, this would be rejected
- Triplet is NOT detected

---

## Important Methodological Details

### Configuration Parameters

From `ar3_gw_vs_hw.yaml`:

```yaml
triplets:
  valid_patterns:
    - ["man_face", "toy_present", "woman_face"]
    - ["woman_face", "toy_present", "man_face"]
  require_consecutive: true
  max_gap_frames: 2
```

**What this means:**
- Gazes must be in the specified order
- Up to 2 empty frames can occur between gazes
- The three gazes can't be separated by more than 2 frames each

### Toy Absent Mapping

For conditions without the toy (e.g., GIVE_WITHOUT):
```yaml
toy_absent_mapping:
  "toy_present": "toy_location"
```

This tells AR3: "When looking for `toy_present` in GIVE_WITHOUT trials, look for `toy_location` instead"

### Segment Filtering

```yaml
segments:
  include:
    - "interaction"
```

Only analyzes the core interaction phase (not approach or departure), focusing on when the event is actually happening.

---

## Visualizations in AR3

The analysis generates several visualizations:

### 1. Triplets by Condition
- Bar chart showing mean triplets per trial for each condition
- Error bars show variability
- Helps compare which conditions elicit more social coordination

### 2. Triplets by Age Group
- Compares infant vs. adult triplet production
- Shows developmental differences
- Adults typically show more triplets (more sophisticated social cognition)

### 3. Data Tables
- **Directional bias**: Counts for each pattern direction
- **Temporal summary**: First vs. subsequent occurrences
- **Frequency tables**: Detailed breakdowns by condition and age

---

## Interpreting Your Results

### When Triplets Are Found:

**Presence of triplets** (even if rare) indicates:
- ✅ At least some participants demonstrate social triangulation
- ✅ The looking strategy exists in the population
- ✅ Evidence for sophisticated social cognition

### When Triplets Are Rare:

**Low frequencies don't invalidate the finding:**
- Triplets are **cognitively demanding** - requiring 3 sequential gazes in seconds
- Even occasional triplets show the **capacity exists**
- Individual differences are expected and interesting
- May be more common in certain conditions or age groups

### Comparing Conditions:

In your results:
- **GIVE_WITH**: 0.056 triplets/trial
- **HUG_WITH**: 0.069 triplets/trial

The slightly higher rate in HUG_WITH is interesting but:
- Difference is small (0.013 triplets/trial)
- No inferential statistics yet to test significance
- Could be due to chance variation with small counts

---

## Limitations and Future Directions

### Current Limitations:

1. **Low base rates**: Triplets are rare events (~6% of trials), which can limit statistical power
2. **Individual variability**: Some participants produce many triplets, others produce none (floor effects)
3. **Single metric focus**: Current analysis focuses on frequency, not quality or timing of triplets
4. **Overdispersion potential**: Count data may violate Poisson assumptions (system detects and warns)

### Future Directions:

1. **Negative Binomial models**: When overdispersion detected, fit alternative GLMM families
2. **Developmental trajectories**: More granular age analyses with interaction terms
3. **Individual differences profiling**: Cluster participants by triplet production patterns
4. **Sequence expansion**: Explore other meaningful gaze patterns beyond the defined triplets
5. **Temporal dynamics**: Analyze timing and duration of triplet sequences, not just frequency
6. **Predictive modeling**: Use triplet production to predict other developmental outcomes

---

## The Bottom Line

**AR3 reveals whether infants use social gaze triangulation** - looking between both actors and the object in organized sequences. This is the most sophisticated form of gaze coordination measured in the pipeline, representing true **social-cognitive integration** of people and objects.

While triplets are relatively rare (~6% of trials), their presence demonstrates that some infants actively coordinate their attention across the entire social scene, not just focusing on individual elements.

---

## Connection to Broader Research Goals

AR3 connects to the verb-argument structure hypothesis:
- Triplets suggest infants recognize **all three arguments** (giver, receiver, object) as components of the event
- Social coordination implies understanding of **relational structure** (who is doing what to whom with what)
- Goes beyond AR1/AR2 by showing **integrated, sequential processing** of the entire event structure

This is critical evidence for **pre-linguistic event understanding**!
