# New Data Structure - Verified Analysis

**Date**: 2025-10-26
**Data Location**: `data/csvs_human_verified_vv/`
**Status**: Analysis complete, event_presentation_id method verified

---

## Key Changes from Previous Data

### Sample Size Update
- **Previous**: 36 child participants (from `data/raw/child-gl/`)
- **New**: 51 child participants (from `data/csvs_human_verified_vv/child/`)
- **Adult**: 15 adult participants (from `data/csvs_human_verified_vv/adult/`)

### Age Distribution (Verified)
- **Range**: 7-12 months (same as before)
- **Mean**: 9.2 months (was 9.4 months)
- **Median**: 9.0 months (was 10.0 months)

**Age breakdown** (N=51):
```
 7 months:  8 participants (15.7%)
 8 months: 10 participants (19.6%)
 9 months: 11 participants (21.6%) ← largest group
10 months: 11 participants (21.6%) ← largest group
11 months:  9 participants (17.6%)
12 months:  2 participants (3.9%)
```

---

## Column Structure Changes

### New Columns (18 total):

| Column | Description | Example Values |
|--------|-------------|----------------|
| `Participant` | Unique ID | "Eight-0101-1579" |
| `Frame Number` | Session frame number | 1, 2, 3... |
| `Time` | Timestamp (HH:MM:SS:MS) | "00:00:05:8667" |
| `What` | Gaze target object | "toy", "man", "woman", "screen", "no" |
| `Where` | Gaze location detail | "face", "body", "hands", "other", "signal" |
| `Onset` | Event onset time (sec) | 5.8667 |
| `Offset` | Event offset time (sec) | 5.9 |
| `Blue Dot Center` | Gaze coordinates | "(x, y)" |
| `event_verified` | **NEW** Verified event type | "gw", "hw", "swo", etc. |
| `frame_count_event` | **NEW** Frame number within event | 1, 2, 3... |
| `trial_number` | Trial number within event | 1, 2, 3... |
| `trial_number_global` | **NEW** Nth occurrence of event for participant | 1, 2, 3... |
| `frame_count_trial_number` | **NEW** Frame within trial | 1, 2, 3... |
| `segment` | Event phase | "approach", "interaction", "departure" |
| `frame_count_segment` | **NEW** Frame within segment | 1, 2, 3... |
| `participant_type` | Participant category | "infant", "adult" |
| `participant_age_months` | Age in months | 7.0-12.0 |
| `participant_age_years` | Age in years | 0.6-1.0 |

### Removed Columns (from old data):
- `trial_block_cumulative_order` (NOT in new data)
- `trial_block_frame` (NOT in new data)
- `trial_block_trial` (NOT in new data)
- `session_frame` → replaced by `Frame Number`
- `trial_frame` → replaced by `frame_count_trial_number`
- `segment_frame` → replaced by `frame_count_segment`
- `trial_cumulative_by_event` → replaced by `trial_number_global`

---

## Event Structure (Verified)

### Event Types (11 total):

All 11 event types confirmed:
- `gw` = GIVE WITH toy
- `gwo` = GIVE WITHOUT toy
- `hw` = HUG WITH toy
- `hwo` = HUG WITHOUT toy
- `sw` = SHOW WITH toy
- `swo` = SHOW WITHOUT toy
- `ugw` = UPSIDE-DOWN GIVE WITH toy
- `ugwo` = UPSIDE-DOWN GIVE WITHOUT toy
- `uhw` = UPSIDE-DOWN HUG WITH toy
- `uhwo` = UPSIDE-DOWN HUG WITHOUT toy
- `f` = FLOATING (control)

**Event coverage per participant**:
- Mean: 10.9 event types (out of 11)
- Min: 6 event types
- Max: 11 event types

**Note**: Not all participants saw all 11 event types:
- `gw`: 50 participants (1 missing)
- `f`, `ugw`, `ugwo`, `uhw`, `uhwo`: 50 participants each (1 missing)
- `gwo`, `hw`, `hwo`, `sw`, `swo`: All 51 participants

---

## Event Presentations

### Total Presentations:
- **Total across all participants**: 2,568 event presentations
- **Mean per participant**: 50.4 presentations (range: 24-80)

**This is MUCH higher than previous data**:
- Previous: ~12 presentations per participant
- New: ~50 presentations per participant
- **Reason**: More repetitions per event type

### Presentations Per Event Type:

**Example participant (Eight-0101-947)**:
```
Event   | Presentations | Total Frames
--------|---------------|-------------
f       | 4             | 599
gw      | 3             | 448
gwo     | 3             | 460
hw      | 5             | 819
hwo     | 9             | 1353  ← Most repeated
sw      | 4             | 599
swo     | 5             | 921
ugw     | 7             | 1053
ugwo    | 3             | 448
uhw     | 5             | 748
uhwo    | 6             | 902
--------|---------------|-------------
TOTAL   | 54            | 8,350 frames
```

**Key finding**: Each event type is repeated **3-9 times** per participant (not ~3 as in old data)

