"""Update test files with gaze_fixations terminology."""

from pathlib import Path

print("="*80)
print("UPDATING TEST FILES: gaze_fixations -> gaze_fixations")
print("="*80)

# Find all test files
test_files = list(Path("tests").rglob("*.py"))

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

    # Text in comments/docstrings
    ('gaze fixation', 'gaze fixation'),
    ('Gaze fixation', 'Gaze fixation'),
]

updated = []
skipped = []

for path in test_files:
    if path.name == "__init__.py":
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
            print(f"  OK: {path}")
            updated.append(str(path))
        else:
            # Don't print skipped files to reduce noise
            skipped.append(str(path))

    except Exception as e:
        print(f"  ERROR: {path} - {e}")
        skipped.append(str(path))

print(f"\n{'='*80}")
print(f"COMPLETE: {len(updated)} files updated, {len(skipped)} no changes needed")
print(f"{'='*80}")

if updated:
    print("\nUpdated files:")
    for f in updated:
        print(f"  {f}")
