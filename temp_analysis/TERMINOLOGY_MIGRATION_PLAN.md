# Terminology Migration Plan: "gaze event" → "gaze fixation"

**Status:** Planning Phase - No Changes Made Yet
**Date:** 2025-10-27
**Scope:** Project-wide terminology standardization
**Estimated Effort:** 6-8 hours
**Risk Level:** Medium (requires careful testing)

---

## Executive Summary

**Current:** "gaze event" terminology is confusing (conflicts with "stimulus event")
**Target:** "gaze fixation" terminology is standard and clear
**Impact:** 66 files affected, ~535 occurrences
**Approach:** Systematic find-replace with verification at each stage

---

## Phase 1: Core Code Changes (HIGHEST PRIORITY)

### 1.1 Data Files (RENAME)
**Impact:** BREAKING - Analysis modules depend on these filenames

```
CURRENT                                    NEW
data/processed/gaze_events.csv         → data/processed/gaze_fixations.csv
data/processed/gaze_events_child.csv   → data/processed/gaze_fixations_child.csv
data/processed/gaze_events_adult.csv   → data/processed/gaze_fixations_adult.csv
```

**Action:** Rename files AND update all references
**Files affected:** 15+ modules reference these paths
**Testing required:** Run full pipeline after change

---

### 1.2 Python Modules - Preprocessing (7 occurrences)

#### File: `src/preprocessing/gaze_detector.py`
**Changes:**
- Class: `GazeEvent` → `GazeFixation`
- Function: `detect_gaze_events()` → `detect_gaze_fixations()`
- Function: `_extract_events_from_group()` → `_extract_fixations_from_group()`
- Function: `_finalize_event()` → `_finalize_fixation()`
- All docstrings mentioning "gaze event"
- Comment references

**Estimated:** 30 minutes

#### File: `src/preprocessing/master_log_generator.py`
**Changes:**
- Import statement: `from src.preprocessing.gaze_detector import detect_gaze_events`
- Function call: `detect_gaze_events()` → `detect_gaze_fixations()`
- Docstring references
- Variable names: `gaze_events` → `gaze_fixations`

**Estimated:** 15 minutes

---

### 1.3 Python Modules - Analysis (AR1-AR7) (45+ occurrences)

#### Files to update:
- `src/analysis/ar1_gaze_duration.py` (10 occurrences)
- `src/analysis/ar2_transitions.py` (8 occurrences)
- `src/analysis/ar3_social_triplets.py` (7 occurrences)
- `src/analysis/ar4_dwell_times.py` (6 occurrences)
- `src/analysis/ar5_development.py` (5 occurrences)
- `src/analysis/ar6_learning.py` (4 occurrences)
- `src/analysis/ar7_dissociation.py` (5 occurrences)

**Changes per file:**
- Function: `_load_gaze_events()` → `_load_gaze_fixations()`
- Variable: `df = _load_gaze_events()` → `df = _load_gaze_fixations()`
- Docstrings: "gaze events" → "gaze fixations"
- Comments: Update all references
- File path strings: `"gaze_events.csv"` → `"gaze_fixations.csv"`

**Estimated:** 2 hours (all 7 files)

---

### 1.4 Main Pipeline (`src/main.py`) (3 occurrences)
**Changes:**
- Import statements
- Logging messages: "Generating gaze events" → "Detecting gaze fixations"
- Variable names

**Estimated:** 10 minutes

---

## Phase 2: Tests (CRITICAL FOR VALIDATION)

### 2.1 Unit Tests (25+ occurrences)

#### Files:
- `tests/unit/test_gaze_detector.py` (RENAME to `test_gaze_fixation_detector.py`)
- `tests/unit/test_ar2_transitions.py`
- `tests/unit/test_ar4_dwell.py`
- `tests/unit/test_ar5_development.py`
- `tests/unit/test_ar6_learning.py`
- `tests/unit/test_ar7_dissociation.py`

**Changes:**
- Test function names: `test_detect_gaze_events()` → `test_detect_gaze_fixations()`
- Fixture names: `gaze_events_df` → `gaze_fixations_df`
- File path references in test data
- Assert statements and error messages

**Estimated:** 2 hours

