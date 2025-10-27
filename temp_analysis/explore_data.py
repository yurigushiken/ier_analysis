"""Exploratory analysis of raw data structure."""

import pandas as pd
from pathlib import Path

# Expected columns
EXPECTED_COLUMNS = [
    'Participant', 'Frame Number', 'Time', 'What', 'Where', 'Onset', 'Offset',
    'Blue Dot Center', 'event_verified', 'frame_count_event', 'trial_number',
    'trial_number_global', 'frame_count_trial_number', 'segment',
    'frame_count_segment', 'participant_type', 'participant_age_months',
    'participant_age_years'
]

def analyze_participant_file(csv_path):
    """Analyze a single participant CSV file."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {csv_path.name}")
    print(f"{'='*80}")

    df = pd.read_csv(csv_path)

    # 1. Column verification
    print(f"\n1. COLUMN VERIFICATION")
    print(f"   Expected columns: {len(EXPECTED_COLUMNS)}")
    print(f"   Found columns: {len(df.columns)}")

    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    extra = set(df.columns) - set(EXPECTED_COLUMNS)

    if missing:
        print(f"   ⚠️  MISSING: {missing}")
    if extra:
        print(f"   ℹ️  EXTRA: {extra}")
    if not missing and not extra:
        print(f"   ✓ All expected columns present")

    # 2. Frame analysis
    print(f"\n2. FRAME ANALYSIS")
    print(f"   Total rows (frames): {len(df)}")
    print(f"   Frame rate: 30 fps (assumed)")
    print(f"   Duration: ~{len(df) / 30:.1f} seconds")

    # 3. Event analysis
    print(f"\n3. EVENT ANALYSIS")
    if 'event_verified' in df.columns:
        events = df.groupby('event_verified').size().sort_index()
        print(f"   Unique events: {df['event_verified'].nunique()}")
        print(f"   Event types and frame counts:")
        for event, count in events.items():
            print(f"      {event:8s}: {count:5d} frames (~{count/30:.1f}s)")

    # 4. Trial analysis
    print(f"\n4. TRIAL ANALYSIS")
    if 'trial_number_global' in df.columns:
        trials = df['trial_number_global'].unique()
        print(f"   Unique trial_number_global values: {len(trials)}")
        print(f"   Trial numbers: {sorted(trials)}")

        # Show frames per trial
        trial_frames = df.groupby('trial_number_global').size()
        print(f"\n   Frames per trial_number_global:")
        for trial, frame_count in trial_frames.items():
            event_in_trial = df[df['trial_number_global'] == trial]['event_verified'].iloc[0]
            print(f"      Trial {trial}: {frame_count:3d} frames (~{frame_count/30:.1f}s) - {event_in_trial}")

    # 5. Event repetition analysis
    print(f"\n5. EVENT REPETITION ANALYSIS")
    if 'event_verified' in df.columns and 'trial_number_global' in df.columns:
        event_trials = df.groupby('event_verified')['trial_number_global'].nunique()
        print(f"   How many times each event appears (by trial_number_global):")
        for event, count in event_trials.items():
            print(f"      {event:8s}: {count} times")

    # 6. What-Where pair analysis
    print(f"\n6. WHAT-WHERE PAIR ANALYSIS")
    if 'What' in df.columns and 'Where' in df.columns:
        pairs = df.groupby(['What', 'Where']).size().sort_values(ascending=False)
        print(f"   Unique What-Where pairs: {len(pairs)}")
        print(f"   Frame counts by pair:")
        for (what, where), count in pairs.items():
            print(f"      {what:8s}, {where:8s}: {count:5d} frames")

    # 7. Segment analysis
    print(f"\n7. SEGMENT ANALYSIS")
    if 'segment' in df.columns:
        segments = df.groupby('segment').size()
        print(f"   Segments and frame counts:")
        for segment, count in segments.items():
            print(f"      {segment:12s}: {count:5d} frames (~{count/30:.1f}s)")

    # 8. Sample rows
    print(f"\n8. SAMPLE DATA (first 3 rows)")
    print(df.head(3).to_string())

    return df

def main():
    # Analyze child files
    child_dir = Path("data/csvs_human_verified_vv/child")
    adult_dir = Path("data/csvs_human_verified_vv/adult")

    print("\n" + "="*80)
    print("EXPLORING RAW DATA STRUCTURE")
    print("="*80)

    # Get sample files
    child_files = list(child_dir.glob("*.csv"))
    adult_files = list(adult_dir.glob("*.csv"))

    print(f"\nFound {len(child_files)} child files")
    print(f"Found {len(adult_files)} adult files")

    # Analyze 2 child files and 1 adult file
    sample_files = []
    if child_files:
        sample_files.extend(child_files[:2])
    if adult_files:
        sample_files.append(adult_files[0])

    dfs = []
    for csv_path in sample_files:
        df = analyze_participant_file(csv_path)
        dfs.append(df)

    # Summary across files
    print(f"\n{'='*80}")
    print("SUMMARY ACROSS SAMPLE FILES")
    print(f"{'='*80}")
    print(f"Files analyzed: {len(dfs)}")
    print(f"Total frames across samples: {sum(len(df) for df in dfs)}")

    # Event frame ranges
    print(f"\nEvent frame ranges across all samples:")
    all_events = pd.concat([
        df.groupby(['event_verified', 'trial_number_global']).size().reset_index(name='frames')
        for df in dfs
    ])

    event_stats = all_events.groupby('event_verified')['frames'].agg(['min', 'max', 'mean'])
    print(event_stats.to_string())

if __name__ == "__main__":
    main()
