"""Fix UTF-8 encoding issues in ar2_transitions.py"""

from pathlib import Path

# Read the file
file_path = Path("src/analysis/ar2_transitions.py")
content = file_path.read_text(encoding='utf-8')

# Count replacements
before_count = content.count('ÃƒÆ')

# Replace corrupted UTF-8 sequences with ASCII arrows
# The corrupted sequence represents an arrow (→)
content = content.replace(
    'ÃƒÆ'Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ'Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ÃƒÆ'Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢',
    '->'
)

# Also check for en-dash corruption (–) which might appear as another sequence
content = content.replace('ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å"', '-')

after_count = content.count('ÃƒÆ')

# Write back
file_path.write_text(content, encoding='utf-8')

print(f"Fixed ar2_transitions.py:")
print(f"  Corrupted sequences before: {before_count}")
print(f"  Corrupted sequences after: {after_count}")
print(f"  Replacements made: {before_count - after_count}")
