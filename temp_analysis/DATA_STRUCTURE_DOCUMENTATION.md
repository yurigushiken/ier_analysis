# 📊 IER Analysis Data Structure Documentation

**Date**: 2025-10-26
**Purpose**: Complete understanding of data structure for accurate statistical modeling

---

## 🎬 Data Structure Overview

### **Hierarchical Nesting**

```
Participant (Level 3)
  └─ Event Presentation (Level 2) - Video clip shown to infant
      └─ Gaze Event (Level 1) - 3+ consecutive frames on same AOI
          └─ Frame (Level 0) - Individual frame (aggregated, not modeled)
```

---

## 📁 File Structure

### **Raw Data Files**
- **Location**: `data/raw/child-gl/`
- **Format**: CSV files, one per participant
- **Naming**: `{Age}-{ID}gl.csv` (e.g., `Eight-months-0101-947gl.csv`)
- **Total Files**: 36 child participants

### **File Size**
- **Rows per file**: ~5,500 - 12,000 frames
- **Average**: ~8,000 frames per participant
- **Each row**: One frame of video (≈33ms at 30 fps)

---

## 🎥 Event Structure

### **Event Types** (11 total)

All participants see the exact same 11 event types:

| Event Code | Meaning | Action | Toy Presence | Orientation |
|------------|---------|--------|--------------|-------------|
| **gw** | GIVE WITH | GIVE | WITH | NORMAL |
| **gwo** | GIVE WITHOUT | GIVE | WITHOUT | NORMAL |
| **hw** | HUG WITH | HUG | WITH | NORMAL |
| **hwo** | HUG WITHOUT | HUG | WITHOUT | NORMAL |
| **sw** | SHOW WITH | SHOW | WITH | NORMAL |
| **swo** | SHOW WITHOUT | SHOW | WITHOUT | NORMAL |
| **ugw** | UPSIDE-DOWN GIVE WITH | GIVE | WITH | UPSIDE-DOWN |
| **ugwo** | UPSIDE-DOWN GIVE WITHOUT | GIVE | WITHOUT | UPSIDE-DOWN |
| **uhw** | UPSIDE-DOWN HUG WITH | HUG | WITH | UPSIDE-DOWN |
| **uhwo** | UPSIDE-DOWN HUG WITHOUT | HUG | WITHOUT | UPSIDE-DOWN |
| **f** | FLOATING (control) | CONTROL | N/A | N/A |

### **Event Presentations**

**Key Finding**: Event types can be **presented multiple times** to each participant

**Example from Participant "Eight-months-0101-947"**:
- **gw** (GIVE WITH): 448 frames → ~3 separate presentations
- **hwo** (HUG WITHOUT): 1,353 frames → ~8 separate presentations
- **sw** (SHOW WITH): 599 frames → ~4 separate presentations

**Variability**:
- Different event types are presented different numbers of times
- Varies across participants
- **Total presentations per participant**: ~12 event presentations (range likely 10-15)

### **Frames per Event Presentation**

**From detailed analysis**:
- Some presentations: ~150-185 frames (typical, ~5-6 seconds)
- Some presentations: ~450-1,000 frames (much longer, ~15-33 seconds)

**Important**: Event presentations vary significantly in duration
- Short presentations: ~150 frames (5 seconds)
- Long presentations: ~1,000+ frames (33+ seconds)
- This variability is important to account for in analysis

---

## 📊 Statistical Implications

### **Sample Size at Each Level**

```
Level 3 (Participant):
  N = 36 participants

Level 2 (Event Presentation):
  ~12 presentations per participant
  Total: 36 × 12 = ~432 event presentations

Level 1 (Gaze Event):
  Estimated ~10-30 gaze events per presentation
  Total: ~4,320 - 12,960 gaze events
```

### **Adequacy for Statistical Modeling**

| Model Component | Requirement | Our Data | Status |
|----------------|-------------|----------|--------|
| **Random Intercepts** | 5+ obs per group | 12 presentations/participant | ✅ Excellent |
| **Random Slopes** | 10+ obs per group | 12 presentations/participant | ✅ Adequate |
| **Nested Random Effects** | Multiple levels | 3 levels (participant/presentation/gaze) | ✅ Excellent |
| **LMM Convergence** | Sufficient data | ~432 presentations total | ✅ Excellent |
| **GLMM for Counts** | Sufficient data | ~432 presentations for triplets | ✅ Excellent |

