# Quickstart Guide: Infant Event Representation Analysis

**Feature**: 001-infant-event-analysis
**Last Updated**: 2025-10-25
**Target Audience**: Researchers, developers, and anyone running the analysis pipeline

## Overview

This guide provides step-by-step instructions for setting up and running the infant event representation analysis pipeline. The system processes eye-tracking data to generate comprehensive statistical reports analyzing infant cognition.

## Prerequisites

### Required Software
- **Python**: 3.12
- **Conda**: Miniconda or Anaconda (recommended for environment management)
- **Git**: For version control (optional but recommended)

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk Space**: 2 GB for dependencies + space for your data and results
- **CPU**: Multi-core processor recommended for faster processing

### Required Data
- Annotated eye-tracking CSV files in `data/csvs_human_verified_vv/child/` and `data/csvs_human_verified_vv/adult/`
- Each CSV must contain the current dataset columns (see [data-model.md](./data-model.md))

## Installation

### Step 1: Clone the Repository (if applicable)

```bash
git clone <repository-url>
cd ier_analysis
```

### Step 2: Create Conda Environment

The project uses a conda environment named `ier_analysis` as specified in the constitution.

```bash
# Create environment from environment.yml
conda env create -f config/environment.yml

# Activate environment
conda activate ier_analysis
```

**Alternative**: If `environment.yml` is not yet created, manually create the environment:

```bash
# Create conda environment with Python 3.12
conda create -n ier_analysis python=3.12 -y

# Activate environment
conda activate ier_analysis

# Install dependencies
pip install -r config/requirements.txt
```

### Step 3: Verify Installation

```bash
# Test Python version
python --version
# Should output: Python 3.12.x

# Test key dependencies
python -c "import pandas; print(f'pandas {pandas.__version__}')"
python -c "import scipy; print(f'scipy {scipy.__version__}')"
python -c "import matplotlib; print(f'matplotlib {matplotlib.__version__}')"
python -c "import jinja2; print(f'jinja2 {jinja2.__version__}')"

# Run test suite (after implementation)
pytest tests/
```

### Step 4: Open in VS Code

```bash
# Open project in VS Code
code .

# VS Code will prompt to select Python interpreter
# Choose the ier_analysis conda environment
```

## Configuration

### Pipeline Configuration

Edit `config/pipeline_config.yaml` to customize analysis parameters:

```yaml
analysis:
  alpha: 0.05                    # Statistical significance threshold
  min_gaze_frames: 3             # Minimum frames for gaze fixation
  min_statistical_n: 3           # Minimum sample size for tests

edge_cases:
  strategy: "halt_on_any_error"   # HALT on structural or data quality issues
  outlier_threshold_offscreen_pct: 0.5  # Flag trials > 50% off-screen

reporting:
  figure_dpi: 300                # Resolution for figures
  error_bar_type: "sem"          # Standard error of mean

paths:
  raw_data: "data/csvs_human_verified_vv"
  processed_data: "data/processed"
  results: "results"
  final_reports: "reports"

logging:
  level: "INFO"                  # DEBUG, INFO, WARNING, ERROR
  file: "logs/pipeline.log"
  console: true
```

**Important**: Do not modify the configuration unless you understand the implications for scientific reproducibility. All changes are logged and tracked.

## Running the Analysis

### Quick Start: Full Pipeline

Run the complete analysis from raw data to final report:

```bash
# Ensure conda environment is activated
conda activate ier_analysis

# Run full pipeline
python src/main.py
```

**Expected Output**:
```
[2025-10-25 14:32:15] [INFO] Starting IER Analysis Pipeline v1.0.0
[2025-10-25 14:32:15] [INFO] Loading configuration from config/pipeline_config.yaml
[2025-10-25 14:32:16] [INFO] Phase 1: Preprocessing
[2025-10-25 14:32:16] [INFO] Loaded 89 CSV files from data/csvs_human_verified_vv/child/
[2025-10-25 14:32:18] [INFO] Detected 15,432 gaze fixations
[2025-10-25 14:32:18] [INFO] Saved gaze_fixations.csv to data/processed/
[2025-10-25 14:32:19] [INFO] Phase 2: Individual Analyses
[2025-10-25 14:32:45] [INFO] AR-1 (Gaze Duration) complete
[2025-10-25 14:33:12] [INFO] AR-2 (Transitions) complete
...
[2025-10-25 14:38:20] [INFO] Phase 3: Report Compilation
[2025-10-25 14:38:45] [INFO] Final report saved to reports/final_report.html
[2025-10-25 14:38:45] [INFO] Pipeline complete!
```

### Running Individual Components

#### Preprocessing Only

```bash
python src/preprocessing/master_log_generator.py
```

**Output**: `data/processed/gaze_fixations.csv`

#### Individual Analyses

```bash
# AR-1: Gaze Duration Analysis
python -m src.analysis.ar1_gaze_duration

# AR-2: Gaze Transitions
python -m src.analysis.ar2_transitions

# AR-3: Social Gaze Triplets
python -m src.analysis.ar3_social_triplets

# AR-4: Dwell Time Analysis
python -m src.analysis.ar4_dwell_times

# AR-5: Developmental Trajectory Analysis
python -m src.analysis.ar5_development

# AR-6: Trial-Order Effects (Learning/Habituation)
python -m src.analysis.ar6_learning

# AR-7: Event Dissociation Analysis
python -m src.analysis.ar7_dissociation
```

