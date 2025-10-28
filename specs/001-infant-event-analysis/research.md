# Research & Technology Decisions: Infant Event Representation Analysis

**Feature**: 001-infant-event-analysis
**Date**: 2025-10-25
**Purpose**: Document technology choices, best practices, and research findings for implementation

## Executive Summary

This document records the research and decisions made for implementing the infant event representation analysis pipeline. All technical choices prioritize scientific reproducibility, statistical rigor, and audit readiness per the project constitution.

## Technology Stack Decisions

### Decision 1: Python Scientific Stack

**Decision**: Python 3.12 with pandas, numpy, scipy, statsmodels, matplotlib

**Rationale**:
- **Latest Stable**: Python 3.12 offers improved performance (~25% faster than 3.10) and better type hints
- **Scientific Standard**: Python is the de facto standard for scientific data analysis with mature, well-tested libraries
- **Statistical Rigor**: scipy and statsmodels provide validated implementations of t-tests, ANOVA, regression, Chi-squared tests
- **Reproducibility**: Conda environments and pip requirements.txt provide exact dependency versioning
- **VS Code Integration**: Excellent debugging, testing, and code navigation support in VS Code
- **Community Support**: Extensive documentation, peer-reviewed validation, and active maintenance
- **Audit Trail**: All libraries are open-source with transparent implementations

**Alternatives Considered**:
- **R with tidyverse**: Excellent for statistical analysis but less flexible for complex pipeline automation and report generation
- **MATLAB**: Strong statistical tools but proprietary, expensive, and less suited for automated pipelines
- **Julia**: High performance but smaller ecosystem, less mature reporting tools

**References**:
- Python 3.12 Release Notes (2023): Performance improvements and type system enhancements
- McKinney, W. (2010). "Data Structures for Statistical Computing in Python" (pandas origin paper)
- Virtanen, P. et al. (2020). "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python"
- Seabold, S. & Perktold, J. (2010). "statsmodels: Econometric and statistical modeling with python"

### Decision 2: Report Generation Strategy

**Decision**: Jinja2 HTML templates + matplotlib/seaborn figures + WeasyPrint for PDF, developed in VS Code

**Rationale**:
- **VS Code Native**: Direct Python development without Jupyter dependencies or notebook interfaces
- **Template Clarity**: Jinja2 HTML templates are clean, version-controllable, and easy to review
- **Programmatic Control**: Full Python control over report content, layout, and styling
- **Reproducibility**: Templates + data → reports with no intermediate state or cell execution order issues
- **PDF Generation**: WeasyPrint renders HTML to PDF preserving visualizations, tables, and formatting
- **Debugging**: Standard Python debugging in VS Code (breakpoints, step-through, variable inspection)
- **Testing**: Report generation functions can be unit tested like any other code

**Alternatives Considered**:
- **Jupyter notebooks**: Requires notebook ecosystem, cell execution state management, less natural for TDD
- **ReportLab**: Low-level PDF generation, requires manual layout management, more code
- **Matplotlib savefig + LaTeX**: Complex toolchain, requires LaTeX installation
- **Quarto**: Excellent but adds another language dependency and rendering toolchain

**Implementation Approach**:
```python
# Example report generation flow
from jinja2 import Template
import matplotlib.pyplot as plt
from weasyprint import HTML

# 1. Run analysis, generate figures
fig, ax = plt.subplots()
ax.bar(conditions, means)
fig.savefig('results/AR1/duration_plot.png', dpi=300)

# 2. Load HTML template
with open('templates/ar1_template.html') as f:
    template = Template(f.read())

# 3. Render with data
html_content = template.render(
    analysis='AR-1',
    stats_table=stats_df.to_html(),
    figures=['duration_plot.png'],
    interpretation="Infants looked longer at..."
)

# 4. Save HTML and generate PDF
with open('results/AR1/report.html', 'w') as f:
    f.write(html_content)
HTML('results/AR1/report.html').write_pdf('results/AR1/report.pdf')
```

