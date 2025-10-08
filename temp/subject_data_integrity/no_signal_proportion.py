"""
Compute the proportion of gaze samples labeled as the "no/signal" pair for
every participant file and render a ranked bar chart.

Outputs:
* `temp/data_integrity/no_signal_proportion.json` - machine readable summary.
* `temp/data_integrity/no_signal_proportion.png`  - bar chart (highest to lowest).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent
JSON_PATH = OUTPUT_DIR / "no_signal_proportion.json"
PNG_PATH = OUTPUT_DIR / "no_signal_proportion.png"


@dataclass
class NoSignalRecord:
    path: Path
    total_rows: int
    no_signal_rows: int

    @property
    def proportion(self) -> float:
        return (self.no_signal_rows / self.total_rows) if self.total_rows else 0.0

    @property
    def rel_path(self) -> str:
        return str(self.path.relative_to(ROOT))

    @property
    def participant(self) -> str:
        return self.path.stem


def collect_records() -> List[NoSignalRecord]:
    records: List[NoSignalRecord] = []
    for csv_path in sorted(RAW_DATA_DIR.rglob("*.csv")):
        total_rows = 0
        no_signal_rows = 0
        with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                continue
            if not {"What", "Where"}.issubset(reader.fieldnames):
                raise ValueError(f"'What' or 'Where' columns missing in {csv_path}")
            for row in reader:
                total_rows += 1
                what = (row.get("What") or "").strip().lower()
                where = (row.get("Where") or "").strip().lower()
                if what == "no" and where == "signal":
                    no_signal_rows += 1
        if total_rows == 0:
            continue
        records.append(NoSignalRecord(csv_path, total_rows, no_signal_rows))
    return records


def write_json(records: List[NoSignalRecord]) -> None:
    payload = [
        {
            "path": record.rel_path,
            "participant": record.participant,
            "total_rows": record.total_rows,
            "no_signal_rows": record.no_signal_rows,
            "proportion_no_signal": record.proportion,
        }
        for record in records
    ]
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_plot(records: List[NoSignalRecord]) -> None:
    sorted_records = sorted(records, key=lambda r: r.proportion, reverse=True)
    labels = [record.participant for record in sorted_records]
    values = [record.proportion for record in sorted_records]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(sorted_records)), values, color="#4C72B0")
    plt.xticks(range(len(sorted_records)), labels, rotation=90, fontsize=8)
    plt.ylabel("Proportion of samples with What='no' & Where='signal'")
    plt.title("Proportion of Missing Signal by Participant (descending)")
    plt.tight_layout()

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2%}",
            ha="center",
            va="bottom",
            fontsize=6,
        )

    plt.savefig(PNG_PATH, dpi=200)
    plt.close()


def main() -> None:
    records = collect_records()
    if not records:
        raise SystemExit("No CSV files processed.")
    write_json(records)
    write_plot(records)
    print(
        f"Computed no-signal proportions for {len(records)} files. "
        f"Results written to {JSON_PATH.relative_to(ROOT)} and "
        f"{PNG_PATH.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
