"""
Count how many trials per participant are entirely missing gaze signal
(`What="no"` and `Where="signal"` for every row) and plot the results.

Outputs:
* `temp/data_integrity/no_signal_full_trial.json` - summary per participant.
* `temp/data_integrity/no_signal_full_trial.png`  - bar chart ranked high to low.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent
JSON_PATH = OUTPUT_DIR / "no_signal_full_trial.json"
PNG_PATH = OUTPUT_DIR / "no_signal_full_trial.png"


REQUIRED_COLUMNS = {"What", "Where", "Participant", "trial_number_global"}


def iter_csv_files() -> Iterable[Path]:
    return sorted(p for p in RAW_DATA_DIR.rglob("*.csv") if p.is_file())


@dataclass
class TrialRecord:
    participant: str
    group: str
    trial_id: str
    total_rows: int
    no_signal_rows: int
    file_path: Path

    @property
    def rel_path(self) -> str:
        return str(self.file_path.relative_to(ROOT))

    def is_full_no_signal(self) -> bool:
        return self.total_rows > 0 and self.no_signal_rows == self.total_rows


def parse_trials(csv_path: Path) -> List[TrialRecord]:
    grouped: Dict[str, Dict[str, object]] = {}
    participant_name: str | None = None
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(
                f"Missing required columns {missing_columns} in {csv_path}"
            )
        for row in reader:
            trial_id = (row.get("trial_number_global") or "").strip()
            if not trial_id:
                # Skip rows without a valid trial identifier.
                continue
            participant_name = participant_name or (row.get("Participant") or "").strip()
            what = (row.get("What") or "").strip().lower()
            where = (row.get("Where") or "").strip().lower()
            stats = grouped.setdefault(
                trial_id,
                {
                    "total_rows": 0,
                    "no_signal_rows": 0,
                },
            )
            stats["total_rows"] += 1
            if what == "no" and where == "signal":
                stats["no_signal_rows"] += 1

    if not grouped:
        return []

    participant_name = participant_name or csv_path.stem
    records: List[TrialRecord] = []
    for trial_id, stats in grouped.items():
        records.append(
            TrialRecord(
                participant=participant_name,
                group=csv_path.parent.name,
                trial_id=trial_id,
                total_rows=stats["total_rows"],
                no_signal_rows=stats["no_signal_rows"],
                file_path=csv_path,
            )
        )
    return records


def collect_trials() -> List[TrialRecord]:
    records: List[TrialRecord] = []
    for csv_path in iter_csv_files():
        records.extend(parse_trials(csv_path))
    return records


def aggregate_trials(trials: List[TrialRecord]) -> List[Dict[str, object]]:
    grouped: Dict[str, Dict[str, object]] = {}
    for trial in trials:
        entry = grouped.setdefault(
            trial.participant,
            {
                "participant": trial.participant,
                "group": trial.group,
                "total_trials": 0,
                "full_no_signal_trials": 0,
                "all_trial_paths": [],
                "full_no_signal_trial_paths": [],
                "full_no_signal_trial_ids": [],
            },
        )
        entry["total_trials"] += 1
        entry["all_trial_paths"].append(
            {"trial_id": trial.trial_id, "path": trial.rel_path}
        )
        if trial.is_full_no_signal():
            entry["full_no_signal_trials"] += 1
            entry["full_no_signal_trial_paths"].append(trial.rel_path)
            entry["full_no_signal_trial_ids"].append(trial.trial_id)
    return sorted(
        grouped.values(),
        key=lambda item: (
            item["full_no_signal_trials"],
            item["total_trials"],
        ),
        reverse=True,
    )


def write_json(summary: List[Dict[str, object]]) -> None:
    JSON_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_plot(summary: List[Dict[str, object]]) -> None:
    if not summary:
        return

    labels = [item["participant"] for item in summary]
    values = [item["full_no_signal_trials"] for item in summary]
    groups = [item["group"] for item in summary]

    color_map = {
        "child-gl": "#4C72B0",
        "adult-gl": "#55A868",
    }
    colors = [color_map.get(group, "#999999") for group in groups]

    width = max(10.0, 0.4 * len(labels))
    plt.figure(figsize=(width, 6))
    bars = plt.bar(range(len(labels)), values, color=colors)
    plt.xticks(range(len(labels)), labels, rotation=90, fontsize=8)
    plt.ylabel("Trials entirely 'no/signal'")
    plt.title("Fully Missing-Signal Trials per Participant (descending)")
    plt.tight_layout()

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            str(value),
            ha="center",
            va="bottom",
            fontsize=6,
        )

    legend_elements = []
    for group, color in color_map.items():
        if group in groups:
            legend_elements.append(plt.Line2D([0], [0], color=color, lw=4, label=group))
    if legend_elements:
        plt.legend(handles=legend_elements, title="Group", loc="upper right")

    plt.savefig(PNG_PATH, dpi=200)
    plt.close()


def main() -> None:
    trials = collect_trials()
    if not trials:
        raise SystemExit("No CSV trials processed.")
    summary = aggregate_trials(trials)
    write_json(summary)
    write_plot(summary)
    print(
        f"Aggregated {len(trials)} trials across {len(summary)} participants. "
        f"Summary written to {JSON_PATH.relative_to(ROOT)} and plot to "
        f"{PNG_PATH.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
