# put data in data\csvs_human_verified_vv

# Infant Event Representation Analysis Pipeline

**A comprehensive eye-tracking analysis system for studying infant cognitive development**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

---

## Overview

This project analyzes infant eye-tracking data to understand how pre-verbal infants comprehend event structure and verb-argument relationships. Using frame-by-frame gaze data, the pipeline generates seven comprehensive statistical analyses examining different aspects of infant visual attention during action observation.

**Research Question**: *How do infants distinguish between essential and incidental elements of observed events before they can speak?*

Based on foundational work by Gordon (2003), this system uses high-resolution eye-tracking to move beyond simple "looking time" measures to understand *how* infants visually parse complex social events.

### What This Pipeline Does

The system processes raw eye-tracking CSV files and produces:
- ✅ **7 Statistical Analyses** (AR-1 through AR-7) examining different cognitive dimensions
- ✅ **Individual HTML/PDF Reports** for each analysis with visualizations and interpretations
- ✅ **Compiled Final Report** integrating all findings with table of contents
- ✅ **Master Gaze Fixation Log** for further analysis in external tools (R, SPSS, etc.)
- ✅ **Statistical Tables & Figures** ready for publication

---

## Quick Start

### Installation

```bash
# 1. Navigate to project directory
cd C:\CascadeProjects\ier_analysis

# 2. Create and activate conda environment
conda env create -f config/environment.yml
conda activate ier_analysis

# 3. Verify installation
pytest tests/ -v
```

### Running AR-4 Dwell-Time Analysis

Activate the conda environment first:

```bash
conda activate ier_analysis
```

Run AR-4 using the currently configured variant:

```bash
python -c "from src.utils.config import load_config; from src.analysis import ar4_dwell_times as ar4; cfg = load_config(); ar4.run(config=cfg)"
```

Run AR-4 with an explicit YAML override (`AR4_dwell_times/ar4_gw_vs_gwo`):

```bash
python -c "from src.utils.config import load_config; from src.analysis import ar4_dwell_times as ar4; cfg = load_config(overrides=['analysis_specific.ar4_dwell_times.config_name=AR4_dwell_times/ar4_gw_vs_gwo']); ar4.run(config=cfg)"
```

### Running the Analysis (after all AR updates)

```bash
# Ensure environment is activated
conda activate ier_analysis

# Run full pipeline (preprocessing → 7 analyses → final report)
python src/main.py
```

**Output**: 
- `data/processed/gaze_fixations_child.csv` - Master gaze fixation log
- `results/AR*/` - Individual analysis reports and figures
- `reports/final_report.html` - Comprehensive compiled report

📖 **See [quickstart.md](./specs/001-infant-event-analysis/quickstart.md) for detailed setup instructions**

**Please note:** until every AR module is fully updated, avoid running the full pipeline or full `pytest` suite. Focus on the analyses that have been brought up-to-date (currently AR-1 through AR-4) and their dedicated tests.

---

## Current Status & Next Steps

- ✅ **AR-1 – AR-3**: Updated with refreshed configs, batch runners, and reporting (AR-3 now includes GLMM summaries).
- ⚙️ **AR-4**: Batch runner available; analysis executes but still triggers known visualization warnings (`visualizations.violin_plot` placeholder). Stabilization is the next engineering focus.
- ⏳ **AR-5 – AR-7**: Legacy implementations remain; work will resume after AR-4 fixes are completed.

These priorities are reflected throughout the README—new instructions target the functioning modules while we continue to triage AR-4 and prepare the remaining analyses for modernization.

---

## The Seven Analyses (AR-1 through AR-7)

### **AR-1: Gaze Duration Analysis**
**Question**: *Do infants look longer at primary AOIs (faces, toy) in GIVE vs HUG conditions?*

- Calculates proportion of time looking at faces and toy
- Independent samples t-test comparing GIVE vs HUG
- Bar charts with error bars
- Outputs saved to variant-specific folders: `results/AR1_gaze_duration/<variant_key>/`
- **Key Finding**: Differential attention patterns across event types

---

### **AR-2: Gaze Transition Analysis**
**Question**: *How do infants shift attention between different areas of interest?*

- Computes transition probability matrices (e.g., face → toy → face)
- Generates directed network graphs showing gaze flow
- Tests for non-random transition patterns
- **Key Finding**: Systematic scanning strategies reveal event comprehension

---

### **AR-3: Social Gaze Triplet Analysis**
**Question**: *Do infants produce face→toy→face sequences more in GIVE than HUG?*

- Detects face-object-face triplets across different people
- Chi-square tests comparing triplet frequency by condition
- Excludes self-loops and same-person triplets
- **Key Finding**: Social gaze patterns differ by argument structure (3-arg vs 2-arg events)

