"""Audit AR1 analysis logic and assumptions."""

import pandas as pd
import numpy as np

print("="*80)
print("AUDIT: AR1 GAZE DURATION ANALYSIS LOGIC")
print("="*80)

# Load gaze events
df = pd.read_csv('data/processed/gaze_events_child.csv')
print(f"\n1. LOADED DATA")
print(f"   Total gaze events: {len(df)}")
print(f"   Participants: {df['participant_id'].nunique()}")
print(f"   Columns: {list(df.columns)}")

# Check for required columns
print(f"\n2. COLUMN VERIFICATION")
required_cols = ['participant_id', 'condition_name', 'trial_number', 'aoi_category', 'gaze_duration_ms']
for col in required_cols:
    if col in df.columns:
        print(f"   ✓ {col}")
    else:
        print(f"   ✗ MISSING: {col}")

# Verify AR1 logic: toy AOIs
print(f"\n3. TOY AOI IDENTIFICATION")
TOY_AOIS = ("toy_present", "toy_location")
ONSCREEN_EXCLUDE = ("off_screen",)

print(f"   Toy AOIs defined: {TOY_AOIS}")
print(f"   Excluded from denominator: {ONSCREEN_EXCLUDE}")

df_filtered = df[~df['aoi_category'].isin(ONSCREEN_EXCLUDE)].copy()
print(f"   Total gaze events: {len(df)}")
print(f"   After excluding off_screen: {len(df_filtered)}")
print(f"   Percentage on-screen: {len(df_filtered)/len(df)*100:.1f}%")

df_filtered['is_toy'] = df_filtered['aoi_category'].isin(TOY_AOIS)
print(f"   Gaze events on toy AOIs: {df_filtered['is_toy'].sum()}")
print(f"   Toy gaze events breakdown:")
for aoi in TOY_AOIS:
    count = (df_filtered['aoi_category'] == aoi).sum()
    print(f"      {aoi}: {count}")

# Verify trial-level proportion calculation
print(f"\n4. TRIAL-LEVEL PROPORTION CALCULATION")
print(f"   AR1 calculates: toy_duration / total_onscreen_duration per trial")

# Sample calculation for one participant, one trial
sample_participant = df['participant_id'].iloc[0]
sample_trial = df[df['participant_id'] == sample_participant]['trial_number'].iloc[0]
sample_data = df[(df['participant_id'] == sample_participant) & (df['trial_number'] == sample_trial)]

print(f"\n   Example: {sample_participant}, trial {sample_trial}")
print(f"   Total gaze events in trial: {len(sample_data)}")

sample_filtered = sample_data[~sample_data['aoi_category'].isin(ONSCREEN_EXCLUDE)]
print(f"   On-screen gaze events: {len(sample_filtered)}")

total_duration = sample_filtered['gaze_duration_ms'].sum()
toy_duration = sample_filtered[sample_filtered['aoi_category'].isin(TOY_AOIS)]['gaze_duration_ms'].sum()
toy_proportion = toy_duration / total_duration if total_duration > 0 else 0

print(f"   Total on-screen duration: {total_duration:.1f} ms")
print(f"   Toy duration: {toy_duration:.1f} ms")
print(f"   Proportion on toy: {toy_proportion:.3f}")

# Replicate AR1 calculation across all data
print(f"\n5. REPLICATING AR1 CALCULATION")

filtered = df[~df['aoi_category'].isin(ONSCREEN_EXCLUDE)].copy()
filtered['is_toy'] = filtered['aoi_category'].isin(TOY_AOIS)

# Calculate trial totals
trial_totals = filtered.groupby(['participant_id', 'condition_name', 'trial_number'])['gaze_duration_ms'].sum().reset_index()
trial_totals.columns = ['participant_id', 'condition_name', 'trial_number', 'total_duration']

# Calculate toy totals
toy_totals = filtered[filtered['is_toy']].groupby(['participant_id', 'condition_name', 'trial_number'])['gaze_duration_ms'].sum().reset_index()
toy_totals.columns = ['participant_id', 'condition_name', 'trial_number', 'toy_duration']

# Merge
merged = pd.merge(trial_totals, toy_totals, on=['participant_id', 'condition_name', 'trial_number'], how='left')
merged['toy_duration'].fillna(0.0, inplace=True)
merged['toy_proportion'] = merged['toy_duration'] / merged['total_duration']

print(f"   Total trials analyzed: {len(merged)}")
print(f"   Trials with toy looking: {(merged['toy_duration'] > 0).sum()}")
print(f"   Mean toy proportion (all trials): {merged['toy_proportion'].mean():.3f}")
print(f"   Median toy proportion: {merged['toy_proportion'].median():.3f}")

# Aggregate to participant level by condition
print(f"\n6. PARTICIPANT-LEVEL AGGREGATION")
participant_means = merged.groupby(['condition_name', 'participant_id'])['toy_proportion'].mean().reset_index()
print(f"   Participant × condition combinations: {len(participant_means)}")

# Summary by condition
condition_summary = participant_means.groupby('condition_name').agg(
    mean_toy_proportion=('toy_proportion', 'mean'),
    n=('participant_id', 'nunique')
).reset_index()

print(f"\n   Summary by condition:")
print(condition_summary.to_string(index=False))

# Check GIVE vs HUG comparison
print(f"\n7. GIVE vs HUG COMPARISON (AR1 PRIMARY ANALYSIS)")
give_with = participant_means[participant_means['condition_name'].str.contains('GIVE') &
                               participant_means['condition_name'].str.contains('WITH')]
hug_with = participant_means[participant_means['condition_name'].str.contains('HUG') &
                             participant_means['condition_name'].str.contains('WITH')]

print(f"   GIVE_WITH participants: {len(give_with)}")
print(f"   HUG_WITH participants: {len(hug_with)}")
print(f"   GIVE_WITH mean: {give_with['toy_proportion'].mean():.3f}")
print(f"   HUG_WITH mean: {hug_with['toy_proportion'].mean():.3f}")

# Check age data availability
print(f"\n8. AGE DATA VERIFICATION")
print(f"   Age column present: {'age_months' in df.columns}")
if 'age_months' in df.columns:
    age_data = df.groupby('participant_id')['age_months'].first()
    print(f"   Unique ages: {sorted(age_data.unique())}")
    print(f"   Age range: {age_data.min()} - {age_data.max()} months")
    print(f"   Missing ages: {age_data.isna().sum()}")

    # Check if age groups are present
    if 'age_group' in df.columns:
        age_groups = df.groupby('participant_id')['age_group'].first()
        print(f"   Age groups present: {sorted(age_groups.unique())}")
        print(f"   Age group distribution:")
        print(age_groups.value_counts().to_string())
    else:
        print(f"   ⚠️  age_group column NOT found")

# Check trial_number structure
print(f"\n9. TRIAL STRUCTURE VERIFICATION")
print(f"   'trial_number' column type: {df['trial_number'].dtype}")
print(f"   Trial numbers range: {df['trial_number'].min()} - {df['trial_number'].max()}")
print(f"   Trials per participant (sample of 5):")
trials_per_p = df.groupby('participant_id')['trial_number'].nunique().head()
print(trials_per_p.to_string())

print("\n" + "="*80)
print("AUDIT COMPLETE - KEY FINDINGS BELOW")
print("="*80)