---

## event_presentation_id Construction (VERIFIED)

### Method:
```python
event_presentation_id = f"{participant}_{event}_{trial_number_global}"
```

### Verification Results:
- **Total unique IDs**: 2,568
- **Expected count**: 2,568
- **Duplicates**: 0

✅ **SUCCESS**: The method creates unique identifiers for all event presentations

### Example IDs:
```
Eight-0101-1579_gwo_1   ← 1st presentation of "gwo" for participant Eight-0101-1579
Eight-0101-1579_gwo_2   ← 2nd presentation of "gwo" for participant Eight-0101-1579
Eight-0101-1579_gwo_3   ← 3rd presentation of "gwo" for participant Eight-0101-1579
Eight-0101-1579_hw_1    ← 1st presentation of "hw" for participant Eight-0101-1579
Eight-0101-1579_hw_2    ← 2nd presentation of "hw" for participant Eight-0101-1579
```

### Usage in Code:
```python
# Create unique event presentation identifier
event_data['event_presentation_id'] = (
    event_data['Participant'] + '_' +
    event_data['event_verified'] + '_' +
    event_data['trial_number_global'].astype(str)
)
```

---

## Nesting Structure (Updated)

### Hierarchical Organization:

```
Level 3: Participant
  ├─ N = 51 participants
  ├─ Age: 7-12 months (mean=9.2, SD=1.5)
  └─ Each sees 6-11 event types (mean=10.9)
       │
       └─ Level 2: Event Presentation
            ├─ N ≈ 50 presentations per participant
            ├─ Total = 2,568 presentations across all participants
            ├─ Each event type shown 3-9 times (variable by participant)
            ├─ Unique ID: participant_event_trial_number_global
            └─ Duration: variable frames per presentation
                 │
                 └─ Level 1: Gaze Fixation
                      ├─ N ≈ 10-30 per presentation
                      ├─ Defined as 3+ consecutive frames on same AOI
                      └─ Total ≈ 25,680-77,040 gaze fixations (estimate)
                           │
                           └─ Level 0: Frame
                                ├─ Variable frames per participant (5,000-8,500)
                                ├─ Each row in CSV = 1 frame
                                └─ Aggregated (not modeled directly)
```

---

## Statistical Implications

### Sample Size Assessment (UPDATED):

| Level | N | Change from Previous | Adequacy for LMM/GLMM |
|-------|---|---------------------|----------------------|
| **Participants** | 51 | +15 (was 36) | ✅ Excellent (increased power) |
| **Presentations per participant** | ~50 | +38 (was ~12) | ✅ MUCH BETTER for random slopes |
| **Total presentations** | 2,568 | +2,136 (was ~432) | ✅ Excellent power |
| **Repetitions per event type** | 3-9 | ~3x more (was ~3) | ✅ BETTER for AR-6 trial-order analysis |

### Power Implications:

**AR-6 (Trial-Order Effects)** - **GREATLY IMPROVED**:
- Previous: ~3 presentations per event type per participant
- New: 3-9 presentations per event type per participant
- **Impact**: Much better power for random slopes estimation
- **Recommendation**: Random slopes now HIGHLY feasible

**All other analyses** - **IMPROVED**:
- More presentations = better precision
- More participants = better generalizability
- Increased power for all LMM/GLMM analyses

---

## Documentation Updates Required

### Files to Update:

1. **spec.md**:
   - Change "36 participants" → "51 participants"
   - Change "~12 presentations" → "~50 presentations"
   - Update age statistics (mean=9.2 months)
   - Remove all references to `data/raw/`
   - Update to `data/csvs_human_verified_vv/`

2. **plan.md**:
   - Update sample size section
   - Update nesting structure
   - Remove trial_block references
   - Update column list

3. **pipeline_config.yaml**:
   - Update data paths
   - Update column names (event → event_verified, etc.)
   - Remove trial_block validation rules

4. **All analysis configs (ar1-ar7)**:
   - Update expected sample sizes
   - Update power estimates
   - AR-6: Emphasize improved feasibility of random slopes

5. **research.md**:
   - Update sample size justifications
   - Update nesting structure diagrams

---

## Action Items

- [ ] Update spec.md with new sample size (51 participants, ~50 presentations)
- [ ] Update plan.md with new data structure
- [ ] Update pipeline_config.yaml paths and columns
- [ ] Update all AR configs with new sample sizes
- [ ] Remove all `data/raw/` references from documentation
- [ ] Update nesting hierarchy diagrams
- [ ] Verify adult data structure (15 participants)

---

## Summary

✅ **event_presentation_id method verified**: `participant_event_trial_number_global` creates unique IDs
✅ **Sample size increased**: 51 participants (was 36), 2,568 presentations (was ~432)
✅ **Statistical power improved**: Much better for random slopes and all LMM/GLMM analyses
✅ **Data structure confirmed**: Same 11 event types, similar age range (7-12 months)
✅ **Column changes documented**: New columns added, trial_block columns removed

**Next step**: Update all documentation files to reflect new data structure