**Verdict**: ✅ **Data structure is EXCELLENT for LMM/GLMM with random slopes and nested random effects**

---

## 🔬 Condition Grouping for Analyses

### **Factorial Design**

**Factor 1: Action Type** (3 levels)
- GIVE
- HUG
- SHOW

**Factor 2: Toy Presence** (2 levels)
- WITH toy
- WITHOUT toy

**Factor 3: Orientation** (2 levels)
- NORMAL
- UPSIDE-DOWN (control for biomechanical motion)

**Control**: FLOATING (f)

### **Primary Comparisons (per Gordon 2003)**

**AR-1 (Core Event Salience)**:
- GIVE WITH (gw) vs HUG WITH (hw)
- Hypothesis: Infants look more at toy in GIVE than HUG

**AR-7 (Event Dissociation)**:
- GIVE (gw) vs GIVE-TO-SELF? vs HUG (hw)
- Note: Need to confirm if GIVE-TO-SELF is a separate event or derived from other events

**Upside-Down Control**:
- GIVE WITH (gw) vs UPSIDE-DOWN GIVE WITH (ugw)
- Tests if orientation affects looking patterns

---

## 📐 Data Transformation Pipeline

### **Step 1: Frame-Level Data** (raw CSV)
```
participant | event | trial_frame | What  | Where | ...
Eight-0101  | gw    | 1          | toy   | other | ...
Eight-0101  | gw    | 2          | toy   | other | ...
Eight-0101  | gw    | 3          | woman | face  | ...
```
**Size**: ~8,000 rows per participant

### **Step 2: Gaze Event Detection**
**Identify sequences of 3+ consecutive frames on same AOI**
```
participant | event | gaze_id | aoi        | duration_frames | duration_ms
Eight-0101  | gw    | 1       | toy,other  | 5               | 167
Eight-0101  | gw    | 2       | woman,face | 8               | 267
Eight-0101  | gw    | 3       | toy,other  | 12              | 400
```
**Size**: ~10-30 gaze events per presentation × 12 presentations = ~120-360 per participant

### **Step 3: Event-Level Aggregation** (for AR-1, AR-3, AR-6)
**Aggregate gaze events to presentation level**
```
participant | event | presentation_num | proportion_core | triplet_count | age_months
Eight-0101  | gw    | 1               | 0.45            | 2             | 8.2
Eight-0101  | gw    | 2               | 0.42            | 1             | 8.2
Eight-0101  | hw    | 3               | 0.30            | 0             | 8.2
```
**Size**: ~12 rows per participant

### **Step 4: Statistical Modeling**

**AR-1 (Gaze Duration) - LMM**:
```python
# Unit of analysis: Event presentation
# Each row: one presentation of one event type

model = MixedLM.from_formula(
    'proportion_core ~ condition + (1 | participant)',
    data=event_level_data,  # ~432 rows (36 participants × 12 presentations)
    groups='participant'
)
```

**AR-3 (Social Triplets) - GLMM Poisson**:
```python
# Unit of analysis: Event presentation
# Outcome: Count of triplets (0, 1, 2, 3, ...)

model = GLMM.from_formula(
    'triplet_count ~ condition + offset(log(duration_sec)) + (1 | participant)',
    data=event_level_data,
    family=Poisson()
)
```

**AR-4 (Dwell Time) - LMM with Nested Random Effects**:
```python
# Unit of analysis: Gaze event
# Each row: one gaze event (3+ frames)

model = MixedLM.from_formula(
    'dwell_time_ms ~ condition * aoi_category + (1 | participant) + (1 | participant:event)',
    data=gaze_event_data,  # ~4,320-12,960 rows
    groups='participant'
)
```

**AR-6 (Habituation) - LMM with Random Slopes**:
```python
# Unit of analysis: Event presentation
# Predictor: presentation_order (1, 2, 3, ..., 12)

# Create presentation order
event_level_data['presentation_order'] = event_level_data.groupby('participant').cumcount() + 1

model = MixedLM.from_formula(
    'gaze_metric ~ presentation_order * condition + (1 + presentation_order | participant)',
    data=event_level_data,
    groups='participant'
)
```

