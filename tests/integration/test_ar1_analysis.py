from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pandera")

from src.analysis import ar1_gaze_duration  # type: ignore


@pytest.mark.skip(reason="AR-1 analysis module not implemented")
def test_ar1_analysis_generates_report(tmp_path: Path):
    assert tmp_path is not None
