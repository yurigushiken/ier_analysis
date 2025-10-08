"""
Visualize how each participant's event counts compare to the global minimum
number of trials per `event_verified` label.

Outputs:
* `event_trial_min_diff.json` – baseline minimum and extra trials per participant.
* `event_trial_min_diff.png`  – stacked bar chart highlighting additional trials
  above the shared minimum.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from event_trial_counts import (
    EVENT_COLORS,
    EVENT_ORDER,
    collect_summaries,
    ensure_event_order,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parent
JSON_PATH = OUTPUT_DIR / "event_trial_min_diff.json"
CSV_PATH = OUTPUT_DIR / "event_trial_min_diff.csv"
PNG_PATH = OUTPUT_DIR / "event_trial_min_diff.png"


def compute_min_counts(summaries, events_ordered) -> Dict[str, int]:
    return {
        event: min(summary.event_counts.get(event, 0) for summary in summaries)
        for event in events_ordered
    }


def build_payload(summaries, min_counts, events_ordered):
    payload: List[Dict[str, object]] = []
    for summary in summaries:
        baseline = {event: min_counts.get(event, 0) for event in events_ordered}
        extras = {
            event: max(0, summary.event_counts.get(event, 0) - min_counts.get(event, 0))
            for event in events_ordered
        }
        payload.append(
            {
                "participant": summary.participant,
                "group": summary.group,
                "path": summary.rel_path,
                "baseline_min_counts": baseline,
                "extra_trials": extras,
                "total_trials": summary.total_trials,
            }
        )
    return payload


def write_json(payload) -> None:
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(payload, events_ordered) -> None:
    headers = ["participant", "group", "path", "total_trials"]
    for event in events_ordered:
        headers.append(f"{event}_baseline")
        headers.append(f"{event}_extra")
        headers.append(f"{event}_total")

    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in payload:
            baseline = row["baseline_min_counts"]
            extras = row["extra_trials"]
            writer.writerow(
                [
                    row["participant"],
                    row["group"],
                    row["path"],
                    row["total_trials"],
                    *(
                        val
                        for event in events_ordered
                        for val in (
                            baseline.get(event, 0),
                            extras.get(event, 0),
                            baseline.get(event, 0) + extras.get(event, 0),
                        )
                    ),
                ]
            )


def write_plot(summaries, min_counts, events_ordered) -> None:
    if not summaries:
        return

    summaries_sorted = sorted(summaries, key=lambda s: (s.group, s.participant))
    labels = [summary.participant for summary in summaries_sorted]
    indices = range(len(summaries_sorted))

    width = max(12.0, 0.5 * len(labels))
    plt.figure(figsize=(width, 6))

    # Baseline stack (minimum shared counts per event).
    baseline_bottoms = [0] * len(summaries_sorted)
    for event in events_ordered:
        baseline_value = min_counts.get(event, 0)
        if baseline_value <= 0:
            continue
        values = [
            min(baseline_value, summary.event_counts.get(event, 0))
            for summary in summaries_sorted
        ]
        if not any(values):
            continue
        plt.bar(
            indices,
            values,
            bottom=baseline_bottoms,
            color=EVENT_COLORS.get(event, "#999999"),
            alpha=0.35,
            edgecolor="none",
        )
        baseline_bottoms = [
            bottom + value for bottom, value in zip(baseline_bottoms, values)
        ]

    # Extras stack (trials above the minimum).
    extra_bottoms = baseline_bottoms[:]
    legend_containers = []
    for event in events_ordered:
        values = [
            max(
                0,
                summary.event_counts.get(event, 0) - min_counts.get(event, 0),
            )
            for summary in summaries_sorted
        ]
        if not any(values):
            continue
        container = plt.bar(
            indices,
            values,
            bottom=extra_bottoms,
            color=EVENT_COLORS.get(event, "#999999"),
            label=event,
        )
        legend_containers.append(container)
        extra_bottoms = [
            bottom + value for bottom, value in zip(extra_bottoms, values)
        ]

    plt.xticks(indices, labels, rotation=90, fontsize=8)
    plt.ylabel("Trials per event (baseline + extra)")
    plt.title("Trials above the minimum event count per participant")

    if legend_containers:
        event_handles = legend_containers
        event_labels = [container.get_label() for container in legend_containers]
        legend_events = plt.legend(
            handles=event_handles,
            labels=event_labels,
            title="event_verified (extra trials)",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
        )
        plt.gca().add_artist(legend_events)

    baseline_patch = Patch(
        facecolor="#555555",
        alpha=0.35,
        edgecolor="none",
        label="Minimum trials shared across participants",
    )
    plt.legend(handles=[baseline_patch], loc="upper left")

    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=200)
    plt.close()


def main() -> None:
    summaries = collect_summaries()
    if not summaries:
        raise SystemExit("No participant summaries available.")

    events_present = ensure_event_order(
        sorted({event for summary in summaries for event in summary.event_counts})
    )
    events_ordered = events_present
    min_counts = compute_min_counts(summaries, events_ordered)
    payload = build_payload(summaries, min_counts, events_ordered)
    write_json(payload)
    write_csv(payload, events_ordered)
    write_plot(summaries, min_counts, events_ordered)

    print(
        f"Wrote comparison artifacts to {JSON_PATH.relative_to(ROOT)}, "
        f"{CSV_PATH.relative_to(ROOT)}, and {PNG_PATH.relative_to(ROOT)}."
    )


if __name__ == "__main__":
    main()