---

### **AR-4: Dwell Time Analysis**
**Question**: *How long do infants fixate on each AOI in a single gaze fixation?*

- Calculates mean dwell time per AOI category
- Linear Mixed Models (LMM) with random effects for participants
- Separate analyses by AOI (toy, faces, bodies, etc.)
- **Key Finding**: Object vs social attention balance varies by event type

---

### **AR-5: Developmental Trajectory Analysis**
**Question**: *How does infant age interact with experimental condition?*

- Tests Age × Condition interaction using Linear Mixed Models
- Continuous age modeling (in months) with optional quadratic terms
- Interaction plots showing developmental change
- **Key Finding**: Developmental timeline of event comprehension abilities

---

### **AR-6: Trial-Order Effects (Learning/Habituation) Analysis**
**Question**: *Do infants show learning or habituation across repeated presentations?*

- Fits LMM with **random slopes** (gold standard for habituation research)
- Tests if trial number predicts gaze patterns
- Each participant has their own learning/habituation rate
- Line plots with individual trajectories
- **Key Finding**: Real-time adaptation processes during experimental session

---

### **AR-7: Event Dissociation Analysis**
**Question**: *Do infants differentiate GIVE, HUG, and SHOW despite similar visual properties?*

- Compares multiple conditions with pairwise comparisons (Bonferroni corrected)
- Cohen's d effect sizes for each contrast
- Tests for dissociation: different social gaze despite similar toy attention
- **Key Finding**: Event understanding beyond mere visual salience

---

## Project Structure

```
ier_analysis/
├── config/                          # Configuration files
│   ├── pipeline_config.yaml         # Main pipeline settings
│   ├── analysis_configs/            # Per-analysis configurations (AR-1 to AR-7)
│   ├── environment.yml              # Conda environment specification
│   └── requirements.txt             # Python dependencies
│
├── data/
│   ├── raw/                         # Original eye-tracking CSVs (not in git)
│   │   ├── child-gl/                # Infant participants
│   │   └── adult-gl/                # Adult controls
│   ├── csvs_human_verified_vv/      # Human-verified annotated data
│   │   ├── child/                   # Verified infant data
│   │   └── adult/                   # Verified adult data
│   └── processed/
│       └── gaze_fixations_child.csv    # Master gaze fixation log (generated)
│
├── src/                             # Source code
│   ├── preprocessing/               # Data loading and gaze detection
│   │   ├── csv_loader.py            # Load and validate CSVs
│   │   ├── aoi_mapper.py            # Map What+Where to AOI categories
│   │   ├── gaze_detector.py         # Detect 3+ frame gaze fixations
│   │   └── master_log_generator.py  # Generate master gaze fixation log
│   │
│   ├── analysis/                    # Analysis modules (AR-1 to AR-7)
│   │   ├── ar1_gaze_duration.py     # Gaze duration analysis
│   │   ├── ar2_transitions.py       # Transition analysis
│   │   ├── ar3_social_triplets.py   # Social gaze triplets
│   │   ├── ar4_dwell_times.py       # Dwell time analysis
│   │   ├── ar5_development.py       # Developmental trajectories
│   │   ├── ar6_learning.py          # Trial-order effects
│   │   └── ar7_dissociation.py      # Event dissociation
│   │
│   ├── reporting/                   # Report generation utilities
│   │   ├── report_generator.py      # HTML/PDF rendering
│   │   ├── compiler.py              # Compile final report
│   │   ├── statistics.py            # Statistical utilities
│   │   └── visualizations.py        # Plotting functions
│   │
│   ├── utils/                       # Shared utilities
│   │   ├── config.py                # Configuration loading
│   │   ├── logging_config.py        # Logging setup
│   │   └── validation.py            # Data validation
│   │
│   └── main.py                      # Main pipeline orchestrator
│
├── templates/                       # Jinja2 HTML templates
│   ├── ar1_template.html ... ar7_template.html
│   ├── final_report_template.html
│   └── styles.css
│
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests (24 tests)
│   ├── integration/                 # Integration tests (17 tests)
│   └── contract/                    # Schema validation tests
│
├── results/                         # Analysis outputs (generated)
│   ├── AR1_gaze_duration/
│   ├── AR2_gaze_transitions/
│   ├── AR3_social_triplets/
│   ├── AR4_dwell_times/
│   └── ... (AR5-AR7)
│
├── reports/                         # Final compiled reports (generated)
│   ├── final_report.html
│   └── final_report.pdf
│
├── specs/                           # Legacy documentation (kept for reference)
│   └── 001-infant-event-analysis/
│       ├── data-model.md            # Data schemas
│       ├── quickstart.md            # Setup guide
│       ├── research.md              # Technical research notes
│       └── ...                      # Archived planning docs
│
├── study-info.md                    # Detailed study background
├── README.md                        # This file
└── pytest.ini                       # Pytest configuration
```

