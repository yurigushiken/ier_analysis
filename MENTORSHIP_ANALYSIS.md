# Dr. Gordon's Vision: A Comprehensive Analysis and Mentorship Guide

**Prepared for:** Your Career Development
**Date:** 2025-11-23
**Purpose:** Understanding the theoretical foundations and analysis logic of the IER project

---

## Executive Summary

You are fulfilling Dr. Peter Gordon's groundbreaking vision to demonstrate that **pre-linguistic infants understand verb-argument structure through their visual attention patterns**. This document provides a comprehensive analysis of:

1. Gordon's theoretical framework from the Project Description
2. The logic and predictions for AR1-AR7
3. Whether comparisons should be infant vs. adult or condition vs. condition
4. The role of "transformed data" in AR2-AR7
5. Critical evaluation of your current experimental design

---

## Part 1: Dr. Gordon's Core Theoretical Vision

### The Central Hypothesis

From the Project Description PDF, Gordon's fundamental claim is:

> **"The human conceptual system constructs event representations that possess argument-like structures independent of overt linguistic input."**

### The Evidence Inspiring This Work

**Home Sign Systems** (Goldin-Meadow, 1985):
- Deaf children of hearing parents invent their own gesture systems
- These systems show **primitive argument structure**
- Example: "Giving" gestures distinguish giver, recipient, and object
- **Conclusion**: Argument structure exists **before language** - it's conceptual, not linguistic

### Gordon's Event Representation Model (Figure 1, Page 3)

Gordon proposes this mapping:

```
WORLD → COGNITION → LANGUAGE
  ↓           ↓            ↓
Event     Event Rep     Verb-Argument
Structure (Main Act +   Structure
          Participants)
```

**Key insight**: Before mapping to language, infants must:
1. **Identify the "Main Act"** - What is the intentional-causal focus?
2. **Determine Relevant Participants** - Which elements are essential vs. incidental?

### The Give/Hug Paradigm (Pages 6-7)

Gordon's original experiments (Scherf & Gordon, 1998, 2000):

**GIVE Event:**
- **Main Act**: Transfer of possession
- **Arguments**: Giver (girl), Recipient (boy), Object (toy)
- **Prediction**: Toy is RELEVANT → infants attend to it

**HUG Event:**
- **Main Act**: Physical embrace
- **Arguments**: Hugger (girl), Huggee (boy)
- **Prediction**: Toy is IRRELEVANT → infants should ignore it

**Original Finding (10-month-olds, Figure 3):**
- GIVE condition: Dishabituation when toy removed (p=.02)
- HUG condition: NO dishabituation when toy removed (p=.11)

**Interpretation**: Infants only notice toy removal when it's an argument!

---

## Part 2: Understanding Your Data Types

### Raw Data (NOT Transformed)

**Location**: `data/csvs_human_verified_vv/child/` and `.../adult/`

**Structure**: Frame-by-frame What+Where pairs

Example row:
```
Eight-0101-947,00:00:05:8667,woman,face,5.8667,5.9,gw,176,1,1,interaction,8,infant
```

**This is the ground truth** - human-verified gaze coordinates.

### Processed Data (TRANSFORMED)

**Location**: `data/processed/gaze_fixations_child.csv`

**Structure**: Aggregated gaze fixations

Example:
```
participant_id,age_months,trial_number,condition,segment,aoi_category,
gaze_duration_ms,gaze_onset_time,gaze_offset_time
Eight-0101-1579,8,1,gwo,interaction,woman_face,1099.9,10.8667,11.9667
```

**Key Transformation**:
- **Raw**: Frame 51, 52, 53, 54... all on "woman_face"
- **Transformed**: One fixation record "woman_face, 1100ms duration"

### Your Question: "Do AR2-7 Use Transformed Data?"

**Answer**: YES, but here's the critical nuance:

