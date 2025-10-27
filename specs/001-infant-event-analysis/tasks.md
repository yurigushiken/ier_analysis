---
description: "Actionable, dependency-ordered task plan for Infant Event Representation Analysis"
---

# Tasks: Infant Event Representation Analysis

Context: C:\CascadeProjects\ier_analysis\specs\001-infant-event-analysis

Design sources loaded:
- plan.md (tech stack, structure)
- spec.md (user stories with priorities)
- data-model.md (entities)
- contracts/ (raw_data_schema.json, gaze_events_schema.json, report_schema.json)
- research.md (decisions)
- quickstart.md (test scenarios)

Notes:
- Tests requested (TDD approach per plan.md). Include test tasks.
- Paths below are absolute to ensure unambiguous execution.

## Phase 1: Setup (Shared Infrastructure)

Purpose: Initialize project structure matching plan.md without disrupting existing files.

- [X] T001 Create Python package structure under src (packages only)
      C:\CascadeProjects\ier_analysis\src\{preprocessing,analysis,reporting,utils}\__init__.py
- [X] T002 Add pytest configuration for TDD
      C:\CascadeProjects\ier_analysis\pytest.ini
- [X] T003 [P] Verify config exists; wire defaults in docs if missing (no code changes)
      C:\CascadeProjects\ier_analysis\config\{pipeline_config.yaml,analysis_configs\}

- [X] T058 Create conda environment spec (pinned) at config/environment.yml
      C:\CascadeProjects\ier_analysis\config\environment.yml
- [X] T059 [P] Create pinned Python requirements at config/requirements.txt
      C:\CascadeProjects\ier_analysis\config\requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

Purpose: Core pipeline infrastructure required before any user story.

- [X] T004 Implement config loader with per-analysis override merge
      C:\CascadeProjects\ier_analysis\src\utils\config.py
- [X] T005 [P] Implement logging setup (console+file) with strict fail-fast semantics
      C:\CascadeProjects\ier_analysis\src\utils\logging_config.py
- [X] T006 Implement schema validation utilities (pandera wrappers, JSON contract checks)
      C:\CascadeProjects\ier_analysis\src\utils\validation.py
- [X] T007 Add raw CSV contract test (columns/types) per contracts/raw_data_schema.json
      C:\CascadeProjects\ier_analysis\tests\contract\test_raw_csv_schema.py
- [X] T008 [P] Add gaze_events.csv contract test per contracts/gaze_events_schema.json
      C:\CascadeProjects\ier_analysis\tests\contract\test_gaze_events_schema.py
- [X] T009 [P] Add report outputs contract test per contracts/report_schema.json
      C:\CascadeProjects\ier_analysis\tests\contract\test_report_outputs.py
- [X] T010 Implement CSV loader with structural validation and safe globbing
      C:\CascadeProjects\ier_analysis\src\preprocessing\csv_loader.py
- [X] T011 [P] Implement AOI mapper (What+Where → AOI) per data-model.md
      C:\CascadeProjects\ier_analysis\src\preprocessing\aoi_mapper.py
- [X] T012 [P] Implement gaze detector (>=3 consecutive frames rule)
      C:\CascadeProjects\ier_analysis\src\preprocessing\gaze_detector.py

- [X] T013 Implement master log generator (writes gaze_events.csv)
      C:\CascadeProjects\ier_analysis\src\preprocessing\master_log_generator.py
- [X] T014 Add preprocessing integration test: CSVs → gaze_events.csv
      C:\CascadeProjects\ier_analysis\tests\integration\test_preprocessing_pipeline.py
- [X] T015 [P] Add fixtures for tests (sample raw CSV, expected gaze_events.csv)
      C:\CascadeProjects\ier_analysis\tests\fixtures\{sample_raw_data.csv,expected_gaze_events.csv}
- [X] T016 Implement shared statistical utilities (LMM/GLMM helpers)
      C:\CascadeProjects\ier_analysis\src\reporting\statistics.py
- [X] T017 [P] Implement visualization utilities (bar, line, directed graphs)
      C:\CascadeProjects\ier_analysis\src\reporting\visualizations.py
