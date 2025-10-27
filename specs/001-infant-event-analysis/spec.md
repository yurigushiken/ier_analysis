# Feature Specification: Infant Event Representation Analysis System

**Feature Branch**: `001-infant-event-analysis`
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Create a specification for a comprehensive analysis of infant event representation, building on the work of Gordon (2003). We have data inside of data dir and subdirs in the root. We will be processing this annotated data into a single, master 'gaze_events.csv' log, where a 'gaze' is formally defined as three or more consecutive frames on a single Area of Interest. This master log will be the foundation for seven core analytical requirements (ARs) designed to probe infant cognition."

## Clarifications

### Session 2025-10-25

- Q: When the system encounters edge cases (e.g., participant with missing trials, insufficient data for statistical tests), how should it behave? → A: HALT on missing required data (validation failure). Analysis-level insufficiency (e.g., n < 3 for a specific comparison) is reported within that analysis and the comparison is skipped.
- Q: When data validation detects issues during preprocessing, which issues should stop the pipeline entirely (critical errors) versus which should log warnings and continue? → A: HALT on both structural errors and data quality issues. No partial results are produced until data are corrected.
- Q: What is the expected structure of the raw annotated CSV files? → A: Every participant CSV has columns exactly: Participant, Frame Number, Time, What, Where, Onset, Offset, Blue Dot Center, event_verified, frame_count_event, trial_number, trial_number_global, frame_count_trial_number, segment, frame_count_segment, participant_type, participant_age_months, participant_age_years. Data are CSV files in `data/csvs_human_verified_vv/child/` and `data/csvs_human_verified_vv/adult/`.
- Q: How should the "Where" column values be mapped to the analytical AOI categories? → A: AOI categories are defined by What+Where pairs: screen/other (on-screen non-AOI), woman/face, man/face, toy/other (toy present in "with" trials), toy2/other (toy location in "without" trials), man/body, woman/body, man/hands, woman/hands. Off-screen (no/signal) is excluded from gaze events and denominators.
- Q: For the Social Gaze Triplet pattern, should it specifically be man/face → toy/other → woman/face (or reverse), or should it also include sequences like man/face → toy/other → man/face (same person)? → A: Must be different people (man/face → toy/other → woman/face OR woman/face → toy/other → man/face only)

### Session 2025-10-26 - Data Structure Clarification

- **Q: What is the actual event/trial structure in the data?** → A: **51 child participants aged 7-12 months** (mean=9.2, SD=1.5). Each participant sees **6-11 event types** (gw, gwo, hw, hwo, sw, swo, ugw, ugwo, uhw, uhwo, f) with mean=10.9 event types. Event types are **presented multiple times** (total ~50 event presentations per participant, range 24-80). Each event type is repeated **3-9 times** per participant. Each event presentation lasts variable frames (~5-33 seconds at 30fps). Each row in CSV is one frame. Total 5,000-8,500 frames per participant. **Total: 2,568 event presentations across all 51 participants**.

- **Q: What do the event codes mean?** → A: **Event codes**: gw=GIVE WITH toy, gwo=GIVE WITHOUT toy, hw=HUG WITH toy, hwo=HUG WITHOUT toy, sw=SHOW WITH toy, swo=SHOW WITHOUT toy, ugw/ugwo/uhw/uhwo=UPSIDE-DOWN variants (control for biomechanical motion), f=FLOATING (control). Design is 3 Actions (GIVE/HUG/SHOW) × 2 Toy Presence (WITH/WITHOUT) × 2 Orientations (NORMAL/UPSIDE-DOWN) + 1 Control.

- **Q: What is the nesting structure for statistical modeling?** → A: **3-level hierarchy**: Participant (N=51) → Event Presentation (N≈50 per participant, 2,568 total) → Gaze Event (N≈10-30 per presentation, derived from 3+ consecutive frames on same AOI) → Frame (aggregated, not modeled). This structure requires **Linear Mixed Models (LMM) and Generalized Linear Mixed Models (GLMM)** to properly account for repeated measures and nesting.

