"""
Comprehensive Analysis of New Data Structure
Path: data/csvs_human_verified_vv/
"""

import csv
from pathlib import Path
from collections import defaultdict, Counter
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("NEW DATA STRUCTURE ANALYSIS")
print("Path: data/csvs_human_verified_vv/")
print("=" * 80)

# Data paths
CHILD_DATA_PATH = Path("data/csvs_human_verified_vv/child")
ADULT_DATA_PATH = Path("data/csvs_human_verified_vv/adult")

# ============================================================================
# 1. FILE INVENTORY
# ============================================================================

print("\n" + "=" * 80)
print("1. FILE INVENTORY")
print("=" * 80)

child_files = list(CHILD_DATA_PATH.glob("*.csv"))
adult_files = list(ADULT_DATA_PATH.glob("*.csv"))

print(f"\nChild participant files: {len(child_files)}")
print(f"Adult participant files: {len(adult_files)}")

print(f"\nFirst 10 child files:")
for i, f in enumerate(child_files[:10], 1):
    print(f"  {i:2d}. {f.name}")

# ============================================================================
# 2. COLUMN STRUCTURE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("2. COLUMN STRUCTURE")
print("=" * 80)

sample_file = child_files[0]
print(f"\nAnalyzing: {sample_file.name}")

with open(sample_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    sample_rows = list(reader)[:5]

print(f"\nTotal columns: {len(headers)}")
print(f"\nColumn names:")
for i, col in enumerate(headers, 1):
    print(f"  {i:2d}. {col}")

print(f"\nFirst 3 rows (key columns):")
key_cols = ['Participant', 'event_verified', 'trial_number', 'trial_number_global',
            'What', 'Where', 'segment', 'participant_age_months']
for i, row in enumerate(sample_rows[:3], 1):
    print(f"\n  Row {i}:")
    for col in key_cols:
        if col in row:
            print(f"    {col}: {row[col]}")

# ============================================================================
# 3. LOAD ALL CHILD DATA
# ============================================================================

print("\n" + "=" * 80)
print("3. LOADING ALL CHILD PARTICIPANT DATA")
print("=" * 80)

all_participants = {}
all_event_types = Counter()

for csv_file in child_files:
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if not rows:
                continue

            participant_id = rows[0]['Participant']
            age_months = float(rows[0]['participant_age_months'])

            # Get unique events
            events = [row['event_verified'] for row in rows]
            unique_events = list(set(events))
            event_counts = Counter(events)

            # Track trial_number_global values per event
            events_with_trials = defaultdict(set)
            for row in rows:
                event = row['event_verified']
                trial_global = row['trial_number_global']
                events_with_trials[event].add(trial_global)

            all_participants[participant_id] = {
                'age_months': age_months,
                'total_frames': len(rows),
                'unique_events': unique_events,
                'event_counts': event_counts,
                'events_with_trials': events_with_trials,
                'filename': csv_file.name
            }

            all_event_types.update(unique_events)

    except Exception as e:
        print(f"Error loading {csv_file.name}: {e}")

print(f"\nLoaded {len(all_participants)} participants")

# ============================================================================
# 4. EVENT TYPES
# ============================================================================

print("\n" + "=" * 80)
print("4. EVENT TYPES FOUND")
print("=" * 80)

print(f"\nUnique event types: {len(all_event_types)}")
print(f"\nEvent types (sorted):")
for event in sorted(all_event_types.keys()):
    count = all_event_types[event]
    print(f"  {event:12s} - found in {count} participants")

# ============================================================================
# 5. AGE DISTRIBUTION
# ============================================================================

print("\n" + "=" * 80)
print("5. AGE DISTRIBUTION")
print("=" * 80)

ages = [data['age_months'] for data in all_participants.values()]
ages_sorted = sorted(ages)

print(f"\nAge statistics:")
print(f"  N: {len(ages)}")
print(f"  Min: {min(ages):.1f} months")
print(f"  Max: {max(ages):.1f} months")
print(f"  Mean: {sum(ages)/len(ages):.1f} months")
print(f"  Median: {ages_sorted[len(ages_sorted)//2]:.1f} months")

# Age distribution
age_distribution = Counter([round(age) for age in ages])
print(f"\nAge distribution:")
for age in sorted(age_distribution.keys()):
    count = age_distribution[age]
    bar = "█" * count
    print(f"  {age:2d} months: {count:2d} participants {bar}")

# ============================================================================
# 6. EVENT_PRESENTATION_ID CONSTRUCTION TEST
# ============================================================================

print("\n" + "=" * 80)
print("6. EVENT_PRESENTATION_ID CONSTRUCTION TEST")
print("=" * 80)

print("\nProposed method: participant + event + trial_number_global")
print("\nTesting with sample participant...")

# Test with first participant
sample_participant_id = list(all_participants.keys())[0]
sample_data = all_participants[sample_participant_id]

print(f"\nSample participant: {sample_participant_id}")
print(f"Unique events: {len(sample_data['unique_events'])}")

print(f"\nEvent presentations (using trial_number_global):")
total_presentations = 0
for event in sorted(sample_data['events_with_trials'].keys()):
    trial_globals = sorted([int(t) for t in sample_data['events_with_trials'][event]])
    n_presentations = len(trial_globals)
    total_presentations += n_presentations
    print(f"  {event:12s}: {n_presentations} presentations (trial_number_global: {trial_globals})")

print(f"\nTotal presentations for this participant: {total_presentations}")

# Test unique ID generation
print(f"\nSample event_presentation_ids:")
for event in sorted(list(sample_data['events_with_trials'].keys())[:3]):
    for trial_global in sorted([int(t) for t in sample_data['events_with_trials'][event]])[:2]:
        event_id = f"{sample_participant_id}_{event}_{trial_global}"
        print(f"  {event_id}")

# ============================================================================
# 7. PRESENTATIONS PER PARTICIPANT STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("7. EVENT PRESENTATIONS PER PARTICIPANT")
print("=" * 80)

presentations_per_participant = []
events_per_participant = []

for participant_id, data in all_participants.items():
    n_events = len(data['unique_events'])
    n_presentations = sum(len(trials) for trials in data['events_with_trials'].values())

    presentations_per_participant.append(n_presentations)
    events_per_participant.append(n_events)

print(f"\nUnique event types per participant:")
print(f"  Mean: {sum(events_per_participant)/len(events_per_participant):.1f}")
print(f"  Min: {min(events_per_participant)}")
print(f"  Max: {max(events_per_participant)}")

print(f"\nTotal presentations per participant:")
print(f"  Mean: {sum(presentations_per_participant)/len(presentations_per_participant):.1f}")
print(f"  Min: {min(presentations_per_participant)}")
print(f"  Max: {max(presentations_per_participant)}")

# Distribution of presentations
presentation_distribution = Counter(presentations_per_participant)
print(f"\nDistribution of total presentations:")
for n in sorted(presentation_distribution.keys()):
    count = presentation_distribution[n]
    print(f"  {n:2d} presentations: {count} participants")

# ============================================================================
# 8. TOTAL EVENT PRESENTATIONS ACROSS ALL PARTICIPANTS
# ============================================================================

print("\n" + "=" * 80)
print("8. TOTAL EVENT PRESENTATIONS (ALL PARTICIPANTS)")
print("=" * 80)

total_presentations = sum(presentations_per_participant)
print(f"\nTotal event presentations: {total_presentations}")
print(f"  Participants: {len(all_participants)}")
print(f"  Average per participant: {total_presentations / len(all_participants):.1f}")

# ============================================================================
# 9. VERIFY UNIQUE event_presentation_id
# ============================================================================

print("\n" + "=" * 80)
print("9. VERIFY UNIQUE event_presentation_id METHOD")
print("=" * 80)

print("\nGenerating all event_presentation_ids...")

all_event_ids = set()
duplicate_ids = []

for participant_id, data in all_participants.items():
    for event, trial_globals in data['events_with_trials'].items():
        for trial_global in trial_globals:
            event_id = f"{participant_id}_{event}_{trial_global}"

            if event_id in all_event_ids:
                duplicate_ids.append(event_id)

            all_event_ids.add(event_id)

print(f"\nTotal unique event_presentation_ids: {len(all_event_ids)}")
print(f"Expected (from sum): {total_presentations}")

if len(all_event_ids) == total_presentations:
    print(f"\n✅ SUCCESS: All event_presentation_ids are unique!")
    print(f"   Method works: participant + event + trial_number_global")
else:
    print(f"\n⚠️  WARNING: Count mismatch")
    print(f"   Unique IDs: {len(all_event_ids)}")
    print(f"   Expected: {total_presentations}")

if duplicate_ids:
    print(f"\n⚠️  Found {len(duplicate_ids)} duplicate IDs:")
    for dup in duplicate_ids[:10]:
        print(f"   {dup}")
else:
    print(f"\n✅ No duplicate IDs found")

# ============================================================================
# 10. DETAILED PARTICIPANT SAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("10. DETAILED PARTICIPANT EXAMPLES")
print("=" * 80)

print("\nFirst 3 participants (detailed):")
for i, (participant_id, data) in enumerate(list(all_participants.items())[:3]):
    print(f"\n{'-' * 80}")
    print(f"Participant: {participant_id}")
    print(f"Age: {data['age_months']:.1f} months")
    print(f"Total frames: {data['total_frames']:,}")
    print(f"Unique events: {len(data['unique_events'])}")
    print(f"Total presentations: {sum(len(t) for t in data['events_with_trials'].values())}")

    print(f"\nEvent breakdown:")
    for event in sorted(data['unique_events']):
        n_presentations = len(data['events_with_trials'][event])
        frames = data['event_counts'][event]
        print(f"  {event:12s}: {n_presentations} presentations, {frames:4d} frames")

# ============================================================================
# 11. SUMMARY FOR DOCUMENTATION
# ============================================================================

print("\n" + "=" * 80)
print("11. SUMMARY FOR DOCUMENTATION")
print("=" * 80)

print(f"\n📊 KEY FINDINGS:")
print(f"{'─' * 80}")

print(f"\n1. SAMPLE SIZE:")
print(f"   - Participants: {len(all_participants)}")
print(f"   - Age range: {min(ages):.1f} - {max(ages):.1f} months")
print(f"   - Mean age: {sum(ages)/len(ages):.1f} months")

print(f"\n2. EVENT TYPES:")
print(f"   - Unique event types: {len(all_event_types)}")
print(f"   - Event types: {sorted(all_event_types.keys())}")

print(f"\n3. EVENT PRESENTATIONS:")
print(f"   - Total presentations (all participants): {total_presentations}")
print(f"   - Mean presentations per participant: {sum(presentations_per_participant)/len(presentations_per_participant):.1f}")
print(f"   - Range: {min(presentations_per_participant)} - {max(presentations_per_participant)}")

print(f"\n4. event_presentation_id METHOD:")
print(f"   ✅ Formula: participant + '_' + event + '_' + trial_number_global")
print(f"   ✅ Unique IDs: {len(all_event_ids)}")
print(f"   ✅ No duplicates: {len(duplicate_ids) == 0}")

print(f"\n5. COLUMNS IN NEW DATA:")
print(f"   - event_verified (NEW): Verified event type")
print(f"   - trial_number_global (NEW): Nth occurrence of event for participant")
print(f"   - frame_count_event, frame_count_trial_number, frame_count_segment")
print(f"   - REMOVED: trial_block_* columns (not in new data)")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Save results
output_file = Path("temp_analysis/new_data_analysis.txt")
with open(output_file, 'w') as f:
    f.write("NEW DATA STRUCTURE ANALYSIS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Path: data/csvs_human_verified_vv/\n\n")
    f.write(f"Participants: {len(all_participants)}\n")
    f.write(f"Age range: {min(ages):.1f} - {max(ages):.1f} months\n")
    f.write(f"Event types: {sorted(all_event_types.keys())}\n")
    f.write(f"Total presentations: {total_presentations}\n\n")
    f.write(f"event_presentation_id formula:\n")
    f.write(f"  participant + '_' + event + '_' + trial_number_global\n\n")
    f.write(f"Unique IDs: {len(all_event_ids)}\n")
    f.write(f"Duplicates: {len(duplicate_ids)}\n")

print(f"\n✓ Results saved to: {output_file}")
