"""
Summarize how many unique trials per participant include each `event_verified`
label and visualize the counts.

Outputs (written to the script directory):
* `event_trial_counts.json` – machine-readable per-participant summary.
* `event_trial_counts.png`  – stacked bar chart of event counts by participant.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent
JSON_PATH = OUTPUT_DIR / "event_trial_counts.json"
PNG_PATH = OUTPUT_DIR / "event_trial_counts.png"


EVENT_ORDER = [
    "gw",
    "gwo",
    "hw",
    "hwo",
    "ugw",
    "ugwo",
    "uhw",
    "uhwo",
    "sw",
    "swo",
    "f",
]

EVENT_COLORS = {
    "gw": "#4C72B0",
    "gwo": "#55A868",
    "hw": "#C44E52",
    "hwo": "#8172B3",
    "ugw": "#CCB974",
    "ugwo": "#64B5CD",
    "uhw": "#8C8C8C",
    "uhwo": "#E17C05",
    "sw": "#937860",
    "swo": "#DA8BC3",
    "f": "#8EBA42",
}

REQUIRED_COLUMNS = {"event_verified", "trial_number_global", "Participant"}


@dataclass
class ParticipantSummary:
    participant: str
    group: str
    path: Path
    event_counts: Dict[str, int]
    total_trials: int

    @property
    def rel_path(self) -> str:
        return str(self.path.relative_to(ROOT))


def iter_csv_files() -> Iterable[Path]:
    return sorted(p for p in RAW_DATA_DIR.rglob("*.csv") if p.is_file())


def parse_file(csv_path: Path) -> ParticipantSummary | None:
    per_event_trials: Dict[str, Set[str]] = defaultdict(set)
    all_trials: Set[str] = set()
    participant_name: str | None = None

    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return None
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing expected columns {missing} in {csv_path}"
            )
        for row in reader:
            event = (row.get("event_verified") or "").strip()
            trial = (row.get("trial_number_global") or "").strip()
            if not event or not trial:
                continue
            participant_name = participant_name or (row.get("Participant") or "").strip()
            per_event_trials[event].add(trial)
            all_trials.add(trial)

    if not all_trials:
        return None

    participant_name = participant_name or csv_path.stem
    event_counts = {event: len(trials) for event, trials in per_event_trials.items()}
    return ParticipantSummary(
        participant=participant_name,
        group=csv_path.parent.name,
        path=csv_path,
        event_counts=event_counts,
        total_trials=len(all_trials),
    )


def collect_summaries() -> List[ParticipantSummary]:
    summaries: List[ParticipantSummary] = []
    for csv_file in iter_csv_files():
        summary = parse_file(csv_file)
        if summary is not None:
            summaries.append(summary)
    return summaries


def ensure_event_order(events: List[str]) -> List[str]:
    """Return EVENT_ORDER augmented with any unexpected labels at the end."""
    ordered = list(EVENT_ORDER)
    for event in events:
        if event not in ordered:
            ordered.append(event)
    return ordered


def write_json(summaries: List[ParticipantSummary]) -> None:
    payload = []
    for summary in summaries:
        payload.append(
            {
                "participant": summary.participant,
                "group": summary.group,
                "path": summary.rel_path,
                "total_trials": summary.total_trials,
                "event_counts": summary.event_counts,
            }
        )
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_plot(summaries: List[ParticipantSummary]) -> None:
    if not summaries:
        return

    all_events = ensure_event_order(
        sorted(
            {
                event
                for summary in summaries
                for event in summary.event_counts.keys()
            }
        )
    )

    # Sort by group then participant for readability.
    summaries_sorted = sorted(
        summaries,
        key=lambda s: (s.group, s.participant),
    )

    labels = [summary.participant for summary in summaries_sorted]
    indices = range(len(summaries_sorted))

    width = max(12.0, 0.5 * len(labels))
    plt.figure(figsize=(width, 6))

    bottoms = [0] * len(summaries_sorted)
    legend_containers = []

    for event in all_events:
        values = [
            summary.event_counts.get(event, 0) for summary in summaries_sorted
        ]
        if not any(values):
            continue
        color = EVENT_COLORS.get(event, "#999999")
        container = plt.bar(
            indices,
            values,
            bottom=bottoms,
            label=event,
            color=color,
        )
        legend_containers.append(container)
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]

    plt.xticks(indices, labels, rotation=90, fontsize=8)
    plt.ylabel("Unique trials containing event")
    plt.title("Trials per event_verified by participant")
    if legend_containers:
        plt.legend(
            handles=legend_containers,
            labels=[container.get_label() for container in legend_containers],
            title="event_verified",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
        )
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=200)
    plt.close()


def main() -> None:
    summaries = collect_summaries()
    if not summaries:
        raise SystemExit("No participant CSV files processed.")
    write_json(summaries)
    write_plot(summaries)
    print(
        f"Generated trial counts for {len(summaries)} participants. "
        f"Outputs: {JSON_PATH.relative_to(ROOT)} and {PNG_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
