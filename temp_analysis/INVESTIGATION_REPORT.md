# Investigation Report: AR1 Condition Filtering & Terminology

**Date:** 2025-10-27
**Investigator:** Claude
**Status:** Investigation Complete - No Changes Made Yet

---

## ISSUE 1: UPSIDE_DOWN Variants Included in GIVE vs HUG Comparison

### Current Behavior

**AR1 Code (lines 116-124):**
```python
give = participant_means[
    participant_means["condition_name"].str.upper().str.contains("GIVE") &
    participant_means["condition_name"].str.upper().str.contains("WITH")
]["toy_proportion"]

hug = participant_means[
    participant_means["condition_name"].str.upper().str.contains("HUG") &
    participant_means["condition_name"].str.upper().str.contains("WITH")
]["toy_proportion"]
```

**What This Selects:**

**GIVE group includes:**
- GIVE_WITH
- UPSIDE_DOWN_GIVE_WITH

**HUG group includes:**
- HUG_WITH
- UPSIDE_DOWN_HUG_WITH

### Why This is Problematic

**Scientific Issue:** UPSIDE_DOWN variants are **biomechanical controls**, not the primary manipulation.

**Purpose of upside-down conditions:**
- Test if effects are due to **event understanding** (what you want) vs **visual motion patterns** (control)
- If infants only respond to motion, upside-down should work same as upright
- If infants understand meaning, upside-down may reduce or eliminate effect

