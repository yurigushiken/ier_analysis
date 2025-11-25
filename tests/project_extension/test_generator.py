from pathlib import Path

import pandas as pd

from project_extension.src import generator


def _write_boundary_fixture(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, frame_count in enumerate([138, 139, 140], start=0):
        rows.append(
            {
                "Participant": "Eight-0101-1579",
                "Frame Number": 500 + idx,
                "What": "screen",
                "Where": "other",
                "Onset": 13.7 + idx * 0.0333,
                "Offset": 13.7333 + idx * 0.0333,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 8,
                "event_verified": "gwo",
                "segment": "departure",
                "frame_count_trial_number": frame_count,
            }
        )
    for idx, frame_count in enumerate([1, 2, 3], start=0):
        rows.append(
            {
                "Participant": "Eight-0101-1579",
                "Frame Number": 600 + idx,
                "What": "screen",
                "Where": "other",
                "Onset": 14.0 + idx * 0.0333,
                "Offset": 14.0333 + idx * 0.0333,
                "trial_number": 1,
                "participant_type": "infant",
                "participant_age_months": 8,
                "event_verified": "gwo",
                "segment": "approach",
                "frame_count_trial_number": frame_count,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(target_dir / "boundary_fixture.csv", index=False)


def test_generator_creates_threshold_outputs(tmp_path):
    child_dir = tmp_path / "child_data"
    adult_dir = tmp_path / "adult_data"
    _write_boundary_fixture(child_dir)
    _write_boundary_fixture(adult_dir)

    output_root = tmp_path / "outputs"
    thresholds = [3]

    generator.generate_for_thresholds(
        thresholds,
        child_dirs=[child_dir],
        adult_dirs=[adult_dir],
        output_root=output_root,
    )

    for threshold in thresholds:
        for cohort in ("child", "adult", "combined"):
            csv_path = output_root / f"min{threshold}" / f"gaze_fixations_{cohort}_min{threshold}.csv"
            assert csv_path.exists(), f"Missing output: {csv_path}"
            df = pd.read_csv(csv_path)
            assert "min_frames" in df.columns
            assert (df["min_frames"] == threshold).all()
            assert (df["gaze_start_frame"] <= df["gaze_end_frame"]).all()

