"""Investigate condition filtering and terminology issues."""

import pandas as pd
from pathlib import Path

print("="*80)
print("INVESTIGATION: AR1 CONDITION FILTERING & TERMINOLOGY")
print("="*80)

# Load data
df = pd.read_csv('data/processed/gaze_fixations.csv')

print("\n" + "="*80)
print("ISSUE 1: UPSIDE_DOWN VARIANTS IN GIVE vs HUG COMPARISON")
print("="*80)

print("\n1. ALL CONDITIONS IN DATA:")
conditions = df['condition_name'].unique()
for cond in sorted(conditions):
    print(f"   - {cond}")

print("\n2. CURRENT AR1 LOGIC (Lines 116-124 in ar1_gaze_duration.py):")
print("""
   give = participant_means[
       participant_means["condition_name"].str.upper().str.contains("GIVE") &
       participant_means["condition_name"].str.upper().str.contains("WITH")
   ]["toy_proportion"]

   hug = participant_means[
       participant_means["condition_name"].str.upper().str.contains("HUG") &
       participant_means["condition_name"].str.upper().str.contains("WITH")
   ]["toy_proportion"]
""")

print("\n3. WHAT GETS SELECTED:")
# Simulate the selection
participant_means = df.groupby(['condition_name', 'participant_id']).size().reset_index()

give_conditions = participant_means[
    participant_means["condition_name"].str.upper().str.contains("GIVE") &
    participant_means["condition_name"].str.upper().str.contains("WITH")
]['condition_name'].unique()

hug_conditions = participant_means[
    participant_means["condition_name"].str.upper().str.contains("HUG") &
    participant_means["condition_name"].str.upper().str.contains("WITH")
]['condition_name'].unique()

print("\n   GIVE conditions selected:")
for cond in sorted(give_conditions):
    print(f"      - {cond}")

print("\n   HUG conditions selected:")
for cond in sorted(hug_conditions):
    print(f"      - {cond}")

print("\n4. SCIENTIFIC QUESTION:")
print("""
   - UPSIDE_DOWN variants are BIOMECHANICAL CONTROLS
   - They test if the effect is about:")
     * Understanding event meaning (what we want to test)
     * vs. Visual motion patterns (control)"

   - Including them may:
     DILUTE the effect if upside-down reduces understanding
     STRENGTHEN if upside-down doesn't affect understanding
     CONFOUND if upside-down has different effect
""")

print("\n5. POSSIBLE YAML CONFIGURATION OPTIONS:")
print("""
Option A: Specify exact conditions to compare
---
comparisons:
  primary:
    group1: ["GIVE_WITH"]
    group2: ["HUG_WITH"]
  controls:
    group1: ["UPSIDE_DOWN_GIVE_WITH"]
    group2: ["UPSIDE_DOWN_HUG_WITH"]

Option B: Use pattern matching with exclusions
---
comparisons:
  primary:
    include_patterns: ["GIVE", "WITH"]
    exclude_patterns: ["UPSIDE_DOWN", "WITHOUT"]

Option C: Use condition tags/categories
---
condition_categories:
  upright_with: ["GIVE_WITH", "HUG_WITH", "SHOW_WITH"]
  upside_down_with: ["UPSIDE_DOWN_GIVE_WITH", "UPSIDE_DOWN_HUG_WITH"]

comparisons:
  primary:
    categories: ["upright_with"]
    contrast: ["GIVE_WITH", "HUG_WITH"]
""")

print("\n" + "="*80)
print("ISSUE 2: TERMINOLOGY - 'GAZE EVENT' vs ALTERNATIVES")
print("="*80)

print("\n1. CURRENT TERMINOLOGY:")
print("""
   Term: "gaze fixation"
   Definition: 3+ consecutive frames looking at same AOI
   Count in data: 26,560 (combined child + adult)
""")

print("\n2. WHY IT'S CONFUSING:")
print("""
   'Event' is OVERLOADED in this project:

   a) VIDEO EVENT (e.g., 'gw', 'hw', 'f')
      - The stimulus video showing an action
      - 11 types total
      - 150-185 frames long (~5 seconds)

   b) EVENT EXPOSURE / TRIAL
      - Each time participant sees a video event
      - Tracked by trial_number or trial_number_global
      - ~1,916 trials in child data

   c) GAZE EVENT (CURRENT USAGE)
      - 3+ consecutive frames on same AOI
      - ~26,560 in combined data
      - Detected by preprocessing pipeline
""")

print("\n3. ALTERNATIVE TERMINOLOGY OPTIONS:")

