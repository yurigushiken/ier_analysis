#!/usr/bin/env python3
"""Fix encoding issues in AR2 transitions module."""

from pathlib import Path

file_path = Path("src/analysis/ar2_transitions.py")

# Read with UTF-8
content = file_path.read_text(encoding='utf-8')

# Count before
count_before = content.count('\u00c3')
print(f"Corrupted sequences found: {count_before}")

# Replace the specific corrupted sequences
# These represent arrows and dashes that got double-encoded
replacements = [
    ('ÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ'Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ'Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢', '->'),
    ('ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å"', '-'),
]

for old, new in replacements:
    count = content.count(old)
    if count > 0:
        print(f"Replacing '{old[:20]}...' -> '{new}' ({count} occurrences)")
        content = content.replace(old, new)

# Count after
count_after = content.count('\u00c3')
print(f"Corrupted sequences remaining: {count_after}")

# Write back
file_path.write_text(content, encoding='utf-8')
print(f"\n✓ Fixed {file_path}")