- **Q: What does AR-6 analyze? Is this a habituation study?** → A: **No, this is NOT a habituation study**. AR-6 analyzes **trial-order effects**: whether looking patterns change across **repeated presentations of the same event type**. Uses the `trial_number_global` column (1st presentation of "gw", 2nd presentation of "gw", 3rd presentation of "gw"). Each event type is shown **3-9 times** per participant (mean ~4-5 repetitions). Tests if looking patterns systematically increase (learning), decrease (adaptation/fatigue), or stay stable across these repetitions. This is analyzed **within event type**, not across the entire session.

- **Q: What does AR-7 compare? Is there a GIVE-TO-SELF condition?** → A: **No GIVE-TO-SELF condition exists**. AR-7 compares **GIVE vs HUG vs SHOW** to demonstrate dissociation between visual attention and event understanding. Key hypothesis: SHOW elicits high toy attention (like GIVE) but different social gaze patterns, demonstrating that "seeing is not giving."

- **Q: How should off-screen frames (no,signal AOI) be handled in gaze event detection?** → A: **Exclude and break sequences**. Off-screen frames (no,signal) break gaze event sequences. Only count consecutive frames where infant is looking at valid on-screen AOIs. This ensures gaze events represent active visual engagement with the stimulus.

- **Q: What about adult control data?** → A: **Process separately, keep separate reports**. Adult data (N=15 participants in `data/csvs_human_verified_vv/adult/`) will be processed with the same pipeline but kept in separate reports. Not included in primary child analyses. May be used for comparison in later analyses or publications.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Core Event Salience Discovery (Priority: P1)

As a developmental psychology researcher, I want to determine whether infants selectively attend to objects based on their relevance to an event's meaning (such as a toy in 'GIVE' vs. 'HUG' scenarios), so that I can test the central hypothesis about infant event comprehension.

**Why this priority**: This is the foundational research question of the entire study. Without this analysis, the core hypothesis cannot be validated. It represents the primary deliverable and is independently valuable even if no other analyses are performed.

**Independent Test**: Can be fully tested by processing gaze event data and generating a complete statistical report showing mean gaze durations across experimental conditions with appropriate visualizations and hypothesis test results.

**Acceptance Scenarios**:

1. **Given** the processed gaze events log, **When** the researcher executes AR-1 analysis, **Then** the system generates both HTML and PDF reports containing bar charts of mean looking time at the toy by condition, summary statistics tables, and statistical test results (t-test and ANOVA)
2. **Given** multiple experimental conditions in the dataset, **When** AR-1 analysis completes, **Then** the report clearly states whether infants looked significantly longer at the toy in the GIVE condition compared to HUG condition with exact statistical values (t-statistic, degrees of freedom, p-value)
3. **Given** the raw annotated frame-by-frame data files, **When** the preprocessing pipeline executes, **Then** a single master gaze_events.csv file is created defining gazes as 3+ consecutive frames on the same AOI

---

### User Story 2 - Visual Scanning Strategy Analysis (Priority: P2)

As a researcher studying infant attention patterns, I want to analyze how infants visually explore scenes by tracking gaze transitions between areas of interest, so that I can understand their information-gathering strategies and how these change with age.

**Why this priority**: This provides critical insights into the cognitive processes underlying the primary findings. It helps explain HOW infants arrive at their understanding, not just what they attend to. It builds on P1 by adding mechanistic depth.

**Independent Test**: Can be fully tested by analyzing transition probabilities from gaze events and producing complete transition matrices and visualizations for each age group and condition.

**Acceptance Scenarios**:

1. **Given** the gaze events log, **When** AR-2 analysis executes, **Then** the system produces transition probability matrices showing the likelihood of moving from each AOI to every other AOI
2. **Given** transition probabilities for each condition, **When** the analysis completes, **Then** directed graph visualizations are generated with arrow thickness representing transition probability
3. **Given** observed transition frequencies, **When** statistical validation runs, **Then** Chi-squared test results compare observed vs. expected frequencies with full statistical reporting

---

### User Story 3 - Social Cognition Pattern Detection (Priority: P2)

As a social cognition researcher, I want to identify specific "Social Gaze Triplet" sequences (face-toy-face patterns) in infant viewing behavior, so that I can quantitatively assess joint attention and social understanding.

**Why this priority**: Social cognition is a key theoretical construct in developmental psychology. This analysis provides unique evidence about whether infants process events as social interactions. It's independently valuable but conceptually builds on understanding basic attention patterns.

**Independent Test**: Can be fully tested by parsing gaze sequences to count triplet patterns and generating statistical reports comparing frequencies across conditions and age groups.

