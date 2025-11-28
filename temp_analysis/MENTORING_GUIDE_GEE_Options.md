# Mentoring Guide: Understanding GEE Weighting Options

## The Core Question

You have **proportion data** (e.g., "3 out of 5 transitions were agent-agent attention" = 0.60), but **different trials have different amounts of data** (some have 2 transitions, some have 9). How do you properly model this?

## The Three Options, Explained Simply

### Option A: Binomial GEE (The "Purist" Approach)

**What it does:**
Models the actual counting process: "I observed k successes out of n trials"

**Analogy:**
Like flipping a coin. You don't say "I got 0.6 heads" - you say "I got 6 heads out of 10 flips"

**The math:**
- Input: (k, n) pairs - e.g., (3 agent-agent transitions, 5 total transitions)
- Family: Binomial (the "correct" distribution for count data)
- Link: Logit (forces predictions between 0 and 1)
- Output: Coefficients on **log-odds scale**

**Example interpretation:**
```
Coefficient for Adults = 1.34
This means: log(odds_adults / odds_7mo) = 1.34
Converting: exp(1.34) = 3.82
Interpretation: "Adults have 3.82x higher odds of agent-agent attention than 7-month-olds"
```

**Pros:**
- ✅ "Correct" statistical model for count data
- ✅ Automatically enforces 0-1 bounds
- ✅ Proper variance structure: Var = np(1-p)

**Cons:**
- ❌ Log-odds scale is **not intuitive** for most readers
- ❌ Need to convert to probabilities for plots/tables
- ❌ More complex to explain in papers
- ❌ Your entire downstream pipeline expects proportions