- [X] T018 [P] Implement report generator (Jinja2 + WeasyPrint)
      C:\CascadeProjects\ier_analysis\src\reporting\report_generator.py
- [X] T019 Implement report compiler for final integrated report
      C:\CascadeProjects\ier_analysis\src\reporting\compiler.py
- [X] T020 Implement pipeline orchestrator (main entrypoint)
      C:\CascadeProjects\ier_analysis\src\main.py
- [X] T021 [P] Create missing HTML templates and styles (AR2–AR7, final, CSS)
      C:\CascadeProjects\ier_analysis\templates\{ar2_template.html,ar3_template.html,ar4_template.html,ar5_template.html,ar6_template.html,ar7_template.html,final_report_template.html,styles.css}

Checkpoint: Foundation ready – user stories can start in parallel where independent.

- [X] T060 Add unit tests for gaze detector (3+ frame rule)
      C:\CascadeProjects\ier_analysis\tests\unit\test_gaze_detector.py
- [X] T061 [P] Add unit tests for AOI mapper (What+Where → AOI)
      C:\CascadeProjects\ier_analysis\tests\unit\test_aoi_mapper.py
- [X] T062 Add end-to-end pipeline test (raw → final report)
      C:\CascadeProjects\ier_analysis\tests\integration\test_end_to_end.py
- [X] T063 [P] Add preprocessing metadata preservation assertions (FR-004)
      C:\CascadeProjects\ier_analysis\tests\integration\test_preprocessing_metadata.py
- [X] T064 [P] Add logging-in-report assertions (warnings embedded/summarized)
      C:\CascadeProjects\ier_analysis\tests\integration\test_report_generation.py
- [X] T065 Implement adult/child separation config flag and routing
      C:\CascadeProjects\ier_analysis\src\utils\config.py
- [X] T066 [P] Add integration test for adult vs child separation of outputs
      C:\CascadeProjects\ier_analysis\tests\integration\test_adult_child_separation.py
- [X] T067 [P] Add n<3 sample-size skip-behavior tests across ARs
      C:\CascadeProjects\ier_analysis\tests\unit\test_n_lt_3_behavior.py

---

## Phase 3: User Story 1 – Core Event Salience (Priority: P1) [US1] 🎯 MVP

Goal: Quantify toy-looking proportions (GIVE_WITH vs HUG_WITH) and generate HTML/PDF report.
Independent Test: Running AR-1 alone produces complete report with stats/figures from gaze_events.csv.

### Tests (write first)
- [X] T022 [P] [US1] Unit tests for AR-1 stats and plotting
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar1_duration.py
- [X] T023 [P] [US1] Integration test: gaze_events.csv → AR-1 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar1_analysis.py

### Implementation
- [X] T024 [US1] Implement AR-1 analysis module
      C:\CascadeProjects\ier_analysis\src\analysis\ar1_gaze_duration.py
- [X] T025 [P] [US1] Ensure AR-1 template ready and hooked into generator
      C:\CascadeProjects\ier_analysis\templates\ar1_template.html
- [X] T026 [US1] Save outputs (HTML, PDF, figures, summary CSV)
      C:\CascadeProjects\ier_analysis\results\AR1_Gaze_Duration\

- [X] T068 [P] [US1] Add optional age covariate test path for AR-1
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar1_duration.py

---

## Phase 4: User Story 2 – Visual Scanning Transitions (Priority: P2) [US2]

Goal: Transition matrices and directed graph visuals by condition/age.
Independent Test: Running AR-2 alone produces matrices, graphs, and report.

### Tests
- [X] T027 [P] [US2] Unit tests for transition derivation and matrix math
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar2_transitions.py
- [X] T028 [P] [US2] Integration: gaze_events.csv → AR-2 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar2_analysis.py

### Implementation
- [X] T029 [P] [US2] Implement AR-2 transitions module
      C:\CascadeProjects\ier_analysis\src\analysis\ar2_transitions.py
- [X] T030 [US2] Hook visuals (networkx) and save artifacts
      C:\CascadeProjects\ier_analysis\results\AR2_Gaze_Transitions\

