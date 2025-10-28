with open('src/analysis/ar2_transitions.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

line265 = lines[264]  # 0-indexed
print("Line 265 length:", len(line265))
print("Contains arrow corruption:", 'ÃƒÆ' in line265)
print("First 50 chars:", line265[:50])
print("Char at position 40-60:", repr(line265[40:60]))

# Try to find and replace
if 'ÃƒÆ' in line265:
    print("\nCORRUPTION FOUND!")
    # Find the position
    pos = line265.find('ÃƒÆ')
    print(f"Position: {pos}")
    print(f"Context: {repr(line265[pos-5:pos+30])}")