**Acceptance Scenarios**:

1. **Given** sequential gaze event data, **When** AR-3 analysis executes, **Then** the system identifies and counts all instances of Person A → Toy → Person B gaze sequences per trial
2. **Given** triplet counts across conditions, **When** statistical analysis completes, **Then** reports show mean frequencies with bar charts and statistical comparisons (t-test/ANOVA) between experimental conditions
3. **Given** age group differences in the data, **When** AR-3 completes, **Then** the report includes developmental comparisons showing how social gaze patterns change with infant age

---

### User Story 4 - Cognitive Processing Depth Measurement (Priority: P3)

As a cognitive development researcher, I want to measure average dwell times on different areas of interest, so that I can assess how deeply infants process different event elements.

**Why this priority**: Dwell time analysis provides convergent evidence for the primary findings by showing depth of processing. While valuable, it's complementary to the duration analysis in P1 and can be conducted independently later.

**Independent Test**: Can be fully tested by calculating mean dwell times from individual gaze durations and producing statistical comparisons across AOIs and conditions.

**Acceptance Scenarios**:

1. **Given** individual gaze durations in the events log, **When** AR-4 analysis runs, **Then** mean dwell times are calculated for each AOI across all participants
2. **Given** dwell time measurements, **When** analysis completes, **Then** bar charts visualize mean dwell times by condition with statistical test results
3. **Given** the GIVE WITH and HUG WITH conditions, **When** statistical validation runs, **Then** the report includes t-test/ANOVA results comparing dwell times on the toy between conditions

---

### User Story 5 - Developmental Trajectory Modeling (Priority: P3)

As a developmental researcher, I want to model how infant age interacts with experimental condition to affect looking behavior, so that I can understand the developmental timeline of event comprehension abilities.

**Why this priority**: Understanding developmental change is theoretically important but requires sufficient data across age groups. This is a more advanced analysis that builds on the foundational findings and may require larger sample sizes.

**Independent Test**: Can be fully tested by fitting statistical models with Age × Condition interaction terms and producing interaction plots with full model diagnostics.

**Acceptance Scenarios**:

1. **Given** gaze data with age group labels, **When** AR-5 analysis executes, **Then** a two-way ANOVA or mixed-effects model tests the Age × Condition interaction
2. **Given** the fitted statistical model, **When** analysis completes, **Then** an interaction plot shows how the condition effect changes across age groups
3. **Given** model results, **When** reporting completes, **Then** the full ANOVA table with F-statistics, degrees of freedom, and p-values is presented with interpretation of the interaction significance

---

### User Story 6 - Within-Session Learning Analysis (Priority: P3)

As a learning researcher, I want to analyze trial-by-trial changes in looking behavior within experimental sessions, so that I can model habituation and learning processes.

**Why this priority**: Learning curves provide insights into real-time adaptation but are secondary to understanding the basic phenomena. This can be analyzed independently and adds depth once primary patterns are established.

**Independent Test**: Can be fully tested by plotting key metrics against trial number and fitting regression models to test for learning effects.

**Acceptance Scenarios**:

1. **Given** trial-numbered gaze events, **When** AR-6 analysis runs, **Then** line graphs plot social gaze triplet frequency (or other metrics) across sequential trials
2. **Given** trial-by-trial data, **When** regression analysis executes, **Then** the system tests whether trial number significantly predicts looking metrics
3. **Given** multiple conditions, **When** analysis completes, **Then** the report compares learning slopes between conditions and presents full regression statistics (coefficients, R-squared, p-values)

---

### User Story 7 - Complex Event Dissociation Test (Priority: P3)

As a researcher testing specific theoretical predictions, I want to analyze the SHOW condition to demonstrate a dissociation between visual attention to an object and social understanding patterns, so that I can provide evidence that seeing does not equal understanding.

**Why this priority**: This is a confirmatory hypothesis test for a specific theoretical claim. While theoretically important, it depends on having validated the primary analysis methods (AR-1 and AR-3) and is most valuable as a capstone demonstration.

**Independent Test**: Can be fully tested by applying AR-1 and AR-3 methods to SHOW condition data and synthesizing results into a comparative narrative report.

**Acceptance Scenarios**:

