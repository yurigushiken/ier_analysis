"""
Verify exact age range of infant participants
"""

import csv
from pathlib import Path
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("AGE VERIFICATION")
print("=" * 80)

CHILD_DATA_PATH = Path("data/raw/child-gl")
child_files = list(CHILD_DATA_PATH.glob("*.csv"))

print(f"\nTotal child participant files: {len(child_files)}")

# Collect ages
participant_ages = {}

for csv_file in child_files:
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            first_row = next(reader)

            participant_id = first_row['Participant']
            age_months = float(first_row['participant_age_months'])
            age_years = float(first_row['participant_age_years'])

            participant_ages[participant_id] = {
                'age_months': age_months,
                'age_years': age_years,
                'filename': csv_file.name
            }
    except Exception as e:
        print(f"Error reading {csv_file.name}: {e}")

print(f"\nParticipants processed: {len(participant_ages)}")

# Analyze ages
ages_in_months = [data['age_months'] for data in participant_ages.values()]
ages_sorted = sorted(ages_in_months)

print("\n" + "=" * 80)
print("AGE STATISTICS")
print("=" * 80)

print(f"\nAge in months:")
print(f"  Minimum: {min(ages_in_months):.2f} months")
print(f"  Maximum: {max(ages_in_months):.2f} months")
print(f"  Mean: {sum(ages_in_months) / len(ages_in_months):.2f} months")
print(f"  Median: {ages_sorted[len(ages_sorted)//2]:.2f} months")

# Calculate standard deviation
mean_age = sum(ages_in_months) / len(ages_in_months)
variance = sum((age - mean_age) ** 2 for age in ages_in_months) / len(ages_in_months)
std_dev = variance ** 0.5
print(f"  Std Dev: {std_dev:.2f} months")

# Age distribution
print("\n" + "=" * 80)
print("AGE DISTRIBUTION")
print("=" * 80)

# Round to nearest month for distribution
age_distribution = {}
for age in ages_in_months:
    age_rounded = round(age)
    age_distribution[age_rounded] = age_distribution.get(age_rounded, 0) + 1

print("\nParticipants per age (months):")
for age in sorted(age_distribution.keys()):
    count = age_distribution[age]
    bar = "█" * count
    print(f"  {age:2d} months: {count:2d} participants {bar}")

# Check if within 6-12 month range
print("\n" + "=" * 80)
print("AGE RANGE VERIFICATION")
print("=" * 80)

within_6_12 = sum(1 for age in ages_in_months if 6 <= age <= 12)
below_6 = sum(1 for age in ages_in_months if age < 6)
above_12 = sum(1 for age in ages_in_months if age > 12)

print(f"\nAge range analysis:")
print(f"  Within 6-12 months: {within_6_12} participants ({within_6_12/len(ages_in_months)*100:.1f}%)")
print(f"  Below 6 months: {below_6} participants")
print(f"  Above 12 months: {above_12} participants")

if below_6 > 0:
    print(f"\n⚠️  Found {below_6} participants below 6 months:")
    for participant_id, data in participant_ages.items():
        if data['age_months'] < 6:
            print(f"    {participant_id}: {data['age_months']:.2f} months ({data['filename']})")

if above_12 > 0:
    print(f"\n⚠️  Found {above_12} participants above 12 months:")
    for participant_id, data in participant_ages.items():
        if data['age_months'] > 12:
            print(f"    {participant_id}: {data['age_months']:.2f} months ({data['filename']})")

# Age groups from filenames
print("\n" + "=" * 80)
print("AGE GROUPS FROM FILENAMES")
print("=" * 80)

age_group_counts = {}
for csv_file in child_files:
    filename = csv_file.name
    # Extract age group (e.g., "Eight-months", "Nine-months")
    if '-months-' in filename:
        age_group = filename.split('-months-')[0]
        age_group_counts[age_group] = age_group_counts.get(age_group, 0) + 1

print("\nAge groups from filenames:")
for age_group in sorted(age_group_counts.keys()):
    count = age_group_counts[age_group]
    print(f"  {age_group}-months: {count} participants")

# Detailed participant list
print("\n" + "=" * 80)
print("COMPLETE PARTICIPANT LIST (sorted by age)")
print("=" * 80)

sorted_participants = sorted(participant_ages.items(), key=lambda x: x[1]['age_months'])

print(f"\n{'Participant ID':<25} {'Age (months)':<15} {'Age (years)':<15} {'Filename':<30}")
print("-" * 85)
for participant_id, data in sorted_participants:
    print(f"{participant_id:<25} {data['age_months']:<15.2f} {data['age_years']:<15.2f} {data['filename']:<30}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if within_6_12 == len(ages_in_months):
    print(f"\n✅ CONFIRMED: All {len(ages_in_months)} participants are within 6-12 months range")
elif within_6_12 > 0:
    print(f"\n⚠️  PARTIAL: {within_6_12}/{len(ages_in_months)} participants are within 6-12 months")
    print(f"   Range is actually {min(ages_in_months):.2f} - {max(ages_in_months):.2f} months")
else:
    print(f"\n❌ WARNING: No participants within 6-12 month range")
    print(f"   Actual range: {min(ages_in_months):.2f} - {max(ages_in_months):.2f} months")

# Save results
output_file = Path("temp_analysis/age_verification.txt")
with open(output_file, 'w') as f:
    f.write("AGE VERIFICATION RESULTS\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Total participants: {len(participant_ages)}\n")
    f.write(f"Age range: {min(ages_in_months):.2f} - {max(ages_in_months):.2f} months\n")
    f.write(f"Mean age: {sum(ages_in_months) / len(ages_in_months):.2f} months\n")
    f.write(f"Within 6-12 months: {within_6_12} participants\n")
    if below_6 > 0:
        f.write(f"Below 6 months: {below_6} participants\n")
    if above_12 > 0:
        f.write(f"Above 12 months: {above_12} participants\n")

print(f"\n✓ Results saved to: {output_file}")
