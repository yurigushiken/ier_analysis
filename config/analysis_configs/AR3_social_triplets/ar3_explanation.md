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

### Descriptive Statistics Only

Currently, AR3 provides **descriptive statistics** (means, counts, frequencies) but not inferential statistics like t-tests or ANOVA. This is because:

1. **Low frequencies**: Triplets are relatively rare events (mean ~0.06 per trial)
2. **Zero-inflated data**: Most trials have 0 triplets, some have 1-2
3. **GLMM pending**: Generalized Linear Mixed Models are needed for proper analysis but require additional dependencies

### Key Metrics Reported

#### 1. Mean Triplets per Trial
- **What it means**: Average number of triplets per trial for each condition
- **Interpretation**: Low values (0.05-0.07) indicate triplets are relatively uncommon

#### 2. Directional Bias
- **What it measures**: Which pattern (man→toy→woman vs. woman→toy→man) is more common
- **Interpretation**: Balanced counts suggest no systematic directional preference

#### 3. Temporal Summary
- **First occurrence**: How many triplets happened in each participant's first trial
- **Subsequent occurrences**: How many happened in later trials
- **Interpretation**: If triplets are more common in later trials, might suggest learning or familiarization

#### 4. Age Group Differences
- **Compares**: Infants vs. adults (or different infant age groups)
- **From results**: Adults show higher rates (0.111) than children (0.049)
- **Interpretation**: Social gaze coordination may develop with age/experience

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

1. **No inferential statistics**: Can't yet test if condition differences are statistically significant
2. **Low base rates**: Rare events make statistical modeling challenging
3. **Descriptive only**: Results show patterns but can't confirm effects

### Planned Improvements:

1. **GLMM implementation**: Generalized Linear Mixed Models for zero-inflated count data
2. **Developmental trajectory**: More detailed age analyses
3. **Individual differences**: Clustering participants by triplet production
4. **Sequential patterns**: Are there other meaningful sequences beyond the defined triplets?

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
