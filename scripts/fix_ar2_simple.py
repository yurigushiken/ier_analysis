"""Simple direct string replacement for AR2 encoding corruption."""

# Read the file
with open('src/analysis/ar2_transitions.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

changes = 0

# Check and fix each line
for i, line in enumerate(lines):
    original = line

    # Check for corruption marker (both arrow and en-dash patterns)
    if 'ÃƒÆ' in line or '\u00c3\u0083' in line or 'ÃƒÂ¢' in line:
        print(f"Line {i+1}: Found corruption")
        print(f"  Before: {line[:80]}...")

        # Simple replacements for known patterns
        # Pattern 1: label assignment
        if 'label = f"{from_a}' in line and 'ÃƒÆ' in line:
            line = '            label = f"{from_a} -> {to_a}"\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 2: condition_a_transition
        elif 'condition_a_transition = f"{condition_a} ({from_a}' in line:
            line = '        condition_a_transition = f"{condition_a} ({from_a} -> {to_a})"\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 3: condition_b_transition
        elif 'condition_b_transition = f"{condition_b} ({from_b}' in line:
            line = '        condition_b_transition = f"{condition_b} ({from_b} -> {to_b})"\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 4: heatmap title
        elif '_save_heatmap(matrix, heatmap_path, f"{legend_label}' in line:
            line = '            _save_heatmap(matrix, heatmap_path, f"{legend_label} - {condition_name}")\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 5: heatmap caption
        elif '"caption": f"{legend_label}' in line and 'heatmaps.append' in line:
            line = '            heatmaps.append({"path": f"figures/{heatmap_path.name}", "caption": f"{legend_label} - {condition_name}"})\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 6: graph title
        elif 'title=f"{legend_label}' in line:
            line = '                title=f"{legend_label} - {condition_name}",\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

        # Pattern 7: graph caption
        elif 'graphs.append({"path": f"figures/{directed_graph_path.name}", "caption": f"{legend_label}' in line:
            line = '            graphs.append({"path": f"figures/{directed_graph_path.name}", "caption": f"{legend_label} - {condition_name}"})\n'
            changes += 1
            print(f"  After:  {line[:80]}...")

    lines[i] = line

print(f"\nTotal changes: {changes}")

# Write back
with open('src/analysis/ar2_transitions.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File saved")