**Output**: Individual reports in `results/AR*_*/report.html` and `report.pdf`

#### Report Compilation Only

```bash
# Compile existing individual reports into final report
python src/reporting/compiler.py
```

**Output**: `reports/final_report.html` and `reports/final_report.pdf`

## Understanding the Output

### Directory Structure After Running

```
ier_analysis/
├── data/
│   ├── csvs_human_verified_vv/ # Your original verified data (unchanged)
│   │   ├── child/
│   │   └── adult/
│   └── processed/
│       └── gaze_fixations.csv     # ✓ Master gaze fixation log
│
├── results/
│   ├── AR1_Gaze_Duration/
│   │   ├── report.html         # ✓ AR-1 report (open in browser)
│   │   ├── report.pdf          # ✓ AR-1 report (for printing)
│   │   ├── duration_by_condition.png
│   │   └── summary_stats.csv
│   ├── AR2_Gaze_Transitions/
│   │   ├── report.html
│   │   ├── report.pdf
│   │   ├── transition_matrices.csv
│   │   └── directed_graph_*.png
│   └── ... (AR-3 through AR-7)
│
├── reports/
│   ├── final_report.html       # ✓ Compiled final report
│   └── final_report.pdf        # ✓ Compiled final report
│
└── logs/
    └── pipeline.log            # Detailed execution log
```

### Key Outputs

1. **gaze_fixations.csv**: Master log of all detected gaze fixations
   - 16 columns describing each gaze (participant, trial, AOI, duration, etc.)
   - Can be opened in Excel or any CSV viewer for inspection

2. **Individual Analysis Reports** (AR-1 through AR-7):
   - **AR-1**: Gaze Duration (GIVE vs HUG comparison with t-tests)
   - **AR-2**: Gaze Transitions (transition matrices, network graphs)
   - **AR-3**: Social Gaze Triplets (face→toy→face sequence detection)
   - **AR-4**: Dwell Times (mean fixation duration per AOI with LMM)
   - **AR-5**: Developmental Trajectory (Age × Condition interactions)
   - **AR-6**: Trial-Order Effects (habituation/learning with random slopes)
   - **AR-7**: Event Dissociation (GIVE vs HUG vs SHOW comparisons)
   
   Each report contains:
   - **HTML version**: Open in web browser, best for viewing on screen
   - **PDF version**: For printing or archival
   - Methods section explaining the analysis
   - Statistical results with p-values, effect sizes
   - Visualizations (bar charts, graphs, interaction plots)
   - Narrative interpretation of findings

3. **Final Compiled Report**:
   - Integrates all 7 analyses into one cohesive document
   - Includes table of contents with hyperlinks
   - Ready for sharing with collaborators or publication

4. **Pipeline Log** (`logs/pipeline.log`):
   - Detailed record of all operations
   - Warnings about data quality issues
   - Exclusions and their reasons
   - Essential for troubleshooting

## Interpreting Results

### Reading Statistical Tables

All statistical tests follow this format:

| Comparison | Test | Statistic | df | p-value | Effect Size | Significant? |
|------------|------|-----------|----|---------| ------------|--------------|
| GIVE vs HUG | t-test | t = 2.45 | 87 | p = .016 | d = 0.52 | Yes (α=.05) |

