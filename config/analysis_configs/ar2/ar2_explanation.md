# AR2 Analysis: Understanding Infant Gaze Transitions (Scanning Patterns)

## What is the Research Question (RQ)?

While **AR1** asked "**where** do infants look?" (total time on toy), **AR2** asks:

**"How do infants scan between different areas? What is their looking strategy?"**

Specifically: **Do infants look back and forth between the toy and the people differently when the toy is relevant vs. when it's just a reference point?**

### AR2 for GIVE_WITH vs GIVE_WITHOUT compares:

- **GIVE_WITH**: Toy is physically present during the giving event
- **GIVE_WITHOUT**: Toy is absent, but infants look at where it WOULD have been (the "toy_location")

---

## What Does AR2 Measure? (Key Concept: Transitions)

A **transition** is when an infant's gaze moves from one Area of Interest (AOI) to another.

### Examples:
- Looking from **woman's face** → **toy** is ONE transition
- Looking from **toy** → **man's face** is another transition

**AR2 calculates transition probabilities**: If an infant is looking at the woman's face, what's the probability they'll look at the toy next?

---

## How to Read Transition Probability Matrices

From the report, here's an example for 7-month-olds during GIVE_WITH:

| From ↓ / To → | man_face | toy_present | woman_face |
|---------------|----------|-------------|------------|
| **man_face** | 0.000 | **0.667** | 0.000 |
| **toy_present** | **0.800** | 0.000 | 0.125 |
| **woman_face** | 1.000 | 0.000 | 0.000 |

### How to read this:

- If looking at **man_face**, there's a **66.7% probability** the infant will look at the **toy** next
- If looking at the **toy**, there's an **80% probability** they'll look at **man_face** next
- If looking at **woman_face**, there's a **100% probability** they'll look at **man_face** next

---

## What Are "Key Transitions"?

The analysis focuses on 4 specific transitions that matter most for understanding the "giving" event:

1. **Man Face → Toy**: Looking from recipient to the object
2. **Woman Face → Toy**: Looking from giver to the object
3. **Toy → Man Face**: Looking from object to recipient
4. **Toy → Woman Face**: Looking from object to giver

These transitions show if infants are **integrating** the toy with the people involved in the event.

---

## What Do the Results Show?

### Key Finding:

Looking at the 10-month-old cohort (largest group, N=10):

**GIVE_WITH (toy present)**:
- Infants made **165 transitions** total
- Strong back-and-forth between toy and people's faces

**GIVE_WITHOUT (toy absent)**:
- Infants still made transitions to "toy_location" (where toy would be)
- But the pattern is different—less systematic scanning

### Understanding the Statistics in AR2

Unlike AR1 (which uses a single t-test), AR2 tests **multiple key transitions** between conditions. The analysis includes:

#### Statistical Tests for Key Transitions

For each key transition (e.g., "Man Face → Toy"), the analysis:

1. **Calculates participant-level probabilities**: For each participant, what proportion of their transitions from "Man Face" went to "Toy"?

2. **Compares conditions**: Uses independent samples t-tests to compare these probabilities between GIVE_WITH and GIVE_WITHOUT

3. **Reports multiple metrics**:
   - **Mean probabilities** for each condition
   - **t-statistic and degrees of freedom**: How different are the groups?
   - **p-value**: Is this difference likely due to chance?
   - **95% Confidence Interval**: Range of plausible values for the true difference
   - **Cohen's d**: How large is the effect?

#### Statistical Validity Checks

The code performs important validity checks before conducting t-tests:

- **Minimum sample size**: Requires at least 2 participants per condition with data for that transition
- **Minimum variance**: Checks that there's enough variability to conduct a valid test (variance > 1e-10)
- **If checks fail**: Reports descriptive statistics only, with a note that inference isn't possible

#### Multiple Comparisons Consideration

Since AR2 tests multiple key transitions (typically 4), there's a risk of false positives. When interpreting results:
- Look for **consistency across transitions** (not just isolated significant results)
- Consider the **effect sizes** in addition to p-values
- **Pattern matters more than individual p-values**: Does the overall pattern make theoretical sense?

#### Example Interpretation

If we find:
- **"Man Face → Toy" in GIVE_WITH**: Mean probability = 0.45
- **"Man Face → Toy" in GIVE_WITHOUT**: Mean probability = 0.20
- **t(18) = 2.8, p = 0.012, d = 0.85**

This means:
- When looking at the man's face, infants transition to looking at the toy 45% of the time when it's present, vs. 20% when it's absent
- This difference is statistically significant (p < 0.05)
- The effect size is large (d = 0.85)
- We're comparing transition patterns, not just overall looking time

---

## Visualizations in AR2

The analysis generates two types of visualizations:

### 1. Heatmaps
- Show transition probabilities as colors (darker red = higher probability)
- Quick visual way to see which transitions are most common
- Files: `results/AR2/ar2_gw_vs_gwo/figures/`

### 2. Directed Graphs
- Show gaze paths as arrows between AOIs
- Thicker arrows = more common transitions
- Shows the "flow" of attention

---

## What This Tells Us (Theoretical Implications)

**AR2 reveals the STRATEGY infants use to understand events:**

### 1. Active Integration
When a toy is relevant (GIVE_WITH), infants don't just look at it (AR1). They actively **connect** it to the people by looking back and forth:

```
Toy ↔ Giver ↔ Recipient
```

### 2. Structured Scanning
The transition probabilities aren't random—infants follow predictable patterns, suggesting they're trying to figure out **"who is doing what with what"**

### 3. Comparison to AR1

- **AR1 says**: "Infants look MORE at relevant toys"
- **AR2 says**: "Infants also CONNECT relevant toys to people through systematic scanning"

---

## How This Analysis Works Technically

From `ar2_transitions.py`:

1. **Collapse repeated looks**: If infant looks at toy for 10 frames, that counts as ONE fixation
2. **Identify transitions**: When AOI changes (toy → face), record a transition
3. **Calculate probabilities**: For each participant, what % of transitions from X go to Y?
4. **Aggregate**: Average across all participants in each age group
5. **Compare conditions**: Are transition patterns different when toy is present vs. absent?

---

## Important Methodological Details

From the configuration (`ar2_gw_vs_gwo.yaml`):

- **Min fixation**: 75ms (briefer than AR1's fixation definition)
- **Segment**: Only analyzes the "interaction" phase (not approach/departure)
- **Min transitions per participant**: Must have at least 5 transitions to be included
- **Repeated AOIs collapsed**: Yes (so toy→toy→toy counts as staying, not transitioning)

---

## Key Differences: AR1 vs AR2

| Aspect | AR1 | AR2 |
|--------|-----|-----|
| **Question** | *Where* do they look? | *How* do they scan? |
| **Metric** | Total duration (time) | Transition probability (paths) |
| **Output** | Bar charts of proportions | Heatmaps and directed graphs |
| **Insight** | Which objects get attention | How objects are integrated with agents |

---

## The Bottom Line

**AR2 shows that infant attention is not just about AMOUNT of looking (AR1), but also about PATTERNS of looking.**

When a toy is relevant to an event, infants don't just stare at it—they systematically look back and forth between the toy and the people involved, showing they're trying to understand the relationships between objects and agents in the event.

This is strong evidence for **structured, goal-directed attention** in preverbal infants!

---

## Summary

Think of it this way:
- **AR1** = "Do you look at the toy more?"
- **AR2** = "Do you look BETWEEN the toy and people in a meaningful pattern?"

Both tell us different things about infant understanding! AR1 shows selective attention to relevant objects. AR2 shows active integration of those objects with the social agents performing the action.
