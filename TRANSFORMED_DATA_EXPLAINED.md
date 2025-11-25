# Understanding the "Transformed Data" in Detail

**Created**: 2025-11-23
**Purpose**: Explain exactly what the processed/transformed gaze fixations data is

---

## The Transformation Explained

### FROM: Raw Frame-by-Frame Data

**File Location**: `data/csvs_human_verified_vv/child/*.csv`

**Example**: `Eight-0101-1579gl.csv`

**Structure**: One row per video frame (~30 frames per second)

```csv
Participant,Frame Number,Time,What,Where,Onset,Offset,event_verified,segment,...
Eight-0101-1579,277,00:00:09:2333,screen,other,9.2333,9.2667,gwo,approach,...
Eight-0101-1579,278,00:00:09:2667,screen,other,9.2667,9.3,gwo,approach,...
Eight-0101-1579,279,00:00:09:3000,screen,other,9.3,9.3333,gwo,approach,...
...
Eight-0101-1579,293,00:00:09:7333,man,body,9.7333,9.7667,gwo,approach,...
Eight-0101-1579,294,00:00:09:7667,man,body,9.7667,9.8,gwo,approach,...
Eight-0101-1579,295,00:00:09:8000,man,body,9.8,9.8333,gwo,approach,...
...
```

**Key Characteristics**:
- ✅ **Frame-by-frame**: Every 33ms (1/30th second) gets a row
- ✅ **What+Where pairs**: Where the infant is looking at each frame
  - "screen, other" = looking at screen but not specific AOI
  - "man, body" = looking at man's body
  - "woman, face" = looking at woman's face
  - "toy, other" = looking at toy
- ✅ **Human-verified**: Researchers manually coded each frame
- ✅ **Repetitive**: Same AOI appears in many consecutive rows

**Example Sequence**:
```
Frame 277-279: "screen, other" (3 frames = 100ms)
Frame 293-298: "man, body" (6 frames = 200ms)
Frame 299-305: "man, face" (7 frames = 233ms)
```

---

### TO: Aggregated Gaze Fixations

**File Location**: `data/processed/gaze_fixations_child.csv`

**Structure**: One row per gaze fixation (3+ consecutive frames on same AOI)

```csv
participant_id,age_months,trial_number,condition,segment,aoi_category,gaze_duration_ms,gaze_start_frame,gaze_end_frame,...
Eight-0101-1579,8,1,gwo,approach,screen_nonAOI,500.0,2,16,...
Eight-0101-1579,8,1,gwo,approach,man_body,199.99,17,22,...
Eight-0101-1579,8,1,gwo,approach,man_face,200.0,23,28,...
Eight-0101-1579,8,1,gwo,approach,man_body,99.99,29,31,...
```

**Key Characteristics**:
- ✅ **Gaze fixations**: Consecutive frames collapsed into single rows
- ✅ **Duration calculated**: Each fixation has a total duration in milliseconds
- ✅ **AOI categories**: What+Where pairs → standardized categories
  - "man, body" → `man_body`
  - "woman, face" → `woman_face`
  - "toy, other" → `toy_present`
  - "screen, other" → `screen_nonAOI`
- ✅ **Temporal info preserved**: Start frame, end frame, onset time, offset time
- ✅ **Metadata added**: Condition names, age groups, participant type

---

## The Transformation Process (Step-by-Step)

### Step 1: Load Raw Frame-by-Frame Data

```
Input: Eight-0101-1579gl.csv (thousands of rows)

Frame 277: screen, other (onset: 9.2333)
Frame 278: screen, other (onset: 9.2667)
Frame 279: screen, other (onset: 9.3000)
Frame 280: screen, other (onset: 9.3333)
...
Frame 293: man, body (onset: 9.7333)
Frame 294: man, body (onset: 9.7667)
Frame 295: man, body (onset: 9.8000)
...
```

### Step 2: Map What+Where to AOI Categories

```
Mapping Rules:
  "screen, other" → screen_nonAOI
  "man, body" → man_body
  "man, face" → man_face
  "man, hands" → man_hands
  "woman, body" → woman_body
  "woman, face" → woman_face
  "woman, hands" → woman_hands
  "toy, other" → toy_present
  "toy2, other" → toy_location (where toy WOULD be if present)
  "no, signal" → off_screen
```