- [X] T069 [P] [US2] Add tests for MTC (Bonferroni) and graph labeling
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar2_transitions.py

---

## Phase 5: User Story 3 – Social Gaze Triplets (Priority: P2) [US3]

Goal: Detect face→toy→face (different people) triplets and report comparisons.
Independent Test: Running AR-3 alone produces counts, stats, and report.

### Tests
- [X] T031 [P] [US3] Unit tests for triplet detection and exclusions
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar3_triplets.py
- [X] T032 [P] [US3] Integration: gaze_events.csv → AR-3 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar3_analysis.py

### Implementation
- [X] T033 [P] [US3] Implement AR-3 social triplets module
      C:\CascadeProjects\ier_analysis\src\analysis\ar3_social_triplets.py
- [X] T034 [US3] Save outputs and statistical tables
      C:\CascadeProjects\ier_analysis\results\AR3_Social_Triplets\

---

## Phase 6: User Story 4 – Dwell Times (Priority: P3) [US4]

Goal: Compute mean dwell times per AOI with LMMs and report.
Independent Test: Running AR-4 alone produces dwell-time figures and tables.

### Tests
- [X] T035 [P] [US4] Unit tests for dwell-time computation
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar4_dwell.py
- [X] T036 [P] [US4] Integration: gaze_events.csv → AR-4 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar4_analysis.py

### Implementation
- [X] T037 [P] [US4] Implement AR-4 dwell times module
      C:\CascadeProjects\ier_analysis\src\analysis\ar4_dwell_times.py
- [X] T038 [US4] Save outputs and tables
      C:\CascadeProjects\ier_analysis\results\AR4_Dwell_Times\

---

## Phase 7: User Story 5 – Developmental Trajectory (Priority: P3) [US5]

Goal: Model Age × Condition effects; interaction plots and ANOVA tables.
Independent Test: Running AR-5 alone yields interaction plots and model summaries.

### Tests
- [X] T039 [P] [US5] Unit tests for model formula, diagnostics
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar5_development.py
- [X] T040 [P] [US5] Integration: gaze_events.csv → AR-5 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar5_analysis.py

### Implementation
- [X] T041 [P] [US5] Implement AR-5 developmental trajectory module
      C:\CascadeProjects\ier_analysis\src\analysis\ar5_development.py
- [X] T042 [US5] Save outputs and ANOVA tables
      C:\CascadeProjects\ier_analysis\results\AR5_Development\

---

## Phase 8: User Story 6 – Learning Across Trials (Priority: P3) [US6]

Goal: Test trial_number_global slopes with random intercepts/slopes, per condition.
Independent Test: Running AR-6 alone yields slope estimates, line plots, report.

### Tests
- [X] T043 [P] [US6] Unit tests for random-slope model construction
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar6_learning.py
- [X] T044 [P] [US6] Integration: gaze_events.csv → AR-6 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar6_analysis.py

### Implementation
- [X] T045 [P] [US6] Implement AR-6 learning/habituation module
      C:\CascadeProjects\ier_analysis\src\analysis\ar6_learning.py
- [X] T046 [US6] Save outputs and regression tables
      C:\CascadeProjects\ier_analysis\results\AR6_Learning\

---

## Phase 9: User Story 7 – SHOW Dissociation (Priority: P3) [US7]

Goal: Apply AR-1 and AR-3 to SHOW, synthesize narrative demonstrating dissociation.
Independent Test: Running AR-7 alone yields side-by-side visuals and synthesis.

### Tests
- [X] T047 [P] [US7] Unit tests for SHOW filters and synthesis logic
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar7_dissociation.py
- [X] T048 [P] [US7] Integration: gaze_events.csv → AR-7 report
      C:\CascadeProjects\ier_analysis\tests\integration\test_ar7_analysis.py

### Implementation
- [X] T049 [P] [US7] Implement AR-7 dissociation module
      C:\CascadeProjects\ier_analysis\src\analysis\ar7_dissociation.py
