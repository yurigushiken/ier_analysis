"""Run AR-7 variants defined in config/analysis_configs/AR7_event_dissociation.

Executes AR-7 for each YAML variant present in the analysis_configs directory.
"""
import os
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar7_dissociation as ar7

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR7_event_dissociation"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        if name == "ar7_config":
            continue
        print("Running AR-7 variant:", name)
        variant_key = f"AR7_event_dissociation/{name}"
        try:
            load_analysis_config(variant_key)
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        os.environ["IER_AR7_CONFIG"] = variant_key
        try:
            result = ar7.run(config=cfg)
        finally:
            os.environ.pop("IER_AR7_CONFIG", None)
        print("Result:", result)


if __name__ == "__main__":
    main()