**Interpretation**:
- **p-value < 0.05**: Statistically significant difference
- **Effect size (Cohen's d)**: 0.2 = small, 0.5 = medium, 0.8 = large
- **df**: Degrees of freedom (related to sample size)

### Understanding Visualizations

#### Bar Charts
- **Error bars**: Represent standard error of mean (SEM) or 95% confidence intervals
- **Height**: Mean value for that condition
- **Asterisks**: Statistical significance (* p<.05, ** p<.01, *** p<.001)

#### Directed Graphs (AR-2)
- **Nodes**: Areas of Interest (AOIs)
- **Arrows**: Gaze transitions (direction of looking)
- **Arrow thickness**: Transition probability (thicker = more common)
- **Node size**: Total time looking at that AOI

#### Line Plots (AR-6)
- **X-axis**: Trial number (time progression)
- **Y-axis**: Looking metric (e.g., triplet frequency)
- **Slope**: Learning/habituation trend

## Troubleshooting

### Common Issues

#### 1. "Structural validation failed: missing column 'Participant'"

**Problem**: Verified CSV files don't match expected schema

**Solution**:
- Check that your CSV files have all required columns per the current dataset (see schema)
- Verify column names match exactly (case-sensitive)
- See [contracts/raw_data_schema.json](./contracts/raw_data_schema.json) for full schema

#### 2. "No gaze fixations detected for participant X"

**Problem**: Insufficient consecutive frames on same AOI

**Solution**:
- Check if participant's data has enough valid frames
- Verify AOI labels are correct (What+Where combinations)
- Review raw data for excessive off-screen gazes
- This participant will be excluded from affected analyses

#### 3. "Insufficient statistical power: n < 3"

**Problem**: Not enough participants in a condition for statistical test

**Solution**:
- This is a warning, not an error
- Analysis skips that specific comparison
- Collect more data if possible
- Consider combining age groups if scientifically justified

#### 4. "PDF generation failed"

**Problem**: WeasyPrint or PDF backend issue

**Solution**:
- HTML reports are still available (open in browser and print to PDF)
- Check WeasyPrint installation: `pip install --upgrade weasyprint`
- Check system dependencies for WeasyPrint (varies by OS)
- See logs for specific error message

#### 5. "Pipeline takes longer than 30 minutes"

**Problem**: Large dataset or slow machine

**Solution**:
- This is normal for very large datasets (100+ participants)
- Consider running individual analyses in parallel if needed
- Check that you're not running other heavy processes
- Performance is logged - check which AR is slowest

### Getting Help

1. **Check the logs**: `logs/pipeline.log` contains detailed error messages
2. **Review data model**: [data-model.md](./data-model.md) explains all entities and validation rules
3. **Check contracts**: [contracts/](./contracts/) folder has JSON schemas for validation
4. **Run tests**: `pytest tests/ -v` to identify specific failures

## Advanced Usage

### Running with Custom Parameters

Override configuration via command-line arguments (after implementation):

```bash
python src/main.py --alpha 0.01 --min-gaze-frames 5 --verbose
```

### Analyzing Subset of Data

Edit `config/pipeline_config.yaml` to filter by condition or age group:

```yaml
filters:
  conditions: ["GIVE_WITH", "HUG_WITH"]  # Only analyze these conditions
  age_groups: ["8-month-olds", "12-month-olds"]  # Only these age groups
```

### Exporting Data for External Analysis

The master `gaze_fixations.csv` and summary CSV tables can be imported into:
- **R**: `read.csv("data/processed/gaze_fixations.csv")`
- **SPSS**: File → Import Data → CSV
- **Excel**: Open directly or import as external data
- **Python/pandas**: `pd.read_csv("data/processed/gaze_fixations.csv")`

### Running Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_gaze_detector.py

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

## Best Practices

### Scientific Reproducibility

1. **Never modify raw data**: Always work with copies in `data/processed/`
2. **Document changes**: Git commit any configuration changes with clear messages
3. **Archive results**: Save entire `results/` and `reports/` folders with date stamps
4. **Version dependencies**: Pin exact versions in `requirements.txt`
5. **Record decisions**: Document any manual exclusions or parameter changes

### Data Management

1. **Backup raw data**: Keep original CSV files in a safe location
2. **Version control**: Use git for code and configuration (not large data files)
3. **Organize by date**: Name result folders with timestamps (e.g., `results_2025-10-25/`)
4. **Document anomalies**: Note any unusual findings in lab notebook

### Performance Optimization

1. **Use SSD**: Store data on solid-state drive if possible
2. **Close other applications**: Free up RAM during analysis
3. **Process in batches**: If dataset is huge, consider splitting by condition
4. **Monitor resources**: Use task manager to check CPU/RAM usage

## Maintenance

### Updating Dependencies

```bash
# Activate environment
conda activate ier_analysis

# Update all packages
pip install --upgrade -r config/requirements.txt

# Or update specific package
pip install --upgrade pandas

# Freeze new versions
pip freeze > config/requirements.txt
```

**Warning**: Test thoroughly after updates to ensure reproducibility is maintained.

### Cleaning Up

```bash
# Remove processed data (keep raw data!)
rm -rf data/processed/*

# Remove old results (backup first!)
rm -rf results/* reports/*

# Remove logs
rm -rf logs/*

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

## Next Steps

1. **Review Results**: Open `reports/final_report.html` in your web browser
2. **Validate Findings**: Check that results align with research hypotheses
3. **Explore Data**: Inspect `gaze_fixations.csv` and summary tables
4. **Run Additional Tests**: Modify configuration for exploratory analyses
5. **Share Results**: Distribute reports to collaborators

## Appendix: Environment Setup Details

### environment.yml Example

```yaml
name: ier_analysis
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.12
  - pip
  - pip:
    - pandas==2.2.0
    - numpy==1.26.0
    - scipy==1.12.0
    - statsmodels==0.14.1
    - matplotlib==3.8.2
    - networkx==3.2.1
    - jinja2==3.1.3
    - weasyprint==60.2
    - markdown==3.5.2
    - pytest==8.0.0
    - pytest-cov==4.1.0
    - pandera==0.18.0
    - pyyaml==6.0.1
```

### requirements.txt Example

```
pandas==2.2.0
numpy==1.26.0
scipy==1.12.0
statsmodels==0.14.1
matplotlib==3.8.2
networkx==3.2.1
jinja2==3.1.3
weasyprint==60.2
markdown==3.5.2
pytest==8.0.0
pytest-cov==4.1.0
pandera==0.18.0
pyyaml==6.0.1
```

## Support and Contact

For questions, issues, or contributions, please refer to project documentation or contact the research team.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-25
**Maintained By**: IER Analysis Project Team
