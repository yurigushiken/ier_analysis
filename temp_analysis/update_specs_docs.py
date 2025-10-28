"""Update specification and documentation files with gaze_fixations terminology."""

from pathlib import Path

print("="*80)
print("UPDATING SPECS AND DOCS: gaze_fixations -> gaze_fixations")
print("="*80)

# Files to update
spec_files = [
    "specs/001-infant-event-analysis/spec.md",
    "specs/001-infant-event-analysis/plan.md",
    "specs/001-infant-event-analysis/tasks.md",
    "specs/001-infant-event-analysis/quickstart.md",
    "MENTORSHIP_DATA_FLOW.md",
    "README.md",
    "CHANGELOG.md",
]

replacements = [
    # File names
    ('gaze_fixations.csv', 'gaze_fixations.csv'),
    ('gaze_fixations_child.csv', 'gaze_fixations_child.csv'),
    ('gaze_fixations_adult.csv', 'gaze_fixations_adult.csv'),

    # Variable names
    ('gaze_fixations', 'gaze_fixations'),

    # Function/class names
    ('detect_gaze_fixations', 'detect_gaze_fixations'),
    ('GazeFixation', 'GazeFixation'),

    # Text
    ('gaze fixation', 'gaze fixation'),
    ('Gaze fixation', 'Gaze fixation'),
    ('gaze-event', 'gaze-fixation'),
]

updated = []
skipped = []

for file_path_str in spec_files:
    path = Path(file_path_str)

    if not path.exists():
        print(f"  SKIP: {file_path_str} (does not exist)")
        skipped.append(file_path_str)
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
            print(f"  OK: {file_path_str}")
            updated.append(file_path_str)
        else:
            print(f"  NO CHANGE: {file_path_str}")
            skipped.append(file_path_str)

    except Exception as e:
        print(f"  ERROR: {file_path_str} - {e}")
        skipped.append(file_path_str)

print(f"\n{'='*80}")
print(f"COMPLETE: {len(updated)} files updated")
print(f"{'='*80}")

if updated:
    print("\nUpdated files:")
    for f in updated:
        print(f"  {f}")
