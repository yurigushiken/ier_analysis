# AR1 Analysis: Understanding Infant Attention to Objects

## What is the Research Question (RQ)?

The fundamental question is: **Do infants understand which objects are important vs. incidental in an event?**

Specifically for the **GIVE_WITH vs HUG_WITH** comparison:
- **GIVE_WITH**: A person gives a toy to another person (toy is essential to the event)
- **HUG_WITH**: A person hugs another person while a toy is present (toy is incidental/unimportant)

**Hypothesis**: If infants understand event structure, they should look **more** at the toy during GIVE events (where it matters) than during HUG events (where it doesn't matter).

---

## What Does This Analysis Measure?

The analysis calculates the **proportion of looking time** spent on the toy:

```
Proportion = (Time looking at toy) / (Total time looking at screen)
```

### Example:
- If a baby looks at the screen for 10 seconds total during a trial
- And spends 2 seconds looking at the toy
- The proportion = 2/10 = **0.20 or 20%**

---

## What Do The Results Show?

### Main Finding (from ar1_gw_vs_hw):

| Condition | Mean Toy Proportion | Sample Size |
|-----------|---------------------|-------------|
| GIVE_WITH | 0.199 (19.9%) | 46 infants |
| HUG_WITH | 0.102 (10.2%) | 46 infants |

**Infants looked at the toy almost TWICE as much during GIVE events (20%) compared to HUG events (10%)!**

---

## Is This Difference Statistically Significant?

**YES!** The statistics show:

- **t-test**: t(88.6) = 4.03
- **p-value**: p < 0.001 (highly significant)
- **Effect size (Cohen's d)**: 0.84 (large effect)
- **95% Confidence Interval**: [0.049, 0.144]

### What does this mean?

#### Understanding the t-test
The **t-statistic** of 4.03 with 88.6 degrees of freedom tells us how many standard errors the two group means are apart. The larger the t-value, the more evidence against the null hypothesis (which states there's no difference between groups).

#### Understanding the p-value
- **p < 0.001**: There's less than 0.1% chance this difference happened by accident (if the null hypothesis were true)
- This is well below the standard threshold of p < 0.05
- In statistical terms: We reject the null hypothesis and conclude there IS a real difference between conditions
- **Important**: This doesn't tell us HOW BIG the effect is, just that it's unlikely to be due to chance

#### Understanding Effect Size (Cohen's d)
- **Cohen's d = 0.84**: This quantifies the magnitude of the difference in standardized units
- **Interpretation guidelines**:
  - Small effect: d ≈ 0.2
  - Medium effect: d ≈ 0.5
  - Large effect: d ≈ 0.8 or greater
- Our d = 0.84 is considered a **large effect**, meaning the difference is not only statistically significant but also practically meaningful
- This tells us the groups differ by about 0.84 standard deviations

#### Understanding the Confidence Interval
- **95% CI: [0.049, 0.144]**: We're 95% confident the true difference in proportions lies between 4.9% and 14.4%
- This is calculated from the observed data and sampling variability
- The fact that the entire interval is above 0 further confirms the effect is real (doesn't include "no difference")
- The width of the interval reflects our uncertainty—narrower intervals mean more precise estimates

#### Degrees of Freedom
- **df = 88.6**: This is a Welch-Satterthwaite approximation used when the two groups have unequal variances
- Roughly reflects the sample size: With 46 participants per condition, we have 92 total observations
- Higher df generally means more reliable estimates

---

## What Does This Tell Us?

### Interpretation:

Even pre-linguistic infants (8-12 months old) already understand that:
- The toy is **important** in a "giving" event � they look at it more
- The toy is **not important** in a "hugging" event � they look at it less

This supports the theory that infants have an innate understanding of **"verb-argument structure"** - they know which objects are essential to different types of actions, even before they can talk!

---

## Age Differences

The analysis also tested whether this pattern differs by age:

| Age Group | N | Mean Proportion |
|-----------|---|-----------------|
| 8-month-olds | 26 | 17.6% |
| 12-month-olds | 11 | 13.8% |

**ANOVA results**: F(2, 45) = 2.37, p = 0.105 (not significant)

### Understanding the ANOVA

#### What is ANOVA?
**ANOVA** (Analysis of Variance) tests whether means differ across **more than two groups**. While the t-test compares two conditions (GIVE vs HUG), ANOVA compares multiple age groups simultaneously.

#### Interpreting the F-statistic
- **F(2, 45) = 2.37**: The F-statistic compares variation between age groups to variation within age groups
  - **First number (2)**: Degrees of freedom between groups (3 age groups - 1)
  - **Second number (45)**: Degrees of freedom within groups (48 total participants - 3 groups)
  - Larger F-values indicate bigger differences between groups relative to within-group variability

#### Interpreting the p-value
- **p = 0.105**: There's about a 10.5% probability we'd see age differences this large (or larger) if there were truly no age effect
- This is **above** the conventional α = 0.05 threshold, so we fail to reject the null hypothesis
- **Conclusion**: No strong evidence that toy-looking proportions differ systematically across age groups in this sample

#### Effect Size: Eta-squared
The analysis also calculates **eta-squared (η²)**, which indicates what proportion of total variance is explained by age group:
- η² = 0.095 (from the results)
- This means age group accounts for about 9.5% of the variance in toy-looking proportions
- By convention: η² ≈ 0.01 (small), 0.06 (medium), 0.14 (large)
- Our η² = 0.095 is between small and medium, suggesting age has a modest but not statistically significant effect

#### Why might age differences not be significant?
1. **Sample size**: Some age groups have relatively few participants (e.g., N=11 for 12-month-olds)
2. **High variability**: Individual differences within age groups may be large
3. **True lack of effect**: The phenomenon may be present across the entire 8-12 month age range
4. **Averaging across conditions**: This ANOVA averages GIVE and HUG together; age might interact with condition type

---

## How This Analysis Works

From the code (`ar1_gaze_duration.py`):

1. **Load gaze fixations**: Read pre-processed data with fixation durations per AOI
2. **Filter by condition**: Select only trials for comparison conditions (e.g., GIVE_WITH vs HUG_WITH)
3. **Calculate trial proportions**: For each trial, compute toy duration / total duration
4. **Aggregate by participant**: Average across trials for each participant
5. **Aggregate by condition**: Average across participants for each condition
6. **Statistical testing**: Compare conditions using t-test and ANOVA for age effects

---

## Important Methodological Details

### Gaze Fixation Definition
A **gaze fixation** is 3 or more consecutive frames where the infant's gaze remains on the same Area of Interest (AOI). This conservative threshold ensures brief, transient fixations aren't counted as sustained attention.

### Toy AOIs Included
- `toy_present`: When toy is physically visible
- `toy_location`: Where toy would be (in WITHOUT conditions)

### Statistical Tests
- **Independent samples t-test**: Comparing mean toy-looking proportion between conditions
- **One-way ANOVA**: Testing age-group differences within the primary cohort
- **Significance threshold**: � = 0.05
- **Effect size**: Cohen's d for t-tests, eta-squared for ANOVA

---

## AR1 Variants

The pipeline supports multiple AR1 comparisons:

| Variant | Comparison | Purpose |
|---------|------------|---------|
| `ar1_gw_vs_hw` | GIVE_WITH vs HUG_WITH | Main comparison: relevant vs. incidental toy |
| `ar1_gw_vs_gwo` | GIVE_WITH vs GIVE_WITHOUT | Does physical presence matter? |
| `ar1_gwo_vs_hwo` | GIVE_WITHOUT vs HUG_WITHOUT | Relevance even when toy is absent? |
| `ar1_hw_vs_hwo` | HUG_WITH vs HUG_WITHOUT | Looking at incidental toy vs. its location |

---

## The Bottom Line

This analysis provides strong evidence that infants as young as 8 months can distinguish between objects that are essential to an action (like a toy in "giving") versus objects that are merely present (like a toy during "hugging").

This is a fundamental building block for understanding language and events!

---

## Connection to Gordon (2003)

This work builds on Peter Gordon's foundational research showing that infants understand argument structure. Our high-resolution eye-tracking data allows us to move beyond **if** they looked, to understand **how** and **where** they lookedproviding much richer insights into their cognitive processes.