| Analysis | Input Data | Transformation Applied |
|----------|------------|------------------------|
| **AR1** | Processed fixations | Aggregate by trial → proportion |
| **AR2** | Processed fixations | Collapse consecutive → transitions |
| **AR3** | Processed fixations | Sliding window → triplet detection |
| **AR4** | Processed fixations | Filter outliers → dwell time distribution |
| **AR5** | Processed fixations | + Age variable → developmental interaction |
| **AR6** | Processed fixations | + Trial order → learning curves |
| **AR7** | Processed fixations | Multi-condition → dissociation tests |

**So**: All analyses start with the SAME processed fixations file. They differ in **what they calculate from it**, not in the data itself.

---

## Part 3: Gordon's Explicit Predictions

### From the Project Description

Gordon **DOES** lay out specific predictions:

#### Prediction 1: Argument Status Affects Attention (Page 7)

> "Infants in the GIVE condition showed longer looking time to the novel test trials (NEW) than to the familiar test trials (OLD) (p=.02). However, infants in the HUG condition did not show longer looking times to the NEW test trials."

**For eye-tracking**:
- **AR1**: More total time on toy in GIVE than HUG ✓
- **AR4**: Longer dwells on toy in GIVE than HUG ✓

#### Prediction 2: Developmental Trajectory (Page 7, Figure 4)

> "Eight month olds showed a similar, but attenuated pattern as the 10 month olds (p=.05 for GIVE, ns for HUG). Six month olds, on the other hand, show no effects for either GIVE or HUG conditions."

**For developmental analyses**:
- **AR5**: Should show Age × Condition interaction
- **Progression**: 6mo (no effect) → 8mo (weak) → 10mo (strong)

#### Prediction 3: Intentionality Cues Matter (Page 12, Experiment 9)

> "Early pilot data with 10 month olds in this condition [Hug w/give - unintentional transfer] do not show evidence of dishabituation when the toy is removed on test."

**Interpretation**: Simple physical transfer ≠ GIVE. Must have intentional structure.

#### Prediction 4: Perceptual Salience Alone Is Insufficient (Pages 8-9)

Experiments 4-6 test low-level accounts:

**Experiment 4 (GIVE/HUG Alternation)**:
> "Infants in this experiment do not show longer looking times for the GIVE W/O than the HUG-W/O video (p=.8)."

**Conclusion**: It's not about oddness, it's about meaning.

**Experiment 5 (Give Upside-Down)**:
> "Pilot data with 10 month olds on this procedure currently show no change in looking time when the toy is removed on test."

**Conclusion**: Must be meaningful (upright) to drive attention.

#### Prediction 5: Eye Tracking Shows Intentional Focus (Page 10)

> "For the GIVE video, there is sharp increase in looking at the TOY during the interaction stage... Deletion of the toy in the GIVE w/o video has almost no effect on looking behavior: Infants persist in looking to the location where the toy had been."

**For AR2**: Should see strong toy↔people transitions in GIVE

**For AR3**: Should see person→toy→person triplets in GIVE

#### Prediction 6: Abstract Transfer Matters (Page 13, Experiment 11)

> "If infants are to interpret these animations as acts of 'giving'... this requires they attribute some degree of intentionality to the abstract shapes."

**Prediction**: Intentionality manipulation should modulate effects.

---

## Part 4: Should You Compare Infants to Adults?

### The Answer: **BOTH**, but for Different Purposes

#### Option A: Infant Conditions vs. Adult Conditions (Developmental Comparison)

**Purpose**: Is the infant pattern *like* the adult pattern?

**Assumption**: Adults represent the "mature" endpoint of event comprehension

**Example AR1 Analysis**:
- Infant GIVE vs. HUG: 19.9% vs. 10.2% (difference = 9.7%)
- Adult GIVE vs. HUG: [need data] vs. [need data]
- **Question**: Do infants show the SAME PATTERN as adults?

**Theoretical Interpretation**:
- ✅ **Pattern match**: Infants have adult-like event comprehension
- ❌ **Pattern mismatch**: Infant comprehension is qualitatively different or immature

#### Option B: Infant GIVE_WITH vs. GIVE_WITHOUT (Within-Infant Comparison)

**Purpose**: Do infants notice when argument is removed?

**Assumption**: Relevant elements should be noticed when absent

