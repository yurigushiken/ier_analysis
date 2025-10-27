# Combined Data Summary

**Date:** 2025-10-27
**Action:** Created combined gaze_events.csv and updated all AR analyses to use it by default

---

## ✅ COMPLETED ACTIONS

### 1. Created Combined Gaze Events File
**Location:** `data/processed/gaze_events.csv`

**Contents:**
```
Total gaze events:    26,560
Total participants:   66
  - Infants:          51 participants (19,811 events)
  - Adults:           15 participants (6,749 events)
Age range:            7 - 672 months
Conditions:           11 unique
```

**Source Files:**
- `data/processed/gaze_events_child.csv` (19,811 events, 51 infants)
- `data/processed/gaze_events_adult.csv` (6,749 events, 15 adults)

---

### 2. Updated All AR Modules

**Changed default file loading order:**
- **NEW (Priority 1):** `gaze_events.csv` (combined child + adult)
- **OLD (Priority 2):** `gaze_events_child.csv` (child-only fallback)

**Files updated:**
- ✓ `src/analysis/ar1_gaze_duration.py`
- ✓ `src/analysis/ar2_transitions.py`
- ✓ `src/analysis/ar3_social_triplets.py`
- ✓ `src/analysis/ar4_dwell_times.py`
- ✓ `src/analysis/ar5_development.py`
- ✓ `src/analysis/ar6_learning.py`
- ✓ `src/analysis/ar7_dissociation.py`

**Result:** All AR analyses now use combined data by default!

---

### 3. Re-Ran AR1 Analysis

**Report:** `results/AR1_Gaze_Duration/report.html`

**Previous Results (Child-Only):**
```
Condition                    N Participants    Mean Toy Proportion
GIVE_WITH                    46                0.199
HUG_WITH                     46                0.102
FLOATING                     47                0.102
```

**NEW Results (Combined Child + Adult):**
```
Condition                    N Participants    Mean Toy Proportion
GIVE_WITH                    61                0.210
HUG_WITH                     61                0.113
FLOATING                     62                0.137
GIVE_WITHOUT                 65                0.130
HUG_WITHOUT                  66                0.071
SHOW_WITH                    65                0.150
SHOW_WITHOUT                 65                0.108
UPSIDE_DOWN_GIVE_WITH        61                0.222
UPSIDE_DOWN_GIVE_WITHOUT     63                0.199
UPSIDE_DOWN_HUG_WITH         63                0.151
UPSIDE_DOWN_HUG_WITHOUT      62                0.120
```

**Changes:**
- ✅ Participant counts increased by ~15 per condition (added 15 adults)
- ✅ Mean proportions slightly changed (weighted by combined sample)
- ✅ All 11 conditions now have 60+ participants

---

## 📊 DATA STRUCTURE

### Current File Organization:
```
data/processed/
├── gaze_events.csv           ← COMBINED (26,560 events, 66 participants) [DEFAULT]
├── gaze_events_child.csv     ← Child-only (19,811 events, 51 infants)
└── gaze_events_adult.csv     ← Adult-only (6,749 events, 15 adults)
```

### How Analyses Load Data:
1. **First check:** `gaze_events.csv` exists? → Use it (combined)
2. **Fallback:** `gaze_events_child.csv` exists? → Use it (child-only)
3. **Error:** Neither exists → Raise FileNotFoundError

**Current behavior:** All analyses use `gaze_events.csv` (combined data)

---

## 🎯 SCIENTIFIC IMPLICATIONS

### Advantages of Combined Data:

✅ **Larger sample size**
- More statistical power
- More robust effect size estimates
- Better condition coverage

✅ **Adult reference group**
- Can compare infant vs adult patterns
- Adults serve as "mature understanding" baseline
- Developmental trajectory from infancy to adulthood

✅ **Publication value**
- Stronger findings with larger N
- Cross-age validation
- Richer discussion of developmental changes

### Potential Considerations:

⚠️ **Mixed age ranges**
- Infants: 7-12 months
- Adults: 672 months (56 years)
- May need to analyze separately or add age covariates

⚠️ **Different looking patterns**
- Adults have shorter gaze durations (mean: 11.6 frames vs infants: 18.5 frames)
- Adults may scan more efficiently
- Consider participant_type as a factor in analyses

---

## 💡 RECOMMENDATIONS

### For Current Analyses (AR1-AR7):

**Option 1: Analyze Combined (Current Default)**
- Includes both infants and adults
- Add `participant_type` as a factor or covariate
- Report separate results for infants vs adults in each AR

**Option 2: Filter to Infant-Only**
- Modify each AR to filter: `df[df['participant_type'] == 'infant']`
- Keeps analyses focused on infant development
- Use adults for supplementary/exploratory analyses

**Option 3: Separate Analyses**
- Run all ARs twice: once for infants, once for adults
- Compare patterns across age groups
- Most comprehensive but time-intensive

### Recommended Approach:

**For primary research questions (AR1-AR7):**
- Filter to `participant_type == 'infant'` within each AR
- Focus on infant development (ages 7-12 months)
- This keeps analyses aligned with original research goals

**For supplementary analyses:**
- Use combined data for exploratory comparisons
- Generate adult-only reports for context
- Include in supplementary materials or appendices

---

## 🔧 HOW TO SWITCH BETWEEN MODES

### To Use Child-Only Data:
```python
# In each AR module's _load_gaze_events function, add:
df = pd.read_csv(path)
df = df[df['participant_type'] == 'infant']
return df
```

### To Use Combined Data (Current Default):
```python
# No changes needed - already using combined file
df = pd.read_csv(path)
return df
```

### To Create Separate Adult Reports:
```python
# In each AR module's _load_gaze_events function, add:
df = pd.read_csv(path)
df = df[df['participant_type'] == 'adult']
return df
# Then run: python src/main.py
# Outputs will be adult-only results
```

---

## 📋 NEXT STEPS

### Immediate:
1. ✅ Combined file created
2. ✅ AR modules updated
3. ✅ AR1 re-run with combined data

### Recommended:
1. **Decide on analysis strategy:**
   - Infant-only (primary)?
   - Combined with age factor?
   - Separate infant vs adult reports?

2. **Update other ARs:**
   - Run AR2-AR7 with new default
   - Decide if filtering to infants is needed

3. **Update documentation:**
   - Clarify in reports whether using infant-only or combined
   - Update MENTORSHIP_DATA_FLOW.md to reflect new default

---

## 📁 FILES CREATED

- ✅ `data/processed/gaze_events.csv` - Combined child + adult data
- ✅ `temp_analysis/combine_data.py` - Script to create combined file
- ✅ `temp_analysis/update_ar_defaults.py` - Script to update AR modules
- ✅ `results/AR1_Gaze_Duration/report.html` - Updated AR1 report with combined data

---

**Status:** All systems updated. Combined data is now the default for all analyses.
