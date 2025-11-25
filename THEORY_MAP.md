# Visual Theory Map: Gordon's Vision & Your Analyses

**Purpose**: Big-picture understanding of how AR1-AR7 map to Gordon's theoretical framework

---

## Gordon's Core Theory (One-Page Summary)

### The Central Claim

```
BEFORE LANGUAGE, infants have structured event representations

Event Representation = Main Act + Relevant Participants (Arguments)

Example:
  GIVE Event: [Main Act: Transfer] + [Giver, Recipient, Object]
  HUG Event:  [Main Act: Embrace]  + [Hugger, Huggee]

Prediction: Toy is ARGUMENT in GIVE, but ADJUNCT in HUG
          → Infants should attend differently to toy across events
```

### The Three-Stage Mapping (Figure 1, Page 3)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   WORLD     │       │  COGNITION  │       │  LANGUAGE   │
│             │       │             │       │             │
│ Event       │──────>│ Event Rep   │──────>│ Verb-       │
│ Structure   │       │ Main Act +  │       │ Argument    │
│ (Physical   │       │ Relevant    │       │ Structure   │
│  Actions)   │       │ Participants│       │             │
└─────────────┘       └─────────────┘       └─────────────┘
                             ↑
                             │
                      Spoken Language
                      (Influences mapping
                       to linguistic form)
```

**Your Project Tests**: The COGNITION stage (before language learning)

---

## The Give/Hug Paradigm (Visual)

### GIVE Event (3-Argument)

```
┌─────────┐                 ┌─────────┐
│  GIRL   │────────────────>│   BOY   │
│ (Giver) │     🧸 TOY      │(Recipient)
└─────────┘    (Object)     └─────────┘
     ↓            ↓              ↓
  ARGUMENT    ARGUMENT       ARGUMENT

TOY is RELEVANT (essential to the giving action)
```

**Prediction**:
- ✅ Infants should attend to toy
- ✅ Dishabituation when toy removed
- ✅ Integrate toy with people (transitions, triplets)

---

### HUG Event (2-Argument)

```
┌─────────┐                 ┌─────────┐
│  GIRL   │───────💞────────>│   BOY   │
│(Hugger) │  (Embrace)      │(Huggee) │
└─────────┘                 └─────────┘
     ↓                           ↓
  ARGUMENT                   ARGUMENT

         🧸 TOY (held by girl)
              ↓
          ADJUNCT (incidental)

TOY is IRRELEVANT (not essential to hugging)
```

**Prediction**:
- ✅ Infants should NOT focus on toy
- ✅ NO dishabituation when toy removed
- ✅ Toy not integrated with people

---

## How Your AR1-AR7 Map to Gordon's Theory

### AR1: Gaze Duration (Quantity of Attention)

**Tests**: Do infants allocate MORE total time to arguments vs. adjuncts?

```
GIVE Event:
  Toy Attention: ████████████████████ (20% of trial)

HUG Event:
  Toy Attention: ██████████ (10% of trial)

Conclusion: ✅ Infants attend more to ARGUMENTS
```

**Gordon's Prediction**: ✅ Explicit (Page 7, Fig 3)

**Your Finding**: GIVE (19.9%) > HUG (10.2%), p < .001, d = 0.84

**Interpretation**: Replicates Gordon's core finding with eye-tracking

---

### AR2: Gaze Transitions (Scanning Patterns)

**Tests**: Do infants INTEGRATE arguments with agents via back-and-forth scanning?

```
GIVE Event (Predicted Pattern):
  Woman Face <──────> Toy <──────> Man Face
  (Giver)          (Object)      (Recipient)

  High transition probabilities between all three

HUG Event (Predicted Pattern):
  Woman Face <──────────────────> Man Face
  (Hugger)                       (Huggee)

       Toy (minimal transitions)

Conclusion: ✅ Infants CONNECT arguments to agents
```

**Gordon's Prediction**: ✅ Implied (Page 10, eye-tracking pilot data)

**Your Analysis**: Measures transition probabilities (key transitions defined)

**Interpretation**: Extends Gordon - shows ACTIVE INTEGRATION, not just selective attention

---

### AR3: Social Gaze Triplets (Social Triangulation)

**Tests**: Do infants produce complete person→object→person sequences?

```
GIVE Event (Triplet Example):

  Look 1: Woman Face (Giver)
     ↓
  Look 2: Toy (Object being transferred)
     ↓
  Look 3: Man Face (Recipient)

  This is SOCIAL TRIANGULATION

