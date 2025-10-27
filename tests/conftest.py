from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
ROOT_STR = str(PROJECT_ROOT)
SRC_STR = str(SRC_PATH)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
if SRC_STR not in sys.path:
    sys.path.insert(0, SRC_STR)