**References**:
- Jinja2 documentation: https://jinja.palletsprojects.com/
- WeasyPrint documentation: https://weasyprint.org/

### Decision 3: Statistical Methods - Linear Mixed Models (LMM) and Generalized LMM

**Decision**: Use Linear Mixed Models (LMM) and Generalized Linear Mixed Models (GLMM) as primary methods to properly handle repeated measures structure

**Core Rationale**:
- **Repeated measures structure**: Infants contribute multiple trials, violating independence assumption of traditional tests
- **Modern standard**: LMM is the gold standard for developmental psychology with nested/hierarchical data
- **Better power**: Uses all trial-level data instead of aggregating to participant means
- **Handles missing data**: Maximum likelihood estimation handles unbalanced designs gracefully
- **Individual differences**: Random effects capture participant-specific baselines and trajectories

**Gaze Duration Analysis (AR-1)**:
- **Method**: Linear Mixed Model
- **Formula**: `proportion_core_event ~ condition + (1 | participant)`
- **Fixed effect**: Condition (GIVE vs HUG)
- **Random effect**: Participant-specific intercepts (baseline looking time)
- **Advantages over t-test**: Uses all trials, accounts for within-subject correlation, handles missing trials
- **Implementation**: `statsmodels.regression.mixed_linear_model.MixedLM`

**Gaze Transitions (AR-2)**:
- **Primary Method**: Generalized Linear Mixed Models (GLMM) for transition counts (e.g., Poisson/Negative Binomial) with participant random effects, aligning with repeated-measures structure
- **Fallback**: Chi-squared tests on contingency tables only if GLMMs are infeasible (e.g., convergence failures), with rationale documented
- **Implementation**: `statsmodels` GLMM for counts where feasible; fallback via `scipy.stats.chi2_contingency` with multiple-comparisons correction

**Social Triplets (AR-3)**:
- **Method**: Generalized Linear Mixed Model (GLMM) with Poisson or Negative Binomial family
- **Formula**: `triplet_count ~ condition + (1 | participant)`
- **Distribution**: Poisson for count data (switch to negative binomial if overdispersed)
- **Offset**: `log(trial_count)` to normalize by exposure
- **Advantages over t-test**: Proper distribution for counts, handles zeros, accounts for repeated measures
- **Implementation**: `statsmodels.genmod.bayes_mixed_glm.BinomialBayesMixedGLM` or `pymer4` package

**Dwell Time Analysis (AR-4)**:
- **Method**: Linear Mixed Model
- **Formula**: `dwell_time_ms ~ condition + (1 | participant)`
- **Uses gaze fixation-level data** (not aggregated means)
- **Can extend**: `dwell_time_ms ~ condition * aoi_category + (1 | participant)` for AOI-specific analysis
- **Implementation**: `statsmodels.regression.mixed_linear_model.MixedLM`

**Developmental Trajectory (AR-5)**:
- **Method**: Linear Mixed Model with continuous age
- **Formula**: `gaze_metric ~ age_months * condition + (1 | participant)`
- **Continuous age**: Preserves information (no binning into younger/older)
- **Interaction term**: `age_months:condition` tests if condition effect changes with age
- **Non-linear option**: Add `age_squared` term to test quadratic age effects
- **Advantages over ANOVA**: Continuous age, more power, better model fit diagnostics
- **Implementation**: `statsmodels.regression.mixed_linear_model.MixedLM`

**Learning/Habituation (AR-6)**:
- **Method**: Linear Mixed Model with random slopes (CRITICAL - fixes independence violation)
- **Formula**: `gaze_metric ~ trial_number * condition + (1 + trial_number | participant)`
- **Random intercept**: Each participant has their own baseline
- **Random slope**: Each participant has their own habituation rate
- **Interaction**: Tests if habituation differs between conditions
- **THIS IS ESSENTIAL**: Simple regression violates independence; LMM is the only correct approach
- **Implementation**: `statsmodels.regression.mixed_linear_model.MixedLM`

