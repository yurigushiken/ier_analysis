"""
Insert a trial block counter that increments whenever the 'event' value changes.
"""

from __future__ import annotations

import csv
from pathlib import Path


def add_trial_block_column(csv_path: Path) -> bool:
    """
    Insert 'trial_block_cumulative_number' after the 'event' column.

    Returns True if the file was rewritten, False if it already contained the column
    or if no event column was present.
    """
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        try:
            header = next(reader)
        except StopIteration:
            # Empty file
            return False

        try:
            event_idx = header.index("event")
        except ValueError:
            # Unexpected schema, skip file
            return False

        insert_idx = event_idx + 1
        if (
            len(header) > insert_idx
            and header[insert_idx] == "trial_block_cumulative_number"
        ):
            return False

        new_header = header[:insert_idx] + ["trial_block_cumulative_number"] + header[insert_idx:]

        with tmp_path.open("w", encoding="utf-8-sig", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow(new_header)

            prev_event: str | None = None
            block_counter = 0

            for row in reader:
                # Guard against ragged rows
                if len(row) <= event_idx:
                    writer.writerow(row[:insert_idx] + [""] + row[insert_idx:])
                    continue

                current_event = row[event_idx]
                if prev_event is None or current_event != prev_event:
                    block_counter += 1
                    prev_event = current_event

                value = str(block_counter)
                new_row = row[:insert_idx] + [value] + row[insert_idx:]
                writer.writerow(new_row)

    tmp_path.replace(csv_path)
    return True


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    raw_dir = project_root / "data" / "raw"

    if not raw_dir.exists():
        print("Raw data directory not found. Expected data/raw.")
        return

    updated = 0
    skipped = 0

    for csv_path in sorted(raw_dir.rglob("*.csv")):
        if add_trial_block_column(csv_path):
            updated += 1
        else:
            skipped += 1

    print(f"Processed {updated + skipped} files: {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()