---

### 2.2 Integration Tests (30+ occurrences)

#### Files:
- `tests/integration/test_preprocessing_pipeline.py`
- `tests/integration/test_preprocessing_metadata.py`
- `tests/integration/test_ar3_analysis.py`
- `tests/integration/test_ar4_analysis.py`
- `tests/integration/test_ar5_analysis.py`
- `tests/integration/test_ar6_analysis.py`
- `tests/integration/test_ar7_analysis.py`
- `tests/integration/test_report_generation.py`

**Changes:**
- Expected file paths in assertions
- DataFrame column references (if any)
- Test data fixtures

**Estimated:** 1.5 hours

---

### 2.3 Contract Tests (10+ occurrences)

#### Files:
- `tests/contract/test_gaze_events_schema.py` (RENAME)
- `tests/contract/test_report_outputs.py`
- `tests/fixtures/expected_gaze_events.csv` (RENAME)

**Changes:**
- Test class names
- Schema validation file references
- Expected output file names

**Estimated:** 30 minutes

---

## Phase 3: Specifications & Documentation

### 3.1 Core Specifications (50+ occurrences)

#### File: `specs/001-infant-event-analysis/spec.md`
**Changes:**
- All uses of "gaze event" → "gaze fixation"
- Technical definitions section
- Data model descriptions
- Example code snippets

**Estimated:** 45 minutes

#### File: `specs/001-infant-event-analysis/plan.md`
**Changes:**
- Implementation plan references
- Data processing steps
- Output file names

**Estimated:** 30 minutes

#### File: `specs/001-infant-event-analysis/data-model.md`
**Changes:**
- Entity definitions: "Gaze Event" → "Gaze Fixation"
- Relationship descriptions
- Column names in tables (if CSV column headers change)
- Example data

**Estimated:** 45 minutes

#### File: `specs/001-infant-event-analysis/research.md`
**Changes:**
- Scientific terminology
- Background literature references

**Estimated:** 15 minutes

#### File: `specs/001-infant-event-analysis/tasks.md`
**Changes:**
- Task descriptions
- Acceptance criteria

**Estimated:** 15 minutes

#### File: `specs/001-infant-event-analysis/quickstart.md`
**Changes:**
- User-facing instructions
- File path examples
- Expected output descriptions

**Estimated:** 30 minutes

---

### 3.2 Contracts & Schemas (15+ occurrences)

#### File: `specs/001-infant-event-analysis/contracts/gaze_events_schema.json`
**Action:** RENAME to `gaze_fixations_schema.json`

**Changes:**
- Schema `$id` field
- Description fields
- File references
- Update all imports in test files

**Estimated:** 20 minutes

#### File: `specs/001-infant-event-analysis/contracts/report_schema.json`
**Changes:**
- Expected file name patterns
- Field descriptions

**Estimated:** 10 minutes

---

### 3.3 User Documentation (40+ occurrences)

#### File: `README.md`
**Changes:**
- Project overview section
- Data pipeline description
- Example commands
- File path references
- Glossary/terminology section

**Estimated:** 45 minutes

#### File: `MENTORSHIP_DATA_FLOW.md`
**Changes:**
- ASCII flowchart labels
- File name references: "gaze_events.csv (19,813 events)"
- Section headers
- Explanatory text

**Estimated:** 30 minutes

#### File: `PROJECT_STATUS.md`
**Changes:**
- Component status descriptions
- Output file listings

**Estimated:** 10 minutes

#### File: `CHANGELOG.md`
**Changes:**
- Add new entry for terminology update
- Historical references (keep as-is for accuracy)

**Estimated:** 5 minutes

---

## Phase 4: Configuration & Templates

### 4.1 Configuration Files (5+ occurrences)

#### File: `config/pipeline_config.yaml`
**Changes:**
- Comments referencing gaze events
- Validation section descriptions

**Estimated:** 10 minutes

#### File: `config/analysis_configs/ar4_config.yaml`
**Changes:**
- Description fields
- Comments

**Estimated:** 5 minutes

---

### 4.2 Report Templates (20+ occurrences)

