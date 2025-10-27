"""Configuration loading utilities for the infant event representation analysis pipeline."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Tuple

import yaml


class ConfigurationError(RuntimeError):
    """Raised when configuration files cannot be loaded or validated."""


@dataclass(frozen=True)
class ConfigPaths:
    """Container describing paths to global and analysis-specific configuration files."""

    pipeline: Path
    analysis_dir: Path

    @classmethod
    def from_root(cls, root: Path) -> "ConfigPaths":
        pipeline_path = root / "config" / "pipeline_config.yaml"
        analysis_dir = root / "config" / "analysis_configs"
        return cls(pipeline=pipeline_path, analysis_dir=analysis_dir)


def _read_yaml(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Configuration file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigurationError(f"Configuration at {path} must be a mapping.")
    return data


def _merge_dict(base: MutableMapping[str, Any], updates: Mapping[str, Any]) -> MutableMapping[str, Any]:
    for key, value in updates.items():
        if key in base and isinstance(base[key], MutableMapping) and isinstance(value, Mapping):
            _merge_dict(base[key], value)
        else:
            base[key] = copy.deepcopy(value)
    return base


def load_global_config(root: Path | str = Path(".")) -> Dict[str, Any]:
    root_path = Path(root).resolve()
    paths = ConfigPaths.from_root(root_path)
    return _read_yaml(paths.pipeline)


def load_analysis_config(analysis_name: str, root: Path | str = Path(".")) -> Dict[str, Any]:
    root_path = Path(root).resolve()
    paths = ConfigPaths.from_root(root_path)
    analysis_file = paths.analysis_dir / f"{analysis_name}.yaml"
    return _read_yaml(analysis_file)


def load_config(
    analysis: Optional[str] = None,
    *,
    root: Path | str = Path("."),
    env_prefix: str = "IER",
    overrides: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = Path(root).resolve()
    global_config = load_global_config(root_path)
    result: Dict[str, Any] = copy.deepcopy(global_config)

    if analysis:
        analysis_config = load_analysis_config(analysis, root=root_path)
        _merge_dict(result, analysis_config)

    env_overrides = _collect_env_overrides(prefix=env_prefix)
    _merge_dict(result, env_overrides)

    if overrides:
        for override in overrides:
            path, value = _parse_override(override)
            _apply_override(result, path, value)

    return result


def split_child_adult_config(config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    child_config = copy.deepcopy(config)
    adult_config = copy.deepcopy(config)

    child_config["paths"]["raw_data"] = config["paths"].get("raw_data_child", config["paths"]["raw_data"])
    adult_config["paths"]["raw_data"] = config["paths"].get("raw_data_adult", config["paths"]["raw_data"])

    child_config.setdefault("features", {})["enable_adult"] = False
    adult_config.setdefault("features", {})["enable_adult"] = True

    return child_config, adult_config


def _collect_env_overrides(prefix: str) -> Dict[str, Any]:
    namespace = {}
    prefix_with_sep = f"{prefix}_" if prefix else ""
    for key, value in os.environ.items():
        if not key.startswith(prefix_with_sep):
            continue
        stripped = key[len(prefix_with_sep) :]
        path = stripped.lower().split("__")
        _apply_override(namespace, path, _coerce_value(value))
    return namespace


def _parse_override(override: str) -> tuple[list[str], Any]:
    if "=" not in override:
        raise ConfigurationError(f"Override must be in key=value format: {override}")
    key, value = override.split("=", 1)
    path = [part.strip() for part in key.split(".") if part.strip()]
    if not path:
        raise ConfigurationError(f"Override has empty key in expression: {override}")
    return path, _coerce_value(value)


def _apply_override(config: MutableMapping[str, Any], path: Iterable[str], value: Any) -> None:
    parts = list(path)
    current: MutableMapping[str, Any] = config
    for index, part in enumerate(parts):
        if index == len(parts) - 1:
            current[part] = value
        else:
            if part not in current or not isinstance(current[part], MutableMapping):
                current[part] = {}
            current = current[part]  # type: ignore[assignment]


def _coerce_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


__all__ = [
    "ConfigurationError",
    "ConfigPaths",
    "load_config",
    "load_global_config",
    "load_analysis_config",
    "split_child_adult_config",
]
