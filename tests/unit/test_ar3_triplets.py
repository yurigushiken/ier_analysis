from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analysis import ar3_social_triplets as ar3


@pytest.fixture()
def base_config(tmp_path: Path) -> dict[str, object]:
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    return {
        "paths": {
            "processed_data": str(processed_dir),
            "results": str(results_dir),
        },
        "analysis_specific": {
            "ar3_social_triplets": {
                "config_name": "ar3/ar3_give_vs_hug",
            }
        },
    }


def test_load_variant_configuration_defaults_to_config(base_config: dict[str, object]):
    variant_config, variant_name = ar3._load_variant_configuration(base_config)

    assert variant_name == "ar3/ar3_give_vs_hug"
    assert variant_config["variant_key"] == "ar3_give_vs_hug"


def test_load_variant_configuration_prefers_env(monkeypatch: pytest.MonkeyPatch, base_config: dict[str, object]):
    monkeypatch.setenv("IER_AR3_CONFIG", "ar3/ar3_give_vs_give_without")

    variant_config, variant_name = ar3._load_variant_configuration(base_config)

    assert variant_name == "ar3/ar3_give_vs_give_without"
    assert variant_config["variant_key"] == "ar3_give_vs_give_without"


def test_compute_directional_bias_counts_patterns():
    triplets = pd.DataFrame(
        [
            {"participant_id": "P1", "condition_name": "GIVE_WITH", "pattern": "man_face>toy_present>woman_face"},
            {"participant_id": "P1", "condition_name": "GIVE_WITH", "pattern": "woman_face>toy_present>man_face"},
            {"participant_id": "P2", "condition_name": "HUG_WITH", "pattern": "man_face>toy_present>woman_face"},
        ]
    )

    directional = ar3.compute_directional_bias(triplets)

    assert set(directional["pattern"]) == {
        "man_face>toy_present>woman_face",
        "woman_face>toy_present>man_face",
    }
    give_forward = directional.loc[
        (directional["condition_name"] == "GIVE_WITH")
        & (directional["pattern"] == "man_face>toy_present>woman_face"),
        "count",
    ]
    assert give_forward.iloc[0] == 1


def test_compute_temporal_summary_counts_first_vs_rest():
    triplets = pd.DataFrame(
        [
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "trial_number": 1,
                "pattern": "man_face>toy_present>woman_face",
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "trial_number": 2,
                "pattern": "man_face>toy_present>woman_face",
            },
            {
                "participant_id": "P1",
                "condition_name": "GIVE_WITH",
                "trial_number": 3,
                "pattern": "woman_face>toy_present>man_face",
            },
            {
                "participant_id": "P2",
                "condition_name": "HUG_WITH",
                "trial_number": 1,
                "pattern": "man_face>toy_present>woman_face",
            },
        ]
    )

    temporal = ar3.compute_temporal_summary(triplets)

    give_row = temporal.loc[temporal["condition_name"] == "GIVE_WITH"].iloc[0]
    assert give_row["first_occurrence"] == 1
    assert give_row["subsequent_occurrences"] == 2

    hug_row = temporal.loc[temporal["condition_name"] == "HUG_WITH"].iloc[0]
    assert hug_row["first_occurrence"] == 1
    assert hug_row["subsequent_occurrences"] == 0