**Event Dissociation (AR-7)**:
- **Method**: Linear Mixed Model with multiple conditions
- **Formula**: `gaze_metric ~ condition + (1 | participant)`
- **Planned contrasts**: Theory-driven comparisons (GIVE vs GIVE-TO-SELF, etc.)
- **Post-hoc**: Bonferroni correction for pairwise comparisons
- **Implementation**: `statsmodels.regression.mixed_linear_model.MixedLM`

**Model Diagnostics (All Analyses)**:
- Check residual normality (Q-Q plots)
- Check homoscedasticity (residuals vs fitted)
- Report AIC/BIC for model comparison
- Report variance components (ICC - intraclass correlation)
- Check for overdispersion in GLMM (deviance / df)

**Effect Sizes**:
- LMM: Cohen's d from fixed effects, R² marginal (fixed only) and conditional (fixed + random)
- GLMM: Rate ratios (exponentiated coefficients)

**References**:
- Barr et al. (2013). "Random effects structure for confirmatory hypothesis testing" - Journal of Memory and Language
- Mirman (2014). "Growth Curve Analysis and Visualization Using R"
- West, Welch & Galecki (2014). "Linear Mixed Models: A Practical Guide Using Statistical Software"
- Bates et al. (2015). "Fitting Linear Mixed-Effects Models Using lme4" - Journal of Statistical Software

### Decision 4: Visualization Library

**Decision**: Matplotlib primary, seaborn allowed for higher-level statistical plots

**Rationale**:
- **Publication Quality**: matplotlib provides fine-grained control; seaborn accelerates common statistical graphics
- **Flexibility**: Use seaborn where it improves clarity and development speed (e.g., catplot, barplot with CIs)
- **Directed Graphs**: networkx with matplotlib backend remains for transition visualizations
- **Reproducibility**: Deterministic rendering, same output across platforms
- **Error Bars**: matplotlib or seaborn CIs; explicit configuration for SEM vs CI

**Visualization Standards** (per spec and scientific conventions):
- Bar charts with standard error bars using `plt.bar(x, height, yerr=sem)`
- Proper axis labels with units using `plt.xlabel()`, `plt.ylabel()`
- Legends positioned for clarity using `plt.legend(loc='best')`
- Color schemes accessible (colorblind-friendly palettes from matplotlib.cm)
- Font sizes appropriate for publication (10-12pt for labels)
- DPI set to 300 for print quality using `fig.savefig(..., dpi=300)`

**Implementation**:
```python
import seaborn as sns
import matplotlib.pyplot as plt

# Example: Bar chart with error bars using seaborn
ax = sns.barplot(data=df, x='condition', y='proportion_toy', ci='se', capsize=0.1)
ax.set_xlabel('Condition', fontsize=12)
ax.set_ylabel('Mean Proportion Looking (toy)', fontsize=12)
plt.tight_layout()
plt.savefig('results/AR1/duration_plot.png', dpi=300)
```

**Usage Guidance for Seaborn**:
- Prefer seaborn for categorical summaries (barplot, pointplot) and confidence intervals
- Maintain consistent styling; document whether error bars are SEM or 95% CI
- For specialized visuals (directed graphs), continue with matplotlib + networkx

**References**:
- Hunter, J.D. (2007). "Matplotlib: A 2D Graphics Environment"
- Matplotlib documentation: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html

### Decision 5: Data Validation Strategy

**Decision**: Schema-based validation with pydantic or pandera

**Rationale**:
- **Type Safety**: Enforce column types, ranges, and constraints
- **Early Failure**: Catch structural errors before processing
- **Documentation**: Schemas serve as executable documentation
- **Testing**: Schemas enable property-based testing

