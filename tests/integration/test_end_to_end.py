from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pandera")
pytest.importorskip("weasyprint")

import src.main as pipeline_main  # noqa: E402


@pytest.mark.skip(reason="End-to-end pipeline currently requires full data and implementations")
def test_pipeline_runs_end_to_end(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(Path.cwd())
    pipeline_main.main()
