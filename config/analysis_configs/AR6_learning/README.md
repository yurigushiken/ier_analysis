AR-6 example variants and explanation.

Place AR-6 variant YAML files in this folder. Each variant may define one or more `cohorts` with `data_path` relative to `paths.processed_data`.

Fields supported in a variant:
- variant_key, variant_label
- cohorts: list of {key,label,data_path,participant_filters}
- trial_order_effects: slope_threshold, classify_participants