1. **Given** SHOW condition data, **When** AR-7 analysis executes, **Then** both gaze duration (AR-1) and social triplet frequency (AR-3) analyses are performed
2. **Given** results from both sub-analyses, **When** synthesis completes, **Then** the report presents side-by-side visualizations showing high toy attention but low social gaze patterns
3. **Given** the dissociation findings, **When** the final report generates, **Then** a narrative interpretation explains how this pattern demonstrates the distinction between visual attention and event comprehension

---

### User Story 8 - Comprehensive Multi-Analysis Report Generation (Priority: P1)

As a principal investigator, I want to generate a single comprehensive report that integrates findings from all seven analytical requirements, so that I can present a complete picture of the research findings to stakeholders and for publication.

**Why this priority**: Scientific communication requires integrated reporting. While individual analyses are valuable, the ability to synthesize all findings into a coherent narrative is essential for the research to have impact. This is a P1 deliverable alongside the core analysis.

**Independent Test**: Can be fully tested by executing the report compilation pipeline and verifying that all individual analysis outputs are correctly integrated with appropriate cross-references and unified formatting.

**Acceptance Scenarios**:

1. **Given** completed individual AR reports, **When** the compilation process runs, **Then** a single HTML and PDF report is generated containing all seven analyses with proper sectioning and formatting
2. **Given** the final compiled report, **When** validation checks run, **Then** all visualizations render correctly, statistical tables are properly formatted, and cross-references between sections work properly
3. **Given** the complete analysis pipeline, **When** executed from raw data to final report, **Then** the entire workflow completes without manual intervention and produces reproducible results

---

### Edge Cases

**Handling Strategy**: HALT on any structural or data quality error during validation and preprocessing. No partial results. Analysis modules may skip specific comparisons due to insufficient sample size and will report the limitation.

- **Missing participant data**: If a participant has missing data for certain trials or conditions (e.g., fussy infant, technical failure), exclude that participant from analyses requiring those specific trials/conditions while retaining them for other analyses where data is complete
- **Zero AOI fixations**: If an infant never looks at a particular AOI during a trial, record zero duration/frequency for that AOI and include in statistical analyses (valid data point)
- **Insufficient gaze length**: Gaze sequences shorter than the 3-frame minimum are not recorded as gaze events in the master log (filtered during preprocessing)
- **Ambiguous frames**: Frames where gaze spans exactly between two AOIs are excluded from gaze event detection (conservative approach to ensure data quality)
- **Insufficient statistical power**: If there are too few data points in an age group or condition to perform valid statistical tests (n < 3), skip that specific comparison, log a warning in the report, and note the limitation
- **Outlier trials**: Trials with excessive off-screen time are flagged in the report; off-screen frames are excluded entirely from gaze events and denominators
- **Missing SHOW condition**: If SHOW condition data is missing or insufficient for AR-7 analysis, skip AR-7 entirely, log a warning, and proceed with AR-1 through AR-6 analyses

## Requirements *(mandatory)*

### Functional Requirements

#### Data Processing & Preparation

- **FR-001**: System MUST read all annotated frame-by-frame CSV files from the data directory and subdirectories
- **FR-002**: System MUST identify gaze events by detecting sequences of 3 or more consecutive frames on the same Area of Interest (AOI), where AOI is determined by the combination of "What" and "Where" column values
- **FR-003**: System MUST generate a master gaze_events.csv file containing all identified gaze events with fields including: participant_id, trial_number, condition, event_segment, AOI, gaze_start_frame, gaze_end_frame, gaze_duration, age_group
- **FR-004**: System MUST preserve all relevant metadata from raw data files (participant demographics, experimental conditions, trial information) in the master gaze events log
- **FR-005**: System MUST validate data integrity by checking for required fields and flagging missing or malformed data
- **FR-005a**: System MUST halt pipeline execution with an error message when structural validation fails (missing required columns per current dataset schema; unparseable CSV files; incorrect file format)
- **FR-005b**: System MUST halt pipeline execution when data quality issues are detected (missing required values, out-of-range values, invalid AOI combinations). No analyses may proceed until corrected
- **FR-005c**: Statistical insufficiency in otherwise valid data (e.g., n < 3) MUST be reported within analysis outputs as a limitation (skip that comparison) without halting the entire pipeline

#### AR-1: Gaze Duration Analysis