#### File: `templates/ar1_template.html`
**Changes:**
- Section headings: "Gaze Event Definition" → "Gaze Fixation Definition"
- Body text describing the 3+ frame rule
- Table captions
- Figure captions

**Estimated:** 20 minutes

#### File: `templates/base_report.html`
**Changes:**
- Common terminology in headers/footers
- Glossary definitions

**Estimated:** 10 minutes

---

## Phase 5: Generated/Temporary Files (LOW PRIORITY)

### 5.1 Temp Analysis Files
**Action:** Delete or update after migration

Files:
- `temp_analysis/*` (60+ files with references)

**Estimated:** These are working files - can be cleaned up or left as historical record

---

## DETAILED MIGRATION PROCEDURE

### Step 1: Backup
```bash
# Create backup branch
git checkout -b backup-before-terminology-migration
git push origin backup-before-terminology-migration

# Create backup of data files
cp -r data/processed data/processed_backup
```

### Step 2: Update Code (Critical Path)

**Order matters - do in this sequence:**

1. **Update `gaze_detector.py` first**
   - Rename class, functions, variables
   - Run unit tests: `pytest tests/unit/test_gaze_detector.py -v`

2. **Update `master_log_generator.py`**
   - Update imports and calls
   - Run integration test: `pytest tests/integration/test_preprocessing_pipeline.py -v`

3. **Rename data files**
   ```bash
   cd data/processed
   mv gaze_events.csv gaze_fixations.csv
   mv gaze_events_child.csv gaze_fixations_child.csv
   mv gaze_events_adult.csv gaze_fixations_adult.csv
   ```

4. **Update all AR modules (ar1-ar7)**
   - Update `_load_gaze_events()` → `_load_gaze_fixations()`
   - Update file path strings
   - Update all docstrings
   - Test each: `pytest tests/integration/test_arX_analysis.py -v`

5. **Update `main.py`**
   - Update imports
   - Update function calls
   - Test full pipeline: `python src/main.py`

### Step 3: Update Tests

1. **Rename test files**
   ```bash
   mv tests/unit/test_gaze_detector.py tests/unit/test_gaze_fixation_detector.py
   mv tests/contract/test_gaze_events_schema.py tests/contract/test_gaze_fixations_schema.py
   mv tests/fixtures/expected_gaze_events.csv tests/fixtures/expected_gaze_fixations.csv
   ```

2. **Update test content**
   - Search/replace in all test files
   - Update fixture references
   - Run full test suite: `pytest tests/ -v`

### Step 4: Update Documentation

1. **Specifications** (do in order):
   - `spec.md`
   - `plan.md`
   - `data-model.md`
   - `research.md`
   - `quickstart.md`
   - `tasks.md`

2. **User docs**:
   - `README.md`
   - `MENTORSHIP_DATA_FLOW.md`
   - `PROJECT_STATUS.md`

3. **Add CHANGELOG entry**:
   ```markdown
   ## [Unreleased]
   ### Changed
   - **TERMINOLOGY:** Renamed "gaze event" to "gaze fixation" throughout codebase for clarity
     - Gaze fixation: 3+ consecutive frames on same AOI (previously called "gaze event")
     - This distinguishes from stimulus events (video clips like gw, hw)
     - Data files renamed: gaze_events.csv → gaze_fixations.csv
     - All APIs updated: detect_gaze_events() → detect_gaze_fixations()
   ```

### Step 5: Update Templates
- `templates/ar1_template.html`
- `templates/base_report.html`
- Regenerate reports: `python src/main.py`

### Step 6: Verification
```bash
# 1. Run full test suite
pytest tests/ -v --tb=short

# 2. Run full pipeline
python src/main.py

# 3. Check generated reports
open results/AR1_Gaze_Duration/report.html

# 4. Verify data files exist
ls -la data/processed/gaze_fixations*.csv

# 5. Search for any remaining "gaze event" references
grep -r "gaze.event" --include="*.py" --include="*.md" . | grep -v temp_analysis | grep -v backup
```

---

## SEARCH & REPLACE PATTERNS

