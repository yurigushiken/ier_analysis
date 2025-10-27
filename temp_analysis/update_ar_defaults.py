"""Update all AR modules to use gaze_events.csv by default."""

from pathlib import Path
import re

# AR modules to update
ar_files = [
    "src/analysis/ar2_transitions.py",
    "src/analysis/ar3_social_triplets.py",
    "src/analysis/ar4_dwell_times.py",
    "src/analysis/ar5_development.py",
    "src/analysis/ar6_learning.py",
    "src/analysis/ar7_dissociation.py",
]

# Pattern to find and replace
old_pattern = r'child_path = processed_dir / "gaze_events_child\.csv"\s+default_path = processed_dir / "gaze_events\.csv"\s+if child_path\.exists\(\):\s+path = child_path\s+elif default_path\.exists\(\):'

new_pattern = '''default_path = processed_dir / "gaze_events.csv"
    child_path = processed_dir / "gaze_events_child.csv"

    if default_path.exists():
        path = default_path
    elif child_path.exists():'''

print("="*80)
print("UPDATING AR MODULES TO USE gaze_events.csv BY DEFAULT")
print("="*80)

updated = []
for ar_file in ar_files:
    path = Path(ar_file)
    if not path.exists():
        print(f"⚠️  File not found: {ar_file}")
        continue

    content = path.read_text()

    # Check if pattern exists
    if 'child_path = processed_dir / "gaze_events_child.csv"' in content:
        # Replace: swap the order so default_path is checked first
        new_content = content.replace(
            'child_path = processed_dir / "gaze_events_child.csv"\n    default_path = processed_dir / "gaze_events.csv"\n\n    if child_path.exists():\n        path = child_path\n    elif default_path.exists():',
            'default_path = processed_dir / "gaze_events.csv"\n    child_path = processed_dir / "gaze_events_child.csv"\n\n    if default_path.exists():\n        path = default_path\n    elif child_path.exists():'
        )

        if new_content != content:
            path.write_text(new_content)
            print(f"✓ Updated: {ar_file}")
            updated.append(ar_file)
        else:
            print(f"⚠️  No changes needed: {ar_file}")
    else:
        print(f"ℹ️  Pattern not found: {ar_file}")

print(f"\n{'='*80}")
print(f"COMPLETE: {len(updated)} files updated")
print(f"{'='*80}")

if updated:
    print("\nUpdated files:")
    for f in updated:
        print(f"  - {f}")
