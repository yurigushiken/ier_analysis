"""
Ensure trial block-related columns appear in the desired order.
"""

from __future__ import annotations

import csv
from itertools import zip_longest
from pathlib import Path


def reposition_trial_column(csv_path: Path) -> bool:
    """Make sure trial block columns are grouped together in the desired order."""
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        try:
            header = next(reader)
        except StopIteration:
            return False

        if "trial_block_cumulative_number" not in header:
            return False

        ordered = list(header)

        block_columns = [
            "trial_block_frame",
            "trial_block_trial",
            "trial_frame",
        ]

        # Remove block columns so we can reinsert them in the desired spot
        removed = []
        for col in block_columns:
            if col in ordered:
                ordered.remove(col)
                removed.append(col)

        if not removed:
            return False

        target_idx = ordered.index("trial_block_cumulative_number")
        for offset, col in enumerate(block_columns):
            if col in removed:
                ordered.insert(target_idx + 1 + offset, col)

        if ordered == header:
            return False

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
        if reposition_trial_column(csv_path):
            updated += 1
        else:
            skipped += 1

    print(f"Processed {updated + skipped} files: {updated} updated, {skipped} skipped.")


if __name__ == "__main__":
    main()