**Example AR2 Analysis**:
- GIVE_WITH: Strong toy→face transitions
- GIVE_WITHOUT: Weak (or no) toy_location→face transitions
- **Question**: Does removing the toy change scanning patterns?

**Theoretical Interpretation**:
- ✅ **Different patterns**: Infants encode toy's physical presence
- ✅ **Same patterns**: Infants have abstract "toy role" representation

### Gordon's Actual Design Uses BOTH

From pages 6-7:

**Within-Infant (Primary Test)**:
- Habituate to GIVE_WITH → Test with GIVE_WITHOUT
- Habituate to HUG_WITH → Test with HUG_WITHOUT
- **Logic**: Dishabituation shows argument detection

**Between-Condition (Secondary Test)**:
- Compare GIVE vs. HUG conditions
- **Logic**: Different events should yield different patterns

**Developmental (Tertiary Test)**:
- 6-month, 8-month, 10-month age groups
- **Logic**: Developmental trajectory shows when capacity emerges

### My Recommendation for Your Analyses

| Analysis | Primary Comparison | Secondary Comparison | Tertiary Comparison |
|----------|-------------------|---------------------|---------------------|
| **AR1** | GIVE_WITH vs. HUG_WITH | GIVE_WITH vs. GIVE_WITHOUT | Infant vs. Adult (all conditions) |
| **AR2** | GIVE_WITH vs. GIVE_WITHOUT | GIVE_WITH vs. HUG_WITH | Infant vs. Adult |
| **AR3** | GIVE_WITH vs. HUG_WITH | — | Infant vs. Adult |
| **AR4** | GIVE_WITH vs. HUG_WITH | GIVE_WITH vs. GIVE_WITHOUT | Infant vs. Adult |
| **AR5** | Age × Condition Interaction | — | — |
| **AR6** | Trial 1 vs. Trial 5 (learning) | GIVE vs. HUG learning rates | — |
| **AR7** | GIVE vs. HUG vs. SHOW | — | — |

**Rationale**:
1. **Primary**: Tests the core argument-structure hypothesis
2. **Secondary**: Tests related theoretical questions
3. **Tertiary**: Establishes developmental context

---

## Part 5: Critical Evaluation - Is Your Design Logical?

### Strengths of Your Current Setup

✅ **AR1 (Gaze Duration)**: Directly tests Gordon's core finding
✅ **AR2 (Transitions)**: Novel extension - Gordon predicted this (page 10 eye-tracking)
✅ **AR3 (Triplets)**: Captures "social triangulation" Gordon mentioned
✅ **AR4 (Dwell Time)**: Quality vs. quantity distinction - theoretically sound
✅ **AR5 (Development)**: Explicitly predicted by Gordon (Fig 4, page 7)
✅ **AR6 (Learning)**: Gordon used habituation, so learning curves are relevant
✅ **AR7 (Dissociation)**: SHOW is Gordon's Experiment 13 (page 14)

### Potential Theoretical Concerns

⚠️ **Concern 1: Adult Comparisons May Be Misleading**

**Issue**: Gordon never claimed adults and infants should be *identical*

**Reason**:
- Adults have language - they might process events linguistically
- Adults have learned cultural scripts for giving/hugging
- Adults might use different strategies (top-down vs. infant bottom-up)

**Solution**:
- Frame adult data as **"endpoint reference"**, not **"correct answer"**
- Focus on infant PATTERN (GIVE ≠ HUG), not absolute values
- If infant≠adult, doesn't invalidate infant findings

⚠️ **Concern 2: GIVE_WITHOUT Comparison Is Ambiguous**

**Gordon's Design**:
- Habituation to GIVE_WITH
- Test with GIVE_WITHOUT
- **Logic**: Dishabituation shows toy was encoded

**Your AR2 Design**:
- Compare GIVE_WITH vs. GIVE_WITHOUT directly
- **Ambiguity**: What does similarity or difference mean?

**Possible Interpretations**:
1. **Similar patterns**: Infants have abstract representation (toy role exists even when toy absent)
2. **Different patterns**: Infants encode physical presence (no abstraction)

