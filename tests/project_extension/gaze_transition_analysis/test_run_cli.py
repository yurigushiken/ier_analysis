import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_cli_generates_transition_outputs(tmp_path):
    fixtures_dir = Path("tests/project_extension/fixtures")
    config_path = tmp_path / "gw_transition_test.yaml"
    config_path.write_text(
        "\n".join(
            [
                f'input_fixations: "{(fixtures_dir / "gaze_transition_sample.csv").as_posix()}"',
                "condition_codes:",
                "  - 'gw'",
                "aoi_nodes:",
                "  - 'man_face'",
                "  - 'woman_face'",
                "  - 'man_body'",
                "  - 'woman_body'",
                "  - 'toy_present'",
                "cohorts:",
                "  - label: '7-month-olds'",
                "    min_months: 7",
                "    max_months: 7",
                "  - label: '10-month-olds'",
                "    min_months: 10",
                "    max_months: 10",
            ]
        )
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "project_extension.analyses.gaze_transition_analysis.run",
            "--config",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"CLI exited with {completed.returncode}: {completed.stderr}")

    output_root = tmp_path / config_path.stem
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    assert (tables_dir / "gw_transition_test_transition_counts.csv").exists()
    assert (tables_dir / "gw_transition_test_transition_matrix.csv").exists()
    assert (figures_dir / "gw_transition_test_transition_heatmap.png").exists()
    assert (tables_dir / "gw_transition_test_strategy_proportions.csv").exists()
    assert (tables_dir / "gw_transition_test_strategy_summary.csv").exists()
    assert (figures_dir / "gw_transition_test_gaze_strategy_comparison.png").exists()
    assert (output_root / "reports" / "gw_transition_test_strategy_summary.txt").exists()
    assert (output_root / "reports" / "gw_transition_test_strategy_gee.txt").exists()

