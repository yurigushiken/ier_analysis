"""Final fix for AR2 encoding issues - replaces all corrupted arrows/dashes with ASCII."""

# Read the file
with open('src/analysis/ar2_transitions.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
changes_made = 0

# Find all lines with corruption indicators
if '\u00c3\u0083' in content:  # Start of the corruption sequence
    print("Found corruption markers in file")

    # These are the corrupted UTF-8 sequences we need to replace
    # We'll search for them by looking for the characteristic pattern
    original_length = len(content)

    # Replace common corruption patterns
    # Pattern 1: The long arrow sequence
    while True:
        start_pos = content.find('label = f"{from_a} \u00c3')
        if start_pos == -1:
            break
        # Find the end of this line
        end_pos = content.find('"', start_pos + 20)
        if end_pos == -1:
            break
        # Replace the entire f-string value
        content = content[:start_pos] + 'label = f"{from_a} -> {to_a}"' + content[end_pos+1:]
        changes_made += 1
        print(f"Fixed label assignment #{changes_made}")

    # Pattern 2: condition_a_transition
    while True:
        start_pos = content.find('condition_a_transition = f"{condition_a} ({from_a} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find(')"', start_pos + 30)
        if end_pos == -1:
            break
        content = content[:start_pos] + 'condition_a_transition = f"{condition_a} ({from_a} -> {to_a})' + content[end_pos:]
        changes_made += 1
        print(f"Fixed condition_a_transition #{changes_made}")

    # Pattern 3: condition_b_transition
    while True:
        start_pos = content.find('condition_b_transition = f"{condition_b} ({from_b} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find(')"', start_pos + 30)
        if end_pos == -1:
            break
        content = content[:start_pos] + 'condition_b_transition = f"{condition_b} ({from_b} -> {to_b})' + content[end_pos:]
        changes_made += 1
        print(f"Fixed condition_b_transition #{changes_made}")

    # Pattern 4: heatmap titles
    while True:
        start_pos = content.find('_save_heatmap(matrix, heatmap_path, f"{legend_label} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find('")', start_pos + 30)
        if end_pos == -1:
            break
        # Extract the condition name variable
        before = content[start_pos:start_pos+200]
        content = content[:start_pos] + '_save_heatmap(matrix, heatmap_path, f"{legend_label} - {condition_name}' + content[end_pos:]
        changes_made += 1
        print(f"Fixed heatmap title #{changes_made}")

    # Pattern 5: heatmap captions
    while True:
        start_pos = content.find('"caption": f"{legend_label} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find('"}', start_pos + 20)
        if end_pos == -1:
            break
        content = content[:start_pos] + '"caption": f"{legend_label} - {condition_name}"' + content[end_pos+2:]
        changes_made += 1
        print(f"Fixed heatmap caption #{changes_made}")

    # Pattern 6: directed graph titles
    while True:
        start_pos = content.find('title=f"{legend_label} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find('"', start_pos + 20)
        if end_pos == -1:
            break
        content = content[:start_pos] + 'title=f"{legend_label} - {condition_name}"' + content[end_pos+1:]
        changes_made += 1
        print(f"Fixed graph title #{changes_made}")

    # Pattern 7: directed graph captions
    while True:
        start_pos = content.find('graphs.append({"path": f"figures/{directed_graph_path.name}", "caption": f"{legend_label} \u00c3')
        if start_pos == -1:
            break
        end_pos = content.find('"})', start_pos + 30)
        if end_pos == -1:
            break
        content = content[:start_pos] + 'graphs.append({"path": f"figures/{directed_graph_path.name}", "caption": f"{legend_label} - {condition_name}"}' + content[end_pos+2:]
        changes_made += 1
        print(f"Fixed graph caption #{changes_made}")

    print(f"\nTotal changes made: {changes_made}")
    print(f"Length before: {original_length}, after: {len(content)}")

else:
    print("No corruption markers found - file may already be clean")

# Write back
with open('src/analysis/ar2_transitions.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFile saved successfully")
