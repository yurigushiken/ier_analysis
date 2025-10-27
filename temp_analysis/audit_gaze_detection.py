"""Audit gaze event detection logic."""

import pandas as pd
from pathlib import Path

print("="*80)
print("AUDIT: GAZE EVENT DETECTION LOGIC")
print("="*80)

# Load one raw participant file
raw_file = Path("data/csvs_human_verified_vv/child/Eight-0101-947gl.csv")
print(f"\n1. Loading raw file: {raw_file.name}")
df_raw = pd.read_csv(raw_file)
print(f"   Total frames: {len(df_raw)}")

# Manually detect gaze events using same logic as gaze_detector.py
print(f"\n2. Manually detecting gaze events (3+ consecutive frames on same AOI)")

# Map What+Where to AOI categories
aoi_mapping = {
    "no,signal": "off_screen",
    "screen,other": "screen_nonAOI",
    "woman,face": "woman_face",
    "man,face": "man_face",
    "toy,other": "toy_present",
    "toy2,other": "toy_location",
    "man,body": "man_body",
    "woman,body": "woman_body",
    "man,hands": "man_hands",
    "woman,hands": "woman_hands",
}

df_raw['aoi_key'] = df_raw['What'] + ',' + df_raw['Where']
df_raw['aoi_category'] = df_raw['aoi_key'].map(aoi_mapping)

print(f"   AOI categories mapped: {df_raw['aoi_category'].notna().sum()} / {len(df_raw)} frames")

# Sort by trial and frame
df_raw = df_raw.sort_values(['trial_number', 'Frame Number'])

# Detect consecutive frames
gaze_events = []
for trial in df_raw['trial_number'].unique():
    trial_data = df_raw[df_raw['trial_number'] == trial]

    current_aoi = None
    frame_buffer = []

    for idx, row in trial_data.iterrows():
        aoi = row['aoi_category']

        if pd.isna(aoi):  # Invalid AOI, reset
            if len(frame_buffer) >= 3:
                gaze_events.append({
                    'trial': trial,
                    'aoi': current_aoi,
                    'frames': len(frame_buffer),
                    'start_frame': frame_buffer[0],
                    'end_frame': frame_buffer[-1]
                })
            current_aoi = None
            frame_buffer = []
            continue

        if aoi == current_aoi:
            frame_buffer.append(row['Frame Number'])
        else:
            # Finalize previous event if >= 3 frames
            if len(frame_buffer) >= 3:
                gaze_events.append({
                    'trial': trial,
                    'aoi': current_aoi,
                    'frames': len(frame_buffer),
                    'start_frame': frame_buffer[0],
                    'end_frame': frame_buffer[-1]
                })
            # Start new event
            current_aoi = aoi
            frame_buffer = [row['Frame Number']]

    # Finalize last event in trial
    if len(frame_buffer) >= 3:
        gaze_events.append({
            'trial': trial,
            'aoi': current_aoi,
            'frames': len(frame_buffer),
            'start_frame': frame_buffer[0],
            'end_frame': frame_buffer[-1]
        })

df_gaze = pd.DataFrame(gaze_events)
print(f"   Detected gaze events: {len(df_gaze)}")
print(f"   Average frames per gaze event: {df_gaze['frames'].mean():.1f}")
print(f"   Median frames per gaze event: {df_gaze['frames'].median():.1f}")
print(f"   Range: {df_gaze['frames'].min()} - {df_gaze['frames'].max()} frames")

print(f"\n3. Gaze events by AOI category:")
print(df_gaze.groupby('aoi')['frames'].agg(['count', 'mean', 'sum']))

print(f"\n4. Gaze events by trial:")
trial_summary = df_gaze.groupby('trial').agg({'aoi': 'count', 'frames': 'sum'})
trial_summary.columns = ['n_gaze_events', 'total_frames_in_gazes']
print(trial_summary)

# Compare with processed file
print(f"\n5. Comparing with processed gaze_events_child.csv")
df_processed = pd.read_csv('data/processed/gaze_events_child.csv')
participant_id = df_raw['Participant'].iloc[0]
df_processed_participant = df_processed[df_processed['participant_id'] == participant_id]

print(f"   Processed file - this participant: {len(df_processed_participant)} gaze events")
print(f"   Manual detection - this participant: {len(df_gaze)} gaze events")
print(f"   Match: {'✓ YES' if len(df_processed_participant) == len(df_gaze) else '✗ NO - DISCREPANCY!'}")

if len(df_processed_participant) != len(df_gaze):
    print(f"\n   ⚠️  DISCREPANCY DETECTED!")
    print(f"   Difference: {abs(len(df_processed_participant) - len(df_gaze))} events")

# Show sample gaze events
print(f"\n6. Sample gaze events (first 5):")
print(df_gaze.head(5).to_string(index=False))

# Check total across all participants
print(f"\n7. FULL DATASET SUMMARY")
print(f"   Total gaze events in processed file: {len(df_processed)}")
print(f"   Unique participants: {df_processed['participant_id'].nunique()}")
print(f"   Gaze events per participant (mean): {len(df_processed) / df_processed['participant_id'].nunique():.1f}")

print(f"\n8. Distribution of gaze duration (frames):")
duration_stats = df_processed['gaze_duration_frames'].describe()
print(duration_stats)

print(f"\n9. Gaze events by AOI category (full dataset):")
aoi_counts = df_processed['aoi_category'].value_counts()
print(aoi_counts)

print(f"\n10. Gaze events by condition (full dataset):")
condition_counts = df_processed['condition_name'].value_counts()
print(condition_counts)

print("\n" + "="*80)
print("AUDIT COMPLETE")
print("="*80)
