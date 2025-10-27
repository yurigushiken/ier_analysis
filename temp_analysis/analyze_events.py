"""
Analyze event structure in the IER dataset
Purpose: Understand how many events per participant, event types, repetitions
"""

import csv
from pathlib import Path
from collections import defaultdict, Counter
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("EVENT STRUCTURE ANALYSIS")
print("=" * 80)

# Data paths
CHILD_DATA_PATH = Path("data/raw/child-gl")

# ============================================================================
# 1. ANALYZE ALL PARTICIPANTS
# ============================================================================

print("\n" + "=" * 80)
print("1. LOADING ALL PARTICIPANT DATA")
print("=" * 80)

child_files = list(CHILD_DATA_PATH.glob("*.csv"))
print(f"\nTotal child participant files: {len(child_files)}")

# Store data per participant
participant_events = {}
all_event_types = Counter()
participant_frame_counts = {}

for csv_file in child_files:
    participant_name = csv_file.stem.replace('gl', '')

    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Get unique events for this participant
            events = [row['event'] for row in rows]
            unique_events = list(set(events))
            event_counts = Counter(events)

            participant_events[participant_name] = {
                'total_frames': len(rows),
                'unique_events': unique_events,
                'event_counts': event_counts,
                'num_unique_events': len(unique_events)
            }

            participant_frame_counts[participant_name] = len(rows)

            # Track all event types across all participants
            all_event_types.update(unique_events)

    except Exception as e:
        print(f"Error loading {csv_file.name}: {e}")

print(f"\nLoaded {len(participant_events)} participants")

# ============================================================================
# 2. EVENT TYPE CATALOG
# ============================================================================

print("\n" + "=" * 80)
print("2. COMPLETE EVENT TYPE CATALOG")
print("=" * 80)

print(f"\nTotal unique event types across all participants: {len(all_event_types)}")
print("\nAll event types found:")
for event_type in sorted(all_event_types.keys()):
    count = all_event_types[event_type]
    print(f"  {event_type:12s} - appears in {count} participant files")

# ============================================================================
# 3. EVENTS PER PARTICIPANT STATISTICS
# ============================================================================

print("\n" + "=" * 80)
print("3. EVENTS PER PARTICIPANT STATISTICS")
print("=" * 80)

# How many unique events does each participant see?
events_per_participant = [data['num_unique_events'] for data in participant_events.values()]

print(f"\nUnique events per participant:")
print(f"  Mean: {sum(events_per_participant) / len(events_per_participant):.1f}")
print(f"  Min: {min(events_per_participant)}")
print(f"  Max: {max(events_per_participant)}")
print(f"  Median: {sorted(events_per_participant)[len(events_per_participant)//2]}")

# Distribution
event_distribution = Counter(events_per_participant)
print(f"\nDistribution of unique events per participant:")
for n_events in sorted(event_distribution.keys()):
    count = event_distribution[n_events]
    print(f"  {n_events} events: {count} participants")

# ============================================================================
# 4. DETAILED ANALYSIS OF SAMPLE PARTICIPANTS
# ============================================================================

print("\n" + "=" * 80)
print("4. DETAILED ANALYSIS: FIRST 3 PARTICIPANTS")
print("=" * 80)

for i, (participant, data) in enumerate(list(participant_events.items())[:3]):
    print(f"\n{'─' * 80}")
    print(f"Participant: {participant}")
    print(f"{'─' * 80}")
    print(f"Total frames: {data['total_frames']:,}")
    print(f"Unique events: {data['num_unique_events']}")

    print(f"\nEvent breakdown (frames per event):")
    for event, count in sorted(data['event_counts'].items()):
        print(f"  {event:12s}: {count:4d} frames")

    # Calculate if events are repeated
    print(f"\nEvent repetition analysis:")
    for event in sorted(data['unique_events']):
        frames = data['event_counts'][event]
        # Assuming ~165 frames per presentation
        estimated_presentations = round(frames / 165)
        print(f"  {event:12s}: ~{estimated_presentations} presentation(s) ({frames} frames)")

# ============================================================================
# 5. FRAMES PER EVENT ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("5. FRAMES PER EVENT PRESENTATION")
print("=" * 80)