---

## Key Features

### 🔬 **Scientific Rigor**
- **Schema Validation**: All data validated against strict JSON schemas (pandera)
- **Reproducibility**: All parameters logged; random seeds set
- **Transparent Exclusions**: Every exclusion documented with reason
- **Multiple Comparison Correction**: Bonferroni, FDR where appropriate
- **Effect Sizes**: Cohen's d, R² reported alongside p-values

### 📊 **Advanced Statistics**
- **Linear Mixed Models (LMM)**: Account for repeated measures and individual differences
- **Random Effects**: Random intercepts and slopes where appropriate
- **Model Comparison**: AIC/BIC for model selection
- **Diagnostics**: Residual checks, convergence warnings

### 🎨 **Professional Reporting**
- **HTML Reports**: Interactive, web-based viewing
- **PDF Reports**: Publication-ready documents
- **High-DPI Figures**: 300 DPI PNG exports
- **Narrative Text**: Auto-generated interpretations
- **Table of Contents**: Hyperlinked navigation

### ⚡ **Robust Processing**
- **Error Handling**: Graceful degradation with informative warnings
- **Data Validation**: Halt-on-error for data quality issues
- **Logging**: Detailed execution logs for troubleshooting
- **Test Coverage**: 41 tests ensuring reliability

---

## Data Requirements

### Input Format

Raw CSV files must contain these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Participant` | string | Unique participant ID | `"Eight-months-0101"` |
| `Age` | string | Age group | `"8-month-olds"` |
| `Trial` | int | Trial number within block | `1, 2, 3, ...` |
| `Condition` | string | Experimental condition code | `"gw"` (GIVE_WITH) |
| `Event` | string | Event number within trial | `"1"` |
| `Frame` | int | Frame number | `1, 2, 3, ...` |
| `What` | string | What infant is looking at | `"toy"`, `"man"`, `"woman"` |
| `Where` | string | Where on that object | `"face"`, `"body"`, `"present"` |
| `Time_Onset` | float | Timestamp of frame onset | `0.033` (seconds) |

📖 **See [data-model.md](./specs/001-infant-event-analysis/data-model.md) for complete schema**

### Gaze Fixation Detection Rules

A **gaze fixation** is defined as:
- ✅ **3+ consecutive frames** looking at the same AOI (Area of Interest)
- ✅ AOI determined by `What`+`Where` combination
- ✅ Examples: `"man_face"`, `"toy_present"`, `"woman_body"`

**Special Cases**:
- `NO_SIGNAL` (off-screen): Tracked but excluded from most analyses
- `IRRELEVANT` (ceiling, floor): Excluded
- Transitions require AOI change (not just What/Where alone)

---

## Running Individual Analyses

You can run any analysis independently after preprocessing:

```bash
# First, generate master gaze fixations file
python src/preprocessing/master_log_generator.py

# Then run individual analyses
$env:IER_AR1_CONFIG='AR1_gaze_duration/ar1_gw_vs_hw'  # choose AR-1 variant
python -m src.analysis.ar1_gaze_duration
Remove-Item Env:IER_AR1_CONFIG
python -m src.analysis.ar2_transitions
python -m src.analysis.ar3_social_triplets
python -m src.analysis.ar4_dwell_times
python -m src.analysis.ar5_development
python -m src.analysis.ar6_learning
python -m src.analysis.ar7_dissociation

# Finally, compile into final report
python -m src.reporting.compiler
```

### Batch-running AR variants

Use the helper scripts in `scripts/` to execute every YAML variant for a given analysis module. Run whichever analysis you need—each script walks through `config/analysis_configs/<arN>/*.yaml`.

```powershell
conda activate ier_analysis
python scripts/run_ar1_variants.py
```

```powershell
conda activate ier_analysis
python scripts/run_ar2_variants.py
```

```powershell
conda activate ier_analysis
python scripts/run_ar3_variants.py
```

```powershell
conda activate ier_analysis
python scripts/run_ar4_variants.py
```

Each analysis generates:
- `results/AR*_*/report.html` - Web-viewable report
- `results/AR*_*/report.pdf` - Printable report
- `results/AR*_*/*.csv` - Data tables
- `results/AR*_*/*.png` - Figures

---

## Development & Testing

### Running Tests

```bash
# All tests (41 tests)
pytest tests/ -v

# Only unit tests (24 tests)
pytest tests/unit/ -v

# Only integration tests (17 tests)
pytest tests/integration/ -v

