"""Comprehensive verification of terminology migration across ALL files."""

from pathlib import Path
import re

print("="*80)
print("COMPREHENSIVE TERMINOLOGY MIGRATION VERIFICATION")
print("="*80)

# Search all relevant file types
extensions = [".py", ".md", ".html", ".yaml", ".yml", ".txt", ".json"]
exclude_dirs = {
    ".git",
    "__pycache__",
    "venv",
    "env",
    ".pytest_cache",
    ".mypy_cache",
    "backup_before_terminology_migration",  # Exclude our backup
    "node_modules",
    ".venv"
}

# Track findings
files_with_old_terminology = {}
total_files_scanned = 0

print("\nScanning codebase...")

for ext in extensions:
    for path in Path(".").rglob(f"*{ext}"):
        # Skip excluded directories
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue

        # Skip verification scripts themselves
        if "verify_migration" in str(path) or "comprehensive_verification" in str(path):
            continue

        total_files_scanned += 1

        try:
            content = path.read_text(encoding='utf-8')

            # Search for old terminology patterns
            old_patterns = [
                "gaze_fixations",
                "gaze fixation",
                "Gaze fixation",
                "Gaze Fixation",
                "GAZE EVENT",
                "detect_gaze_fixations",
                "GazeFixation",
                "test_gaze_fixations",
                "gaze_fixations_file",
                "gaze_fixations.csv",
                "gaze_fixations_child",
                "gaze_fixations_adult",
            ]

            found_patterns = []
            for pattern in old_patterns:
                if pattern in content:
                    # Count occurrences
                    count = content.count(pattern)
                    found_patterns.append(f"{pattern} ({count}x)")

            if found_patterns:
                files_with_old_terminology[str(path)] = found_patterns

        except Exception as e:
            # Skip binary files or files that can't be read
            pass

print(f"\nScanned {total_files_scanned} files")
print("="*80)

if files_with_old_terminology:
    print(f"\n[WARNING] Found {len(files_with_old_terminology)} files with old terminology:\n")

    # Categorize by directory
    specs_files = []
    src_files = []
    test_files = []
    config_files = []
    doc_files = []
    other_files = []

    for file_path, patterns in files_with_old_terminology.items():
        if "specs" in file_path or ".specify" in file_path:
            specs_files.append((file_path, patterns))
        elif "src" in file_path:
            src_files.append((file_path, patterns))
        elif "test" in file_path:
            test_files.append((file_path, patterns))
        elif "config" in file_path:
            config_files.append((file_path, patterns))
        elif file_path.endswith(".md") or "doc" in file_path.lower():
            doc_files.append((file_path, patterns))
        else:
            other_files.append((file_path, patterns))

    # Report by category
    if specs_files:
        print("SPECS/SPECKIT FILES:")
        for file_path, patterns in specs_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()

    if src_files:
        print("SOURCE CODE FILES:")
        for file_path, patterns in src_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()

    if test_files:
        print("TEST FILES:")
        for file_path, patterns in test_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()

    if config_files:
        print("CONFIG FILES:")
        for file_path, patterns in config_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()

    if doc_files:
        print("DOCUMENTATION FILES:")
        for file_path, patterns in doc_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()

    if other_files:
        print("OTHER FILES:")
        for file_path, patterns in other_files:
            print(f"  {file_path}")
            for pattern in patterns:
                print(f"    - {pattern}")
        print()
else:
    print("\n[SUCCESS] No files found with old terminology!")
    print("Migration appears to be complete.")

print("="*80)
print("VERIFICATION COMPLETE")
print("="*80)
