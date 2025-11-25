import subprocess
import sys
from pathlib import Path

import pandas as pd


def _write_cli_config(config_path: Path, fixtures_dir: Path) -> None:
    config_contents = "\n".join(
        [
            f'input_threshold_dir: "{fixtures_dir.as_posix()}"',
            'input_filename: "gaze_fixations_sample_min4.csv"',
            "condition_codes:",
            "  - 'gw'",
            "min_trials_per_participant: 1",
            "aoi_groups:",
            "  giver:",
            "    - 'man_face'",
            "  recipient:",
            "    - 'woman_face'",
            "  object:",
            "    - 'toy_present'",
            "cohorts:",
            "  - label: 'sample'",
            "    min_months: 7",
            "    max_months: 12",
            "report:",
            "  research_question: 'RQ'",
            "  hypothesis: 'H'",
            "  prediction: 'P'",
        ]
    )
    config_path.write_text(config_contents)


def test_cli_generates_expected_outputs(tmp_path):
    analysis_dir = tmp_path / "cli_tri_argument"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    config_path = analysis_dir / "config.yaml"
    fixtures_dir = Path("tests/project_extension/fixtures")
    _write_cli_config(config_path, fixtures_dir)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "project_extension.analyses.tri_argument_fixation.run",
            "--config",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"CLI exited with {completed.returncode}: {completed.stderr}")

    output_root = analysis_dir / config_path.stem
    prefix = config_path.stem
    summary_path = output_root / "tables" / f"{prefix}_tri_argument_summary.csv"
    assert summary_path.exists()
    summary_df = pd.read_csv(summary_path)
    assert {"cohort", "success_rate"}.issubset(summary_df.columns)
    assert (output_root / "figures" / f"{prefix}_tri_argument_success.png").exists()
    assert (output_root / "reports" / f"{prefix}_tri_argument_report.txt").exists()
    assert (output_root / "reports" / f"{prefix}_tri_argument_report.html").exists()
    assert (output_root / "reports" / f"{prefix}_tri_argument_report.pdf").exists()
    assert (output_root / "tables" / f"{prefix}_event_structure_breakdown.csv").exists()
    assert (output_root / "figures" / f"{prefix}_event_structure_breakdown.png").exists()