**After mapping**:
```
Frame 277: screen_nonAOI
Frame 278: screen_nonAOI
Frame 279: screen_nonAOI
...
Frame 293: man_body
Frame 294: man_body
Frame 295: man_body
...
```

### Step 3: Detect Gaze Fixations (3+ Consecutive Frames)

**Rule**: A fixation = 3 or more consecutive frames on the SAME AOI

```
Frames 2-16: screen_nonAOI (15 frames) ✓ VALID (≥3 frames)
  → Create fixation record

Frames 17-22: man_body (6 frames) ✓ VALID (≥3 frames)
  → Create fixation record

Frames 23-28: man_face (6 frames) ✓ VALID (≥3 frames)
  → Create fixation record

Frames 29-31: man_body (3 frames) ✓ VALID (exactly 3 frames)
  → Create fixation record

[If there were only 2 frames, would be INVALID - too brief]
```

### Step 4: Calculate Duration and Temporal Info

**For each fixation**:

```
Fixation 1 (screen_nonAOI, frames 2-16):
  - gaze_start_frame: 2
  - gaze_end_frame: 16
  - gaze_duration_frames: 16 - 2 + 1 = 15 frames
  - gaze_duration_ms: 15 frames × 33.33ms/frame = 500.0ms
  - gaze_onset_time: 9.2333 (onset of frame 2)
  - gaze_offset_time: 9.7333 (offset of frame 16)

Fixation 2 (man_body, frames 17-22):
  - gaze_duration_frames: 6 frames
  - gaze_duration_ms: 6 × 33.33 = 199.99ms
  - gaze_onset_time: 9.7333
  - gaze_offset_time: 9.9333
```

### Step 5: Add Metadata

**Enrich each fixation with**:
- Participant ID
- Age (months and years)
- Condition code (gwo) → Condition name (GIVE_WITHOUT)
- Segment (approach, interaction, departure)
- Trial number

**Final output row**:
```csv
Eight-0101-1579,infant,8,8-month-olds,1,gwo,GIVE_WITHOUT,approach,screen_nonAOI,2,16,15,500.0,9.2333,9.7333
```

---

## Visual Comparison: Raw vs. Transformed

### Raw Data (Frame-by-Frame)

```
TRIAL 1, CONDITION: GIVE_WITHOUT, SEGMENT: approach

Time     Frame  What    Where   → AOI
9.2333   277    screen  other   → screen_nonAOI
9.2667   278    screen  other   → screen_nonAOI
9.3000   279    screen  other   → screen_nonAOI
9.3333   280    screen  other   → screen_nonAOI
9.3667   281    screen  other   → screen_nonAOI
...
9.7333   293    man     body    → man_body
9.7667   294    man     body    → man_body
9.8000   295    man     body    → man_body
9.8333   296    man     body    → man_body
9.8667   297    man     body    → man_body
9.9000   298    man     body    → man_body
9.9333   299    man     face    → man_face
9.9667   300    man     face    → man_face
10.0000  301    man     face    → man_face
...

↓↓↓ TRANSFORMATION ↓↓↓
(Collapse consecutive frames into fixations)
```

### Transformed Data (Gaze Fixations)

```
TRIAL 1, CONDITION: GIVE_WITHOUT, SEGMENT: approach

Fixation  AOI            Start  End   Frames  Duration  Onset    Offset
1         screen_nonAOI  2      16    15      500.0ms   9.2333   9.7333
2         man_body       17     22    6       199.9ms   9.7333   9.9333
3         man_face       23     28    6       200.0ms   9.9333   10.1333
4         man_body       29     31    3       99.9ms    10.1333  10.2333
5         man_body       33     35    3       99.9ms    10.2667  10.3667
6         man_face       36     50    15      500.0ms   10.3667  10.8667
```

**Notice**:
- ✅ 6 fixation rows instead of hundreds of frame rows
- ✅ Each fixation is a meaningful "gaze event"
- ✅ Duration is pre-calculated
- ✅ Much easier to analyze transitions, patterns, etc.

---

## Why This Transformation?

### Benefits of Transformed Data

1. **Reduced Data Volume**
   - Raw: ~300-500 frames per trial × hundreds of trials = millions of rows
   - Transformed: ~20-50 fixations per trial = manageable dataset

