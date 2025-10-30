"""Run AR-6 variants defined in config/analysis_configs/AR6_trial_order.

Executes AR-6 for each YAML variant present in the analysis_configs directory.
"""
import os
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar6_learning as ar6

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR6_trial_order"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        if name == "ar6_config":
            continue
        print("Running AR-6 variant:", name)
        variant_key = f"AR6_trial_order/{name}"
        try:
            load_analysis_config(variant_key)
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        os.environ["IER_AR6_CONFIG"] = variant_key
        try:
            result = ar6.run(config=cfg)
        finally:
            os.environ.pop("IER_AR6_CONFIG", None)
        print("Result:", result)


if __name__ == "__main__":
    main()