**Implementation Approach**:
- Use pandera for DataFrame schema validation (integrates naturally with pandas)
- Define schemas for:
  - Raw CSV structure (current 18-column dataset schema with types)
  - gaze_fixations.csv schema (master log structure)
  - AOI category enumeration (10 valid What+Where pairs)
  - Experimental condition enumeration (GIVE, HUG, SHOW variants)

**Validation Levels** (STRICT - fail on ANY data errors):
- **Structural Errors (HALT execution)**:
  - Required columns missing: Participant, Frame Number, Time, What, Where, Onset, Offset, Blue Dot Center, event_verified, frame_count_event, trial_number, trial_number_global, frame_count_trial_number, segment, frame_count_segment, participant_type, participant_age_months, participant_age_years
  - Columns have incorrect types (str for categorical, int for frames, float for age_months)
  - CSV not parseable as valid UTF-8
  - Invalid file format or encoding
- **Data Quality Errors (HALT execution)**:
  - Missing values in required fields
  - Out-of-range values (e.g., age_months > 100 or < 0)
  - Invalid AOI combinations (not in the 10 valid What+Where pairs)
  - Duplicate participant IDs or trial identifiers
  - Negative frame numbers or timestamps

**NO PARTIAL RESULTS**: Pipeline must halt immediately on any data error with clear error message. No analysis proceeds with invalid data.

**References**:
- pandera documentation: https://pandera.readthedocs.io/

### Decision 6: Testing Strategy

**Decision**: pytest with TDD approach, comprehensive coverage across unit/integration/contract levels

**Test Organization**:
- **Unit tests**: Test individual functions in isolation
  - Gaze fixation detection logic (3+ frame threshold)
  - AOI mapping (What+Where → category)
  - Statistical functions (ensure correct scipy/statsmodels usage)
  - Visualization functions (check figure creation, no errors)
- **Integration tests**: Test component interactions
  - Preprocessing pipeline (CSV → gaze_fixations.csv)
  - Individual analysis modules (gaze_fixations.csv → reports)
  - Report compilation (individual reports → final report)
- **Contract tests**: Validate data schemas
  - Raw CSV structure matches spec
  - gaze_fixations.csv has required columns
  - Report outputs exist in expected locations

**TDD Workflow** (per constitution):
1. Write failing test describing expected behavior
2. Implement minimum code to pass test
3. Refactor while keeping tests passing
4. Repeat for next requirement

**Coverage Requirements**:
- Minimum 80% line coverage (pytest-cov)
- 100% coverage for critical paths (gaze detection, statistical tests)
- All edge cases tested (empty data, missing columns, insufficient samples)

**Fixtures**:
- Sample raw CSV with known AOI patterns
- Expected gaze_fixations.csv output for comparison
- Mock data for testing statistical edge cases (n=2, n=3, all same value)

**References**:
- pytest documentation: https://docs.pytest.org/
- pytest-cov plugin: https://pytest-cov.readthedocs.io/

### Decision 7: Configuration Management

**Decision**: Hybrid YAML configuration approach - global pipeline config + per-analysis configs

**Global Configuration File** (`config/pipeline_config.yaml`):
```yaml
analysis:
  alpha: 0.05  # Statistical significance threshold
  min_gaze_frames: 3  # Minimum frames for gaze fixation
  min_statistical_n: 3  # Minimum sample size for tests

edge_cases:
  strategy: "strict_fail"  # HALT on ANY data errors
  outlier_threshold_offscreen_pct: 0.5  # Threshold for reporting

reporting:
  figure_dpi: 300
  error_bar_type: "sem"  # Standard error of mean

paths:
  raw_data: "data/csvs_human_verified_vv"
  processed_data: "data/processed"
  results: "results"
  final_reports: "reports"

logging:
  level: "INFO"
  file: "logs/pipeline.log"
  console: true
```