2. **Meaningful Units**
   - Raw: Individual frames are too granular (33ms snapshots)
   - Transformed: Fixations represent actual "looking events" (100ms+)

3. **Analysis-Ready**
   - Raw: Would need to aggregate frames for every analysis
   - Transformed: Already aggregated, ready for AR1-AR7

4. **Standardized AOI Categories**
   - Raw: "what, where" pairs (10 combinations)
   - Transformed: Consistent `aoi_category` labels

5. **Pre-Filtered for Quality**
   - Raw: Includes 1-frame or 2-frame "looks" (likely noise)
   - Transformed: Only ≥3 frames (conservative threshold for valid fixations)

---

## What ALL AR Analyses Do with This Data

### AR1: Gaze Duration

**Uses**: Transformed fixations

**Calculation**:
```
For each trial:
  1. Sum all fixation durations where aoi_category = "toy_present"
  2. Sum all fixation durations (total trial time)
  3. Calculate proportion: toy_duration / total_duration

For each participant:
  4. Average proportions across trials

For each condition:
  5. Average participant means
  6. Compare GIVE_WITH vs. HUG_WITH (t-test)
```

**Example**:
```
Trial 1 (GIVE_WITH):
  - Fixation 1: toy_present, 450ms
  - Fixation 2: woman_face, 500ms
  - Fixation 3: toy_present, 350ms
  - Fixation 4: man_face, 400ms
  - Total toy: 450 + 350 = 800ms
  - Total time: 450 + 500 + 350 + 400 = 1700ms
  - Proportion: 800/1700 = 0.47 (47%)
```

---

### AR2: Gaze Transitions

**Uses**: Transformed fixations

**Calculation**:
```
For each trial:
  1. Extract AOI sequence from fixations (ordered by time)
     Example: [woman_face, toy_present, man_face, toy_present]

  2. Collapse consecutive repeated AOIs (if configured)
     Example: [woman_face, woman_face, toy_present] → [woman_face, toy_present]

  3. Identify transitions (AOI[i] → AOI[i+1])
     Example: woman_face→toy_present, toy_present→man_face, man_face→toy_present

For each participant:
  4. Count all transitions
  5. Calculate probabilities: P(AOI_j | AOI_i) = count(i→j) / count(i→*)

For each condition:
  6. Average transition matrices across participants
  7. Test key transitions (e.g., toy→face) between conditions
```

**Example**:
```
Fixation sequence:
  1. woman_face (500ms)
  2. toy_present (450ms)
  3. man_face (400ms)
  4. toy_present (350ms)

Transitions:
  woman_face → toy_present (1 occurrence)
  toy_present → man_face (1 occurrence)
  man_face → toy_present (1 occurrence)

If woman_face appeared 5 times total, and transitioned to toy 3 times:
  P(toy | woman_face) = 3/5 = 0.60 (60%)
```

---

### AR3: Social Gaze Triplets

**Uses**: Transformed fixations

**Calculation**:
```
For each trial:
  1. Extract AOI sequence: [woman_face, toy_present, man_face, ...]

  2. Use sliding window (size=3) to check for triplet patterns:
     Window 1: [woman_face, toy_present, man_face] → MATCH! (triplet detected)
     Window 2: [toy_present, man_face, woman_body] → No match
     Window 3: [man_face, woman_body, toy_present] → No match

  3. Valid patterns:
     - man_face → toy_present → woman_face
     - woman_face → toy_present → man_face

For each participant:
  4. Count total triplets detected

For each condition:
  5. Calculate mean triplets per trial
  6. Compare GIVE_WITH vs. HUG_WITH (GLMM)
```

**Example**:
```
Fixation sequence:
  1. woman_face (onset: 10.5s)
  2. toy_present (onset: 11.0s)
  3. man_face (onset: 11.5s)
  4. screen_nonAOI (onset: 12.0s)

Check window [1, 2, 3]:
  woman_face → toy_present → man_face

This matches pattern: woman_face → toy → man_face
  → Triplet detected! (count = 1 for this trial)
```

---

### AR4: Dwell Time

**Uses**: Transformed fixations

**Calculation**:
```
For each fixation:
  1. Filter: Keep only if duration is 100-5000ms (outlier removal)
  2. Filter: Remove extreme values (>3 SD from participant mean)

For each participant × condition:
  3. Calculate mean dwell time (average of all fixation durations)

For each condition:
  4. Fit LMM: dwell_time ~ condition + (1|participant)
  5. Compare GIVE_WITH vs. HUG_WITH
```