**Gordon doesn't explicitly predict which!**

**My Recommendation**:
- Run the analysis as planned
- **Interpret carefully**:
  - If SIMILAR: Infants represent the "giving" schema abstractly
  - If DIFFERENT: Infants track physical properties, not just abstract roles
- **Both are interesting findings**, not right/wrong

⚠️ **Concern 3: AR3 Triplet Frequency Is Low**

**From your results**: ~6% of trials show triplets

**Question**: Is this evidence FOR or AGAINST Gordon's theory?

**Gordon's View** (implied from pages 10-11):
- Triplets are **sophisticated** but not **necessary** for event understanding
- Even occasional triplets show the **capacity exists**
- Individual differences expected

**My Assessment**:
- ✅ Low frequency is OK - triplets are a "gold standard" marker
- ✅ Compare triplet rates across conditions (GIVE vs. HUG)
- ✅ Don't expect all infants to show triplets

### Missing from Gordon's Original Work

🔍 **What Gordon DIDN'T Test**:

1. **Frame-by-frame scanning patterns** (AR2, AR3) - You're pioneering this
2. **Dwell time quality** (AR4) - Novel contribution
3. **Trial-order learning effects** (AR6) - Assumes habituation but doesn't analyze it
4. **Multi-condition dissociation** (AR7) - Only 2-way comparisons in original

**Implication**: AR2-AR7 are **extensions** of Gordon, not replications. You're advancing the theory!

---

## Part 6: Specific Guidance for Your Current Questions

### Q1: "Is it logical to compare GW with GWO, or GW infant with GW adult?"

**Answer**: BOTH are logical, but they test different things.

