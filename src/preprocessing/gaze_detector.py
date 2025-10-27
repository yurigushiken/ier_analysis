"""Gaze event detection logic using 3+ consecutive frame rule."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable, List

import pandas as pd

from src.preprocessing.aoi_mapper import map_what_where_to_aoi


@dataclass
class GazeEvent:
    participant_id: str
    participant_type: str
    age_months: int
    age_group: str
    trial_number: int
    condition: str
    condition_name: str
    segment: str
    aoi_category: str
    gaze_start_frame: int
    gaze_end_frame: int
    gaze_duration_frames: int
    gaze_duration_ms: float
    gaze_onset_time: float
    gaze_offset_time: float


def detect_gaze_events(dataframe: pd.DataFrame, *, min_frames: int = 3) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=[field.name for field in fields(GazeEvent)])

    events: List[GazeEvent] = []

    grouped = dataframe.sort_values(["Participant", "trial_number", "Frame Number"]).groupby(
        ["Participant", "trial_number"], sort=False
    )

    for (_, _), group in grouped:
        _extract_events_from_group(group, events, min_frames=min_frames)

    return pd.DataFrame([event.__dict__ for event in events])


def _extract_events_from_group(group: pd.DataFrame, events: List[GazeEvent], *, min_frames: int) -> None:
    current_aoi = None
    buffer: List[pd.Series] = []

    for _, row in group.iterrows():
        try:
            aoi = map_what_where_to_aoi(row["What"], row["Where"])
        except Exception:
            current_aoi = None
            buffer = []
            continue

        if aoi == current_aoi:
            buffer.append(row)
        else:
            _finalize_event(buffer, events, min_frames)
            current_aoi = aoi
            buffer = [row]

    _finalize_event(buffer, events, min_frames)


def _finalize_event(buffer: List[pd.Series], events: List[GazeEvent], min_frames: int) -> None:
    if len(buffer) < min_frames:
        return

    first = buffer[0]
    last = buffer[-1]

    duration_ms = (float(last["Offset"]) - float(first["Onset"])) * 1000.0

    events.append(
        GazeEvent(
            participant_id=first["Participant"],
            participant_type=first["participant_type"],
            age_months=int(first["participant_age_months"]),
            age_group=str(first.get("age_group", "")),
            trial_number=int(first["trial_number"]),
            condition=first["event_verified"],
            condition_name=str(first.get("condition_name", "")),
            segment=first["segment"],
            aoi_category=map_what_where_to_aoi(first["What"], first["Where"]),
            gaze_start_frame=int(first["frame_count_trial_number"]),
            gaze_end_frame=int(last["frame_count_trial_number"]),
            gaze_duration_frames=len(buffer),
            gaze_duration_ms=duration_ms,
            gaze_onset_time=float(first["Onset"]),
            gaze_offset_time=float(last["Offset"]),
        )
    )


__all__ = ["detect_gaze_events", "GazeEvent"]
