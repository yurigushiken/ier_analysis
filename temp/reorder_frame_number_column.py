"""
Rename 'Frame Number' to 'frame_number' and place it after 'Blue Dot Center'.
"""

from __future__ import annotations

import csv
from itertools import zip_longest
from pathlib import Path


def adjust_frame_column(csv_path: Path) -> bool:
    """
    Rewrite the CSV so that the frame column is named 'frame_number' and appears
    immediately after 'Blue Dot Center'.

    Returns True if any change was made, False otherwise.
    """
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        try:
            header = next(reader)
        except StopIteration:
            return False

        if "Blue Dot Center" not in header:
            return False

        if "Frame Number" in header:
            frame_key = "Frame Number"
        elif "frame_number" in header:
            frame_key = "frame_number"
        else:
            return False

        # Header with the frame column renamed
        header_renamed = [
            "frame_number" if col == frame_key else col for col in header
        ]

        # Remove the frame column to compute the target position
        header_without_frame = [
            col for col in header_renamed if col != "frame_number"
        ]

        try:
            blue_idx = header_without_frame.index("Blue Dot Center")
        except ValueError:
            return False

        new_header = (
            header_without_frame[: blue_idx + 1]
            + ["frame_number"]
            + header_without_frame[blue_idx + 1 :]
        )

        if new_header == header:
            # Already matching original header: only rename needed
            if frame_key == "Frame Number":
                # We still need to rewrite to rename the column
                pass
            else:
                return False

        if new_header == header_renamed and frame_key == "frame_number":
            # Column already renamed and positioned
            return False

        with tmp_path.open("w", encoding="utf-8-sig", newline="") as dst:
            writer = csv.writer(dst)
            writer.writerow(new_header)

            for row in reader:
                row_dict = {
                    key: value for key, value in zip_longest(header, row, fillvalue="")
                }
                if frame_key != "frame_number":
                    row_dict["frame_number"] = row_dict.pop(frame_key, "")

                new_row = [row_dict.get(col, "") for col in new_header]
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
        if adjust_frame_column(csv_path):
            updated += 1
        else:
            skipped += 1

    print(f"Processed {updated + skipped} files: {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()