**Per-Analysis Configuration Files** (`config/analysis_configs/arX_config.yaml`):
Each analysis (AR-1 through AR-7) has its own configuration file with analysis-specific parameters.

**Example** (`config/analysis_configs/ar2_config.yaml`):
```yaml
analysis_name: "AR-2: Gaze Transitions"
description: "Sequential gaze transition analysis between AOI categories"

statistics:
  multiple_comparison_correction: "bonferroni"
  min_transition_count: 5  # Minimum transitions to include in chi-squared

visualization:
  graph_layout: "spring"  # networkx layout algorithm
  node_size_metric: "total_duration"
  edge_thickness_scale: 1.5
  show_edge_labels: true
  colormap: "tab10"

output:
  generate_transition_matrices: true
  separate_by_condition: true
  export_graph_data: true
```

**Rationale**:
- **Modularity**: Each analysis is truly independent with its own settings (SC-007 compliance)
- **Transparency**: All analysis parameters explicitly documented
- **Reproducibility**: Configuration versioned with code
- **Flexibility**: Easy to adjust AR-2 graph settings without affecting AR-1
- **Self-documenting**: Config file explains what each analysis does
- **Audit Trail**: Changes to configuration tracked in git
- **Testing**: Can test each analysis with different configs easily

**Implementation**:
- Load global config and analysis-specific config at analysis start
- Merge configs (analysis-specific overrides global when conflicts)
- Pass merged config to analysis functions
- Log both global and analysis-specific configuration values in reports
- Validate config structure on load (required keys present)

```python
def run_ar2_transitions(gaze_fixations_path):
    global_config = load_config('config/pipeline_config.yaml')
    ar2_config = load_config('config/analysis_configs/ar2_config.yaml')
    config = {**global_config, **ar2_config}  # Merge
    # Run analysis with merged config...
```

**References**:
- PyYAML documentation: https://pyyaml.org/

### Decision 8: Logging Strategy

**Decision**: Python logging module with structured logging to file and console

**Implementation**:
- **Console**: INFO level, progress indicators, warnings
- **File**: DEBUG level, all operations, data quality issues
- **Report**: WARNING and ERROR messages embedded in analysis reports

**Log Format**:
```
[2025-10-25 14:32:15] [INFO] [preprocessing.csv_loader] Loaded 89 CSV files from data/csvs_human_verified_vv/child/
[2025-10-25 14:32:16] [WARNING] [preprocessing.gaze_detector] Participant Eight-0101-947 trial 3: Only 2 consecutive frames on toy/other, below 3-frame threshold
[2025-10-25 14:32:45] [INFO] [analysis.ar1_gaze_duration] Excluding 3 participants from GIVE condition due to missing trials
```

**Strict Error Handling**:
- **ANY data errors**: LOG ERROR + halt pipeline immediately
- **No partial results**: Pipeline fails fast with clear diagnostic message
- **Error details**: Log exact location (file, row, column) and nature of error
- **No silent failures**: All errors are fatal and explicitly reported

**References**:
- Python logging documentation: https://docs.python.org/3/library/logging.html

## Best Practices Research

### Best Practice 1: Gaze Fixation Detection

**Research Question**: What are standard practices for defining gaze fixations in infant eye-tracking research?

**Findings**:
- **Minimum Duration**: 3-5 frames is standard for infant research (accounts for infant gaze instability)
- **AOI Buffering**: Some studies use spatial buffers around AOIs to account for calibration drift
- **Consecutive Frame Rule**: Strict requirement for consecutive frames reduces false positives

**Decision**: Use 3 consecutive frames as specified, no spatial buffering (conservative approach ensures data quality)

**References**:
- Aslin, R.N. (2007). "What's in a look? Developmental Science"
- Franchak, J.M. et al. (2011). "Head-mounted eye tracking: A new method to describe infant looking"

### Best Practice 2: Statistical Power and Sample Size

**Research Question**: What minimum sample sizes are appropriate for infant developmental research?

