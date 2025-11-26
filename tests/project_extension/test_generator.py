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


def _write_mixed_aoi_fixture(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    frame_number = 1
    for what in ("screen", "toy"):
        for idx in range(3):
            rows.append(
                {
                    "Participant": "Eight-0101-1579",
                    "Frame Number": frame_number,
                    "What": what,
                    "Where": "other",
                    "Onset": 10.0 + frame_number * 0.01,
                    "Offset": 10.01 + frame_number * 0.01,
                    "trial_number": 1,
                    "participant_type": "infant",
                    "participant_age_months": 8,
                    "event_verified": "gwo",
                    "segment": "approach",
                    "frame_count_trial_number": frame_number,
                }
            )
            frame_number += 1
    df = pd.DataFrame(rows)
    df.to_csv(target_dir / "mixed_fixture.csv", index=False)


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


def test_generator_excludes_screen_nonroi(tmp_path):
    child_dir = tmp_path / "child_mixed"
    adult_dir = tmp_path / "adult_mixed"
    _write_mixed_aoi_fixture(child_dir)
    _write_mixed_aoi_fixture(adult_dir)

    thresholds = [1]

    output_all = tmp_path / "outputs_all"
    generator.generate_for_thresholds(
        thresholds,
        child_dirs=[child_dir],
        adult_dirs=[adult_dir],
        output_root=output_all,
    )
    combined_all = pd.read_csv(output_all / "min1" / "gaze_fixations_combined_min1.csv")
    assert "screen_nonAOI" in set(combined_all["aoi_category"])

    output_filtered = tmp_path / "outputs_filtered"
    generator.generate_for_thresholds(
        thresholds,
        child_dirs=[child_dir],
        adult_dirs=[adult_dir],
        output_root=output_filtered,
        exclude_screen_nonroi=True,
    )
    combined_filtered = pd.read_csv(
        output_filtered / "min1" / "gaze_fixations_combined_min1.csv"
    )
    categories = set(combined_filtered["aoi_category"])
    assert "screen_nonAOI" not in categories
    assert "toy_present" in categories
    assert len(combined_filtered) < len(combined_all)

