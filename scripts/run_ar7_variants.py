"""Run AR-7 variants defined in config/analysis_configs/AR7_dissociation.

Executes AR-7 for each YAML variant present in the analysis_configs directory.
"""
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar7_dissociation as ar7

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR7_dissociation"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        print("Running AR-7 variant:", name)
        try:
            variant_cfg = load_analysis_config(f"AR7_dissociation/{name}")
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        # ar7.run will load the variant internally; just run
        result = ar7.run(config=cfg)
        print("Result:", result)


if __name__ == "__main__":
    main()
