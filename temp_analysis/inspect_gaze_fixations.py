"""Inspect gaze_fixations.csv structure and trial_number column."""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("INSPECTING GAZE_FIXATIONS.CSV")
print("=" * 80)

# Load the processed data
data_path = Path("data/processed/gaze_fixations.csv")
print(f"\nLoading: {data_path}")

if not data_path.exists():
    print(f"ERROR: File not found at {data_path}")
    exit(1)

df = pd.read_csv(data_path)

print(f"\nLoaded successfully")
print(f"Total rows: {len(df):,}")
print(f"Total participants: {df['participant_id'].nunique()}")

# Show all columns
print("\n" + "=" * 80)
print("COLUMNS IN GAZE_FIXATIONS.CSV")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    dtype = df[col].dtype
    null_count = df[col].isna().sum()
    unique_count = df[col].nunique()
    print(f"{i:2d}. {col:35s} | dtype: {str(dtype):12s} | nulls: {null_count:6d} | unique: {unique_count:6d}")

# Inspect trial_number column specifically
print("\n" + "=" * 80)
print("TRIAL_NUMBER COLUMN ANALYSIS")
print("=" * 80)

print(f"\nData type: {df['trial_number'].dtype}")
print(f"Min value: {df['trial_number'].min()}")
print(f"Max value: {df['trial_number'].max()}")
print(f"Unique values: {df['trial_number'].nunique()}")
print(f"Null values: {df['trial_number'].isna().sum()}")

print("\nValue distribution:")
print(df['trial_number'].value_counts().sort_index().head(20))

# Check trial_number per participant
print("\n" + "=" * 80)
print("TRIAL_NUMBER PER PARTICIPANT")
print("=" * 80)

participant_trials = df.groupby('participant_id')['trial_number'].agg(['min', 'max', 'nunique', 'count'])
participant_trials = participant_trials.rename(columns={
    'min': 'min_trial',
    'max': 'max_trial',
    'nunique': 'unique_trials',
    'count': 'fixations'
})

print("\nSample of 10 participants:")
print(participant_trials.head(10).to_string())

print(f"\nSummary statistics:")
print(f"  Min trials per participant: {participant_trials['unique_trials'].min()}")
print(f"  Max trials per participant: {participant_trials['unique_trials'].max()}")
print(f"  Mean trials per participant: {participant_trials['unique_trials'].mean():.1f}")
print(f"  Median trials per participant: {participant_trials['unique_trials'].median():.1f}")

# Check if trial numbers restart for each participant
print("\n" + "=" * 80)
print("DO TRIAL NUMBERS RESTART PER PARTICIPANT?")
print("=" * 80)

sample_participants = df['participant_id'].unique()[:5]
for pid in sample_participants:
    pid_data = df[df['participant_id'] == pid]
    trials = sorted(pid_data['trial_number'].unique())
    print(f"\n{pid}:")
    print(f"  Trials: {trials}")
    print(f"  Range: {min(trials)} to {max(trials)}")
    print(f"  Count: {len(trials)}")

# Check relationship with condition
print("\n" + "=" * 80)
print("TRIAL_NUMBER BY CONDITION")
print("=" * 80)

condition_trials = df.groupby('condition_name')['trial_number'].agg(['min', 'max', 'nunique', 'count'])
print(condition_trials.to_string())

# Sample some actual rows
print("\n" + "=" * 80)
print("SAMPLE DATA (First 20 rows)")
print("=" * 80)

sample_cols = ['participant_id', 'trial_number', 'condition_name', 'segment', 'aoi_category', 'gaze_duration_ms']
print(df[sample_cols].head(20).to_string(index=False))

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