- **FR-006**: System MUST calculate the proportion of on-screen looking time spent on each AOI for each participant and condition (off-screen excluded from numerator and denominator)
- **FR-007**: System MUST fit Linear Mixed Models (LMM) with participant random effects to compare toy-looking proportions between GIVE_WITH and HUG_WITH conditions; report fixed-effect estimates, confidence intervals, and p-values
- **FR-008**: System MUST fit LMMs to model toy-looking proportions across age (continuous and/or grouped) with appropriate fixed effects; only fall back to t-tests/ANOVA if LMMs are infeasible
- **FR-009**: System MUST generate bar charts visualizing mean proportion of toy-looking by condition with error bars
- **FR-010**: System MUST produce summary statistics tables containing means, standard deviations, and sample sizes for each comparison group
- **FR-011**: System MUST generate both HTML and PDF format reports for AR-1 containing all visualizations, tables, and statistical interpretations

#### AR-2: Gaze Transition Analysis

- **FR-012**: System MUST identify all gaze-to-gaze transitions (when one gaze event ends and another begins on a different on-screen AOI; off-screen frames do not form gaze events)
- **FR-013**: System MUST calculate transition probability matrices showing P(AOI_j | AOI_i) for all AOI pairs
- **FR-014**: System MUST compute transition matrices separately for each experimental condition and age group
- **FR-015**: System MUST use GLMMs for transition counts where applicable (e.g., Poisson/Negative Binomial with participant random effects); only fall back to Chi-squared tests if GLMMs are infeasible
- **FR-016**: System MUST generate directed graph visualizations where nodes represent AOIs and edge thickness represents transition probability
- **FR-017**: System MUST generate both HTML and PDF format reports for AR-2 containing transition matrices, graphs, and statistical results

#### AR-3: Social Gaze Triplet Analysis

- **FR-018**: System MUST parse gaze sequences to identify all instances of social gaze triplet patterns: (1) man/face → toy/other → woman/face, or (2) woman/face → toy/other → man/face (sequences must involve two different people; same-person patterns are excluded)
- **FR-019**: System MUST count the frequency of social gaze triplets per trial for each participant
- **FR-020**: System MUST calculate mean triplet frequencies for each experimental condition and age group
- **FR-021**: System MUST use GLMMs for triplet count comparisons between conditions and across age (e.g., Poisson/Negative Binomial with participant random effects); only fall back to t-test/ANOVA if GLMMs are infeasible
- **FR-022**: System MUST generate bar charts showing mean social gaze triplet frequencies with error bars
- **FR-023**: System MUST generate both HTML and PDF format reports for AR-3 containing visualizations and statistical results

#### AR-4: Dwell Time Analysis

- **FR-024**: System MUST calculate the average duration of individual gaze events (dwell time) for each AOI using onset/offset times in milliseconds
- **FR-025**: System MUST compute mean dwell times separately by participant, condition, and AOI
- **FR-026**: System MUST use LMMs to compare mean dwell times (e.g., dwell_time_ms ~ condition + (1 | participant)), with AOI-specific models as needed
- **FR-027**: System MUST generate bar charts visualizing mean dwell times by AOI and condition
- **FR-028**: System MUST generate both HTML and PDF format reports for AR-4 containing visualizations and statistical results

#### AR-5: Developmental Trajectory Analysis

- **FR-029**: System MUST fit LMMs with continuous age and Condition, including the Age × Condition interaction
- **FR-030**: System MUST test the significance of the Age × Condition interaction to determine if condition effects change with age and report estimates and confidence intervals
- **FR-031**: System MUST generate interaction plots showing condition effects at each age level
- **FR-032**: System MUST produce full ANOVA summary tables with F-statistics, degrees of freedom, and p-values
- **FR-033**: System MUST generate both HTML and PDF format reports for AR-5 containing interaction plots and model results

#### AR-6: Learning/Habituation Analysis

- **FR-034**: System MUST order gaze events and derived metrics by trial number within each participant session
- **FR-035**: System MUST fit LMMs with random intercepts and random slopes for trial number to test whether trial_number_global predicts looking metrics (e.g., social gaze triplet frequency)
- **FR-036**: System MUST test whether learning slopes (trial_number_global coefficients) differ between experimental conditions (interaction term)
- **FR-037**: System MUST generate line graphs plotting key metrics across sequential trials
- **FR-038**: System MUST produce regression summary tables with coefficients, R-squared values, and p-values
- **FR-039**: System MUST generate both HTML and PDF format reports for AR-6 containing line graphs and regression results

