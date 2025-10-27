from __future__ import annotations

import pytest

from src.preprocessing.aoi_mapper import UnknownAOIError, load_aoi_mapping, map_what_where_to_aoi


def test_map_what_where_to_aoi_default_mapping():
    assert map_what_where_to_aoi("man", "face") == "man_face"
    assert map_what_where_to_aoi("woman", "hands") == "woman_hands"


def test_map_what_where_to_aoi_unknown_combination():
    with pytest.raises(UnknownAOIError):
        map_what_where_to_aoi("unknown", "value")


def test_load_aoi_mapping_overrides():
    config = {
        "aoi_mapping": {
            "toy,other": "custom_toy",
        }
    }

    mapping = load_aoi_mapping(config)
    assert mapping[("toy", "other")] == "custom_toy"
    assert mapping[("man", "face")] == "man_face"


def test_map_what_where_to_aoi_strip_whitespace():
    config = {
        "aoi_mapping": {
            "toy, other": "toy_present",
        }
    }
    assert map_what_where_to_aoi("toy", "other", config=config) == "toy_present"


def test_map_what_where_to_aoi_case_sensitive():
    with pytest.raises(UnknownAOIError):
        map_what_where_to_aoi("Toy", "Other")
