"""Report generation utilities for analysis outputs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

LOGGER = logging.getLogger(__name__)

TEMPLATE_DIR = Path("templates")


def _create_environment(template_dir: Path) -> Environment:
    loader = FileSystemLoader(str(template_dir))
    return Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))


@dataclass
class ReportAsset:
    html_path: Path
    pdf_path: Optional[Path]
    figures: List[Path]
    tables: List[Path]


def render_report(
    template_name: str,
    context: Dict[str, Any],
    *,
    output_html: Path,
    output_pdf: Path,
    template_dir: Path | None = None,
) -> ReportAsset:
    env = _create_environment(template_dir or TEMPLATE_DIR)
    template = env.get_template(template_name)
    rendered_html = template.render(**context)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(rendered_html, encoding="utf-8")

    pdf_path: Optional[Path] = None
    try:
        from weasyprint import HTML  # type: ignore

        HTML(string=rendered_html, base_url=str(output_html.parent)).write_pdf(str(output_pdf))
        pdf_path = output_pdf
    except ImportError:  # pragma: no cover
        LOGGER.warning("WeasyPrint not available; PDF report generation skipped for %s", output_pdf)
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("Failed to generate PDF %s: %s", output_pdf, exc)

    figures = [Path(p) for p in context.get("figures", [])]
    tables = [Path(p) for p in context.get("tables", [])]

    return ReportAsset(html_path=output_html, pdf_path=pdf_path, figures=figures, tables=tables)


__all__ = ["render_report", "ReportAsset"]