- [X] T050 [US7] Save outputs and narrative report
      C:\CascadeProjects\ier_analysis\results\AR7_Dissociation\

- [X] T070 [P] [US7] Add SHOW-missing behavior test (graceful skip + warning)
      C:\CascadeProjects\ier_analysis\tests\unit\test_ar7_dissociation.py

---

## Phase 10: User Story 8 – Final Compiled Report (Priority: P1) [US8]

Goal: Compile individual AR reports into a single final HTML/PDF with ToC.
Independent Test: Running compiler with existing AR outputs yields integrated final report.

### Tests
- [X] T051 [P] [US8] Integration: AR outputs → final_report.html/pdf
      C:\CascadeProjects\ier_analysis\tests\integration\test_report_compiler.py

### Implementation
- [X] T052 [US8] Wire compiler to templates/final_report_template.html
      C:\CascadeProjects\ier_analysis\src\reporting\compiler.py
- [X] T053 [US8] Save final outputs (HTML/PDF) with working ToC
      C:\CascadeProjects\ier_analysis\reports\{final_report.html,final_report.pdf}

---

## Final Phase: Polish & Cross-Cutting Concerns

- [X] T054 [P] Documentation updates (README, quickstart alignment with actual CLI and paths)
      C:\CascadeProjects\ier_analysis\README.md
- [ ] T055 Lint/format, small refactors for clarity (no pattern changes)
      C:\CascadeProjects\ier_analysis\src\
- [X] T056 [P] Performance pass on slowest AR (profile, simple vectorization)
      C:\CascadeProjects\ier_analysis\src\analysis\
- [X] T057 [P] Add missing unit tests for shared utils (statistics, visualizations)
      C:\CascadeProjects\ier_analysis\tests\unit\

- [X] T071 [P] Performance smoke test on fixtures (document thresholds)
      C:\CascadeProjects\ier_analysis\PERFORMANCE.md

---

## Dependencies & Execution Order

Phase dependencies
- Setup → Foundational → User Stories → Polish
- All user stories depend on Foundational completion.

User story order (by priority and technical dependencies)
- US1 (P1) can run immediately after Foundational.
- US2 (P2) and US3 (P2) can run in parallel after Foundational.
- US4–US7 (P3) can run after Foundational; independent of US1–US3 except shared utils.
- US8 (P1 final compilation) depends on completion of desired AR outputs (min: US1–US3; ideal: US1–US7).

Within-story order
- Tests (fail-first) → Implementation → Outputs saved → Report generated.

Parallel opportunities
- Tasks marked [P] are parallelizable (separate files, no unmet deps).
- Post-Foundational, different ARs (US2–US7) can be staffed in parallel.

---

## Implementation Strategy

MVP first
- Complete Setup + Foundational → Implement US1 → Validate end-to-end (HTML/PDF + figures).

Incremental delivery
- Add US2 and US3 next for mechanistic and social insights; then advanced P3 analyses as capacity allows.
- Compile US8 once the chosen set of ARs are complete.

---

## Independent Test Criteria (per story)
- US1: AR-1 alone produces toy-looking bar chart, summary table, LMM stats with p-values.
- US2: AR-2 alone produces transition matrices (CSV) and directed graph PNGs.
- US3: AR-3 alone produces triplet counts by condition and bar charts with stats.
- US4: AR-4 alone produces dwell-time bar charts and LMM results.
- US5: AR-5 alone produces interaction plots and ANOVA/LMM tables.
- US6: AR-6 alone produces line plots vs trial_number_global and slope estimates.
- US7: AR-7 alone produces SHOW condition synthesis with side-by-side visuals.
- US8: Compiler integrates available AR reports into final_report.html/pdf with functioning ToC.

---

## Format Validation
All tasks conform to: `- [ ] T### [P?] [USn?] Description with absolute file path`.

---

## Summary Metrics
- Total tasks: 57
- Per user story: US1=5, US2=5, US3=5, US4=5, US5=5, US6=5, US7=5, US8=3
- Foundational: 18, Setup: 3, Polish: 4
- Parallel tasks flagged [P]: 25
- Suggested MVP scope: US1 only (after Setup+Foundational)