**Findings**:
- Developmental psychology typically requires n=15-30 per condition for adequate power
- Minimum n=3 for parametric tests (though underpowered)
- Effect sizes in infant attention research: Cohen's d = 0.5-1.0 (medium to large)

**Decision**:
- Set minimum n=3 for any statistical test (per clarifications)
- Log warnings when n < 15 (underpowered but still valid)
- Report effect sizes alongside p-values for all tests

**References**:
- Cohen, J. (1988). "Statistical Power Analysis for the Behavioral Sciences"
- Oakes, L.M. (2017). "Sample Size, Statistical Power, and False Conclusions in Infant Looking-Time Research"

### Best Practice 3: Multiple Comparisons Correction

**Research Question**: When should multiple comparison corrections be applied?

**Findings**:
- Family-wise error rate (FWER) control needed when multiple related tests
- Bonferroni correction (most conservative), Holm-Bonferroni (less conservative)
- FDR (False Discovery Rate) for exploratory analyses

**Decision**:
- Apply Bonferroni correction for AR-2 (multiple AOI pair comparisons)
- Report both corrected and uncorrected p-values for transparency
- Use ANOVA with post-hoc tests (Tukey HSD) for multi-group comparisons

**Implementation**: `statsmodels.stats.multitest.multipletests`

**References**:
- Benjamini, Y. & Hochberg, Y. (1995). "Controlling the false discovery rate"

### Best Practice 4: Directed Graph Visualization

**Research Question**: How to effectively visualize gaze transition patterns?

**Findings**:
- Node size can represent AOI importance (total fixation time)
- Edge thickness represents transition probability
- Layout algorithms: spring layout (force-directed) or circular layout
- Color coding by AOI type enhances interpretability

**Decision**:
- Use networkx spring layout for natural clustering
- Edge thickness proportional to transition probability
- Node size proportional to total gaze duration on AOI
- Color nodes by AOI category (faces, bodies, objects)
- Include transition probability labels on edges

**Implementation**: `networkx.spring_layout`, `matplotlib.patches.FancyArrowPatch`

**References**:
- Holmqvist, K. et al. (2011). "Eye Tracking: A Comprehensive Guide to Methods and Measures"

## Integration Patterns

### Pattern 1: Pipeline Orchestration

**Approach**: Single main.py orchestrator with modular component imports

**Structure**:
```python
# main.py
from src.preprocessing import run_preprocessing
from src.analysis import (
    run_ar1_duration,
    run_ar2_transitions,
    # ... all ARs
)
from src.reporting import compile_final_report

def main():
    # Load config
    config = load_config('config/pipeline_config.yaml')

    # Setup logging
    setup_logging(config)

    # Phase 1: Preprocessing
    gaze_fixations_path = run_preprocessing(config)

    # Phase 2: Individual Analyses (can run in parallel)
    ar_results = []
    for ar_func in [run_ar1_duration, run_ar2_transitions, ...]:
        result = ar_func(gaze_fixations_path, config)
        ar_results.append(result)

    # Phase 3: Compile Final Report
    compile_final_report(ar_results, config)
```

**Rationale**:
- Clear execution flow
- Each phase is a distinct function call
- Easy to run individual analyses (SC-007 requirement)
- Supports parallel execution of ARs if needed

### Pattern 2: Error Handling and Recovery

**Approach**: STRICT FAIL-FAST - halt on ANY data errors (structural or quality)

**Implementation**:
```python
try:
    df = load_csv(filepath)
    validate_structure(df)  # Raises exception on missing columns
    validate_data_quality(df)  # Raises exception on ANY data issues
except ValidationError as e:
    logger.error(f"Data validation failed in {filepath}: {e}")
    logger.error(f"Location: Row {e.row_num}, Column '{e.column_name}'")
    logger.error(f"Expected: {e.expected}, Found: {e.actual}")
    sys.exit(1)  # HALT pipeline - no partial results
```

