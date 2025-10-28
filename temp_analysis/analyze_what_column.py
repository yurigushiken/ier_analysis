"""
Analysis of the 'What' column in verified data
Purpose: Understand all unique values in the 'What' column and detect anomalies
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("ANALYSIS OF 'WHAT' COLUMN IN VERIFIED DATA")
print("=" * 80)

# Data paths
CHILD_DATA_PATH = Path("data/csvs_human_verified_vv/child")
ADULT_DATA_PATH = Path("data/csvs_human_verified_vv/adult")

# Expected values based on study-info.md
EXPECTED_WHAT_VALUES = {'no', 'screen', 'woman', 'man', 'toy', 'toy2'}

# Track all unique values
all_what_values = Counter()
all_what_where_pairs = Counter()
anomalies = []  # (filename, row_num, what_value, where_value)

# Track by participant
participant_what_values = defaultdict(set)

print("\n" + "=" * 80)
print("1. ANALYZING CHILD PARTICIPANTS")
print("=" * 80)

child_files = sorted(CHILD_DATA_PATH.glob("*.csv"))
print(f"\nTotal child CSV files: {len(child_files)}")

for csv_file in child_files:
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                what = row.get('What', '').strip()
                where = row.get('Where', '').strip()

                # Count occurrences
                all_what_values[what] += 1
                all_what_where_pairs[f"{what},{where}"] += 1

                # Track per participant
                participant_id = row.get('Participant', csv_file.stem)
                participant_what_values[participant_id].add(what)

                # Check for anomalies (unexpected values)
                if what not in EXPECTED_WHAT_VALUES:
                    anomalies.append((csv_file.name, row_num, what, where, 'child'))

    except Exception as e:
        print(f"Error processing {csv_file.name}: {e}")

print("\n" + "=" * 80)
print("2. ANALYZING ADULT PARTICIPANTS")
print("=" * 80)

adult_files = sorted(ADULT_DATA_PATH.glob("*.csv"))
print(f"\nTotal adult CSV files: {len(adult_files)}")

for csv_file in adult_files:
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                what = row.get('What', '').strip()
                where = row.get('Where', '').strip()

                # Count occurrences
                all_what_values[what] += 1
                all_what_where_pairs[f"{what},{where}"] += 1

                # Track per participant
                participant_id = row.get('Participant', csv_file.stem)
                participant_what_values[participant_id].add(what)

                # Check for anomalies
                if what not in EXPECTED_WHAT_VALUES:
                    anomalies.append((csv_file.name, row_num, what, where, 'adult'))

    except Exception as e:
        print(f"Error processing {csv_file.name}: {e}")

# ============================================================================
# RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("3. UNIQUE VALUES IN 'WHAT' COLUMN")
print("=" * 80)

print(f"\nTotal unique values: {len(all_what_values)}")
print("\nAll unique 'What' values (with counts):")
for what_value in sorted(all_what_values.keys()):
    count = all_what_values[what_value]
    is_expected = "✓" if what_value in EXPECTED_WHAT_VALUES else "✗ UNEXPECTED"
    print(f"  {what_value:15s} : {count:>10,} occurrences {is_expected}")

print("\n" + "=" * 80)
print("4. EXPECTED VS ACTUAL VALUES")
print("=" * 80)

print(f"\nExpected values (from study-info.md): {sorted(EXPECTED_WHAT_VALUES)}")
print(f"Actual values found: {sorted(all_what_values.keys())}")

unexpected = set(all_what_values.keys()) - EXPECTED_WHAT_VALUES
missing = EXPECTED_WHAT_VALUES - set(all_what_values.keys())

if unexpected:
    print(f"\n⚠ UNEXPECTED values found: {sorted(unexpected)}")
else:
    print(f"\n✓ No unexpected values found")

if missing:
    print(f"\n⚠ MISSING expected values: {sorted(missing)}")
else:
    print(f"\n✓ All expected values are present")

print("\n" + "=" * 80)
print("5. WHAT + WHERE COMBINATIONS")
print("=" * 80)

print(f"\nTotal unique What+Where combinations: {len(all_what_where_pairs)}")
print("\nTop combinations (by frequency):")
for i, (pair, count) in enumerate(all_what_where_pairs.most_common(20), 1):
    print(f"  {i:2d}. {pair:25s} : {count:>10,}")

print("\n" + "=" * 80)
print("6. ANOMALY REPORT")
print("=" * 80)

if anomalies:
    print(f"\n⚠ Found {len(anomalies)} anomalies (unexpected 'What' values):\n")

    # Group by file
    anomalies_by_file = defaultdict(list)
    for filename, row_num, what, where, participant_type in anomalies:
        anomalies_by_file[filename].append((row_num, what, where, participant_type))

    for filename in sorted(anomalies_by_file.keys()):
        file_anomalies = anomalies_by_file[filename]
        participant_type = file_anomalies[0][3]
        print(f"\nFile: {filename} ({participant_type})")
        print(f"  Anomalies: {len(file_anomalies)}")

        # Show first 5 anomalies per file
        for row_num, what, where, _ in file_anomalies[:5]:
            print(f"    Row {row_num}: What='{what}', Where='{where}'")

        if len(file_anomalies) > 5:
            print(f"    ... and {len(file_anomalies) - 5} more")
else:
    print("\n✓ No anomalies detected! All 'What' values match expected values.")

print("\n" + "=" * 80)
print("7. SUMMARY")
print("=" * 80)

print(f"\nDataset Summary:")
print(f"  Child participants: {len(child_files)}")
print(f"  Adult participants: {len(adult_files)}")
print(f"  Total participants: {len(child_files) + len(adult_files)}")
print(f"  Total rows analyzed: {sum(all_what_values.values()):,}")

print(f"\n'What' Column Summary:")
print(f"  Unique values: {len(all_what_values)}")
print(f"  Expected values: {len(EXPECTED_WHAT_VALUES)}")
print(f"  Unexpected values: {len(unexpected)}")
print(f"  Anomalous rows: {len(anomalies)}")

if not unexpected and not anomalies:
    print("\n✓ DATA QUALITY: EXCELLENT")
    print("  All 'What' values conform to expectations!")
else:
    print("\n⚠ DATA QUALITY: NEEDS ATTENTION")
    print(f"  Please review the {len(anomalies)} anomalous entries above.")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Save detailed report
output_path = Path("temp_analysis/what_column_analysis.txt")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("WHAT COLUMN ANALYSIS REPORT\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"Total unique 'What' values: {len(all_what_values)}\n\n")

    f.write("All values with counts:\n")
    for what_value in sorted(all_what_values.keys()):
        count = all_what_values[what_value]
        f.write(f"  {what_value}: {count:,}\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("ANOMALIES\n")
    f.write("=" * 80 + "\n\n")

    if anomalies:
        f.write(f"Total anomalies: {len(anomalies)}\n\n")
        for filename, row_num, what, where, participant_type in anomalies:
            f.write(f"{filename} ({participant_type}), Row {row_num}: What='{what}', Where='{where}'\n")
    else:
        f.write("No anomalies detected.\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("WHAT+WHERE COMBINATIONS\n")
    f.write("=" * 80 + "\n\n")

    for pair, count in all_what_where_pairs.most_common():
        f.write(f"{pair}: {count:,}\n")

print(f"\n✓ Detailed report saved to: {output_path}")
