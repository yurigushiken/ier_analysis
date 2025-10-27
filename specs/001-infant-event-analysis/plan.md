# Implementation Plan: Infant Event Representation Analysis System

**Branch**: `001-infant-event-analysis` | **Date**: 2025-10-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-infant-event-analysis/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This project implements a comprehensive analysis pipeline for infant event representation research based on Gordon (2003). The system processes frame-by-frame eye-tracking data from CSV files, identifies gaze events (3+ consecutive frames on the same AOI), generates a master gaze_events.csv file, and executes seven analytical requirements (AR-1 through AR-7) to probe infant cognition. Each analysis produces self-contained HTML and PDF reports with statistical tests, visualizations, and interpretations. The entire pipeline is automated, modular, and reproducible, with a final compiled report integrating all findings.

**Technical Approach**: Python-based scientific computing pipeline using pandas for data processing, **Linear Mixed Models (LMM) and Generalized Linear Mixed Models (GLMM) via statsmodels** for statistical analysis (properly handling repeated measures structure), matplotlib/seaborn for visualizations, and Jinja2 + WeasyPrint for reproducible reporting. Each analysis module uses LMM to account for trial-level nesting within participants, providing more accurate inference than traditional t-tests/ANOVA. The system follows a modular architecture with separate preprocessing, individual analysis modules (AR-1 to AR-7), and report compilation components. All intermediate results are saved, logging is comprehensive, and the design supports independent execution of individual analyses. Development in VS Code.

## Technical Context

**Language/Version**: Python 3.12 (latest stable with improved type hints and performance)
**Primary Dependencies**:
- Data: pandas 2.x, numpy 1.26+
- Statistics: scipy 1.11+, statsmodels 0.14+
- Visualization: matplotlib 3.8+, seaborn 0.13+ (statistical plots), networkx 3.2+ (directed graphs)
- Reporting: jinja2 (HTML templates), weasyprint (PDF generation)
- Testing: pytest 8.x, pytest-cov (coverage)
- Validation: pandera 0.18+ (DataFrame schema validation)

**Storage**: File-based (CSV for data, HTML/PDF for reports). Raw data in `data/csvs_human_verified_vv/child/` and `data/csvs_human_verified_vv/adult/`, processed data in `data/processed/`, reports in `results/` and `reports/`

**Testing**: pytest with TDD approach - tests written before implementation, comprehensive coverage including:
- Unit tests for gaze event detection, AOI mapping, statistical functions
- Integration tests for end-to-end pipeline execution
- Data validation tests for CSV structure and integrity
- Contract tests for gaze_events.csv schema

**Target Platform**: Cross-platform (Windows/Linux/macOS) scientific computing environment

**Project Type**: Single scientific analysis project (command-line pipeline with automated reporting)

**Performance Goals**:
- Process 50+ participant CSV files in <10 minutes
- Individual analysis reports generate in <2 minutes each
- Full pipeline (preprocessing + 7 analyses + compilation) completes in <30 minutes for typical dataset

**Constraints**:
- Scientific reproducibility: fixed random seeds, versioned dependencies, documented environment
- Statistical validity: minimum n=3 for statistical tests, proper multiple comparison correction
- Data integrity: never modify raw data, all transformations logged and reversible
- Report quality: publication-ready visualizations with proper axis labels, legends, error bars
- Error handling: STRICT VALIDATION - pipeline MUST halt execution on ANY data errors (structural or quality issues) with clear error messages. No partial results from invalid data are acceptable

**Scale/Scope**:
- **51 child participants** (7-12 months old, mean=9.2 months, SD=1.5 months) + 15 adult controls in separate directory
- **6-11 event types** per participant (mean=10.9) from: gw, gwo, hw, hwo, sw, swo, ugw, ugwo, uhw, uhwo, f
- **~50 event presentations** per participant (range 24-80, total **2,568 presentations** across all participants)
- **3-9 repetitions** per event type per participant (variable by event and participant)
- **Variable frames per event presentation** (~5-33 seconds at 30 fps)
- **5,000-8,500 total frames** per participant file
- **10 AOI categories** (What+Where pairs: no/signal, screen/other, woman/face, man/face, toy/other, toy2/other, man/body, woman/body, man/hands, woman/hands)
- **Experimental design**: 3 Actions (GIVE, HUG, SHOW) × 2 Toy Presence (WITH, WITHOUT) × 2 Orientations (NORMAL, UPSIDE-DOWN) + FLOATING control
- **Nesting structure**: Participant (N=51) → Event Presentation (N≈50 per participant, 2,568 total) → Gaze Event (3+ frames) → Frame (aggregated)
- **7 core analyses + 1 compiled report** = 8 total outputs per run

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Scientific Integrity (NON-NEGOTIABLE)
✓ **PASS**: All analyses use established statistical methods (t-tests, ANOVA, Chi-squared, regression)
✓ **PASS**: Gaze event definition (3+ consecutive frames) is transparent and documented
✓ **PASS**: All assumptions explicitly documented in spec (alpha=0.05, error bar conventions)
✓ **PASS**: Edge case handling is conservative (exclude problematic data, log warnings)

