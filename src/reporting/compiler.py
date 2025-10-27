"""Final report compilation utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    from weasyprint import HTML
except ImportError:  # pragma: no cover - platform dependent
    HTML = None

LOGGER = logging.getLogger("ier.reporting.compiler")

TEMPLATE_DIR = Path("templates")
DEFAULT_TEMPLATE = "final_report_template.html"


def _create_environment(template_dir: Path) -> Environment:
    loader = FileSystemLoader(str(template_dir))
    return Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))


@dataclass
class ReportDescriptor:
    report_id: str
    title: str
    html_path: Path
    pdf_path: Optional[Path] = None


@dataclass
class CompiledReport:
    html_path: Path
    pdf_path: Path
    included_reports: List[str]


def _load_html(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Report HTML not found: {path}")
    return path.read_text(encoding="utf-8")


def compile_final_report(
    reports: Sequence[ReportDescriptor],
    *,
    output_html: Path,
    output_pdf: Path,
    template_name: str = DEFAULT_TEMPLATE,
    template_dir: Path | None = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> CompiledReport:
    if not reports:
        raise ValueError("At least one report must be provided for compilation")

    env = _create_environment(template_dir or TEMPLATE_DIR)
    template = env.get_template(template_name)

    sections: List[Dict[str, Any]] = []
    for descriptor in reports:
        html_content = _load_html(descriptor.html_path)
        sections.append(
            {
                "report_id": descriptor.report_id,
                "title": descriptor.title,
                "content": html_content,
                "html_path": descriptor.html_path,
                "pdf_path": descriptor.pdf_path,
            }
        )

    context: Dict[str, Any] = {
        "sections": sections,
        "included_reports": [descriptor.report_id for descriptor in reports],
    }
    if extra_context:
        context.update(extra_context)

    rendered_html = template.render(**context)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(rendered_html, encoding="utf-8")

    pdf_path = output_pdf
    if HTML is None:
        LOGGER.warning("WeasyPrint not available; PDF report generation skipped for %s", output_pdf)
    else:
        try:
            HTML(string=rendered_html, base_url=str(output_html.parent)).write_pdf(str(output_pdf))
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Failed to generate PDF %s: %s", output_pdf, exc)
            pdf_path = output_html.parent / "report.pdf"  # Placeholder path

    return CompiledReport(
        html_path=output_html,
        pdf_path=pdf_path,
        included_reports=[descriptor.report_id for descriptor in reports],
    )


__all__ = ["ReportDescriptor", "CompiledReport", "compile_final_report"]
