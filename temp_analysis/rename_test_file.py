"""Rename test_gaze_fixations_schema.py to test_gaze_fixations_schema.py."""

from pathlib import Path
import shutil

print("="*80)
print("RENAMING TEST FILE")
print("="*80)

old_path = Path("tests/contract/test_gaze_fixations_schema.py")
new_path = Path("tests/contract/test_gaze_fixations_schema.py")

if old_path.exists():
    shutil.move(str(old_path), str(new_path))
    print(f"  OK: {old_path} -> {new_path}")
elif new_path.exists():
    print(f"  SKIP: {new_path} already exists")
else:
    print(f"  ERROR: {old_path} does not exist")

print(f"\n{'='*80}")
print("COMPLETE")
print(f"{'='*80}")
