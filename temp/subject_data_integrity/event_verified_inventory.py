"""
Inventory the `event_verified` values present in every raw data CSV.

The script scans all CSV files under `data/raw`, records which distinct
`event_verified` labels occur in each file, and reports any labels that are
missing from specific files. It writes both a JSON summary and a convenience
table in Markdown so the results are easy to inspect from the repo.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Set


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent
JSON_SUMMARY_PATH = OUTPUT_DIR / "event_verified_inventory.json"
MARKDOWN_SUMMARY_PATH = OUTPUT_DIR / "event_verified_inventory.md"


@dataclass
class FileInventory:
    path: Path
    events_present: Set[str] = field(default_factory=set)

    @property
    def rel_path(self) -> str:
        return str(self.path.relative_to(ROOT))

    def events_sorted(self) -> List[str]:
        return sorted(self.events_present)


def iter_csv_files(directory: Path) -> Iterable[Path]:
    return sorted(p for p in directory.rglob("*.csv") if p.is_file())


def collect_event_labels(csv_path: Path) -> Set[str]:
    events: Set[str] = set()
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return events
        if "event_verified" not in reader.fieldnames:
            raise ValueError(
                f"'event_verified' column missing in {csv_path}"
            )
        for row in reader:
            raw_value = (row.get("event_verified") or "").strip()
            if not raw_value:
                continue
            events.add(raw_value)
    return events


def build_inventory() -> Dict[str, FileInventory]:
    inventory: Dict[str, FileInventory] = {}
    for csv_path in iter_csv_files(RAW_DATA_DIR):
        events_present = collect_event_labels(csv_path)
        rel_path = str(csv_path.relative_to(ROOT))
        inventory[rel_path] = FileInventory(csv_path, events_present)
    return inventory


def inventory_to_json(inventory: Dict[str, FileInventory]) -> Dict[str, object]:
    all_events: Set[str] = set()
    for file_inventory in inventory.values():
        all_events.update(file_inventory.events_present)
    all_events_sorted = sorted(all_events)

    files_summary = [
        {
            "path": rel_path,
            "events_present": sorted(file_inventory.events_present),
        }
        for rel_path, file_inventory in sorted(
            inventory.items(), key=lambda item: item[0]
        )
    ]

    files_missing_events = {
        rel_path: sorted(set(all_events_sorted) - file_inventory.events_present)
        for rel_path, file_inventory in inventory.items()
    }

    events_missing_files: Dict[str, List[str]] = {
        event: sorted(
            rel_path
            for rel_path, file_inventory in inventory.items()
            if event not in file_inventory.events_present
        )
        for event in all_events_sorted
    }

    return {
        "all_events": all_events_sorted,
        "files": files_summary,
        "files_missing_events": files_missing_events,
        "events_missing_files": events_missing_files,
    }


def write_markdown_summary(
    all_events: List[str], files_missing_events: Dict[str, List[str]]
) -> None:
    lines: List[str] = []
    header = ["File"] + all_events
    separator = ["---"] * len(header)
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(separator) + " |")
    for rel_path in sorted(files_missing_events):
        missing = set(files_missing_events[rel_path])
        row_cells = [
            "",
            *(
                ("1" if event not in missing else "0")
                for event in all_events
            ),
        ]
        row_cells[0] = rel_path
        lines.append("| " + " | ".join(row_cells) + " |")
    MARKDOWN_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    summary = inventory_to_json(inventory)
    JSON_SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    write_markdown_summary(
        summary["all_events"], summary["files_missing_events"]
    )
    print(
        f"Wrote JSON summary to {JSON_SUMMARY_PATH.relative_to(ROOT)} "
        f"and Markdown table to {MARKDOWN_SUMMARY_PATH.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