#### AR-7: Complex Event Dissociation Analysis

- **FR-040**: System MUST apply AR-1 LMM methods to SHOW condition data to quantify toy-looking duration
- **FR-041**: System MUST apply AR-3 GLMM methods to SHOW condition data to quantify social gaze triplet frequency
- **FR-042**: System MUST generate side-by-side visualizations comparing high toy attention with low social gaze patterns in SHOW condition
- **FR-043**: System MUST produce a narrative synthesis report interpreting the dissociation as evidence for seeing vs. understanding distinction
- **FR-044**: System MUST generate both HTML and PDF format reports for AR-7 containing comparative visualizations and narrative interpretation

#### Comprehensive Reporting

- **FR-045**: System MUST compile individual AR reports into a single integrated final report
- **FR-046**: System MUST generate the final compiled report in both HTML and PDF formats
- **FR-047**: System MUST include a table of contents with hyperlinks to each analysis section in the final report
- **FR-048**: System MUST ensure all visualizations, tables, and statistical results are properly formatted and rendered in both output formats
- **FR-049**: System MUST include a methods section documenting the gaze event definition, statistical approaches, and analysis pipeline

#### Reproducibility & Automation

- **FR-050**: System MUST provide a single automated pipeline that runs the complete analysis from raw data to final report without manual intervention
- **FR-051**: System MUST organize all code in a modular structure separating preprocessing, individual analyses, and reporting functions
- **FR-052**: System MUST save all intermediate results (gaze_events.csv, individual analysis outputs) to clearly defined directories
- **FR-053**: System MUST log all analysis steps and any data quality warnings or errors encountered during processing
- **FR-054**: System MUST be executable via a single command or script that orchestrates the entire workflow

### Key Entities *(include if feature involves data)*

- **Gaze Event**: A continuous sequence of 3 or more frames where an infant's gaze remains on the same on-screen Area of Interest (off-screen excluded). Key attributes: participant identifier, trial number, experimental condition, AOI label, start frame, end frame, duration in frames/milliseconds, event segment (e.g., pre-action, action, post-action).

- **Area of Interest (AOI)**: A defined region of the visual stimulus that can be tracked, determined by the combination of "What" and "Where" columns. Valid AOI categories: no/signal (off-screen/no gaze detected), screen/other (on-screen but no specific AOI), woman/face, man/face, toy/other (toy present in "with" trials), toy2/other (toy location in "without" trials where no physical toy exists), man/body, woman/body, man/hands, woman/hands. Attributes: AOI category, experimental relevance to event meaning.

- **Trial**: A single experimental viewing instance. Attributes: trial number (sequential within session), experimental condition (GIVE, HUG, SHOW), participant identifier, presentation timestamp.

- **Participant**: An infant subject in the study. Attributes: unique identifier, age in months, age group classification (e.g., 12-month-olds, 16-month-olds, 20-month-olds), session date.

- **Experimental Condition**: The type of social event shown to the infant. Values: GIVE (object transfer event), HUG (affectionate gesture with object present but irrelevant), SHOW (object display event). Attributes: condition name, predicted relevance of toy object.

- **Social Gaze Triplet**: A specific sequence pattern of three consecutive gazes indicating joint attention between two different social agents. Valid patterns: (1) man/face → toy/other → woman/face, or (2) woman/face → toy/other → man/face. Patterns involving the same person (e.g., man/face → toy/other → man/face) are NOT counted as social gaze triplets. Attributes: trial number, participant identifier, frame range of the complete sequence, triplet pattern type.

- **Transition**: A change from one gaze event to another. Attributes: source AOI, target AOI, participant identifier, trial number, transition timestamp.

- **Analysis Report**: A self-contained output document for one analytical requirement. Attributes: AR identifier (AR-1 through AR-7), analysis type (e.g., "Gaze Duration Analysis"), generation timestamp, file format (HTML/PDF), file path. Contains: visualizations, statistical tables, narrative interpretation.

