# Data Integrity Notes – Event Trial Counts

## Overview

- Processed post-archive raw files at `data/raw/*-gl`, covering 51 participants (36 child, 15 adult).
- For each CSV we counted unique `trial_number_global` instances associated with every `event_verified` label.
- All participants exhibited every event type (`f`, `gw`, `gwo`, `hw`, `hwo`, `sw`, `swo`, `ugw`, `ugwo`, `uhw`, `uhwo`); no additional filtering required on that basis.

## Aggregate Counts

- Adult controls: average 6.4 `hwo` trials and roughly 3 trials per remaining event (total 566 event-labelled trials across the group).
- Child participants: average 8.4 `hwo` trials and between 3.8–4.9 trials for other events (1,834 event-labelled trials overall).

## Artifacts

- Script: `temp/data_integrity/event_trial_counts.py`
- Outputs: `temp/data_integrity/event_trial_counts.json`, `temp/data_integrity/event_trial_counts.png`

## Trials Above Global Minimum

- Minimum trials shared across all participants: `gw=1`, `gwo=3`, `hw=3`, `hwo=4`, `ugw=1`, `ugwo=3`, `uhw=3`, `uhwo=2`, `sw=3`, `swo=3`, `f=1`.
- Additional trials distributed unevenly: top contributors are `Eleven-0301-372` (+53 trials), `Seven-0201-1152` (+45), `Ten-0301-1158` (+45), `Eight-0601-5801` (+44), `Eight-0401-1638` (+42).
- Visualization distinguishes shared baseline (semi-transparent) from extra counts; see `temp/data_integrity/event_trial_min_diff.png`.
- Detailed payloads (baseline and extras per participant) stored in `temp/data_integrity/event_trial_min_diff.json`, with a human-readable table (including total counts) in `temp/data_integrity/event_trial_min_diff.csv`. 
