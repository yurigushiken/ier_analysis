from pathlib import Path

import pytest

from project_extension.analyses.tri_argument_fixation import run


def test_gw_analysis_creates_stats_report(tmp_path):
    config_path = tmp_path / "gw_config.yaml"
    config_contents = (
        "input_threshold_dir: \"tests/project_extension/fixtures\"\n"
        "input_filename: \"gw_fixations_sample.csv\"\n"
        "condition_codes:\n"
        "  - 'gw'\n"
        "min_trials_per_participant: 1\n"
        "aoi_groups:\n"
        "  man:\n"
        "    - 'man_face'\n"
        "  woman:\n"
        "    - 'woman_face'\n"
        "  toy:\n"
        "    - 'toy_present'\n"
        "cohorts:\n"
        "  - label: 'sample'\n"
        "    min_months: 7\n"
        "    max_months: 12\n"
        "report:\n"
        "  research_question: 'RQ'\n"
        "  hypothesis: 'H'\n"
        "  prediction: 'P'\n"
        "gee:\n"
        "  enabled: true\n"
        "  reference_cohort: 'sample'\n"
    )
    config_path.write_text(config_contents, encoding="utf-8")

    run.run_analysis(config_path)

    stats_path = config_path.with_suffix("").parent / config_path.stem / "reports" / "gee_results.txt"
    assert stats_path.exists()

