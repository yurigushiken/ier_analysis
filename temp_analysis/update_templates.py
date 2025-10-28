"""Update HTML templates with gaze_fixations terminology."""

from pathlib import Path

print("="*80)
print("UPDATING HTML TEMPLATES: gaze_fixations -> gaze_fixations")
print("="*80)

# Find all template files
template_files = list(Path("templates").rglob("*.html"))

replacements = [
    # Text in templates
    ('gaze fixation', 'gaze fixation'),
    ('Gaze fixation', 'Gaze fixation'),
    ('gaze-event', 'gaze-fixation'),
]

updated = []
skipped = []

for path in template_files:
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
            print(f"  NO CHANGE: {path}")
            skipped.append(str(path))

    except Exception as e:
        print(f"  ERROR: {path} - {e}")
        skipped.append(str(path))

print(f"\n{'='*80}")
print(f"COMPLETE: {len(updated)} files updated")
print(f"{'='*80}")

if updated:
    print("\nUpdated files:")
    for f in updated:
        print(f"  {f}")