**Example**:
```
Participant Eight-0101-1579, GIVE_WITH:
  - Fixation 1 (toy_present): 450ms ✓
  - Fixation 2 (woman_face): 500ms ✓
  - Fixation 3 (toy_present): 8000ms ✗ (outlier, >5000ms)
  - Fixation 4 (man_face): 400ms ✓
  - Fixation 5 (toy_present): 350ms ✓

Valid fixations: [450, 500, 400, 350]
Mean dwell: (450 + 500 + 400 + 350) / 4 = 425ms
```

---

### AR5: Developmental Trajectories

**Uses**: Transformed fixations + Age variable

**Calculation**:
```
For each participant:
  1. Calculate AR1 metric (toy proportion) OR AR2 metric (transitions)
  2. Include age_months as predictor

Fit LMM:
  toy_proportion ~ condition * age_months + (1|participant)

  This tests:
    - Main effect of condition
    - Main effect of age
    - Interaction: Does condition effect CHANGE with age?

Expected pattern (Gordon's prediction):
  6mo: GIVE ≈ HUG (no difference)
  8mo: GIVE > HUG (small difference)
  10mo: GIVE >> HUG (large difference)
  → Significant Age × Condition interaction
```

---

### AR6: Trial-Order Effects

**Uses**: Transformed fixations + Trial order variable

**Calculation**:
```
For each participant:
  1. Calculate AR1 metric (toy proportion) for EACH trial separately
  2. Include trial_number as predictor

Fit LMM with random slopes:
  toy_proportion ~ trial_number + (trial_number|participant)

  This tests:
    - Do fixations decrease/increase over trials? (learning/habituation)
    - Does each participant have their own learning rate?

Expected pattern:
  Trial 1: High attention (novelty)
  Trial 2: Moderate attention
  Trial 3-5: Lower attention (habituation)
  → Negative slope (attention decreases over trials)
```

---

### AR7: Event Dissociation

**Uses**: Transformed fixations from multiple conditions

**Calculation**:
```
For each participant:
  1. Calculate AR1 metric for GIVE, HUG, and SHOW conditions

Compare all pairs:
  GIVE vs. HUG (t-test or LMM)
  GIVE vs. SHOW (t-test or LMM)
  HUG vs. SHOW (t-test or LMM)

Apply Bonferroni correction (α = 0.05/3 = 0.017)

Expected pattern:
  GIVE ≠ HUG (argument structure difference)
  GIVE ≠ SHOW (different types of transfer)
  HUG ≠ SHOW (contact vs. information)
```

---

## Key Insight: Same Data, Different Calculations

**All AR analyses (AR1-AR7) use the EXACT SAME processed data**:
- File: `data/processed/gaze_fixations_child.csv`

**What differs**: The METRIC calculated from the fixations

| Analysis | Metric Calculated | Unit of Analysis |
|----------|-------------------|------------------|
| AR1 | Total duration per AOI | Trial-level proportions |
| AR2 | Transition probabilities | Fixation sequences |
| AR3 | Triplet counts | 3-fixation windows |
| AR4 | Mean dwell time | Individual fixation durations |
| AR5 | Condition effect × Age | Participant-level means + age |
| AR6 | Condition effect × Trial | Trial-level means + trial order |
| AR7 | Multi-condition comparison | Participant-level means (3+ conditions) |

**They all start with the same fixation records** - just aggregate/analyze differently!

---

## One-Sentence Summary

**The transformed data (`gaze_fixations_child.csv`) is a pre-processed dataset where thousands of raw frame-by-frame gaze coordinates have been collapsed into meaningful "gaze fixation" records (3+ consecutive frames on the same area of interest), with each fixation having a calculated duration, standardized AOI category labels, and temporal metadata—this single dataset serves as the input for ALL analyses (AR1-AR7), which differ only in what metrics they calculate from these same fixations (e.g., total duration, transition probabilities, triplet patterns, dwell times, age interactions, trial-order effects, or multi-condition dissociations).**

---

*Created: 2025-11-23*
*Purpose: Comprehensive explanation of transformed gaze fixations data*
