"""Verify the terminology migration was successful."""

from pathlib import Path
import re

print("="*80)
print("TERMINOLOGY MIGRATION VERIFICATION")
print("="*80)

# Check 1: Data files exist
print("\n1. DATA FILES")
expected_files = [
    "data/processed/gaze_fixations.csv",
    "data/processed/gaze_fixations_child.csv",
    "data/processed/gaze_fixations_adult.csv",
]

for file_path in expected_files:
    path = Path(file_path)
    status = "OK" if path.exists() else "MISSING"
    print(f"  [{status}] {file_path}")

# Check 2: Old files should not exist
print("\n2. OLD FILES (should NOT exist)")
old_files = [
    "data/processed/gaze_fixations.csv",
    "data/processed/gaze_fixations_child.csv",
    "data/processed/gaze_fixations_adult.csv",
    "tests/contract/test_gaze_fixations_schema.py",
]

for file_path in old_files:
    path = Path(file_path)
    status = "OK (removed)" if not path.exists() else "WARNING (still exists)"
    print(f"  [{status}] {file_path}")

# Check 3: Key files use new terminology
print("\n3. KEY SOURCE FILES")
key_files = [
    "src/preprocessing/gaze_detector.py",
    "src/preprocessing/master_log_generator.py",
    "src/analysis/ar1_gaze_duration.py",
]

for file_path in key_files:
    path = Path(file_path)
    if not path.exists():
        print(f"  [MISSING] {file_path}")
        continue

    content = path.read_text(encoding='utf-8')

    # Count occurrences of old vs new terminology
    old_count = content.count("gaze_fixations")
    new_count = content.count("gaze_fixations")

    if old_count > 0:
        print(f"  [WARNING] {file_path}: Still has {old_count} 'gaze_fixations' references")
    else:
        print(f"  [OK] {file_path}: {new_count} 'gaze_fixations' references, 0 old references")

# Check 4: Search entire codebase for remaining old references
print("\n4. CODEBASE SCAN")
print("  Searching for remaining 'gaze_fixations' references...")

extensions = [".py", ".md", ".html", ".yaml", ".yml"]
exclude_dirs = {".git", "__pycache__", "venv", "env", ".pytest_cache", ".mypy_cache", "temp_analysis"}

old_references = []

for ext in extensions:
    for path in Path(".").rglob(f"*{ext}"):
        # Skip excluded directories
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue

        try:
            content = path.read_text(encoding='utf-8')

            # Look for old terminology (but exclude this verification script itself)
            if "gaze_fixations" in content or "gaze fixation" in content:
                # Don't count backup files or this verification script
                if "backup" in str(path).lower() or "verify_migration" in str(path):
                    continue

                old_references.append(str(path))
        except Exception:
            pass

if old_references:
    print(f"  [WARNING] Found {len(old_references)} files with old references:")
    for ref in old_references[:10]:  # Show first 10
        print(f"    - {ref}")
    if len(old_references) > 10:
        print(f"    ... and {len(old_references) - 10} more")
else:
    print(f"  [OK] No old references found!")

# Check 5: Import statements
print("\n5. IMPORT STATEMENTS")
import_files = [
    "src/preprocessing/master_log_generator.py",
    "src/analysis/ar1_gaze_duration.py",
]

for file_path in import_files:
    path = Path(file_path)
    if not path.exists():
        print(f"  [MISSING] {file_path}")
        continue

    content = path.read_text(encoding='utf-8')

    if "from src.preprocessing.gaze_detector import detect_gaze_fixations" in content:
        print(f"  [OK] {file_path}: Uses correct import")
    elif "detect_gaze_fixations" in content:
        print(f"  [WARNING] {file_path}: Still imports detect_gaze_fixations")
    else:
        print(f"  [INFO] {file_path}: No gaze detection imports")

print(f"\n{'='*80}")
print("VERIFICATION COMPLETE")
print(f"{'='*80}")
