"""Run AR-5 variants defined in config/analysis_configs/AR5_development.

This script mirrors other run_ar*_variants.py scripts and executes AR-5 for each YAML variant
present in the analysis_configs directory.
"""
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar5_development as ar5

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR5_development"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        print("Running AR-5 variant:", name)
        try:
            variant_cfg = load_analysis_config(f"AR5_development/{name}")
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        # set env to use specific variant if desired (module handles variant override too)
        result = ar5.run(config=cfg)
        print("Result:", result)


if __name__ == "__main__":
    main()
