"""
Quick consistency check to make sure every raw CSV shares the same column headers.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Tuple


def read_header(path: Path) -> Tuple[str, ...]:
    """Return the CSV header as a tuple of column names."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return tuple(next(reader))
        except StopIteration as exc:
            raise ValueError(f"{path} is empty") from exc


def iter_csv_files(root: Path) -> Iterable[Path]:
    """Yield all CSV files under the raw data directory."""
    yield from sorted(root.rglob("*.csv"))


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    raw_dir = project_root / "data" / "raw"

    expected_header: Tuple[str, ...] | None = None
    mismatches: list[tuple[Path, Tuple[str, ...]]] = []
    files_checked = 0

    for csv_path in iter_csv_files(raw_dir):
        header = read_header(csv_path)
        files_checked += 1

        if expected_header is None:
            expected_header = header
        elif header != expected_header:
            mismatches.append((csv_path, header))

    if expected_header is None:
        print("No CSV files found under data/raw.")
        return

    print(f"Checked {files_checked} files.")
    print("Reference columns:")
    for name in expected_header:
        print(f"- {name}")

    if mismatches:
        print("\nMismatched headers detected:")
        for csv_path, header in mismatches:
            print(f"\n{csv_path}:")
            for name in header:
                print(f"- {name}")
    else:
        print("\nAll files share the same column headers.")


if __name__ == "__main__":
    main()
