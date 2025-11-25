"""Understand transition probability matrix structure."""

import pandas as pd
import numpy as np

print("=" * 80)
print("UNDERSTANDING TRANSITION PROBABILITY MATRICES")
print("=" * 80)

# Recreate the example matrix from your report
print("\nYour GIVE_WITH matrix (7-month infants):")
print()

# Example row: man_body
data = {
    'from_aoi': ['man_body', 'man_face', 'man_hands', 'off_screen', 'screen_nonAOI',
                 'toy_present', 'woman_body', 'woman_face'],
    'man_body': [0.000, 0.000, 0.000, 0.000, 0.000, 0.333, 0.500, 0.000],
    'man_face': [0.500, 0.000, 0.000, 0.000, 0.000, 0.667, 1.000, 1.000],
    'off_screen': [0.000, 0.667, 0.000, 0.000, 0.833, 0.583, 0.750, 0.000],
    'screen_nonAOI': [0.000, 0.333, 0.000, 0.500, 0.000, 0.500, 0.000, 1.000],
    'toy_present': [0.792, 0.667, 1.000, 0.833, 1.000, 0.000, 0.500, 0.000],
    'woman_body': [0.000, 0.000, 0.000, 0.000, 1.000, 0.750, 0.000, 0.000],
    'woman_face': [0.333, 0.000, 0.000, 0.000, 0.500, 0.667, 0.000, 0.000],
    'woman_hands': [0.000, 0.000, 0.000, 0.000, 0.000, 0.500, 0.500, 0.000],
}

df = pd.DataFrame(data).set_index('from_aoi')
print(df.to_string())

# Calculate row sums
print("\n" + "=" * 80)
print("ROW SUMS (should be 1.0 if standard transition matrix)")
print("=" * 80)

row_sums = df.sum(axis=1)
for idx, sum_val in row_sums.items():
    status = "OK" if abs(sum_val - 1.0) < 0.01 else "PROBLEM"
    print(f"{idx:20s}: {sum_val:.3f}  [{status}]")

print(f"\nMean row sum: {row_sums.mean():.3f}")
print(f"Min row sum:  {row_sums.min():.3f}")
print(f"Max row sum:  {row_sums.max():.3f}")

# Explanation
print("\n" + "=" * 80)
print("WHAT THIS MEANS")
print("=" * 80)

print("""
ISSUE: Rows sum to > 1.0 (some as high as 5.75!)

This indicates one of these scenarios:

1. MISSING NORMALIZATION
   - Raw counts not divided by total transitions from each AOI
   - Each cell should be: P(to_aoi | from_aoi) = count(from->to) / count(from->any)

2. PARTICIPANT AGGREGATION ISSUE
   - Probabilities computed per participant, then averaged
   - Average of probabilities != probability of average

3. MULTIPLE TRANSITIONS COUNTED
   - If same participant has multiple transitions from_aoi to to_aoi,
     they might be counted separately instead of as a single probability

EXAMPLE - Expected behavior:
From man_body, infant could transition to:
  - man_face:      50 percent of the time
  - toy_present:   30 percent of the time
  - screen_nonAOI: 20 percent of the time
  Total: 100 percent (row sum = 1.0)

Your 'man_body' row sums to: {:.3f} (should be 1.0)
""".format(row_sums['man_body']))

print("\n" + "=" * 80)
print("HOW TO READ YOUR CURRENT MATRIX")
print("=" * 80)

print("""
GIVEN the row sums > 1.0, here's what the numbers likely represent:

INTERPRETATION 1: Proportion of participants showing transition
  - Value = proportion of participants (out of 7) who made this transition
  - 0.667 = 4-5 out of 7 participants made this transition
  - 1.000 = all 7 participants made this transition
  - Rows sum > 1.0 because multiple transitions possible per participant

INTERPRETATION 2: Average transition probability across participants
  - Each participant has their own transition probabilities
  - Values are averages across the 7 participants
  - Some participants may have different AOI sets available
  - Rows sum > 1.0 due to averaging effect

MOST LIKELY: Interpretation 1
  - With N=7 participants, values like 0.333, 0.500, 0.667, 1.000 are suspicious
  - 0.333 ≈ 2-3 / 7 participants
  - 0.500 ≈ 3-4 / 7 participants
  - 0.667 ≈ 4-5 / 7 participants
  - 1.000 = 7 / 7 participants
""")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

print("""
Check your AR2 code for how transition matrices are computed:

CORRECT METHOD (probability matrix):
  For each participant:
    1. Count transitions: from_aoi to to_aoi
    2. Normalize: divide by total transitions FROM from_aoi
    3. Result: P(to | from) for that participant
  Then aggregate across participants (mean or median)

SUSPECTED CURRENT METHOD:
  For each participant:
    1. Mark which transitions occurred (binary: yes/no)
  Then compute: proportion of participants showing each transition

WHICH IS CORRECT?
  - Depends on research question!
  - Probability: "How often do infants transition from X to Y?"
  - Prevalence: "How many infants show X to Y transition at all?"

For gaze transition analysis, PROBABILITY is standard.
""")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
