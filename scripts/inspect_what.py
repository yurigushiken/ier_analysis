#!/usr/bin/env python3
"""
Scan all CSVs in data/csvs_human_verified_vv and report unique entries in the "What" column.
Prints a human- and TTS-friendly summary and lists files containing unexpected or anomalous values.
"""
import csv
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, 'data', 'csvs_human_verified_vv')

# Canonical expected values for the `What` column (from study-info.md).
EXPECTED = set(['no', 'screen', 'woman', 'man', 'toy', 'toy2'])

def normalize(s):
    if s is None:
        return ''
    return s.strip()

def scan():
    global_counts = Counter()
    per_file_unexpected = defaultdict(set)
    per_file_missing_header = []
    files_scanned = 0

    for group in ('child', 'adult'):
        group_dir = os.path.join(DATA_DIR, group)
        if not os.path.isdir(group_dir):
            continue
        for fname in sorted(os.listdir(group_dir)):
            if not fname.lower().endswith('.csv'):
                continue
            path = os.path.join(group_dir, fname)
            files_scanned += 1
            try:
                with open(path, newline='') as fh:
                    reader = csv.DictReader(fh)
                    # find the 'what' header key (case-insensitive)
                    headers = {h.lower(): h for h in reader.fieldnames} if reader.fieldnames else {}
                    if 'what' not in headers:
                        per_file_missing_header.append(path)
                        continue
                    what_key = headers['what']
                    file_values = set()
                    for row in reader:
                        val = normalize(row.get(what_key, ''))
                        lower = val.lower()
                        global_counts[lower] += 1
                        file_values.add(lower)
                    # check unexpected values
                    unexpected = {v for v in file_values if v and v not in EXPECTED}
                    # also record empty/blank as anomaly
                    if '' in file_values:
                        unexpected.add('<BLANK>')
                    if unexpected:
                        per_file_unexpected[path].update(unexpected)
            except Exception as e:
                per_file_unexpected[path].add(f'<ERROR: {e}>')

    return {
        'files_scanned': files_scanned,
        'global_counts': global_counts,
        'per_file_unexpected': per_file_unexpected,
        'missing_header': per_file_missing_header,
    }

def pretty_print(result):
    gc = result['global_counts']
    total_unique = len([k for k in gc.keys() if k])
    print('What-column inspection report')
    print('================================')
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Unique non-empty entries found in `What`: {total_unique}")
    print('')
    print('Global counts (top items):')
    for val, cnt in gc.most_common():
        display = val if val else '<BLANK>'
        print(f"  {display!s:12} : {cnt}")
    print('')
    if result['per_file_unexpected']:
        print('Files with unexpected or anomalous `What` values:')
        for path, issues in sorted(result['per_file_unexpected'].items()):
            print(f"- {os.path.relpath(path, ROOT)} -> {', '.join(sorted(issues))}")
    else:
        print('No per-file anomalies detected.')

    if result['missing_header']:
        print('\nFiles missing a `What` header:')
        for p in result['missing_header']:
            print(' -', os.path.relpath(p, ROOT))

    print('\nCanonical expected `What` set:')
    print('  ' + ', '.join(sorted(EXPECTED)))


if __name__ == '__main__':
    res = scan()
    pretty_print(res)
