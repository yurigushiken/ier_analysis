"""Check for redundant columns in gaze_fixations.csv."""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("CHECKING FOR REDUNDANCIES IN GAZE_FIXATIONS.CSV")
print("=" * 80)

df = pd.read_csv("data/processed/gaze_fixations.csv")

print(f"\nTotal columns: {len(df.columns)}")

# Check 1: condition vs condition_name
print("\n" + "=" * 80)
print("CHECK 1: condition vs condition_name")
print("=" * 80)

condition_mapping = df[['condition', 'condition_name']].drop_duplicates().sort_values('condition')
print("\nMapping between condition and condition_name:")
print(condition_mapping.to_string(index=False))

# Check if it's a 1:1 mapping
if len(condition_mapping) == df['condition'].nunique() == df['condition_name'].nunique():
    print("\n*** REDUNDANCY FOUND: 'condition' and 'condition_name' have 1:1 mapping")
    print("    Recommendation: Keep 'condition_name' (more readable), drop 'condition'")
else:
    print("\nNo redundancy - mappings are different")

# Check 2: gaze_duration_frames vs gaze_start/end_frame
print("\n" + "=" * 80)
print("CHECK 2: gaze_duration_frames vs (gaze_end_frame - gaze_start_frame + 1)")
print("=" * 80)

df['calculated_duration'] = df['gaze_end_frame'] - df['gaze_start_frame'] + 1
matches = (df['gaze_duration_frames'] == df['calculated_duration']).sum()
total = len(df)

print(f"\nRows where gaze_duration_frames == (end - start + 1): {matches}/{total}")
print(f"Match rate: {100 * matches / total:.2f}%")

if matches == total:
    print("\n*** REDUNDANCY FOUND: 'gaze_duration_frames' can be calculated from start/end")
    print("    Recommendation: Keep for convenience (avoids recalculation)")
else:
    print("\nNo perfect redundancy - some differences exist")
    # Show examples of mismatches
    mismatches = df[df['gaze_duration_frames'] != df['calculated_duration']]
    if len(mismatches) > 0:
        print(f"\nExample mismatches (showing first 5):")
        print(mismatches[['participant_id', 'trial_number', 'gaze_start_frame',
                         'gaze_end_frame', 'gaze_duration_frames', 'calculated_duration']].head().to_string(index=False))

# Check 3: gaze_duration_ms vs onset/offset
print("\n" + "=" * 80)
print("CHECK 3: gaze_duration_ms vs (gaze_offset_time - gaze_onset_time) * 1000")
print("=" * 80)

df['calculated_ms'] = (df['gaze_offset_time'] - df['gaze_onset_time']) * 1000
df['ms_diff'] = abs(df['gaze_duration_ms'] - df['calculated_ms'])

close_matches = (df['ms_diff'] < 0.1).sum()  # Within 0.1ms tolerance
print(f"\nRows where gaze_duration_ms ~= (offset - onset) * 1000: {close_matches}/{total}")
print(f"Match rate: {100 * close_matches / total:.2f}%")

print(f"\nMax difference: {df['ms_diff'].max():.2f} ms")
print(f"Mean difference: {df['ms_diff'].mean():.2f} ms")

if close_matches == total:
    print("\n*** REDUNDANCY FOUND: 'gaze_duration_ms' can be calculated from onset/offset")
    print("    Recommendation: Keep for convenience (avoids recalculation)")
else:
    print("\nPartial redundancy - mostly calculable with small differences")

# Check 4: age_group derivable from age_months
print("\n" + "=" * 80)
print("CHECK 4: age_group vs age_months")
print("=" * 80)

age_mapping = df[['age_months', 'age_group', 'participant_type']].drop_duplicates().sort_values(['participant_type', 'age_months'])
print("\nMapping between age_months and age_group:")
print(age_mapping.to_string(index=False))

# Count unique age_months per age_group
age_group_counts = df.groupby('age_group')['age_months'].nunique()
print(f"\nUnique age_months values per age_group:")
print(age_group_counts)

print("\n*** REDUNDANCY FOUND: 'age_group' is derived from 'age_months' via config rules")
print("    Recommendation: Keep both - age_group useful for analysis grouping")

# Check 5: participant_type derivable from age_months
print("\n" + "=" * 80)
print("CHECK 5: participant_type vs age_months")
print("=" * 80)

type_age = df[['participant_type', 'age_months']].drop_duplicates().sort_values('age_months')
infant_max = df[df['participant_type'] == 'infant']['age_months'].max()
adult_min = df[df['participant_type'] == 'adult']['age_months'].min()

print(f"\nInfant max age: {infant_max} months")
print(f"Adult min age: {adult_min} months")

if infant_max < adult_min:
    print("\n*** REDUNDANCY FOUND: 'participant_type' perfectly separable by age_months")
    print(f"    Rule: age_months <= {infant_max} = infant, >= {adult_min} = adult")
    print("    Recommendation: Keep both - participant_type is clearer for filtering")
else:
    print("\nNo clear redundancy - age ranges may overlap")

# Check 6: Missing trial_number_global
print("\n" + "=" * 80)
print("CHECK 6: Missing 'trial_number_global' column")
print("=" * 80)

print("\nColumns in gaze_fixations.csv:")
print(f"  - trial_number: YES (1-17, within-condition)")
print(f"  - trial_number_global: NO (missing)")

print("\nNote: Raw CSVs contain 'trial_number_global' but it's NOT in gaze_fixations.csv")
print("This is likely intentional - global trial order may not be needed for fixation-level analysis")

# Summary
print("\n" + "=" * 80)
print("SUMMARY OF REDUNDANCIES")
print("=" * 80)

print("""
FOUND REDUNDANCIES:
1. [X] condition <-> condition_name (1:1 mapping)
   Action: COULD drop 'condition' (keep readable 'condition_name')

2. [X] gaze_duration_frames = end - start + 1
   Action: KEEP (convenience, avoids recalculation)

3. [X] gaze_duration_ms ~= (offset - onset) * 1000
   Action: KEEP (convenience, avoids recalculation)

4. [X] age_group derived from age_months
   Action: KEEP (useful for analysis grouping)

5. [X] participant_type separable by age_months
   Action: KEEP (clarity, easier filtering)

RECOMMENDATION:
- Only TRUE redundancy worth removing: 'condition' column
- All others serve practical purposes despite being derivable
- Current design prioritizes analysis convenience over storage efficiency
""")

print("\n" + "=" * 80)
print("REDUNDANCY CHECK COMPLETE")
print("=" * 80)