**Rationale**: Scientific integrity requires complete, valid data. No analysis can proceed with ANY invalid data. This ensures all results are trustworthy and reproducible.

### Pattern 3: Report Template System

**Approach**: Template-driven HTML (Jinja2) rendered and then converted to PDF with WeasyPrint

**Template Structure**:
```markdown
# AR-1: Gaze Duration Analysis

## Parameters
```python
# Parameters cell (tagged with 'parameters')
gaze_fixations_path = "data/processed/gaze_fixations.csv"
output_dir = "results/AR1_Gaze_Duration"
config_path = "config/pipeline_config.yaml"
```

## Methods
[Load data, run analysis, generate visualizations]

## Results
[Statistical tables, figures, narrative interpretation]
```

**Execution**:
```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('ar1_template.html')
html = template.render(stats_table=stats_df.to_html(), figures=['duration_plot.png'])
with open('results/AR1_Gaze_Duration/report.html', 'w') as f:
    f.write(html)
HTML('results/AR1_Gaze_Duration/report.html').write_pdf('results/AR1_Gaze_Duration/report.pdf')
```

**Rationale**:
- Reproducible: same template, different data
- Version controlled: templates tracked in git
- Automated: no manual notebook execution

## Implementation Priorities

### Phase 0 (Foundation - Week 1)
1. Environment setup (conda, requirements.txt)
2. Configuration management (YAML loading)
3. Logging infrastructure
4. Data validation schemas (pandera)

### Phase 1 (Preprocessing - Week 2)
1. CSV loader (with structural validation)
2. AOI mapper (What+Where → categories)
3. Gaze fixation detector (3+ frame rule)
4. Master log generator (gaze_fixations.csv)
5. Comprehensive preprocessing tests

### Phase 2 (Core Analyses - Week 3-4)
1. Shared utilities (statistics, visualizations)
2. AR-1 (gaze duration) - highest priority (P1)
3. AR-2 (transitions)
4. AR-3 (social triplets)
5. AR-4 (dwell times)

### Phase 3 (Advanced Analyses - Week 5)
1. AR-5 (developmental trajectory)
2. AR-6 (learning/habituation)
3. AR-7 (dissociation analysis)

### Phase 4 (Reporting - Week 6)
1. Report templates (Jinja2 HTML)
2. Report generation (WeasyPrint)
3. Final report compilation
4. End-to-end integration tests

## Risk Mitigation

### Risk 1: PDF Generation Complexity

**Risk**: WeasyPrint may have issues with complex visualizations or dependencies

**Mitigation**:
- Start with HTML reports (simpler, always works)
- Test PDF generation early with sample report
- Fallback: Use ReportLab or matplotlib PDF backend if WeasyPrint fails
- Document PDF generation issues in troubleshooting guide

### Risk 2: Statistical Assumption Violations

**Risk**: Data may not meet normality or homogeneity of variance assumptions

**Mitigation**:
- Always test assumptions before parametric tests
- Have non-parametric alternatives ready (Mann-Whitney U, Kruskal-Wallis)
- Document assumption test results in reports
- Consult with statistical expert if violations are severe

### Risk 3: Performance with Large Datasets

**Risk**: Pipeline may be slow with 100+ participants

**Mitigation**:
- Profile code early to identify bottlenecks
- Optimize pandas operations (vectorization, avoid loops)
- Consider parallel processing for independent ARs
- Set realistic performance expectations (30 min target is reasonable)

## Conclusion

All technology decisions prioritize scientific reproducibility, statistical rigor, and audit readiness. The Python scientific stack provides mature, well-validated tools for every aspect of the pipeline. The modular architecture supports independent execution, comprehensive testing, and clear separation of concerns. Jinja2 HTML with WeasyPrint provides a standard, reproducible reporting format. All decisions align with the project constitution and development best practices in scientific computing.

**Ready for Phase 1**: Data model and contract generation.