### Reproducibility First
✓ **PASS**: Pipeline is fully automated (single command execution per FR-050, FR-054)
✓ **PASS**: All intermediate results saved (gaze_events.csv, individual reports per FR-052)
✓ **PASS**: Dependencies will be pinned in requirements.txt
✓ **PASS**: Random seed handling: N/A for this project (no randomized processes)
✓ **PASS**: SC-008 explicitly requires reproducible results on repeated runs

### Data Integrity & Provenance
✓ **PASS**: Raw data never modified (read-only from data/csvs_human_verified_vv/ per assumptions)
✓ **PASS**: All transformations documented (FR-053 requires logging of all analysis steps)
✓ **PASS**: Data validation implemented (FR-005a/b/c with strict structural and quality checks)
✓ **PASS**: Pipeline halts on ANY data errors (structural or quality) - no partial results from invalid data

### Code Quality & Maintainability
✓ **PASS**: Modular structure with separated concerns (preprocessing, analyses, reporting per FR-051)
✓ **PASS**: Single-purpose functions enforced by design (each AR is independently executable per SC-007)
✓ **PASS**: File size managed through modularity (7 separate analysis modules + shared utilities)
✓ **PASS**: No duplicate logic (shared statistical and visualization utilities)

### Documentation Excellence
✓ **PASS**: All analyses generate narrative interpretations (FR-011, FR-017, etc.)
✓ **PASS**: Methods section required in reports (FR-049)
✓ **PASS**: README will document setup and execution
✓ **PASS**: Decisions documented in research.md (Phase 0 output)

### Testing & Validation
✓ **PASS**: Comprehensive test requirements per constitution (TDD with fail-first approach)
✓ **PASS**: Data validation tests (FR-005a validates required columns)
✓ **PASS**: Statistical test appropriateness (all methods standard for developmental psychology)
✓ **PASS**: Test coverage enforced through pytest-cov

### Environment Consistency
✓ **PASS**: Python environment reproducible via requirements.txt and conda environment
✓ **PASS**: Dependencies pinned to specific versions
✓ **PASS**: Setup automated via conda environment activation (per constitution line 9)
✓ **PASS**: No manual configuration steps in pipeline execution

**Constitution Compliance**: ✓ ALL GATES PASSED - No violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/001-infant-event-analysis/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (technology decisions, best practices)
├── data-model.md        # Phase 1 output (entities, relationships, validation)
├── quickstart.md        # Phase 1 output (setup and execution guide)
├── contracts/           # Phase 1 output (data schemas, CSV contracts)
│   ├── raw_data_schema.json        # Input CSV structure
│   ├── gaze_events_schema.json     # Master log schema
│   └── report_schema.json          # Report output specifications
├── checklists/
│   └── requirements.md  # Spec quality validation checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── preprocessing/
│   ├── __init__.py
│   ├── csv_loader.py           # Load all CSV files from data/csvs_human_verified_vv/
│   ├── gaze_detector.py        # Identify 3+ frame gaze events
│   ├── aoi_mapper.py           # Map What+Where → AOI categories
│   └── master_log_generator.py # Generate gaze_events.csv
│
├── analysis/
│   ├── __init__.py
│   ├── ar1_gaze_duration.py    # AR-1: Core event salience
│   ├── ar2_transitions.py      # AR-2: Gaze transitions
│   ├── ar3_social_triplets.py  # AR-3: Social cognition patterns
│   ├── ar4_dwell_times.py      # AR-4: Processing depth
│   ├── ar5_development.py      # AR-5: Developmental trajectory
│   ├── ar6_learning.py         # AR-6: Trial-by-trial learning
│   └── ar7_dissociation.py     # AR-7: Complex event dissociation
│
├── reporting/
│   ├── __init__.py
│   ├── visualizations.py       # Shared matplotlib visualization utilities
│   ├── statistics.py           # Shared statistical utilities
│   ├── report_generator.py     # Generate HTML/PDF using Jinja2 + WeasyPrint
│   └── compiler.py             # Compile individual reports into final report
│
├── utils/
│   ├── __init__.py
│   ├── validation.py           # Data validation with pandera schemas
│   ├── logging_config.py       # Logging setup and configuration
│   └── config.py               # Configuration management (YAML loading)
│
└── main.py                     # Main pipeline orchestration

