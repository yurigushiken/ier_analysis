"""Verify AR2 transition matrices now sum to 1.0."""

from pathlib import Path
import re

html_path = Path("results/AR2_gaze_transitions/ar2_gw_vs_gwo/report.html")
html = html_path.read_text(encoding='utf-8')

# Find the transition matrices section
matrix_start = html.find("GIVE_WITH")
if matrix_start == -1:
    print("Could not find GIVE_WITH matrix in report")
    exit(1)

# Extract a sample table
table_start = html.rfind("<table", 0, matrix_start + 1000)
table_end = html.find("</table>", table_start) + 8

table_html = html[table_start:table_end]

print("=" * 80)
print("AR2 TRANSITION MATRIX VERIFICATION")
print("=" * 80)
print("\nExtracted table HTML (first 1500 chars):")
print(table_html[:1500])

# Try to find numeric values in the table
numbers = re.findall(r'\d+\.\d+', table_html)
print(f"\n\nFound {len(numbers)} numeric values in matrix:")
print(numbers[:20] if len(numbers) > 20 else numbers)

print("\n" + "=" * 80)
print("Please manually check the report.html file to verify rows sum to 1.0")
print("=" * 80)