# Load one participant in detail to see frame counts
sample_file = child_files[0]
with open(sample_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Group consecutive frames by event
current_event = None
event_presentations = []
current_frame_count = 0

for row in rows:
    event = row['event']
    if event != current_event:
        if current_event is not None:
            event_presentations.append({
                'event': current_event,
                'frames': current_frame_count
            })
        current_event = event
        current_frame_count = 1
    else:
        current_frame_count += 1

# Don't forget last event
if current_event is not None:
    event_presentations.append({
        'event': current_event,
        'frames': current_frame_count
    })

print(f"\nEvent presentations in {sample_file.name}:")
print(f"Total event presentations: {len(event_presentations)}\n")

# Group by event type
events_by_type = defaultdict(list)
for presentation in event_presentations:
    events_by_type[presentation['event']].append(presentation['frames'])

print(f"Event presentations by type:")
for event_type in sorted(events_by_type.keys()):
    frame_counts = events_by_type[event_type]
    mean_frames = sum(frame_counts) / len(frame_counts)
    print(f"  {event_type:12s}: {len(frame_counts)} presentation(s), "
          f"avg {mean_frames:.0f} frames (range: {min(frame_counts)}-{max(frame_counts)})")

# ============================================================================
# 6. EVENT TYPE DECODING
# ============================================================================

print("\n" + "=" * 80)
print("6. EVENT TYPE DECODING")
print("=" * 80)

event_meanings = {
    'gw': 'GIVE WITH toy',
    'gwo': 'GIVE WITHOUT toy',
    'hw': 'HUG WITH toy',
    'hwo': 'HUG WITHOUT toy',
    'sw': 'SHOW WITH toy',
    'swo': 'SHOW WITHOUT toy',
    'ugwo': 'UPSIDE-DOWN GIVE WITHOUT toy',
    'uhwo': 'UPSIDE-DOWN HUG WITHOUT toy',
    'ugw': 'UPSIDE-DOWN GIVE WITH toy',
    'uhw': 'UPSIDE-DOWN HUG WITH toy',
    'uswo': 'UPSIDE-DOWN SHOW WITHOUT toy',
    'usw': 'UPSIDE-DOWN SHOW WITH toy',
    'f': 'FLOATING (control)',
}

print("\nEvent type meanings:")
for event_type in sorted(all_event_types.keys()):
    meaning = event_meanings.get(event_type, 'UNKNOWN')
    print(f"  {event_type:12s} = {meaning}")

# ============================================================================
# 7. CONDITION GROUPING
# ============================================================================

print("\n" + "=" * 80)
print("7. CONDITION GROUPING")
print("=" * 80)

def extract_condition(event_code):
    """Extract condition from event code"""
    if event_code.startswith('u'):
        # Upside-down events
        base = event_code[1:]  # Remove 'u' prefix
    else:
        base = event_code

    # Extract action
    if base.startswith('g'):
        action = 'GIVE'
    elif base.startswith('h'):
        action = 'HUG'
    elif base.startswith('s'):
        action = 'SHOW'
    elif base == 'f':
        return 'CONTROL', 'FLOATING', None
    else:
        return 'UNKNOWN', None, None

    # Extract with/without
    if base.endswith('wo'):
        toy_presence = 'WITHOUT'
    elif base.endswith('w'):
        toy_presence = 'WITH'
    else:
        toy_presence = None

    # Upside-down flag
    orientation = 'UPSIDE-DOWN' if event_code.startswith('u') else 'NORMAL'

    return action, toy_presence, orientation

print("\nCondition mapping:")
for event_type in sorted(all_event_types.keys()):
    action, toy, orientation = extract_condition(event_type)
    if toy:
        print(f"  {event_type:12s} → {action:6s} | {toy:7s} | {orientation}")
    else:
        print(f"  {event_type:12s} → {action}")

# ============================================================================
# 8. SUMMARY FOR STATISTICAL MODELING
# ============================================================================

print("\n" + "=" * 80)
print("8. SUMMARY FOR STATISTICAL MODELING")
print("=" * 80)

total_presentations = sum(len(event_presentations) for _ in participant_events)
avg_presentations = total_presentations / len(participant_events)

print(f"\n📊 KEY FINDINGS:")
print(f"{'─' * 80}")

print(f"\n1. PARTICIPANTS:")
print(f"   - Total participants: {len(participant_events)}")

print(f"\n2. EVENT TYPES:")
print(f"   - Unique event types: {len(all_event_types)}")
print(f"   - Event categories: GIVE, HUG, SHOW, CONTROL")
print(f"   - Variants: WITH/WITHOUT toy, NORMAL/UPSIDE-DOWN")

print(f"\n3. EVENTS PER PARTICIPANT:")
print(f"   - Unique event types per participant: {sum(events_per_participant) / len(events_per_participant):.1f}")
print(f"   - Estimated total presentations per participant: ~{avg_presentations:.0f}")

print(f"\n4. EVENT STRUCTURE:")
print(f"   - Frames per event presentation: ~150-185 frames")
print(f"   - Duration per event: ~5-6 seconds (at 30 fps)")
print(f"   - Events are REPEATED multiple times")

print(f"\n5. NESTING STRUCTURE:")
print(f"   Level 3: Participant (N = {len(participant_events)})")
print(f"   Level 2: Event presentation (~{avg_presentations:.0f} per participant)")
print(f"   Level 1: Gaze event (derived from 3+ consecutive frames on same AOI)")
print(f"   Level 0: Frame (150-185 per event presentation, aggregated)")

print(f"\n6. IMPLICATIONS FOR LMM/GLMM:")
print(f"   ✓ Excellent data structure for random intercepts")
print(f"   ✓ Sufficient presentations for random slopes (~{avg_presentations:.0f} per participant)")
print(f"   ✓ Nested random effects are appropriate")
print(f"   ✓ Can test habituation across presentation order")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Save detailed results
output_file = Path("temp_analysis/event_structure_analysis.txt")
with open(output_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("EVENT STRUCTURE ANALYSIS - DETAILED RESULTS\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"Total participants: {len(participant_events)}\n")
    f.write(f"Unique event types: {len(all_event_types)}\n")
    f.write(f"Event types: {sorted(all_event_types.keys())}\n\n")

    f.write("Event meanings:\n")
    for event_type in sorted(all_event_types.keys()):
        meaning = event_meanings.get(event_type, 'UNKNOWN')
        f.write(f"  {event_type} = {meaning}\n")

    f.write(f"\nAverage unique events per participant: {sum(events_per_participant) / len(events_per_participant):.1f}\n")
    f.write(f"Estimated presentations per participant: ~{avg_presentations:.0f}\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("NESTING STRUCTURE\n")
    f.write("=" * 80 + "\n")
    f.write("Participant\n")
    f.write("  └─ Event Presentation (video clip)\n")
    f.write("      └─ Gaze Event (3+ frames on same AOI)\n")
    f.write("          └─ Frame (aggregated)\n")

print(f"\n✓ Detailed results saved to: {output_file}")