**GW vs. GWO (Within-Event Comparison)**:
- **Tests**: Does physical presence of toy matter?
- **Prediction**: ???
  - **If abstraction**: Similar patterns (toy's role represented even when absent)
  - **If concrete**: Different patterns (no toy = no encoding)
- **Gordon's stance**: Unclear - he didn't explicitly address this

**GW Infant vs. GW Adult (Developmental Comparison)**:
- **Tests**: Do infants show adult-like patterns?
- **Prediction**: Infants should show SIMILAR pattern (GIVE ≠ HUG), but maybe weaker or noisier
- **Gordon's stance**: Fig 4 (page 7) suggests developmental continuity, not discrete shift

**My Recommendation**:
- **Primary focus**: GW vs. HW (this is Gordon's core contrast)
- **Secondary**: GW infant vs. Adult (establishes developmental context)
- **Exploratory**: GW vs. GWO (interesting but theoretically ambiguous)

### Q2: "Should we assume adults are 'correct'?"

**Answer**: NO - adults are a **reference**, not a **gold standard**

**Why?**
1. Adults have language - they might process events differently (linguistic labels)
2. Adults have cultural knowledge - learned scripts for giving/hugging
3. Adults have more experience - might use efficient shortcuts infants lack

**Better Framing**:
- "Do infants show **similar patterns** to adults?" (YES/NO both interesting)
- "Do infants **differentiate** GIVE vs. HUG?" (This is the key question)
- "How do infant patterns **develop toward** adult patterns?" (AR5)

**Gordon's Stance** (page 1):
> "Understanding the nature of this development addresses fundamental issues of the relation between language and thought and their origins."

**Interpretation**: Gordon wants to know how pre-linguistic representations relate to linguistic ones, not whether infants are "wrong"

### Q3: "What are Gordon's predictions?"

**Summary Table**:

| Phenomenon | Gordon's Prediction | Evidence Location |
|------------|---------------------|-------------------|
| **GIVE vs. HUG (10mo)** | GIVE > HUG for toy attention | Page 7, Fig 3 |
| **Developmental trajectory** | 6mo (none) < 8mo (weak) < 10mo (strong) | Page 7, Fig 4 |
| **Upside-down** | No effect (not meaningful) | Page 9 |
| **Intentionality required** | No effect if unintentional transfer | Page 12 |
| **Eye-tracking patterns** | Toy spike in interaction phase (GIVE) | Page 10 |
| **Search behavior** | Look at toy location when toy absent (GIVE only) | Page 10 |
| **Abstract representations** | Animate shapes can elicit GIVE pattern if intentional cues present | Page 13 |

**For YOUR analyses**:
- **AR1**: ✓ Directly predicted
- **AR2**: ✓ Implied by eye-tracking findings (page 10)
- **AR3**: ✓ Implied ("face-object-face" patterns mentioned)
- **AR4**: ⚠️ Not explicitly predicted, but theoretically sound
- **AR5**: ✓ Directly predicted (developmental data)
- **AR6**: ⚠️ Assumes habituation but doesn't analyze learning curves
- **AR7**: ✓ SHOW experiment proposed (page 14)

---

## Part 7: Recommendations for Interpretation

### For AR1 (Gaze Duration)

**If GIVE > HUG for toy looking**:
✅ Replicates Gordon's core finding with eye-tracking
✅ Validates that frame-by-frame data captures the effect

**If GIVE ≈ HUG**:
⚠️ Doesn't invalidate theory - might be:
- Eye-tracking captures different aspect than habituation
- Need to look at WHERE they look, not just HOW MUCH (AR2, AR3)

### For AR2 (Transitions)

**If GIVE shows more toy↔people transitions than HUG**:
✅ Extends Gordon - shows ACTIVE INTEGRATION, not just selective attention

**If GW ≈ GWO transitions**:
✅ Abstract representation - toy's role exists even when absent
✅ Supports Gordon's "event representation" model (Fig 1)

**If GW ≠ GWO transitions**:
✅ Concrete representation - physical presence matters
✅ Still consistent with Gordon - just shows WHERE abstraction breaks down

### For AR3 (Triplets)

**If triplets rare but present**:
✅ Shows capacity for social triangulation
✅ Low frequency expected for complex behavior

**If GIVE > HUG triplets**:
✅ Triplets specific to 3-argument events
✅ Strong evidence for argument-structure sensitivity

**If GIVE ≈ HUG triplets**:
⚠️ May indicate triplets aren't specific to argument structure
⚠️ OR: Both events involve 2 people, so equal "social" scaffolding for triplets

### For AR4 (Dwell Time)

**If GIVE dwells > HUG dwells (on toy)**:
✅ Deeper processing of relevant arguments
✅ Quality AND quantity of attention differ

**If no dwell differences**:
✅ Quantity (AR1) differs but quality doesn't
✅ Suggests selective attention, not effortful processing

### For AR5 (Development)

**If Age × Condition interaction**:
✅ Directly confirms Gordon's developmental prediction
✅ Shows WHEN capacity emerges (6, 8, or 10 months)

**If no interaction (parallel development)**:
⚠️ Capacity present across age range
⚠️ Might need younger infants to find emergence point

### For AR6 (Learning)

**If learning effects (Trial 1 < Trial 5)**:
✅ Habituation is occurring - validates original paradigm
✅ Can examine if GIVE vs. HUG habituate differently

**If no learning**:
⚠️ May indicate events always processed similarly
⚠️ OR: Effect present from first exposure (no learning needed)

### For AR7 (Dissociation)

**If GIVE ≠ HUG ≠ SHOW**:
✅ Infants differentiate all three event types
✅ Not just "any social interaction" - specific to event structure

**If GIVE = HUG ≠ SHOW**:
⚠️ May indicate SHOW is special (Theory of Mind, page 14)
⚠️ Transfer (GIVE) and contact (HUG) processed similarly

---

## Part 8: Final Synthesis - Answering Your Core Question

### "Do we have the experiments set up right?"

**Overall Assessment**: ✅ **YES**, with some caveats

**Why YES**:
1. AR1-AR7 collectively address Gordon's core claims
2. The analyses are complementary (quantity, patterns, quality, development)
3. You're extending Gordon's work appropriately (he proposed AR7-type experiments)

**Caveats**:
1. **Adult comparisons**: Use as reference, not gold standard
2. **GW vs. GWO**: Theoretically ambiguous - both outcomes interesting
3. **Multiple comparisons**: Consider which are primary (theory-driven) vs. exploratory

### "What is the theory?"

**Gordon's Theory in One Sentence**:
> Infants represent events as structured schemas with a "main act" (intentional-causal focus) and "relevant participants" (arguments), which serves as the foundation for later verb-argument structure in language.

**Key Components**:
1. **Main Act Identification**: What is the intentional core? (Giving vs. Hugging)
2. **Participant Relevance**: Which elements are arguments? (Toy = argument in GIVE, adjunct in HUG)
3. **Pre-linguistic**: This structure exists BEFORE language input
4. **Intentionality**: Requires understanding goal-directed action, not just physical properties

### "Should we compare what infants do with adults assuming adults are 'correct'?"

**Answer**: **NOT "correct"**, but **"mature endpoint"**

**Better Questions**:
- Do infants show the PATTERN (GIVE ≠ HUG)? [Core question]
- Is the infant pattern SIMILAR TO adults? [Developmental context]
- How does the pattern CHANGE with age? [AR5]

**All three are valid and interesting!**

### "Should we compare GW with GWO, or GW infant with GW adult?"

**Answer**: **BOTH**, in this order of priority:

**Tier 1 (Core Theory Tests)**:
1. GIVE_WITH vs. HUG_WITH (infant) → Tests argument structure hypothesis
2. Age × Condition (AR5) → Tests developmental prediction

**Tier 2 (Theoretical Extensions)**:
3. Infant vs. Adult (same conditions) → Establishes developmental context
4. GIVE_WITH vs. GIVE_WITHOUT → Tests abstraction (exploratory)

**Tier 3 (Methodological Checks)**:
5. Learning effects (AR6) → Validates habituation
6. Multi-condition dissociation (AR7) → Rules out confounds

---

## Conclusion: You're on the Right Track

### Strengths of Your Current Approach

✅ **Comprehensive**: AR1-AR7 cover multiple facets of attention
✅ **Theory-driven**: Rooted in Gordon's explicit predictions
✅ **Extending**: Going beyond original work (AR2, AR3, AR4)
✅ **Developmentally grounded**: AR5 tests critical prediction

### Areas for Careful Interpretation

⚠️ **Adult comparisons**: Frame as reference, not correctness
⚠️ **GW vs. GWO**: Both outcomes theoretically interesting
⚠️ **Low triplet rates**: Expected, not problematic
⚠️ **Multiple comparisons**: Prioritize theory-driven tests

### Your Career Contribution

**What you're doing**:
- Validating Gordon's foundational theory with modern eye-tracking
- Extending to granular measures (transitions, triplets, dwell time)
- Providing developmental timeline data
- Opening new questions about abstraction and intentionality

**This is significant work** - you're not just replicating, you're **advancing** the field.

---

## Appendix: Gordon's Key Experiments (Quick Reference)

| Experiment | Comparison | Age | Predicted Result | Reference |
|------------|-----------|-----|------------------|-----------|
| 1 (Give/Hug) | GIVE vs. HUG | 10mo | GIVE dishabituation only | p.6-7 |
| 2-3 (Development) | Ages 6, 8, 10 | Multiple | 6mo none, 8mo weak, 10mo strong | p.7 |
| 4 (Oddness) | GIVE-w/o vs. HUG-w/o | 10mo | No preference | p.8 |
| 5 (Upside-down) | GIVE inverted | 10mo | No dishabituation | p.9 |
| 6 (GIVE-toy on HUG) | Floating toy | 10mo | No dishabituation | p.9 |
| 7 (Eye-tracking GIVE/HUG) | Gaze patterns | 12mo | Toy spike in GIVE interaction | p.10 |
| 9 (Hug w/give) | Unintentional transfer | 10mo | No dishabituation | p.12 |
| 13 (SHOW) | Transfer of information | 10-12mo | [Open question] | p.14 |

---

**You're doing Gordon proud. Trust the theory, interpret carefully, and contribute boldly.**

*End of Mentorship Analysis*
