from pathlib import Path

import pandas as pd
import pytest

from project_extension.analyses.tri_argument_fixation import run


@pytest.fixture(scope="module")
def fixations_fixture_dir() -> Path:
    return Path("tests/project_extension/fixtures")


def test_run_analysis_generates_outputs(tmp_path, fixations_fixture_dir):
    analysis_dir = tmp_path / "tri_argument_analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    config_path = analysis_dir / "custom_test_config.yaml"
    fixtures_posix = fixations_fixture_dir.as_posix()
    config_contents = (
        f"input_threshold_dir: \"{fixtures_posix}\"\n"
        "input_filename: \"gaze_fixations_sample_min4.csv\"\n"
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
    )
    config_path.write_text(config_contents)

    run.run_analysis(config_path)

    output_root = analysis_dir / config_path.stem
    summary_path = output_root / "tables" / "tri_argument_summary.csv"
    assert summary_path.exists()
    summary_df = pd.read_csv(summary_path)
    assert {"cohort", "success_rate"}.issubset(summary_df.columns)

    assert (output_root / "figures" / "tri_argument_success.png").exists()
    assert (output_root / "reports" / "tri_argument_report.txt").exists()
    assert (output_root / "reports" / "tri_argument_report.html").exists()
    assert (output_root / "reports" / "tri_argument_report.pdf").exists()