### For Python Files:
```python
# Class names
GazeEvent → GazeFixation

# Function names
detect_gaze_events → detect_gaze_fixations
_extract_events_from_group → _extract_fixations_from_group
_finalize_event → _finalize_fixation
_load_gaze_events → _load_gaze_fixations

# Variable names
gaze_events → gaze_fixations
gaze_event → gaze_fixation
num_gaze_events → num_gaze_fixations

# File paths (strings)
"gaze_events.csv" → "gaze_fixations.csv"
"gaze_events_child.csv" → "gaze_fixations_child.csv"
"gaze_events_adult.csv" → "gaze_fixations_adult.csv"
"gaze_events_schema.json" → "gaze_fixations_schema.json"

# Comments and docstrings
"gaze event" → "gaze fixation"
"Gaze event" → "Gaze fixation"
"gaze events" → "gaze fixations"
"Gaze events" → "Gaze fixations"
```

### For Markdown Files:
```markdown
gaze event → gaze fixation
Gaze event → Gaze fixation
gaze events → gaze fixations
Gaze events → Gaze fixations
gaze-event → gaze-fixation
`gaze_event` → `gaze_fixation`
```

### For YAML/JSON:
```yaml
gaze_events → gaze_fixations
"gaze event" → "gaze fixation"
```

---

## TESTING CHECKLIST

After each phase:

- [ ] **Unit tests pass:** `pytest tests/unit/ -v`
- [ ] **Integration tests pass:** `pytest tests/integration/ -v`
- [ ] **Contract tests pass:** `pytest tests/contract/ -v`
- [ ] **Full pipeline runs:** `python src/main.py`
- [ ] **Reports generate:** Check `results/` directories
- [ ] **Data files exist:** Check `data/processed/` for renamed files
- [ ] **No remaining references:** `grep -r "gaze.event" --include="*.py" .`
- [ ] **Documentation builds:** Check for broken links/references
- [ ] **Git commit:** Document changes clearly

---

## RISK MITIGATION

### Risks:
1. **Breaking existing analyses:** Renaming data files breaks dependent scripts
2. **Test failures:** Tests may hardcode old file names
3. **Lost data:** Accidental deletion of original files
4. **Incomplete migration:** Missed references cause runtime errors

### Mitigations:
1. **Backup branch:** Create before starting
2. **Incremental commits:** Commit after each phase
3. **Comprehensive testing:** Run full suite after each change
4. **Staged rollout:** Update code → tests → docs (in order)
5. **Keep backups:** Preserve original data files for 30 days

---

## ROLLBACK PLAN

If issues arise:

```bash
# Restore from backup branch
git checkout backup-before-terminology-migration

# Restore data files
rm -rf data/processed
mv data/processed_backup data/processed

# Verify
pytest tests/ -v
python src/main.py
```

---

## ESTIMATED TIMELINE

**Total:** 6-8 hours (1 full workday)

### Breakdown:
- **Phase 1** (Code): 3 hours
- **Phase 2** (Tests): 4 hours
- **Phase 3** (Specs/Docs): 3 hours
- **Phase 4** (Config/Templates): 45 minutes
- **Phase 5** (Cleanup): 30 minutes
- **Verification**: 1 hour

**Recommended approach:** Split across 2 sessions with verification break in between

---

## SUCCESS CRITERIA

**Migration is complete when:**

1. ✅ All Python code uses "fixation" terminology
2. ✅ All data files renamed
3. ✅ Full test suite passes (100%)
4. ✅ Full pipeline runs successfully
5. ✅ Reports generate with correct terminology
6. ✅ All documentation updated
7. ✅ No grep matches for "gaze.event" in core code (excluding backups/temp)
8. ✅ Git commit with clear migration message
9. ✅ CHANGELOG entry added

---

## POST-MIGRATION

### Immediate:
- Run AR1-AR7 analyses to generate new reports
- Verify all reports display "gaze fixation" terminology
- Update any external documentation/presentations
- Notify collaborators of terminology change

### Within 1 week:
- Monitor for any issues with existing scripts
- Update any Jupyter notebooks
- Update any external APIs/integrations
- Clean up temp_analysis backup files

### Before publication:
- Final review of all user-facing documentation
- Ensure consistency across all materials
- Update manuscript draft with correct terminology

---

**END OF MIGRATION PLAN**
