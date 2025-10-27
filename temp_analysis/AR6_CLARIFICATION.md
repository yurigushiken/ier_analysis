# ✅ AR-6 Clarification: Trial-Order Effects (NOT Habituation)

**Date**: 2025-10-26
**Issue**: Incorrectly assumed this was a habituation study
**Resolution**: AR-6 tests trial-order effects within repeated presentations of same event type

---

## ❌ What I Incorrectly Assumed

**Wrong interpretation**:
> "AR-6 tests habituation across the entire session"
> - Presentation 1 (could be any event): High looking time
> - Presentation 2 (different event): Lower looking time
> - Presentation 12 (another event): Much lower looking time

**Why this was wrong**:
- This assumes a fixed presentation order across all event types
- This is a habituation paradigm (getting bored with repeated stimuli)
- **Your study is NOT about habituation**

---

## ✅ Correct Understanding

### **What AR-6 Actually Tests**:

**Trial-order effects within event type**:
- Each event type (gw, gwo, hw, etc.) is shown **~3 times** per participant
- Question: Do looking patterns change from 1st to 3rd presentation of **the same event**?

**Example**:
```
Participant sees "gw" (GIVE WITH) three times during session:

Presentation 1 of gw (trial_cumulative_by_event = 1):
  - Toy looking time: 45%
  - Novel stimulus, high attention

Presentation 2 of gw (trial_cumulative_by_event = 2):
  - Toy looking time: 42%
  - Slightly less attention?

Presentation 3 of gw (trial_cumulative_by_event = 3):
  - Toy looking time: 40%
  - Learning/adaptation effect?
```

**Statistical question**:
- Is the slope (1→2→3) significantly different from zero?
- Does this slope differ between GIVE vs HUG vs SHOW?
- Do individual infants vary in their slopes (random slopes)?

---

## 📊 Data Structure for AR-6

### **Key Column**: `trial_cumulative_by_event`

From README:
> "trial_cumulative_by_event: of the whole session, the nth trial of that particular event (gw, gwo, hw, etc)"

**What this means**:
```
participant | event | trial_cumulative_by_event | gaze_metric
Eight-0101  | gw    | 1                        | 0.45
Eight-0101  | hw    | 1                        | 0.30
Eight-0101  | gw    | 2                        | 0.42  ← 2nd time seeing gw
Eight-0101  | swo   | 1                        | 0.28
Eight-0101  | hw    | 2                        | 0.29  ← 2nd time seeing hw
Eight-0101  | gw    | 3                        | 0.40  ← 3rd time seeing gw
```

**Not randomized order**: Events are NOT shown in fixed order
- "gw" 1st presentation might be shown at session time 5 minutes
- "gw" 2nd presentation might be shown at session time 15 minutes
- "gw" 3rd presentation might be shown at session time 25 minutes

---

## 🔬 Correct Statistical Model

### **Model for AR-6**:

**Option 1: All events together**
```python
# Test if trial-order effect differs by event type
model = MixedLM.from_formula(
    'gaze_metric ~ trial_cumulative_by_event * event + (1 + trial_cumulative_by_event | participant)',
    data=event_data,
    groups='participant'
)
```

**Interpretation**:
- **Main effect of `trial_cumulative_by_event`**: Average change across repetitions (pooled across events)
- **Interaction `trial_cumulative_by_event:event`**: Does the change differ for GIVE vs HUG vs SHOW?
- **Random slope**: Each infant has their own trial-order effect

**Option 2: Separate analysis per event type**
```python
# Example: Just GIVE WITH events
gw_data = event_data[event_data['event'] == 'gw']

model = MixedLM.from_formula(
    'gaze_metric ~ trial_cumulative_by_event + (1 + trial_cumulative_by_event | participant)',
    data=gw_data,
    groups='participant'
)
```

**Interpretation**:
- Tests if looking patterns change across 1st, 2nd, 3rd presentation of "gw"
- Random slope captures individual differences (some infants show learning, others show adaptation)

---

## 📈 Possible Outcomes

### **1. Positive Slope (Learning)**:
```
Looking time INCREASES across presentations
→ Infants are learning about the event structure
→ Greater engagement/understanding with repetition
```

### **2. Negative Slope (Adaptation/Fatigue)**:
```
Looking time DECREASES across presentations
→ Infants are adapting (less novel)
→ Or: fatigue, boredom
```

### **3. No Slope (Stability)**:
```
Looking time STAYS CONSTANT across presentations
→ Robust representation from first exposure
→ Or: event is equally engaging across repetitions
```

### **4. Event-Specific Effects**:
```
GIVE: Positive slope (learning)
HUG: No slope (stable)
SHOW: Negative slope (adaptation)

→ Different event types elicit different trial-order patterns
```

---

## 🎯 Why Random Slopes Are ESSENTIAL

**Individual variability in trial-order effects**:

**Infant A**: Learning effect
- gw presentation 1: 30% toy looking
- gw presentation 2: 40% toy looking
- gw presentation 3: 50% toy looking
- **Slope**: +10% per presentation

**Infant B**: Adaptation effect
- gw presentation 1: 50% toy looking
- gw presentation 2: 40% toy looking
- gw presentation 3: 30% toy looking
- **Slope**: -10% per presentation

**Infant C**: Stable
- gw presentation 1: 40% toy looking
- gw presentation 2: 40% toy looking
- gw presentation 3: 40% toy looking
- **Slope**: 0% per presentation

**Random slope captures this variability**:
- Population-level effect: Average slope across all infants
- Individual-level effects: Each infant's specific slope (BLUPs)
- Variance component: How much infants vary in their slopes

**Without random slopes**:
- Assumes all infants have same slope
- Underestimates standard errors
- May miss important individual differences

---

## 📋 Updated AR-6 Configuration

**File**: [ar6_config.yaml](../config/analysis_configs/ar6_config.yaml)

**Key changes**:
1. **analysis_name**: "AR-6: Trial-Order Effects" (not "Habituation")
2. **trial_variable**: `trial_cumulative_by_event` (not session-wide presentation order)
3. **lmm_formula**: `gaze_metric ~ trial_cumulative_by_event * event + (1 + trial_cumulative_by_event | participant)`
4. **expected_pattern**: "both" (test for any systematic change, not just habituation)

---

## ✅ Summary

**What AR-6 is**:
- Trial-order effects within repeated presentations of same event type
- Uses `trial_cumulative_by_event` column (1st, 2nd, 3rd presentation of each event)
- Tests if looking patterns systematically change across repetitions
- Can differ by event type (GIVE vs HUG vs SHOW)

**What AR-6 is NOT**:
- ❌ NOT a habituation study (not testing session-wide decline)
- ❌ NOT testing fixed presentation order across all events
- ❌ NOT assuming all infants show same pattern

**Why LMM with random slopes is essential**:
- Captures individual differences in trial-order effects
- Some infants learn, some adapt, some stay stable
- Provides accurate inference for population-level effects

---

**This correction improves the scientific validity of AR-6!** ✅