- **Final Compiled Report**: An integrated document combining all individual analysis reports. Attributes: generation timestamp, file format (HTML/PDF), table of contents, cross-references between sections.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Researchers can transform raw annotated data into a validated master gaze events log without manual data manipulation

- **SC-002**: Each of the seven analytical requirements (AR-1 through AR-7) produces a complete, self-contained report in both HTML and PDF formats containing all required visualizations, statistical tables, and narrative interpretations

- **SC-003**: All statistical tests produce standard reporting format including test statistics (t-values, F-values, Chi-squared), degrees of freedom, p-values, and effect sizes where appropriate

- **SC-004**: The complete analysis pipeline executes from raw data to final compiled report via a single automated command without requiring manual intervention

- **SC-005**: All analysis reports include publication-quality visualizations (bar charts, line graphs, directed graphs) with proper axis labels, legends, and error bars

- **SC-006**: The final compiled report successfully integrates all seven individual analysis reports with a functional table of contents and consistent formatting across sections

- **SC-007**: The modular code structure allows individual analytical requirements to be executed independently without running the entire pipeline

- **SC-008**: Analysis results are reproducible - running the pipeline multiple times on the same data produces identical statistical results and visualizations

- **SC-009**: Data quality issues (missing values, insufficient data, outliers) are automatically detected and logged with appropriate warnings in the analysis reports

- **SC-010**: Researchers can interpret findings directly from the reports without needing to examine raw output files or code

- **SC-011**: The system handles datasets with varying numbers of participants, trials, and conditions without requiring code modifications

- **SC-012**: All intermediate data files (especially gaze_events.csv) are saved in documented, human-readable formats that can be inspected and validated independently

## Assumptions

- Raw data files are provided in CSV format stored in data/csvs_human_verified_vv/child/ (infant participants) and data/csvs_human_verified_vv/adult/ (adult control participants) directories
- Each CSV file represents a single session for a single participant, with filename containing age group and unique identifier
- Each CSV file contains the following columns: Participant, Frame Number, Time, What, Where, Onset, Offset, Blue Dot Center, event_verified, frame_count_event, trial_number, trial_number_global, frame_count_trial_number, segment, frame_count_segment, participant_type, participant_age_months, participant_age_years
- AOI categories are determined by the combination of "What" and "Where" columns with these valid pairs: screen/other, woman/face, man/face, toy/other, toy2/other, man/body, woman/body, man/hands, woman/hands (off-screen no/signal excluded from events)
- The "toy/other" AOI only appears in trials with toys present ("with" trials), while "toy2/other" represents looking at the toy location in trials without toys ("without" trials)
- The `event_verified` column contains experimental condition labels (e.g., gw, gwo, sw, swo, hw, hwo, plus upside-down variants)
- The "segment" column contains event segment information (e.g., approach, action, post-action)
- Participant age is provided in months via the "participant_age_months" column, and participant type (infant/adult) via the "participant_type" column
- Frame timing information is available through Onset/Offset timestamps (primary) and frame counters (Frame Number, frame_count_*)
- The experimental design includes at least the GIVE and HUG conditions; SHOW condition is optional for AR-7
- Statistical analysis will use standard significance threshold of α = 0.05 unless otherwise specified
- Reports will be generated using standard scientific visualization conventions (e.g., bar charts with standard error bars)
- The Python scientific stack (pandas, numpy, scipy, matplotlib/seaborn, statsmodels) or equivalent statistical software is available for implementation
- HTML and PDF report generation will use Jinja2 (HTML templates) and WeasyPrint (HTML→PDF)

## Dependencies

- Access to all raw annotated data files stored in the data directory and subdirectories
- Statistical computing environment (Python with scientific libraries, R, or equivalent)
- Report generation tools capable of producing both HTML and PDF outputs
- Sufficient documentation of the Gordon (2003) theoretical framework to inform interpretation sections of reports

## Out of Scope

- Real-time data collection or eye-tracking system integration (this system processes pre-collected, annotated data only)
- Manual data annotation or AOI coding (assumes this has been completed prior to analysis)
- Interactive data exploration dashboards or graphical user interfaces
- Advanced machine learning or pattern recognition beyond the specified seven analytical requirements
- Meta-analysis or integration with datasets from other studies
- Automated manuscript generation or publication submission
- Version control or data management for the raw data files themselves
- Handling video files or raw eye-tracking data formats (only annotated CSV files)
