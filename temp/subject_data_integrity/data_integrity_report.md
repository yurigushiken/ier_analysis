# Data Integrity Report

## Event Coverage Snapshot

- Unique `event_verified` labels detected: `f`, `gw`, `gwo`, `hw`, `hwo`, `sw`, `swo`, `ugw`, `ugwo`, `uhw`, `uhwo`.
- Adult controls (`data/raw/adult-gl/*.csv`): all 15 files include the full set of 11 events.
- Infant records missing events:
  - `data/raw/child-gl/Eight-months-0101-1579gl.csv`: missing `gw`.
  - `data/raw/child-gl/Seven-months-0301-1342lg.csv`: missing `f`, `ugw`, `ugwo`, `uhw`, `uhwo`.

## Signal Dropout Analysis

- Calculated per-file proportions of rows where `What="no"` and `Where="signal"` (missing gaze signal). Source: `temp/data_integrity/no_signal_proportion.json`.
- Adult controls (`data/raw/adult-gl`, n=15): mean dropout 0.093, median 0.062. Lowest dropout `TwentyThree-years-0601-1671vv` at 1.9%; highest adult `ThirtyNine-years-0101-1660vv` at 17.9%.
- Infant participants (`data/raw/child-gl`, n=41): mean dropout 0.505, median 0.488. Highest dropout `Eleven-months-0401-682gl` at 87.4%; lowest infant `Ten-months-0501-455lg` at 2.6%.
- Ranked bar chart of all participants saved to `temp/data_integrity/no_signal_proportion.png`.

## Fully Missing-Signal Trials

- Updated logic groups rows by `trial_number_global` (unique trials per participant) before aggregating.
- 499 trials analysed across 56 participants; results saved to `temp/data_integrity/no_signal_full_trial.json`.
- 22 infant trials were entirely missing signal (e.g., `Eleven-months-0401-682gl`: 8 trials; `Seven-months-0401-1655lg`: 5; `Ten-months-0102-5728lg`: 4). No adult trial was fully missing.
- Ranked bar chart (`temp/data_integrity/no_signal_full_trial.png`) highlights participants with the highest counts of fully missing trials.
