"""
Exploratory Data Analysis for IER Analysis Project
Purpose: Understand data structure to inform statistical decisions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

# Set up visualization
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Data paths
CHILD_DATA_PATH = Path("data/raw/child-gl")
ADULT_DATA_PATH = Path("data/raw/adult-gl")

print("=" * 80)
print("EXPLORATORY DATA ANALYSIS: Infant Event Representation")
print("=" * 80)

# ============================================================================
# 1. LOAD SAMPLE DATA
# ============================================================================

print("\n" + "=" * 80)
print("1. LOADING SAMPLE DATA")
print("=" * 80)

# Get all child CSV files
child_files = list(CHILD_DATA_PATH.glob("*.csv"))
print(f"\nTotal child participant files: {len(child_files)}")

# Load first file to examine structure
sample_file = child_files[0]
print(f"\nLoading sample file: {sample_file.name}")

df_sample = pd.read_csv(sample_file)
print(f"\nShape: {df_sample.shape[0]} rows × {df_sample.shape[1]} columns")

print("\nColumn names:")
for i, col in enumerate(df_sample.columns, 1):
    print(f"  {i:2d}. {col}")

print("\nFirst 3 rows:")
print(df_sample.head(3))

print("\nData types:")
print(df_sample.dtypes)

print("\nBasic statistics:")
print(df_sample.describe())

# ============================================================================
# 2. EXAMINE DATA STRUCTURE ACROSS ALL PARTICIPANTS
# ============================================================================

print("\n" + "=" * 80)
print("2. DATA STRUCTURE ACROSS ALL PARTICIPANTS")
print("=" * 80)

# Load all child data (sample first 10 for speed)
all_data = []
for csv_file in child_files[:10]:  # Start with 10 participants
    try:
        df = pd.read_csv(csv_file)
        df['source_file'] = csv_file.name
        all_data.append(df)
    except Exception as e:
        print(f"Error loading {csv_file.name}: {e}")

df_all = pd.concat(all_data, ignore_index=True)
print(f"\nLoaded data from {len(all_data)} participants")
print(f"Total rows: {df_all.shape[0]:,}")

# ============================================================================
# 3. PARTICIPANTS AND TRIALS STRUCTURE
# ============================================================================

print("\n" + "=" * 80)
print("3. PARTICIPANTS AND TRIALS STRUCTURE")
print("=" * 80)

# Unique participants
unique_participants = df_all['Participant'].unique()
print(f"\nUnique participants: {len(unique_participants)}")
print(f"Participant IDs: {unique_participants[:5]}...")  # Show first 5

# Trials per participant
trials_per_participant = df_all.groupby('Participant')['event'].nunique()
print(f"\nTrials per participant:")
print(f"  Mean: {trials_per_participant.mean():.1f}")
print(f"  Median: {trials_per_participant.median():.1f}")
print(f"  Range: {trials_per_participant.min()} - {trials_per_participant.max()}")
print(f"\nDistribution of trials per participant:")
print(trials_per_participant.value_counts().sort_index())

# Frames per trial
frames_per_trial = df_all.groupby(['Participant', 'event']).size()
print(f"\nFrames per trial:")
print(f"  Mean: {frames_per_trial.mean():.1f}")
print(f"  Median: {frames_per_trial.median():.1f}")
print(f"  Range: {frames_per_trial.min()} - {frames_per_trial.max()}")

# ============================================================================
# 4. AGE DISTRIBUTION
# ============================================================================

print("\n" + "=" * 80)
print("4. AGE DISTRIBUTION")
print("=" * 80)

# Age in months
ages = df_all.groupby('Participant')['participant_age_months'].first()
print(f"\nAge distribution (months):")
print(f"  Mean: {ages.mean():.1f}")
print(f"  Median: {ages.median():.1f}")
print(f"  Range: {ages.min():.1f} - {ages.max():.1f}")
print(f"  SD: {ages.std():.1f}")

print(f"\nUnique ages: {sorted(ages.unique())}")

# Age groups
print(f"\nAge group breakdown:")
younger = ages[ages < 12].count()
older = ages[ages >= 12].count()
print(f"  Younger (<12 months): {younger}")
print(f"  Older (≥12 months): {older}")

# ============================================================================
# 5. AOI ANALYSIS (What + Where combinations)
# ============================================================================

print("\n" + "=" * 80)
print("5. AOI ANALYSIS (What + Where combinations)")
print("=" * 80)

# Create AOI combination
df_all['aoi_combination'] = df_all['What'] + ',' + df_all['Where']

# Count unique AOI combinations
aoi_counts = df_all['aoi_combination'].value_counts()
print(f"\nUnique What+Where combinations: {len(aoi_counts)}")
print(f"\nTop 15 AOI combinations:")
print(aoi_counts.head(15))

# Examine What and Where separately
print(f"\n'What' values:")
print(df_all['What'].value_counts())

print(f"\n'Where' values:")
print(df_all['Where'].value_counts())

# ============================================================================
# 6. EVENT/CONDITION ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("6. EVENT/CONDITION ANALYSIS")
print("=" * 80)

# Unique events
unique_events = df_all['event'].unique()
print(f"\nUnique events: {len(unique_events)}")
print(f"Event types: {sorted(unique_events)}")

# Event distribution
event_counts = df_all['event'].value_counts()
print(f"\nEvent distribution (frame counts):")
print(event_counts)

# Segment analysis
print(f"\nUnique segments:")
print(df_all['segment'].value_counts())

# ============================================================================
# 7. POTENTIAL GAZE EVENTS (3+ consecutive frames)
# ============================================================================

print("\n" + "=" * 80)
print("7. PRELIMINARY GAZE EVENT DETECTION")
print("=" * 80)

# Simple gaze event detection for one participant
sample_participant = df_all[df_all['Participant'] == unique_participants[0]].copy()
sample_participant = sample_participant.sort_values(['event', 'trial_frame'])

# Detect consecutive frames on same AOI
sample_participant['aoi_shift'] = (
    sample_participant['aoi_combination'] != sample_participant['aoi_combination'].shift(1)
)
sample_participant['gaze_event_id'] = sample_participant['aoi_shift'].cumsum()

# Count frames per gaze event
gaze_durations = sample_participant.groupby('gaze_event_id').size()

# Filter for 3+ frames (our definition of gaze event)
valid_gazes = gaze_durations[gaze_durations >= 3]

print(f"\nSample participant: {unique_participants[0]}")
print(f"  Total frames: {len(sample_participant)}")
print(f"  Potential gaze events (3+ frames): {len(valid_gazes)}")
print(f"  Mean gaze duration: {valid_gazes.mean():.1f} frames")
print(f"  Median gaze duration: {valid_gazes.median():.1f} frames")
print(f"  Gaze duration range: {valid_gazes.min()} - {valid_gazes.max()} frames")

# ============================================================================
# 8. MISSING DATA ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("8. MISSING DATA ANALYSIS")
print("=" * 80)

# Count missing values per column
missing_counts = df_all.isnull().sum()
missing_pct = (missing_counts / len(df_all)) * 100

print("\nMissing data by column:")
for col in df_all.columns:
    if missing_counts[col] > 0:
        print(f"  {col}: {missing_counts[col]:,} ({missing_pct[col]:.2f}%)")

if missing_counts.sum() == 0:
    print("  No missing values detected!")

# ============================================================================
# 9. DATA QUALITY CHECKS
# ============================================================================

print("\n" + "=" * 80)
print("9. DATA QUALITY CHECKS")
print("=" * 80)

# Check for negative ages
negative_ages = df_all[df_all['participant_age_months'] < 0]
print(f"\nNegative ages: {len(negative_ages)}")

# Check for extreme ages
extreme_ages = df_all[df_all['participant_age_months'] > 100]
print(f"Extreme ages (>100 months): {len(extreme_ages)}")

# Check for negative frame numbers
negative_frames = df_all[df_all['trial_frame'] < 0]
print(f"Negative frame numbers: {len(negative_frames)}")

# ============================================================================
# 10. SUMMARY STATISTICS FOR STATISTICAL MODELING
# ============================================================================

print("\n" + "=" * 80)
print("10. SUMMARY FOR STATISTICAL MODELING DECISIONS")
print("=" * 80)

print("\n📊 KEY FINDINGS:")
print("-" * 80)

print(f"\n1. SAMPLE SIZE:")
print(f"   - Participants (sample): {len(unique_participants)}")
print(f"   - Trials per participant: {trials_per_participant.mean():.1f} ± {trials_per_participant.std():.1f}")
print(f"   - Total observations (frames): {len(df_all):,}")

print(f"\n2. NESTING STRUCTURE:")
print(f"   - Frames nested within trials")
print(f"   - Trials nested within participants")
print(f"   - → LMM/GLMM is ESSENTIAL to account for this structure")

print(f"\n3. AGE DISTRIBUTION:")
print(f"   - Range: {ages.min():.1f} - {ages.max():.1f} months")
print(f"   - Continuous age analysis is feasible")
print(f"   - Sufficient spread to test developmental effects")

print(f"\n4. TRIAL BALANCE:")
balance_ratio = trials_per_participant.std() / trials_per_participant.mean()
if balance_ratio < 0.3:
    print(f"   - Well-balanced (SD/Mean = {balance_ratio:.2f})")
else:
    print(f"   - Unbalanced (SD/Mean = {balance_ratio:.2f})")
    print(f"   - → LMM handles unbalanced designs gracefully")

print(f"\n5. DATA QUALITY:")
if missing_counts.sum() == 0:
    print(f"   - ✓ No missing values detected")
else:
    print(f"   - ⚠ Missing values present - will need handling")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Save summary
summary_path = Path("temp_analysis/data_summary.txt")
with open(summary_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DATA SUMMARY FOR IER ANALYSIS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Participants: {len(unique_participants)}\n")
    f.write(f"Trials per participant (mean): {trials_per_participant.mean():.1f}\n")
    f.write(f"Age range: {ages.min():.1f} - {ages.max():.1f} months\n")
    f.write(f"Total frames: {len(df_all):,}\n")

print(f"\n✓ Summary saved to: {summary_path}")
