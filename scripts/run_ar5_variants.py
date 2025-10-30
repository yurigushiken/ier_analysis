"""Run AR-5 variants defined in config/analysis_configs/AR5_developmental_trajectories.

This script mirrors other run_ar*_variants.py scripts and executes AR-5 for each YAML variant
present in the analysis_configs directory.
"""
import os
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar5_development as ar5

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR5_developmental_trajectories"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        if name == "ar5_config":
            continue
        print("Running AR-5 variant:", name)
        variant_key = f"AR5_developmental_trajectories/{name}"
        try:
            load_analysis_config(variant_key)
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        os.environ["IER_AR5_CONFIG"] = variant_key
        try:
            result = ar5.run(config=cfg)
        finally:
            os.environ.pop("IER_AR5_CONFIG", None)
        print("Result:", result)


if __name__ == "__main__":
    main()
