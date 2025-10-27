"""Area of Interest (AOI) mapping utilities."""

from __future__ import annotations

from typing import Dict, Tuple

from src.utils.config import load_config

_DEFAULT_MAPPING = {
    ("no", "signal"): "off_screen",
    ("screen", "other"): "screen_nonAOI",
    ("woman", "face"): "woman_face",
    ("man", "face"): "man_face",
    ("toy", "other"): "toy_present",
    ("toy2", "other"): "toy_location",
    ("man", "body"): "man_body",
    ("woman", "body"): "woman_body",
    ("man", "hands"): "man_hands",
    ("woman", "hands"): "woman_hands",
}


class UnknownAOIError(ValueError):
    """Raised when an AOI combination is not recognized."""


def load_aoi_mapping(config: Dict | None = None) -> Dict[Tuple[str, str], str]:
    cfg = config or load_config()
    mapping_config = cfg.get("aoi_mapping", {})
    combined: Dict[Tuple[str, str], str] = dict(_DEFAULT_MAPPING)

    for key, value in mapping_config.items():
        if not isinstance(key, str) or "," not in key:
            continue
        what, where = [part.strip() for part in key.split(",", 1)]
        combined[(what, where)] = value
    return combined


def map_what_where_to_aoi(what: str, where: str, *, config: Dict | None = None) -> str:
    mapping = load_aoi_mapping(config)
    key = (what, where)
    if key not in mapping:
        raise UnknownAOIError(f"Unknown AOI combination: {key}")
    return mapping[key]


__all__ = ["map_what_where_to_aoi", "load_aoi_mapping", "UnknownAOIError"]