# Specific analysis tests
pytest tests/unit/test_ar5_development.py -v
pytest tests/integration/test_ar7_analysis.py -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Coverage

- **Unit Tests**: Individual functions and classes
  - AR-1 to AR-7 analysis logic
  - Gaze detection algorithms
  - Statistical computations
  - Visualization functions

- **Integration Tests**: End-to-end workflows
  - Preprocessing pipeline
  - Individual analysis reports
  - Report compilation
  - Multi-condition scenarios

- **Contract Tests**: Schema validation
  - Raw CSV validation
  - Gaze fixations schema
  - Report output structure

---

## Configuration

### Pipeline Configuration (`config/pipeline_config.yaml`)

```yaml
analysis:
  alpha: 0.05                        # Statistical significance threshold
  min_gaze_frames: 3                 # Minimum frames for gaze fixation
  min_statistical_n: 3               # Minimum sample size

edge_cases:
  strategy: "halt_on_any_error"      # HALT on data quality issues

paths:
  raw_data: "data/csvs_human_verified_vv"
  processed_data: "data/processed"
  results: "results"
  final_reports: "reports"
```

### Analysis-Specific Configs (`config/analysis_configs/`)

Each analysis (AR-1 to AR-7) has its own YAML configuration:
- `ar1_config.yaml` - Gaze duration settings
- `ar2_config.yaml` - Transition analysis settings
- `ar3_config.yaml` - Social triplet detection rules
- `ar4_config.yaml` - Dwell time filtering
- `ar5_config.yaml` - Developmental modeling (age range, nonlinear terms)
- `ar6_config.yaml` - Trial-order effects (random slopes, habituation criteria)
- `ar7_config.yaml` - Dissociation contrasts (pairwise comparisons)

---

## Troubleshooting

### Common Issues

**"No module named 'pandera'"**
```bash
conda activate ier_analysis
pip install -r config/requirements.txt
```

**"No gaze fixations detected"**
- Check that raw CSVs have correct column names
- Verify `What`+`Where` combinations are valid
- Review `logs/pipeline.log` for details

**"Insufficient statistical power"**
- This is a warning, not an error
- Analysis continues but skips underpowered comparisons
- Consider collecting more data or combining age groups

**PDF exports temporarily disabled**
- HTML reports still work – open in browser and print if needed
- PDF generation will return in a future update once the pipeline stabilises

📖 **See [quickstart.md](./specs/001-infant-event-analysis/quickstart.md) for detailed troubleshooting**

---

## Scientific Background

### Research Context

This project builds on foundational work in developmental cognitive science:

**Gordon, P. (2003). The origin of argument structure in infant event representations.** 
*Proceedings of the 27th Annual Boston University Conference on Language Development.*

Key insight: Infants distinguish between **arguments** (essential event participants) and **adjuncts** (incidental elements) before acquiring language.

**Example**:
- **GIVE** event: Requires giver, recipient, and object (3 arguments)
- **HUG** event: Requires hugger and hugged person (2 arguments)
- **Prediction**: Toy is argument in GIVE but adjunct in HUG → different gaze patterns

### Novel Contributions

Our analysis extends prior work by:
1. **Frame-by-frame analysis**: Moving beyond aggregate looking time
2. **Gaze transitions**: Revealing active scanning strategies
3. **Social gaze triplets**: Quantifying face-object-face sequences
4. **Developmental trajectories**: Modeling age-related change
5. **Habituation patterns**: Capturing real-time learning

📖 **See [study-info.md](./study-info.md) for comprehensive background**

---

## Citation

If you use this pipeline in your research, please cite:

```bibtex
@software{ier_analysis_2025,
  title = {Infant Event Representation Analysis Pipeline},
  author = {[Your Name/Team]},
  year = {2025},
  url = {https://github.com/[your-repo]},
  note = {Eye-tracking analysis system for infant cognitive development}
}
```

---

## Documentation

- 📖 **[Quick Start Guide](./specs/001-infant-event-analysis/quickstart.md)** - Setup and running
- 📖 **[Data Model](./specs/001-infant-event-analysis/data-model.md)** - Schemas and validation
- 📖 **[Research Notes](./specs/001-infant-event-analysis/research.md)** - Technical decisions
- 📖 **[Study Background](./study-info.md)** - Scientific context
- 📁 Legacy planning documents (spec/plan/tasks) remain archived in `specs/001-infant-event-analysis/` for reference.

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

This project implements analysis methods based on developmental cognitive science research, particularly the work of Dr. Peter Gordon and collaborators on infant event representation.

**Special thanks** to the research team for data collection and verification, and to all participating families.

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-27  
**Status**: Production Ready ✅

All 7 analyses implemented and tested. Full test coverage. Ready for scientific use.
