"""Run AR-6 variants defined in config/analysis_configs/AR6_learning.

Executes AR-6 for each YAML variant present in the analysis_configs directory.
"""
from pathlib import Path
from src.utils.config import load_config, load_analysis_config
from src.analysis import ar6_learning as ar6

BASE = Path(__file__).resolve().parents[1]
VAR_DIR = BASE / "config" / "analysis_configs" / "AR6_learning"


def main():
    cfg = load_config()
    for yaml_file in VAR_DIR.glob("*.yaml"):
        name = yaml_file.stem
        print("Running AR-6 variant:", name)
        try:
            variant_cfg = load_analysis_config(f"AR6_learning/{name}")
        except Exception as exc:
            print("Failed to load variant", name, exc)
            continue
        # The ar6.run() implementation will load the variant internally; just run
        result = ar6.run(config=cfg)
        print("Result:", result)


if __name__ == "__main__":
    main()
