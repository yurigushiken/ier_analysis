"""Combine child and adult gaze fixation files."""

import pandas as pd
from pathlib import Path

print("="*80)
print("COMBINING CHILD AND ADULT GAZE EVENT DATA")
print("="*80)

# Load both files
child_path = Path('data/processed/gaze_fixations_child.csv')
adult_path = Path('data/processed/gaze_fixations_adult.csv')

print(f"\nLoading files...")
child = pd.read_csv(child_path)
adult = pd.read_csv(adult_path)

print(f"✓ Child data: {len(child):,} events from {child['participant_id'].nunique()} participants")
print(f"✓ Adult data: {len(adult):,} events from {adult['participant_id'].nunique()} participants")

# Verify columns match
if list(child.columns) != list(adult.columns):
    print("\n⚠️  WARNING: Column mismatch!")
    print(f"Child columns: {list(child.columns)}")
    print(f"Adult columns: {list(adult.columns)}")
else:
    print(f"✓ Columns match: {len(child.columns)} columns")

# Combine
combined = pd.concat([child, adult], ignore_index=True)

# Save combined file
output_path = Path('data/processed/gaze_fixations.csv')
combined.to_csv(output_path, index=False)

print(f"\n{'='*80}")
print(f"✓ COMBINED FILE CREATED: {output_path}")
print(f"{'='*80}")
print(f"\nSummary:")
print(f"  Total events:        {len(combined):,}")
print(f"  Total participants:  {combined['participant_id'].nunique()}")
print(f"  Participant types:   {dict(combined['participant_type'].value_counts())}")
print(f"  Age range:           {combined['age_months'].min()} - {combined['age_months'].max()} months")
print(f"  Conditions:          {combined['condition_name'].nunique()} unique conditions")
print(f"\nBreakdown by participant type:")
print(combined.groupby('participant_type').agg({
    'participant_id': 'nunique',
    'gaze_duration_frames': ['count', 'mean']
}).to_string())

print(f"\n{'='*80}")
print("COMPLETE!")
print(f"{'='*80}")
