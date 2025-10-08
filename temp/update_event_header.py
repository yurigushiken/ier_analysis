"""
Rename selected raw CSV headers (e.g., 'event_verified' -> 'event').
"""

from __future__ import annotations

import csv
from pathlib import Path


RENAME_MAP = {
    "event_verified": "event",
    "frame_count_event": "frame_count_trial_block",
    "frame_count_event_block": "frame_count_trial_block",
    "trial_number": "trial_number_within_block",
    "trial_number_within_block": "trial_block_trial_number",
    "frame_count_trial_block": "trial_block_frame_count",
    "frame_count_trial_number": "trial_number_frame_count",
    "trial_number_global": "trial_no_cumulative_by_event",
    "trial_block_cumulative_number": "trial_block_cumulative_order",
    "trial_block_frame_count": "trial_block_frame",
    "trial_number_frame_count": "trial_number_frame",
    "frame_count_segment": "segment_frame",
    "frame_number": "frame_no",
    "trial_block_trial_number": "trial_block_trial_no",
    "trial_number_frame": "trial_no_frame",
    "trial_no_frame": "trial_frame_no",
    "frame_no": "frame",
    "trial_block_trial_no": "trial_block_trial",
    "trial_frame_no": "trial_frame",
    "trial_no_cumulative_by_event": "trial_cumulative_by_event",
    "frame": "session_frame",
}


def rename_event_column(csv_path: Path) -> bool:
    """
    Replace the 'event_verified' header with 'event' for a single file.

    Returns True when a modification was applied, False otherwise.
    """
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        try:
            header = next(reader)
        except StopIteration:
            # Empty file, nothing to do.
            return False

        new_header = [RENAME_MAP.get(col, col) for col in header]
        if new_header == header:
            return False

        with tmp_path.open("w", encoding="utf-8-sig", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow(new_header)
            for row in reader:
                writer.writerow(row)

    tmp_path.replace(csv_path)
    return True


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    raw_dir = project_root / "data" / "raw"

    if not raw_dir.exists():
        print("Raw data directory not found. Expected at data/raw.")
        return

    updated = 0
    skipped = 0
    for csv_path in sorted(raw_dir.rglob("*.csv")):
        changed = rename_event_column(csv_path)
        if changed:
            updated += 1
        else:
            skipped += 1

    print(
        f"Processed {updated + skipped} files: "
        f"{updated} updated, {skipped} already using 'event'."
    )


if __name__ == "__main__":
    main()
