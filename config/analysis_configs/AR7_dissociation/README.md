AR-7 example variants and notes.

Place AR-7 variant YAML files in this folder. Each variant may define one or more `cohorts` with `data_path` relative to `paths.processed_data`.

Fields supported in a variant:
- variant_key, variant_label
- cohorts: list of {key,label,data_path,participant_filters}
- target_conditions: list of condition tokens (GIVE, HUG, SHOW)