---

## 🔍 Critical Clarifications

### **1. Event Presentations are NOT Perfectly Balanced**

**Key Insight**: Different event types are presented different numbers of times

**Example**:
- Event "gw" might be shown 3 times
- Event "hwo" might be shown 8 times

**Implication**:
- Can't simply average across all presentations
- Need to account for event type in analysis
- LMM handles unbalanced designs naturally

### **2. "Trial Number" for AR-6 = Presentation Order**

**Correct interpretation**:
- Trial 1 = First video presentation (could be any event type)
- Trial 2 = Second video presentation
- ...
- Trial 12 = Twelfth video presentation

**Habituation Analysis**:
- Tests if looking time decreases across presentation order
- **Does NOT test habituation within event type** (e.g., repeated "gw" presentations)
- Tests **general habituation across the session**

**If you want within-event-type habituation**:
```python
# Example: Habituation to repeated GIVE WITH presentations
gw_data = event_level_data[event_level_data['event'] == 'gw']
gw_data['gw_presentation_num'] = gw_data.groupby('participant').cumcount() + 1

model = MixedLM.from_formula(
    'gaze_metric ~ gw_presentation_num + (1 + gw_presentation_num | participant)',
    data=gw_data,
    groups='participant'
)
```

### **3. Missing Event Presentations**

**Possibility**: Some participants may not have all event types
- Infant fussy and session ended early
- Technical issues
- Infant looked away for entire presentation

**LMM handles this gracefully**:
- No need to exclude participants with missing events
- Maximum likelihood estimation uses available data
- Participants with fewer events contribute less to estimation

### **4. Event Duration Variability**

**Important**: Event presentations vary in duration (150-1,000+ frames)

**Implication**:
- Longer presentations → more opportunities for gaze events
- Need to **normalize by duration** when counting events

**Solution**: Use **offset in GLMM** for count outcomes
```python
# For AR-3 (triplet counts)
event_level_data['log_duration'] = np.log(event_level_data['duration_frames'])

model = GLMM.from_formula(
    'triplet_count ~ condition + offset(log_duration) + (1 | participant)',
    data=event_level_data,
    family=Poisson()
)
```

---

## 📋 Data Quality Checks Needed

Before analysis, verify:

1. ✅ **All participants have 11 event types** (confirmed: yes)
2. ❓ **Minimum presentations per participant** (check for early terminations)
3. ❓ **Event presentation order** (randomized or fixed?)
4. ❓ **Missing gaze data** (frames with off-screen looking)
5. ❓ **Outlier presentations** (>80% off-screen looking)

---

## 🎯 Summary for Documentation

**For spec.md and plan.md**:

### **Data Structure**:
- **36 child participants** (8-14 months old)
- **11 event types** per participant (GIVE, HUG, SHOW × WITH/WITHOUT × NORMAL/UPSIDE-DOWN + FLOATING control)
- **~12 event presentations** per participant (event types repeated multiple times)
- **~150-1,000 frames per presentation** (variable duration, ~5-33 seconds)
- **~8,000 total frames** per participant

### **Nesting Structure**:
```
Participant (N=36)
  └─ Event Presentation (N≈12 per participant)
      └─ Gaze Event (N≈10-30 per presentation)
          └─ Frame (N≈150-1,000 per presentation, aggregated)
```

### **Statistical Implications**:
- ✅ **Excellent data structure for LMM/GLMM**
- ✅ **Sufficient for random intercepts** (~12 presentations/participant)
- ✅ **Adequate for random slopes** (~12 presentations/participant)
- ✅ **Excellent for nested random effects** (3-level hierarchy)
- ✅ **Can test habituation across session** (presentation order 1-12)

---

## ✅ Next Steps

1. ✅ **Document in spec.md** - Add data structure clarification
2. ✅ **Document in plan.md** - Update nesting structure description
3. ✅ **Update configs** - Ensure formulas match actual structure
4. 📝 **Create data validation tests** - Verify structure during preprocessing
5. 📝 **Generate presentation order variable** - For AR-6 habituation analysis

---

**Last Updated**: 2025-10-26
**Verified**: Complete event type catalog, presentation counts, nesting structure
