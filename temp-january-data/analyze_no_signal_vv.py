from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
VV_DIR = REPO_ROOT / "data" / "csvs_human_verified_vv"
OUT_DIR = REPO_ROOT / "temp-january-data"


def normalize_header_map(fieldnames: Iterable[str]) -> Dict[str, str]:
    lower_to_actual: Dict[str, str] = {}
    for name in fieldnames:
        lower_to_actual[name.lower()] = name
    return lower_to_actual


@dataclass
class ParticipantCounts:
    participant: str
    participant_type: str  # e.g., 'adult' or 'child' if available
    total_rows: int = 0
    no_signal_rows: int = 0

    @property
    def proportion(self) -> float:
        return (self.no_signal_rows / self.total_rows) if self.total_rows else 0.0


def iter_csv_paths() -> Iterable[Tuple[Path, str]]:
    # Yield (path, participant_type_guess) for vv CSV files under adult/child subfolders
    for sub in ("adult", "child"):
        base = VV_DIR / sub
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.csv")):
            yield p, sub


def analyze() -> Dict[str, ParticipantCounts]:
    by_participant: Dict[str, ParticipantCounts] = {}
    for csv_path, ptype_guess in iter_csv_paths():
        with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                continue
            header_map = normalize_header_map(reader.fieldnames)
            # Resolve columns case-insensitively
            p_col = header_map.get("participant")
            what_col = header_map.get("what")
            where_col = header_map.get("where")
            if not (p_col and what_col and where_col):
                # Skip files missing required headers
                continue

            for row in reader:
                participant = (row.get(p_col) or "").strip()
                what = (row.get(what_col) or "").strip().lower()
                where = (row.get(where_col) or "").strip().lower()
                if not participant:
                    # Fallback: use filename stem if Participant missing
                    participant = csv_path.stem

                rec = by_participant.get(participant)
                if rec is None:
                    rec = ParticipantCounts(participant=participant, participant_type=ptype_guess)
                    by_participant[participant] = rec

                rec.total_rows += 1
                if what == "no" and where == "signal":
                    rec.no_signal_rows += 1

    return by_participant


def write_outputs(by_participant: Dict[str, ParticipantCounts]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = sorted(
        by_participant.values(),
        key=lambda r: (-r.no_signal_rows, r.participant.lower()),
    )

    # CSV output
    csv_path = OUT_DIR / "no_signal_counts_ranked.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "participant",
            "participant_type",
            "no_signal_rows",
            "total_rows",
            "proportion_no_signal",
        ])
        for r in records:
            writer.writerow([r.participant, r.participant_type, r.no_signal_rows, r.total_rows, f"{r.proportion:.6f}"])

    # JSON output
    json_path = OUT_DIR / "no_signal_counts_ranked.json"
    payload = [
        {
            "participant": r.participant,
            "participant_type": r.participant_type,
            "no_signal_rows": r.no_signal_rows,
            "total_rows": r.total_rows,
            "proportion_no_signal": r.proportion,
        }
        for r in records
    ]
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # Simple summary text
    txt_path = OUT_DIR / "no_signal_counts_summary.txt"
    lines = [
        f"Participants analyzed: {len(records)}",
        "Top 20 by no-signal rows:",
    ]
    for r in records[:20]:
        lines.append(
            f"{r.participant} ({r.participant_type}) -> no_signal={r.no_signal_rows}, total={r.total_rows}, proportion={r.proportion:.2%}"
        )
    txt_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = analyze()
    write_outputs(results)
    print(f"Analyzed {len(results)} participants. Outputs written to {OUT_DIR}.")


if __name__ == "__main__":
    main()