templates/
├── base_report.html            # Base HTML template with common structure
├── ar1_template.html           # AR-1 specific template
├── ar2_template.html           # AR-2 specific template
├── ar3_template.html           # AR-3 specific template
├── ar4_template.html           # AR-4 specific template
├── ar5_template.html           # AR-5 specific template
├── ar6_template.html           # AR-6 specific template
├── ar7_template.html           # AR-7 specific template
├── final_report_template.html  # Compiled report template
└── styles.css                  # Shared CSS for all reports

tests/
├── unit/
│   ├── test_gaze_detector.py
│   ├── test_aoi_mapper.py
│   ├── test_ar1_duration.py
│   ├── test_ar2_transitions.py
│   ├── test_ar3_triplets.py
│   ├── test_ar4_dwell.py
│   ├── test_ar5_development.py
│   ├── test_ar6_learning.py
│   ├── test_ar7_dissociation.py
│   ├── test_visualizations.py
│   └── test_statistics.py
│
├── integration/
│   ├── test_preprocessing_pipeline.py
│   ├── test_analysis_pipeline.py
│   ├── test_report_generation.py
│   └── test_end_to_end.py
│
├── contract/
│   ├── test_raw_csv_schema.py
│   ├── test_gaze_events_schema.py
│   └── test_report_outputs.py
│
└── fixtures/
    ├── sample_raw_data.csv     # Sample input for testing
    ├── expected_gaze_events.csv # Expected preprocessing output
    └── mock_analyses.py        # Mock data for testing

data/
├── raw/
│   ├── child/                  # Infant participant data (read-only)
│   └── adult/                  # Adult control data (read-only)
│
└── processed/
    └── gaze_events.csv         # Master gaze event log (generated)

results/
├── AR1_Gaze_Duration/
│   ├── report.html
│   ├── report.pdf
│   ├── duration_by_condition.png
│   └── summary_stats.csv
├── AR2_Gaze_Transitions/
│   ├── report.html
│   ├── report.pdf
│   ├── transition_matrices.csv
│   └── directed_graph_*.png
├── AR3_Social_Triplets/
├── AR4_Dwell_Times/
├── AR5_Development/
├── AR6_Learning/
└── AR7_Dissociation/

reports/
├── final_report.html           # Compiled report
└── final_report.pdf            # Compiled report

config/
├── environment.yml             # Conda environment specification
├── requirements.txt            # Pinned Python dependencies
├── pipeline_config.yaml        # Global pipeline configuration (alpha, thresholds, etc.)
└── analysis_configs/           # Per-analysis configuration files
    ├── ar1_config.yaml         # AR-1: Gaze Duration settings
    ├── ar2_config.yaml         # AR-2: Gaze Transitions settings
    ├── ar3_config.yaml         # AR-3: Social Triplets settings
    ├── ar4_config.yaml         # AR-4: Dwell Times settings
    ├── ar5_config.yaml         # AR-5: Development settings
    ├── ar6_config.yaml         # AR-6: Learning settings
    └── ar7_config.yaml         # AR-7: Dissociation settings
```

**Structure Decision**: Single scientific analysis project structure with clear separation between preprocessing, individual analyses, and reporting. This structure:
- Supports modular, independent execution of analyses (SC-007)
- Maintains clear data flow: raw → processed → results → reports
- Enables comprehensive testing at unit, integration, and contract levels
- Preserves raw data integrity (read-only access)
- Organizes outputs for easy navigation and audit
- **Hybrid configuration approach**: Global settings in pipeline_config.yaml, analysis-specific parameters in individual config files for maximum modularity and independent execution

## Complexity Tracking

> **Not Required**: All Constitution Check gates passed. No violations to justify.

