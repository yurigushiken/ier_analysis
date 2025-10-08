"""
Place the frame number column immediately after the event column.
"""

from __future__ import annotations

import csv
from itertools import zip_longest
from pathlib import Path


def reposition_frame(csv_path: Path) -> bool:
    """Move frame_no so it follows event."""
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        try:
            header = next(reader)
        except StopIteration:
            return False

        if "event" not in header:
            return False

        frame_col = None
        for candidate in ("session_frame", "frame", "frame_no", "frame_number"):
            if candidate in header:
                frame_col = candidate
                break

        if frame_col is None:
            return False

        if header.index(frame_col) == header.index("event") + 1:
            return False  # already in place

        ordered = [col for col in header if col != frame_col]
        event_idx = ordered.index("event")
        ordered.insert(event_idx + 1, frame_col)

        with tmp_path.open("w", encoding="utf-8-sig", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow(ordered)
            for row in reader:
                row_dict = {
                    key: value for key, value in zip_longest(header, row, fillvalue="")
                }
                writer.writerow([row_dict.get(col, "") for col in ordered])

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
        if reposition_frame(csv_path):
            updated += 1
        else:
            skipped += 1

    print(f"Processed {updated + skipped} files: {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