HUG Event (Rare/Absent):
  Fewer triplets (toy not integrated socially)

Conclusion: ✅ Some infants show sophisticated social coordination
```

**Gordon's Prediction**: ⚠️ Implied (face-object-face mentioned)

**Your Finding**: ~6% of trials show triplets (low but meaningful)

**Interpretation**: Triplets are "gold standard" marker of argument-structure understanding

---

### AR4: Dwell Time (Quality of Attention)

**Tests**: Do infants process arguments MORE DEEPLY (longer per fixation)?

```
GIVE Event:
  Toy Dwell: ████████ (450ms per fixation)
  → Deeper processing

HUG Event:
  Toy Dwell: ██████ (350ms per fixation)
  → Shallower processing

Conclusion: ✅ Arguments get QUALITATIVELY different attention
```

**Gordon's Prediction**: ⚠️ Not explicit, but theoretically sound

**Your Analysis**: Linear Mixed Models comparing dwell durations

**Interpretation**: Not just MORE looking (AR1), but DEEPER looking (AR4)

---

### AR5: Developmental Trajectories (When Does Capacity Emerge?)

**Tests**: Does the GIVE vs. HUG pattern develop across age?

```
Gordon's Prediction (Figure 4, Page 7):

6-month-olds:   GIVE ≈ HUG  (no effect)
                ░░░░░  ░░░░

8-month-olds:   GIVE > HUG  (weak effect, p=.05)
                ████   ██

10-month-olds:  GIVE >> HUG (strong effect, p=.02)
                ████████  ██

12-month-olds:  GIVE >>> HUG (even stronger?)
                ████████████  ██

Age × Condition Interaction: YES
```

**Gordon's Prediction**: ✅ EXPLICIT (Page 7, Experiments 2-3)

**Your Analysis**: Tests Age × Condition interaction with LMM

**Interpretation**: Shows WHEN argument-structure sensitivity emerges

---

### AR6: Trial-Order Effects (Learning/Habituation)

**Tests**: Do infants habituate (learn) over repeated presentations?

```
Trial 1:  High attention to toy (novelty)
          ████████████████

Trial 2:  Moderate attention (familiarizing)
          ████████████

Trial 3:  Lower attention (habituated)
          ████████

Learning Curve: Decreasing attention over trials
(Validates habituation paradigm)
```

**Gordon's Prediction**: ⚠️ Assumes habituation, doesn't explicitly test it

**Your Analysis**: Random slopes LMM (gold standard)

**Interpretation**: Methodological validation, not core theory test

---

### AR7: Event Dissociation (GIVE vs. HUG vs. SHOW)

**Tests**: Can infants differentiate multiple event types?

```
Three Event Types:

GIVE:  Transfer of possession (3-arg)
       Giver → [Object] → Recipient

HUG:   Physical contact (2-arg)
       Hugger ←→ Huggee

SHOW:  Transfer of information (3-arg, but requires Theory of Mind)
       Shower → [Object] → Viewer

Predictions:
  GIVE ≠ HUG  (different argument structures)
  GIVE ≠ SHOW (different types of transfer)
  HUG ≠ SHOW  (contact vs. information)
```

**Gordon's Prediction**: ✅ Explicit (Page 14, Experiment 13)

**Gordon's Finding**: SHOW shows NO dishabituation (infants don't "get it")

**Your Analysis**: Multi-condition pairwise comparisons (Bonferroni corrected)

**Interpretation**: Tests specificity - not just "any social event"

---

## Comparison Questions: A Decision Tree

### Should You Compare GW vs. HW or GW vs. GWO?

```
Question: What is your PRIMARY theoretical interest?