alternatives = {
    "gaze_fixation": {
        "pros": ["Standard in eye-tracking literature", "Clear meaning", "Distinct from stimulus events"],
        "cons": ["Technically 'fixation' has stricter definition (50-200ms)", "May imply spatial stability"]
    },
    "gaze_sequence": {
        "pros": ["Emphasizes consecutive frames", "Avoids 'event' confusion", "Accurate description"],
        "cons": ["Less standard", "Could imply longer duration"]
    },
    "look": {
        "pros": ["Simple, intuitive", "Natural language", "Used in infant research"],
        "cons": ["Too informal for scientific writing", "Vague duration"]
    },
    "gaze_bout": {
        "pros": ["Used in behavioral ecology", "Implies sustained attention", "Distinct from events"],
        "cons": ["Unfamiliar to some readers", "Could imply longer duration"]
    },
    "gaze_episode": {
        "pros": ["Clear sustained attention", "Distinct from stimulus events", "Professional"],
        "cons": ["'Episode' has other meanings in development", "Slightly verbose"]
    },
    "fixation_event": {
        "pros": ["Combines standard term with current usage", "Clear it's detected instance"],
        "cons": ["Still uses 'event'", "Fixation has technical definition"]
    },
    "sustained_gaze": {
        "pros": ["Emphasizes 3+ frame requirement", "Clear meaning", "Natural"],
        "cons": ["Longer phrase", "Could be ambiguous about threshold"]
    },
    "gaze_unit": {
        "pros": ["Neutral, technical", "Clearly a unit of analysis", "Avoids 'event'"],
        "cons": ["Abstract", "Less intuitive"]
    }
}

for i, (term, details) in enumerate(alternatives.items(), 1):
    print(f"\n   Option {i}: '{term}'")
    print(f"      Pros:")
    for pro in details['pros']:
        print(f"         + {pro}")
    print(f"      Cons:")
    for con in details['cons']:
        print(f"         - {con}")

print("\n4. FIELD-SPECIFIC CONVENTIONS:")
print("""
   Eye-tracking research typically uses:
   - FIXATION: Gaze held on point for 50-200ms (spatial + temporal)
   - SACCADE: Rapid eye movement between fixations
   - DWELL TIME: Total time spent in AOI (sum of fixations)
   - VISIT: Entry into and exit from an AOI (may include multiple fixations)

   Infant research often uses:
   - LOOKING TIME: Total duration of gaze (our 'gaze_duration_ms')
   - LOOK: Instance of looking (informal)
   - GAZE: Visual attention (general term)

   Your definition (3+ frames on same AOI) is closest to:
   - 'Fixation' if requiring spatial stability
   - 'Visit' if allowing eye movements within AOI
   - 'Gaze bout' if emphasizing sustained attention
""")

print("\n5. RECOMMENDATION:")
print("""
   Best options (ranked):

   1. 'gaze_fixation' - Most standard, clear for scientific audience
      - Use: "26,560 gaze fixations were detected"
      - Define: "A gaze fixation was defined as 3+ consecutive
                 frames (≥100ms) on the same AOI"

   2. 'sustained_gaze' - Emphasizes your 3+ frame criterion
      - Use: "26,560 sustained gazes were detected"
      - Define: "A sustained gaze was defined as 3+ consecutive
                 frames on the same AOI"

   3. 'gaze_bout' - Good for behavioral emphasis
      - Use: "26,560 gaze bouts were detected"
      - Define: "A gaze bout was defined as 3+ consecutive
                 frames on the same AOI"

   AVOID: Keeping 'gaze_fixation' - too confusing with stimulus events
""")

print("\n6. DATA STRUCTURE WITH NEW TERMINOLOGY:")
print("""
   Current (CONFUSING):
   - Stimulus event (gw, hw) → contains many gaze fixations

   Proposed (CLEAR):
   - Stimulus event (gw, hw) → contains many gaze fixations
   OR
   - Trial (video presentation) → contains many gaze fixations

   Hierarchy:
   Participant
     └─ Trial (one stimulus event presentation)
         └─ Gaze fixation (3+ frames on same AOI)
             └─ Frame (30fps)
""")

print("\n7. CODE CHANGES NEEDED:")
print("""
   If changing terminology, need to update:

   Files to rename:
   - gaze_fixations.csv → gaze_fixations.csv (or other term)

   Variables to rename:
   - gaze_fixation_id → gaze_fixation_id
   - detect_gaze_fixations() → detect_gaze_fixations()
   - _extract_events_from_group() → _extract_fixations_from_group()

   Documentation to update:
   - All docstrings mentioning "gaze fixation"
   - MENTORSHIP_DATA_FLOW.md
   - README.md
   - Report templates
   - Comments in code

   Estimated changes: ~50 locations across codebase
""")

print("\n" + "="*80)
print("SUMMARY & RECOMMENDATIONS")
print("="*80)

print("\n1. UPSIDE_DOWN VARIANT ISSUE:")
print("""
   YES - Can be made configurable in YAML

   Recommended approach:
   - Add 'comparisons' section to ar1_config.yaml
   - Allow specifying exact condition lists
   - Support multiple comparisons (upright vs upside-down separately)

   Example:
   comparisons:
     primary:
       name: "Upright GIVE vs HUG"
       give_conditions: ["GIVE_WITH"]
       hug_conditions: ["HUG_WITH"]
     control:
       name: "Upside-Down GIVE vs HUG"
       give_conditions: ["UPSIDE_DOWN_GIVE_WITH"]
       hug_conditions: ["UPSIDE_DOWN_HUG_WITH"]
""")

print("\n2. TERMINOLOGY ISSUE:")
print("""
   YES - 'gaze_fixation' is problematic and confusing

   Best replacement: 'gaze_fixation'
   - Standard in eye-tracking research
   - Clear distinction from stimulus events
   - Scientifically appropriate

   Impact:
   - Moderate refactoring (~50 changes)
   - Worth it for clarity
   - Should be done before publication
""")

print("\n" + "="*80)
print("END OF INVESTIGATION")
print("="*80)
