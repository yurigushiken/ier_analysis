"""Comprehensive inventory of 'gaze event' terminology throughout codebase."""

import subprocess
from pathlib import Path
from collections import defaultdict

print("="*80)
print("TERMINOLOGY INVENTORY: 'gaze event' → 'gaze fixation'")
print("="*80)

# Define search patterns
patterns = [
    "gaze.event",
    "gaze_event",
    "gazeEvent",
    "GazeEvent",
]

# Define file types to search
file_extensions = [
    "*.py",
    "*.md",
    "*.yaml",
    "*.yml",
    "*.html",
    "*.txt",
    "*.json",
    "*.csv",
]

root = Path(".")
results_by_type = defaultdict(list)
results_by_file = defaultdict(int)

print("\n1. SEARCHING CODEBASE...")
print(f"   Root: {root.resolve()}")
print(f"   Patterns: {patterns}")
print(f"   File types: {file_extensions}")

# Count occurrences by file
for ext in file_extensions:
    try:
        result = subprocess.run(
            ["grep", "-r", "-n", "-i", "-E", "gaze.?event", "--include", ext, "."],
            capture_output=True,
            text=True,
            cwd=root
        )

        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    file_path = line.split(':', 1)[0]
                    results_by_file[file_path] += 1

                    # Categorize by file type
                    if file_path.endswith('.py'):
                        results_by_type['Python Code'].append(file_path)
                    elif file_path.endswith(('.md', '.txt')):
                        results_by_type['Documentation'].append(file_path)
                    elif file_path.endswith(('.yaml', '.yml')):
                        results_by_type['Configuration'].append(file_path)
                    elif file_path.endswith('.html'):
                        results_by_type['Templates'].append(file_path)
                    elif file_path.endswith('.json'):
                        results_by_type['JSON/Contracts'].append(file_path)
                    elif file_path.endswith('.csv'):
                        results_by_type['Data Files'].append(file_path)
    except Exception as e:
        print(f"   Error searching {ext}: {e}")

# De-duplicate
for category in results_by_type:
    results_by_type[category] = list(set(results_by_type[category]))

print(f"\n2. SUMMARY BY FILE TYPE")
print("="*80)

total_files = 0
total_occurrences = 0

for category, files in sorted(results_by_type.items()):
    occurrences = sum(results_by_file[f] for f in files)
    print(f"\n{category}:")
    print(f"   Files: {len(files)}")
    print(f"   Total occurrences: {occurrences}")
    total_files += len(files)
    total_occurrences += occurrences

print(f"\n{'='*80}")
print(f"TOTAL: {total_files} files, {total_occurrences} occurrences")
print(f"{'='*80}")

print("\n3. DETAILED FILE LIST")
print("="*80)

for category, files in sorted(results_by_type.items()):
    print(f"\n{category}:")
    for file in sorted(files):
        count = results_by_file[file]
        print(f"   {file} ({count} occurrence{'s' if count > 1 else ''})")

print("\n4. HIGH-IMPACT FILES (>10 occurrences)")
print("="*80)

high_impact = [(f, c) for f, c in results_by_file.items() if c > 10]
high_impact.sort(key=lambda x: x[1], reverse=True)

for file, count in high_impact:
    print(f"   {count:3d}  {file}")

print("\n5. SPECIFIC TERMS TO REPLACE")
print("="*80)

term_map = {
    "gaze_event": "gaze_fixation",
    "gaze event": "gaze fixation",
    "Gaze Event": "Gaze Fixation",
    "GazeEvent": "GazeFixation",
    "gazeEvent": "gazeFixation",
    "gaze-event": "gaze-fixation",
    "gaze_events": "gaze_fixations",
    "gaze events": "gaze fixations",
    "Gaze Events": "Gaze Fixations",
}

print("\nTerm mapping:")
for old, new in term_map.items():
    print(f"   '{old}' → '{new}'")

print("\n6. FILES TO RENAME")
print("="*80)

files_to_rename = [
    ("data/processed/gaze_events.csv", "data/processed/gaze_fixations.csv"),
    ("data/processed/gaze_events_child.csv", "data/processed/gaze_fixations_child.csv"),
    ("data/processed/gaze_events_adult.csv", "data/processed/gaze_fixations_adult.csv"),
    ("src/preprocessing/gaze_detector.py", "src/preprocessing/gaze_fixation_detector.py"),
]

for old, new in files_to_rename:
    exists = "EXISTS" if Path(old).exists() else "NOT FOUND"
    print(f"   {old}")
    print(f"   → {new}")
    print(f"      Status: {exists}")
    print()

print("\n7. CRITICAL COMPONENTS AFFECTED")
print("="*80)

critical_components = {
    "Data Pipeline": [
        "src/preprocessing/gaze_detector.py",
        "src/preprocessing/master_log_generator.py",
    ],
    "Analysis Modules": [
        "src/analysis/ar1_gaze_duration.py",
        "src/analysis/ar2_transitions.py",
        "src/analysis/ar3_social_triplets.py",
        "src/analysis/ar4_dwell_times.py",
        "src/analysis/ar5_development.py",
        "src/analysis/ar6_learning.py",
        "src/analysis/ar7_dissociation.py",
    ],
    "Specifications": [
        "specs/001-infant-event-analysis/spec.md",
        "specs/001-infant-event-analysis/plan.md",
        "specs/001-infant-event-analysis/data-model.md",
    ],
    "Documentation": [
        "README.md",
        "MENTORSHIP_DATA_FLOW.md",
        "specs/001-infant-event-analysis/quickstart.md",
    ],
    "Templates": [
        "templates/ar1_template.html",
        "templates/base_report.html",
    ],
}

for component, files in critical_components.items():
    print(f"\n{component}:")
    for file in files:
        if Path(file).exists():
            count = results_by_file.get(file, 0)
            if count > 0:
                print(f"   {file} ({count} occurrences)")
            else:
                print(f"   {file} (check manually)")
        else:
            print(f"   {file} (NOT FOUND)")

print("\n" + "="*80)
print("INVENTORY COMPLETE")
print("="*80)