**Including them together:**
- May DILUTE the effect (if upside-down reduces understanding)
- May STRENGTHEN the effect (if upside-down doesn't affect understanding)
- Could CONFOUND results (if upside-down has asymmetric effect)

**Bottom line:** Mixing them prevents clean interpretation of your primary hypothesis.

---

### Solution: Make It Configurable in YAML

**YES, this can be made configurable.**

**Best Location:** `config/analysis_configs/ar1_config.yaml` (already exists)

**Recommended YAML Structure:**

```yaml
# AR-1: Gaze Duration Analysis Configuration

# ... existing settings ...

# Condition Comparisons
comparisons:
  # Primary comparison (upright conditions only)
  primary:
    name: "Upright GIVE vs HUG"
    description: "Test selective attention in canonical events"
    give_conditions:
      - "GIVE_WITH"
    hug_conditions:
      - "HUG_WITH"

  # Control comparison (upside-down conditions)
  control_biomechanical:
    name: "Upside-Down GIVE vs HUG"
    description: "Test if effect persists with disrupted biomechanics"
    give_conditions:
      - "UPSIDE_DOWN_GIVE_WITH"
    hug_conditions:
      - "UPSIDE_DOWN_HUG_WITH"

  # Combined comparison (current behavior)
  combined:
    name: "All GIVE vs All HUG (upright + upside-down)"
    description: "Test robustness across orientation variants"
    give_conditions:
      - "GIVE_WITH"
      - "UPSIDE_DOWN_GIVE_WITH"
    hug_conditions:
      - "HUG_WITH"
      - "UPSIDE_DOWN_HUG_WITH"

# Which comparison to use for main analysis
active_comparison: "primary"  # Options: "primary", "control_biomechanical", "combined"

# Run all comparisons and report separately
report_all_comparisons: true  # If true, generates results for all defined comparisons
```

### Implementation Changes Needed

**Files to modify:**
1. `config/analysis_configs/ar1_config.yaml` - Add comparisons section (above)
2. `src/analysis/ar1_gaze_duration.py` - Update `_compute_statistics()` to read from config

**Code changes in ar1_gaze_duration.py:**
```python
def _compute_statistics(participant_means, summary, config):
    # Load comparison configuration
    ar1_config = config.get("ar1_config", {})
    comparisons = ar1_config.get("comparisons", {})
    active = ar1_config.get("active_comparison", "primary")

    comparison = comparisons.get(active, {})
    give_conditions = comparison.get("give_conditions", ["GIVE_WITH"])
    hug_conditions = comparison.get("hug_conditions", ["HUG_WITH"])

    # Filter to exact conditions
    give = participant_means[
        participant_means["condition_name"].isin(give_conditions)
    ]["toy_proportion"]

    hug = participant_means[
        participant_means["condition_name"].isin(hug_conditions)
    ]["toy_proportion"]

    # ... rest of statistics calculation ...
```

### Benefits of This Approach

**Flexibility:**
- Run different comparisons without code changes
- Test robustness across multiple contrasts
- Document scientific rationale in config

**Reproducibility:**
- Clear which conditions were compared
- Easy to replicate with different subsets
- Version-controlled in YAML

**Scientific rigor:**
- Separate primary from control analyses
- Report upside-down as supplementary
- Align analysis with theoretical framework

---

## ISSUE 2: "Gaze Fixation" Terminology is Confusing

### Why It's Problematic

**The word "event" is overloaded** in this project:

1. **Stimulus event** (e.g., 'gw', 'hw', 'f')
   - The video showing an action
   - 11 types total
   - 150-185 frames (~5 seconds)

2. **Event exposure / Trial** (tracked by trial_number)
   - Each time participant sees a stimulus event
   - ~1,916 trials in child data

3. **Gaze fixation** (CURRENT USAGE - the problem)
   - 3+ consecutive frames on same AOI
   - ~26,560 in combined data
   - Unit of analysis detected by preprocessing

**When you say "4,266 toy gaze fixations"** it's ambiguous:
- Does this mean 4,266 stimulus events? NO
- Does this mean 4,266 trials? NO
- Does this mean 4,266 instances of 3+ frame gazes? YES

**For publication:** Reviewers will be confused by "gaze fixation" when you're also talking about "GIVE event" and "HUG event"

---

### Alternative Terminology Options

**Ranked by appropriateness:**

#### **1. gaze_fixation** (RECOMMENDED)
**Pros:**
- Standard in eye-tracking research
- Clear meaning to scientific audience
- Distinct from stimulus events
- Professional and precise

**Cons:**
- Technically, "fixation" has strict definition (50-200ms with spatial stability)
- May require clarification in methods

**How to use:**
> "We detected 26,560 gaze fixations across 66 participants. A gaze fixation was defined as 3 or more consecutive frames (minimum 100ms at 30fps) during which the participant's gaze remained on the same Area of Interest (AOI)."

---

#### **2. sustained_gaze** (GOOD ALTERNATIVE)
**Pros:**
- Emphasizes your 3+ frame requirement
- Clear, descriptive
- Natural language
- Appropriate for infant research

**Cons:**
- Slightly less standard than "fixation"
- Two-word phrase (longer)

**How to use:**
> "We identified 26,560 sustained gazes. A sustained gaze was defined as 3 or more consecutive frames on the same AOI."

---

#### **3. gaze_bout** (BEHAVIORAL EMPHASIS)
**Pros:**
- Used in behavioral ecology and ethology
- Implies sustained attention episode
- Distinct from "event"

**Cons:**
- Less familiar to cognitive development audience
- May imply longer durations

**How to use:**
> "We analyzed 26,560 gaze bouts across participants. Each bout consisted of 3+ consecutive frames directed at a single AOI."

---

#### **Other Options Considered:**

**gaze_sequence** - Too vague, "sequence" doesn't imply threshold
**look** - Too informal for publication
**gaze_episode** - "Episode" has other developmental meanings
**fixation_event** - Still uses "event" (no improvement)
**gaze_unit** - Too abstract, less intuitive

---

### Field-Specific Conventions

**Standard Eye-Tracking Terminology:**
- **Fixation:** Gaze held on spatial point (50-200ms, requires stability)
- **Saccade:** Rapid eye movement between fixations
- **Dwell time:** Total time spent in AOI (sum of fixations)
- **Visit:** Entry into and exit from AOI (may include multiple fixations)

**Infant Research Conventions:**
- **Looking time:** Total duration of gaze (what you measure as gaze_duration_ms)
- **Look:** Informal instance of looking
- **Gaze:** General term for visual attention

**Your Definition (3+ frames, same AOI) is closest to:**
- **Fixation** (if frames are spatially stable within AOI)
- **Visit** (if allowing movement within AOI boundaries)
- **Bout** (if emphasizing sustained attention episode)

---

### Recommendation: Use "gaze_fixation"

**Rationale:**
1. **Most standard** in eye-tracking literature
2. **Clear** to reviewers and readers
3. **Distinct** from stimulus events
4. **Professional** tone for publication

**How to address technical definition:**
> "Note: While standard fixation detection requires spatial stability within 1° visual angle, our AOI-based approach defines a fixation as sustained attention (3+ frames) within a functionally-defined region of interest. This is appropriate for infant eye-tracking where precise spatial calibration is challenging (Aslin, 2007)."

---

### Code Changes Needed (If Renaming)

**Impact:** Moderate refactoring (~50-70 changes across codebase)

**Files/Variables to Rename:**

**Data files:**
- `gaze_fixations.csv` → `gaze_fixations.csv`
- `gaze_fixations_child.csv` → `gaze_fixations_child.csv`
- `gaze_fixations_adult.csv` → `gaze_fixations_adult.csv`

**Python modules:**
- `src/preprocessing/gaze_detector.py` → `gaze_fixation_detector.py` (or keep filename, rename functions)

**Function names:**
- `detect_gaze_fixations()` → `detect_gaze_fixations()`
- `_extract_events_from_group()` → `_extract_fixations_from_group()`
- `_finalize_event()` → `_finalize_fixation()`

**Variable names:**
- `gaze_fixation_id` → `gaze_fixation_id`
- `GazeFixation` dataclass → `GazeFixation`

**Column names:**
- Keep column names (gaze_start_frame, gaze_duration_ms) - these are fine
- Only rename references to "event" in comments/docs

**Documentation:**
- All docstrings mentioning "gaze fixation"
- `MENTORSHIP_DATA_FLOW.md`
- `README.md`
- Report templates (`templates/ar1_template.html`, etc.)
- This investigation report

**Estimated effort:** 2-3 hours for careful find-replace + testing

**When to do it:** Before first publication or major presentation

---

## SUMMARY & RECOMMENDATIONS

### Issue 1: UPSIDE_DOWN Variants

**Finding:** YES, currently includes UPSIDE_DOWN variants in GIVE vs HUG comparison

**Problem:** Mixes primary manipulation with biomechanical control

**Solution:** Add `comparisons` section to `ar1_config.yaml`

**Recommendation:**
```yaml
active_comparison: "primary"  # Use upright-only for main analysis

comparisons:
  primary:
    give_conditions: ["GIVE_WITH"]
    hug_conditions: ["HUG_WITH"]
```

**Priority:** HIGH - Affects scientific interpretation

---

### Issue 2: "Gaze Fixation" Terminology

**Finding:** YES, "gaze_fixation" is confusing given overloaded use of "event"

**Problem:** Ambiguous whether referring to stimulus event vs gaze instance

**Solution:** Rename to "gaze_fixation" throughout codebase

**Recommendation:**
- **Terminology:** Use "gaze fixation" in all publications
- **Code:** Rename variables/files when convenient (not urgent)
- **Priority:** MEDIUM - Important for clarity, but can defer until pre-publication

**Quick win:** Update documentation and report templates first, defer code variable renaming

---

## NEXT STEPS (If You Approve)

### For Issue 1 (UPSIDE_DOWN):
1. Add comparisons section to `ar1_config.yaml`
2. Update `_compute_statistics()` in `ar1_gaze_duration.py`
3. Re-run AR1 with `active_comparison: "primary"`
4. Compare results: upright-only vs combined

### For Issue 2 (Terminology):
1. Update `MENTORSHIP_DATA_FLOW.md` to say "gaze fixations"
2. Update report templates to use "gaze fixation"
3. Update docstrings in key modules
4. (Optional) Rename code variables and files

---

**Investigation Complete.** Ready for your decision on implementation.