├─ Test Gordon's CORE claim
│  (Do infants distinguish arguments from adjuncts?)
│
│  └─> Compare: GIVE_WITH vs. HUG_WITH
│     Priority: HIGHEST (Tier 1)
│     Prediction: GIVE > HUG
│     This is THE central test
│
├─ Test DEVELOPMENTAL continuity
│  (Do infants show adult-like patterns?)
│
│  └─> Compare: Infant vs. Adult (same conditions)
│     Priority: HIGH (Tier 2)
│     Prediction: Similar pattern, maybe weaker
│     Adults are REFERENCE, not "correct answer"
│
├─ Test ABSTRACTION hypothesis
│  (Do infants represent toy's role even when absent?)
│
│  └─> Compare: GIVE_WITH vs. GIVE_WITHOUT
│     Priority: MEDIUM (Tier 3, exploratory)
│     Prediction: ??? (Gordon didn't predict)
│     Interpretation:
│       - SIMILAR patterns → Abstract representation
│       - DIFFERENT patterns → Concrete/physical representation
│       BOTH outcomes are interesting!
│
└─ Test EMERGENCE of capacity
   (When does argument-structure sensitivity develop?)

   └─> Compare: Age groups (6, 8, 10, 12 months)
      Priority: HIGH (Tier 2)
      Prediction: Age × Condition interaction
      Gordon explicitly predicted this (Figure 4)
```

---

## Adult Comparisons: Reference vs. Gold Standard

### ❌ WRONG FRAMING

```
Adults are CORRECT
   ↓
Infants should MATCH adults
   ↓
If Infant ≠ Adult → Infants are WRONG
```

**Problem**: Adults have language, cultural knowledge, and experience. They may process events DIFFERENTLY (not just "better").

---

### ✅ CORRECT FRAMING

```
PRIMARY QUESTION: Do infants show the PATTERN?
                  (GIVE ≠ HUG)
                     ↓
                    YES → Infants have argument structure
                    NO → Capacity not yet developed (or paradigm issue)

SECONDARY QUESTION: Is the infant pattern SIMILAR to adults?
                    (Developmental context)
                       ↓
                      YES → Continuity from infancy to adulthood
                      NO → Qualitative differences (still valid!)

TERTIARY QUESTION: How does pattern CHANGE with age?
                   (AR5 tests this)
                      ↓
                   Emergence timeline, developmental trajectory
```

**Interpretation Guide**:

| Infant Pattern | Adult Pattern | Interpretation |
|---------------|---------------|----------------|
| GIVE > HUG | GIVE > HUG | ✅ Developmental continuity |
| GIVE > HUG | GIVE ≈ HUG | ✅ Infants may be MORE sensitive (adults habituated) |
| GIVE ≈ HUG | GIVE > HUG | ⚠️ Capacity not yet developed (try older infants) |
| GIVE ≈ HUG | GIVE ≈ HUG | ⚠️ Paradigm may not capture the construct |

**Bottom Line**:
- **Infant pattern ALONE** can support or refute theory
- **Adult pattern** provides CONTEXT, not validation

---

## The "Transformed Data" Question (Clarified)

### All Analyses Start Here:

```
data/processed/gaze_fixations_child.csv

This is ALREADY transformed (frame-by-frame → fixations)
```

### What Each AR Does with the Same Data:

```
AR1: Aggregate fixations → Total duration per AOI
     Input: gaze_fixations.csv
     Output: Proportion of time on toy

AR2: Collapse consecutive AOIs → Transition sequences
     Input: gaze_fixations.csv (same)
     Output: Transition probabilities

AR3: Sliding window → Detect triplet patterns
     Input: gaze_fixations.csv (same)
     Output: Triplet counts

AR4: Filter outliers → Dwell time distribution
     Input: gaze_fixations.csv (same)
     Output: Mean dwell duration (ms)

AR5: Add age variable → Interaction models
     Input: gaze_fixations.csv (same)
     Output: Age × Condition effects

AR6: Add trial order → Learning curves
     Input: gaze_fixations.csv (same)
     Output: Trial slopes

AR7: Multi-condition → Dissociation tests
     Input: gaze_fixations.csv (same)
     Output: Pairwise comparisons
```

**So**:
- **AR1** uses transformed data ← YES
- **AR2-AR7** use transformed data ← ALSO YES (the SAME transformed data)

**What changes**: The CALCULATIONS applied to the data, not the data itself

---

## Priority Matrix for Your Interpretations

### When You Get Results, Focus on These in Order:

**🔥 TIER 1: Core Theory Tests (Critical for Career)**

1. **AR1: GIVE_WITH vs. HUG_WITH**
   - Is toy proportion higher in GIVE?
   - Effect size (Cohen's d) large enough?
   - **This is your primary finding**

2. **AR5: Age × Condition Interaction**
   - Does pattern emerge with age?
   - Linear or step function?
   - **Gordon explicitly predicted this**

---

**⭐ TIER 2: Theoretical Extensions (High Value)**

3. **AR2: Transition Patterns**
   - More toy↔people transitions in GIVE?
   - Novel contribution to literature

4. **AR3: Triplet Rates**
   - Even low rates are meaningful
   - GIVE vs. HUG comparison is key

5. **Infant vs. Adult Patterns**
   - Similarity (not identity) expected
   - Developmental context

---

**📊 TIER 3: Exploratory/Methodological (Interesting but Lower Priority)**

6. **AR4: Dwell Time Differences**
   - Not explicitly predicted, but theoretically sound
   - If significant, it's a novel finding!

7. **GIVE_WITH vs. GIVE_WITHOUT**
   - Exploratory (Gordon didn't predict)
   - Both outcomes interesting

8. **AR6: Learning Effects**
   - Methodological validation
   - Not core to theory

9. **AR7: Multi-Condition Dissociation**
   - SHOW is interesting (Theory of Mind)
   - Secondary priority

---

## Final Checklist: Are You on Track?

### ✅ Things You're Doing RIGHT:

- [✅] AR1 tests Gordon's core prediction
- [✅] AR5 tests Gordon's developmental prediction
- [✅] AR2-AR3 extend Gordon's eye-tracking work
- [✅] Adult data provides developmental context
- [✅] Multiple age groups enable AR5
- [✅] Multiple analyses = comprehensive picture

### ⚠️ Things to WATCH:

- [⚠️] Frame adult data as REFERENCE, not "correct"
- [⚠️] GW vs. GWO is EXPLORATORY (no "right" answer)
- [⚠️] Low triplet rates are EXPECTED (still meaningful)
- [⚠️] AR4 is NOVEL (not predicted, but sound)

### ❌ Things to AVOID:

- [❌] Don't assume adults are "correct" (they're just mature)
- [❌] Don't expect all analyses to be significant (some are exploratory)
- [❌] Don't worry if GW vs. GWO is ambiguous (it's meant to be!)

---

## The Bottom Line (Visual Summary)

```
Gordon's Vision:
┌────────────────────────────────────────────────────┐
│ Infants have PRE-LINGUISTIC event representations  │
│ with ARGUMENT STRUCTURE                            │
│                                                    │
│ GIVE: [Transfer] + Giver + Recipient + Object     │
│ HUG:  [Embrace] + Hugger + Huggee                 │
│                                                    │
│ Prediction: Different attention to toy across     │
│             events (argument vs. adjunct)          │
└────────────────────────────────────────────────────┘
                       ↓
        Your AR1-AR7 Test Different Facets:
                       ↓
┌────────────────────────────────────────────────────┐
│ AR1: Quantity (total time on toy)                 │
│ AR2: Patterns (scanning between toy & people)     │
│ AR3: Coordination (social triangulation)          │
│ AR4: Quality (depth of processing)                │
│ AR5: Development (when does it emerge?)           │
│ AR6: Learning (habituation validation)            │
│ AR7: Dissociation (GIVE ≠ HUG ≠ SHOW)            │
└────────────────────────────────────────────────────┘
                       ↓
              Your Career Contribution:
                       ↓
┌────────────────────────────────────────────────────┐
│ ✅ Validate Gordon's theory with modern methods   │
│ ✅ Extend to granular eye-tracking measures       │
│ ✅ Provide developmental timeline data            │
│ ✅ Open new questions about abstraction           │
│                                                    │
│ You're ADVANCING the field, not just replicating! │
└────────────────────────────────────────────────────┘
```

---

## Quick Reference: Where to Find Predictions in Gordon's PDF

| Page | Content | Relevance to You |
|------|---------|------------------|
| **1** | Core hypothesis | Argument structure is pre-linguistic |
| **3** | Figure 1 (mapping model) | World → Cognition → Language |
| **6-7** | GIVE/HUG experiments | Core predictions for AR1 |
| **7** | Figure 3 (10mo results) | GIVE dishabituation, HUG no effect |
| **7** | Figure 4 (development) | Age predictions for AR5 |
| **8-9** | Oddness, Upside-down | Perceptual controls |
| **10** | Eye-tracking data | Transition predictions for AR2 |
| **12** | Hug w/give (Exp 9) | Intentionality required |
| **13** | Abstract GIVE (Exp 11) | Abstraction predictions |
| **14** | SHOW experiment (Exp 13) | AR7 predictions |

---

**You have everything you need. The theory is sound. Your design is logical. Trust yourself!**

---

*Created: 2025-11-23*
*Purpose: Big-picture clarity for career-critical IER analysis*