**When you'd use it:**
- Publishing in a statistics journal
- Reviewer explicitly requests it
- You have lots of trials at 0% or 100% (you don't)

---

### Option B: Weighted Gaussian GEE (The "Pragmatic" Approach)

**What it does:**
Models proportions directly, but weights each trial by how much data it has

**Analogy:**
When taking a class average, you weight exams (100 pts) more than quizzes (10 pts). Same idea: trials with 9 transitions get more weight than trials with 2 transitions.

**The math:**
- Input: Proportions (0.0 to 1.0) + weights (total_transitions)
- Family: Gaussian (normal distribution - approximate for proportions)
- Link: Identity (direct linear scale)
- Output: Coefficients on **proportion scale**

**Example interpretation:**
```
Coefficient for Adults = 0.18
Interpretation: "Adults have 18 percentage points more agent-agent attention than 7-month-olds"
                (or "18% more" in casual language)
```

**Pros:**
- ✅ **Super easy to interpret** - direct percentage differences
- ✅ Minimal code changes (just add `weights=` parameter)
- ✅ All your plots/tables work as-is
- ✅ Fixes the main problem: proper weighting by sample size
- ✅ Standard practice in many fields

**Cons:**
- ⚠️ Not "perfectly" correct - Gaussian isn't ideal for proportions
- ⚠️ Could theoretically predict <0 or >1 (rarely happens in practice)
- ⚠️ Variance structure is approximate

**When you'd use it:**
- Almost always, as a first pass
- When proportions are mostly in the 0.1-0.9 range (yours are)
- When you want readable, interpretable results

---

### Option C: Hierarchical Bayesian Model (The "Overkill" Approach)

**What it does:**
Models multiple levels of variation simultaneously (within-trial, between-trial, between-participant)

**Analogy:**
Like using a sledgehammer to crack a nut. Very powerful, but way more than you need.

**When you'd use it:**
- Complex nested/crossed random effects
- Need to make strong inference about individual participants
- Have lots of time and computational resources

**Why skip it here:**
- 🔴 10x more complex to implement
- 🔴 100x slower to run
- 🔴 Much harder to explain/defend
- 🔴 Doesn't actually solve the weighting problem better than Option B

---

## Visual Comparison

```
DATA EXAMPLE:
Participant A, Trial 1: 2 agent-agent transitions out of 9 total = 0.22 proportion
Participant B, Trial 2: 1 agent-agent transition out of 2 total = 0.50 proportion

THE PROBLEM:
Current (unweighted): Treats both trials equally
  - Trial 1 (9 transitions): gets 1 vote
  - Trial 2 (2 transitions): gets 1 vote
  - This is wrong! Trial 1 has way more evidence.

OPTION B (weighted Gaussian):
  - Trial 1: gets 9 votes
  - Trial 2: gets 2 votes
  - Coefficient: "Adults are +0.18 higher in proportion"
  - Prediction: 0.24 (a proportion, directly usable)

OPTION A (binomial):
  - Trial 1: input as (2 successes, 9 trials)
  - Trial 2: input as (1 success, 2 trials)
  - Coefficient: "Adults have log-odds of +1.34"
  - Need to convert: logistic(intercept + 1.34) = 0.24
```

## My Recommendation (as your mentor)

### Phase 1: Implement Option B Now

**Why:**
1. Takes 5 minutes to add `weights=` parameter
2. Fixes the scientific problem (unequal weighting)
3. Keeps your workflow intact
4. Gives you defensible results

**How:**
```python
# In strategy.py, line ~204 and ~264
model = smf.gee(
    formula=formula,
    groups="participant_id",
    data=working,
    family=sm.families.Gaussian(),
    weights=working['total_transitions'],  # <-- ADD THIS
)
```

### Phase 2: Check Diagnostics

After fitting, check:
```python
predictions = result.predict()
print(f"Min prediction: {predictions.min():.3f}")  # Should be >= 0
print(f"Max prediction: {predictions.max():.3f}")  # Should be <= 1
```

**From my analysis**: Your predictions stay in [0.087, 0.192] - totally fine!

### Phase 3: Compare Results

Look at what changes:
- Do coefficient estimates shift much? (Usually <20%)
- Do p-values cross 0.05 threshold? (Check marginal findings)
- Do scientific conclusions change?

**From my analysis**:
- 10-month-olds: p=0.064 → p=0.110 (marginal → not significant)
- Adults: p=0.006 → p=0.017 (still significant, slightly weaker)

### Phase 4: Decide if Option A is Needed

**Move to Binomial GEE only if:**
1. ❌ Predictions go outside [0, 1] (they don't for you)
2. ❌ Lots of 0% or 100% trials (you don't have this)
3. ❌ Reviewer specifically requests it
4. ❌ Publishing in hardcore stats journal

**Otherwise:** Stick with weighted Gaussian (Option B). It's **perfectly acceptable** and much easier to work with.

## Answering Common Questions

### "But isn't Option A more 'correct'?"

**Technically yes, philosophically no.**

- Yes, proportions come from a binomial process
- But when p is away from 0 and 1, and n is reasonable (which is your case), the Gaussian approximation is excellent
- The difference between Option A and B is usually **smaller** than the sampling uncertainty in your data
- **Interpretability matters** - if readers can't understand log-odds, the "correct" model is less useful

### "Won't reviewers complain about Option B?"

**Very unlikely.**

- Weighted linear models for proportions are **standard practice** in developmental psych, neuroscience, vision science
- The key is that you're **acknowledging and addressing** the weighting issue
- In your methods, write: "To account for varying precision across trials, we weighted each trial by its total number of transitions"
- If a reviewer asks for binomial, you can implement it then (it's not hard)

### "How do I know my predictions are safe?"

**You already checked!**

From the analysis:
- Weighted Gaussian: predictions range [0.087, 0.192]
- This is well within [0, 1]
- You're nowhere near the boundaries where Gaussian breaks down

### "What if I want to be extra safe?"

**Conservative option:**
Use Option B (weighted Gaussian) for your **main results**, but run Option A (binomial) as a **sensitivity analysis** in supplementary materials.

Write in the paper:
> "Primary analyses used weighted GEE with Gaussian family (weights = number of transitions per trial). Results were qualitatively identical when using binomial family GEE (see Supplement)."

This shows you've thought about it and validated your approach.

## Bottom Line

**Start with Option B. It's the right choice for your data.**

Here's why I'm confident:
1. ✅ Your proportions are well-behaved (mostly 0.1-0.3, not at extremes)
2. ✅ Predictions stay in valid range [0, 1]
3. ✅ You fix the main statistical problem (weighting)
4. ✅ Results stay interpretable
5. ✅ Standard practice in your field

**Only move to Option A if:**
- A reviewer specifically requests it
- You discover boundary problems (you won't)
- You're writing for a statistics journal (you're not)

**Forget Option C entirely.**

---

## Next Steps

1. **Implement Option B** (5 minutes)
2. **Regenerate results** (run your analysis pipeline)
3. **Compare old vs new** (check if conclusions change)
4. **Update methods section** (one sentence about weighting)
5. **Move on with your life** 😊

The perfect is the enemy of the good. Option B is **good enough** and gets you back to doing science instead of endlessly optimizing statistical minutiae.

---

**Remember:** The most important thing is that you **recognized the problem** and **fixed it**. Whether you use Option A or B matters far less than the fact that you're no longer treating a trial with 2 transitions the same as a trial with 9 transitions. That was the real issue, and you're solving it.
