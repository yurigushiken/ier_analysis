"""Gaze fixation detection logic using 3+ consecutive frame rule."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable, List

import pandas as pd

from src.preprocessing.aoi_mapper import map_what_where_to_aoi


@dataclass
class GazeFixation:
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


def detect_gaze_fixations(dataframe: pd.DataFrame, *, min_frames: int = 3) -> pd.DataFrame:
    """Detect gaze fixations from raw frame data using 3+ consecutive frame rule.

    A gaze fixation is defined as a sequence of 3 or more consecutive frames where
    an infant's gaze remains on the same Area of Interest (AOI). This function
    processes raw eye-tracking data and identifies all valid gaze fixations according
    to the scientific definition from Gordon (2003).
    
    Parameters
    ----------
    dataframe : pd.DataFrame
        Raw frame-by-frame eye-tracking data containing columns:
        - Participant: participant identifier
        - trial_number: trial number within session
        - Frame Number: sequential frame index
        - What, Where: AOI components mapped to AOI categories
        - Onset, Offset: frame timing in seconds
        - participant_type, participant_age_months: demographics
        - event_verified: experimental condition code
        - segment: event segment (approach, action, post)
        - frame_count_trial_number: frame index within trial
    min_frames : int, default=3
        Minimum number of consecutive frames required to constitute a gaze fixation.
        Default is 3 frames as per research protocol.

    Returns
    -------
    pd.DataFrame
        Gaze fixations dataframe with columns:
        - gaze_fixation_id: auto-incremented unique identifier
        - participant_id, participant_type, age_months, age_group
        - trial_number, condition, condition_name, segment
        - aoi_category: mapped AOI label (e.g., "woman_face", "toy_present")
        - gaze_start_frame, gaze_end_frame: frame indices within trial
        - gaze_duration_frames: number of frames in event
        - gaze_duration_ms: duration in milliseconds from Onset/Offset
        - gaze_onset_time, gaze_offset_time: absolute timing in seconds
    
    Notes
    -----
    - Off-screen frames (no,signal AOI) break gaze sequences and are excluded
    - Invalid AOI combinations are silently skipped with sequence reset
    - Fixations are detected independently within each participant × trial combination
    - Frame ordering is critical: data is sorted by Participant, trial_number, Frame Number

    Examples
    --------
    >>> raw_data = load_csv_files(["data/csvs_human_verified_vv/child/"])
    >>> gaze_fixations = detect_gaze_fixations(raw_data, min_frames=3)
    >>> print(f"Detected {len(gaze_fixations)} gaze fixations")
    
    See Also
    --------
    aoi_mapper.map_what_where_to_aoi : Maps What+Where pairs to AOI categories
    master_log_generator.generate_master_log : Wrapper function for full preprocessing
    """
    if dataframe.empty:
        return pd.DataFrame(columns=[field.name for field in fields(GazeFixation)])

    fixations: List[GazeFixation] = []

    grouped = dataframe.sort_values(["Participant", "trial_number", "Frame Number"]).groupby(
        ["Participant", "trial_number"], sort=False
    )

    for (_, _), group in grouped:
        _extract_fixations_from_group(group, fixations, min_frames=min_frames)

    return pd.DataFrame([fixation.__dict__ for fixation in fixations])


def _extract_fixations_from_group(group: pd.DataFrame, fixations: List[GazeFixation], *, min_frames: int) -> None:
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
            _finalize_fixation(buffer, fixations, min_frames)
            current_aoi = aoi
            buffer = [row]

    _finalize_fixation(buffer, fixations, min_frames)


def _finalize_fixation(buffer: List[pd.Series], fixations: List[GazeFixation], min_frames: int) -> None:
    if len(buffer) < min_frames:
        return

    first = buffer[0]
    last = buffer[-1]

    duration_ms = (float(last["Offset"]) - float(first["Onset"])) * 1000.0

    fixations.append(
        GazeFixation(
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


__all__ = ["detect_gaze_fixations", "GazeFixation"]
