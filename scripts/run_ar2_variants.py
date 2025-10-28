#!/usr/bin/env python
"""Execute all AR-2 configuration variants sequentially."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analysis import ar2_transitions as ar2
from src.utils.config import load_config

ANALYSIS_CONFIG_DIR = ROOT / "config" / "analysis_configs"
AR2_CONFIG_DIR = ANALYSIS_CONFIG_DIR / "AR2_gaze_transitions"


def _discover_variant_configs() -> Iterable[str]:
    if not AR2_CONFIG_DIR.exists():
        return []

    for path in sorted(AR2_CONFIG_DIR.glob("*.yaml")):
        rel = path.relative_to(ANALYSIS_CONFIG_DIR)
        config_name = str(rel.with_suffix("")).replace("\\", "/")
        yield config_name


def main() -> int:
    variants = list(_discover_variant_configs())
    if not variants:
        print("No AR-2 variant configuration files were found.", file=sys.stderr)
        return 1

    print(f"Discovered {len(variants)} AR-2 variants.")
    exit_code = 0

    for config_name in variants:
        print(f"\n=== Running AR-2 variant: {config_name} ===")
        try:
            cfg = load_config(overrides=[f"analysis_specific.ar2_transitions.config_name={config_name}"])
            metadata = ar2.run(config=cfg)
        except Exception:  # pragma: no cover - command-line utility
            exit_code = 1
            traceback.print_exc()
            continue

        html_path = metadata.get("html_path", "") if isinstance(metadata, dict) else ""
        print(f"Completed variant {config_name}. Report: {html_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
