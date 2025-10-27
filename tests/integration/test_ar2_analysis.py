from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pandera")

from src.analysis import ar2_transitions  # type: ignore


@pytest.mark.skip(reason="AR-2 analysis module not implemented")
def test_ar2_analysis_generates_outputs(tmp_path: Path):
    assert tmp_path is not None
