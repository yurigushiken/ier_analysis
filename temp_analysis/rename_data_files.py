"""Rename gaze_fixations.csv files to gaze_fixations.csv."""

from pathlib import Path
import shutil

print("="*80)
print("RENAMING DATA FILES: gaze_fixations -> gaze_fixations")
print("="*80)

# Files to rename
files_to_rename = [
    "data/processed/gaze_fixations.csv",
    "data/processed/gaze_fixations_child.csv",
    "data/processed/gaze_fixations_adult.csv",
]

renamed = []
skipped = []

for old_path_str in files_to_rename:
    old_path = Path(old_path_str)

    if not old_path.exists():
        print(f"  SKIP: {old_path} (does not exist)")
        skipped.append(old_path_str)
        continue

    # Generate new path
    new_name = old_path.name.replace("gaze_fixations", "gaze_fixations")
    new_path = old_path.parent / new_name

    # Check if target already exists
    if new_path.exists():
        print(f"  WARNING: {new_path} already exists")
        user_input = input(f"    Overwrite? (y/n): ")
        if user_input.lower() != 'y':
            print(f"    Skipped")
            skipped.append(old_path_str)
            continue

    # Rename
    shutil.move(str(old_path), str(new_path))
    print(f"  OK: {old_path} -> {new_path}")
    renamed.append((old_path_str, str(new_path)))

print(f"\n{'='*80}")
print(f"COMPLETE: {len(renamed)} files renamed, {len(skipped)} skipped")
print(f"{'='*80}")

if renamed:
    print("\nRenamed files:")
    for old, new in renamed:
        print(f"  {old} -> {new}")

if skipped:
    print("\nSkipped files:")
    for f in skipped:
        print(f"  {f}")
