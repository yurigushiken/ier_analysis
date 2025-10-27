from __future__ import annotations

import pytest

pytest.importorskip("pandera")

from src.utils.config import load_config, split_child_adult_config


def test_split_child_adult_config_separates_paths():
    config = load_config()
    child_config, adult_config = split_child_adult_config(config)

    assert child_config["paths"]["raw_data"] == config["paths"].get("raw_data_child")
    assert adult_config["paths"]["raw_data"] == config["paths"].get("raw_data_adult")
    assert not child_config["features"].get("enable_adult")
    assert adult_config["features"].get("enable_adult")
