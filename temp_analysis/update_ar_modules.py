"""Update all AR modules with gaze_fixations terminology."""

from pathlib import Path
import re

print("="*80)
print("UPDATING AR MODULES: gaze_fixations -> gaze_fixations")
print("="*80)

# AR modules to update
ar_files = [
    "src/analysis/ar1_gaze_duration.py",
    "src/analysis/ar2_transitions.py",
    "src/analysis/ar3_social_triplets.py",
    "src/analysis/ar4_dwell_times.py",
    "src/analysis/ar5_development.py",
    "src/analysis/ar6_learning.py",
    "src/analysis/ar7_dissociation.py",
]

replacements = [
    # File names in paths
    ('gaze_fixations.csv', 'gaze_fixations.csv'),
    ('gaze_fixations_child.csv', 'gaze_fixations_child.csv'),
    ('gaze_fixations_adult.csv', 'gaze_fixations_adult.csv'),

    # Variable names
    ('gaze_fixations', 'gaze_fixations'),

    # Function names (but preserve GazeFixation class name if it appears in imports)
    ('detect_gaze_fixations', 'detect_gaze_fixations'),

    # Comments and docstrings
    ('gaze fixation', 'gaze fixation'),
    ('Gaze fixation', 'Gaze fixation'),
    ('gaze-event', 'gaze-fixation'),
]

updated = []
errors = []

for ar_file in ar_files:
    path = Path(ar_file)

    if not path.exists():
        print(f"  SKIP: {ar_file} (does not exist)")
        errors.append(ar_file)
        continue

    try:
        content = path.read_text(encoding='utf-8')
        original_content = content

        # Apply all replacements
        for old, new in replacements:
            content = content.replace(old, new)

        # Check if anything changed
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"  OK: {ar_file}")
            updated.append(ar_file)
        else:
            print(f"  SKIP: {ar_file} (no changes needed)")

    except Exception as e:
        print(f"  ERROR: {ar_file} - {e}")
        errors.append(ar_file)

print(f"\n{'='*80}")
print(f"COMPLETE: {len(updated)} files updated")
print(f"{'='*80}")

if updated:
    print("\nUpdated files:")
    for f in updated:
        print(f"  {f}")

if errors:
    print("\nErrors/Skipped:")
    for f in errors:
        print(f"  {f}")
