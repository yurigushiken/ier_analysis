"""Integration test for final report compilation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.reporting.compiler import CompiledReport, ReportDescriptor, compile_final_report

pytest.importorskip("jinja2")

WEASYPRINT_AVAILABLE = False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "templates"


def _create_sample_report_html(path: Path, report_id: str, title: str) -> None:
    """Create a sample HTML report file."""
    content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        <section id="{report_id}">
            <h2>Overview</h2>
            <p>This is the content for {title}.</p>
            
            <h3>Methods</h3>
            <p>Methods section for {report_id}.</p>
            
            <h3>Results</h3>
            <table>
                <thead>
                    <tr><th>Condition</th><th>Mean</th><th>p-value</th></tr>
                </thead>
                <tbody>
                    <tr><td>GIVE_WITH</td><td>0.45</td><td>0.001</td></tr>
                    <tr><td>HUG_WITH</td><td>0.23</td><td>0.003</td></tr>
                </tbody>
            </table>
            
            <h3>Interpretation</h3>
            <p>Significant differences were found between conditions.</p>
        </section>
    </body>
    </html>
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_compile_final_report_basic(tmp_path: Path):
    """Test basic compilation of multiple reports into final report."""
    # Setup: Create sample individual reports
    ar1_html = tmp_path / "ar1" / "report.html"
    ar2_html = tmp_path / "ar2" / "report.html"
    ar3_html = tmp_path / "ar3" / "report.html"

    _create_sample_report_html(ar1_html, "ar-1", "AR-1: Gaze Duration Analysis")
    _create_sample_report_html(ar2_html, "ar-2", "AR-2: Gaze Transitions")
    _create_sample_report_html(ar3_html, "ar-3", "AR-3: Social Triplets")

    # Setup: Create report descriptors
    reports = [
        ReportDescriptor(
            report_id="AR-1",
            title="AR-1: Gaze Duration Analysis",
            html_path=ar1_html,
            pdf_path=None,
        ),
        ReportDescriptor(
            report_id="AR-2",
            title="AR-2: Gaze Transitions",
            html_path=ar2_html,
            pdf_path=None,
        ),
        ReportDescriptor(
            report_id="AR-3",
            title="AR-3: Social Triplets",
            html_path=ar3_html,
            pdf_path=None,  # PDF optional
        ),
    ]

    # Setup: Output paths
    output_html = tmp_path / "reports" / "final_report.html"
    output_pdf = None

    # Execute: Compile final report
    result = compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    # Verify: Return value
    assert isinstance(result, CompiledReport)
    assert result.html_path == output_html
    assert result.pdf_path is None
    assert set(result.included_reports) == {"AR-1", "AR-2", "AR-3"}

    # Verify: HTML output exists
    assert output_html.exists()
    html_content = output_html.read_text(encoding="utf-8")

    # Verify: All sections are included
    assert "AR-1: Gaze Duration Analysis" in html_content
    assert "AR-2: Gaze Transitions" in html_content
    assert "AR-3: Social Triplets" in html_content

    # Verify: Content from each report is present
    assert "This is the content for AR-1" in html_content
    assert "This is the content for AR-2" in html_content
    assert "This is the content for AR-3" in html_content

    # Verify: Table of contents present
    assert "Table of Contents" in html_content

    # Verify: TOC links are present
    assert 'href="#ar-1"' in html_content
    assert 'href="#ar-2"' in html_content
    assert 'href="#ar-3"' in html_content

    # Verify: Section IDs are present
    assert 'id="ar-1"' in html_content
    assert 'id="ar-2"' in html_content
    assert 'id="ar-3"' in html_content

    # Verify: PDF output disabled
    assert result.pdf_path is None


def test_compile_final_report_with_extra_context(tmp_path: Path):
    """Test compilation with additional context variables."""
    # Setup: Create one sample report
    ar1_html = tmp_path / "ar1" / "report.html"
    _create_sample_report_html(ar1_html, "ar-1", "AR-1: Gaze Duration")

    reports = [
        ReportDescriptor(
            report_id="AR-1",
            title="AR-1: Gaze Duration",
            html_path=ar1_html,
        )
    ]

    output_html = tmp_path / "final_report.html"
    output_pdf = None

    # Execute: Compile with extra context
    extra_context = {
        "executive_summary": "This report analyzes infant gaze patterns across multiple conditions.",
        "total_participants": 51,
        "analysis_date": "2025-10-27",
    }

    result = compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
        extra_context=extra_context,
    )

    # Verify: Extra context is included in HTML
    html_content = output_html.read_text(encoding="utf-8")
    assert "This report analyzes infant gaze patterns" in html_content


def test_compile_final_report_ordering(tmp_path: Path):
    """Test that reports are compiled in the order provided."""
    # Setup: Create reports in specific order
    ar4_html = tmp_path / "ar4" / "report.html"
    ar2_html = tmp_path / "ar2" / "report.html"
    ar1_html = tmp_path / "ar1" / "report.html"

    _create_sample_report_html(ar4_html, "ar-4", "AR-4: Dwell Times")
    _create_sample_report_html(ar2_html, "ar-2", "AR-2: Transitions")
    _create_sample_report_html(ar1_html, "ar-1", "AR-1: Duration")

    # Setup: Provide in non-sequential order
    reports = [
        ReportDescriptor("AR-4", "AR-4: Dwell Times", ar4_html),
        ReportDescriptor("AR-2", "AR-2: Transitions", ar2_html),
        ReportDescriptor("AR-1", "AR-1: Duration", ar1_html),
    ]

    output_html = tmp_path / "final_report.html"
    output_pdf = tmp_path / "final_report.pdf"

    # Execute: Compile
    compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    # Verify: Order is preserved in HTML
    html_content = output_html.read_text(encoding="utf-8")

    # Find positions of each section
    pos_ar4 = html_content.find('id="ar-4"')
    pos_ar2 = html_content.find('id="ar-2"')
    pos_ar1 = html_content.find('id="ar-1"')

    assert pos_ar4 < pos_ar2 < pos_ar1, "Reports should appear in the order provided"


def test_compile_final_report_missing_html_file(tmp_path: Path):
    """Test compilation fails gracefully when a report HTML is missing."""
    # Setup: Create descriptor for non-existent file
    missing_html = tmp_path / "missing" / "report.html"

    reports = [
        ReportDescriptor(
            report_id="AR-1",
            title="Missing Report",
            html_path=missing_html,
        )
    ]

    output_html = tmp_path / "final_report.html"
    output_pdf = tmp_path / "final_report.pdf"

    # Execute & Verify: Should raise FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Report HTML not found"):
        compile_final_report(
            reports,
            output_html=output_html,
            output_pdf=output_pdf,
            template_dir=TEMPLATE_DIR,
        )


def test_compile_final_report_empty_reports_list(tmp_path: Path):
    """Test compilation fails with empty reports list."""
    output_html = tmp_path / "final_report.html"
    output_pdf = tmp_path / "final_report.pdf"

    # Execute & Verify: Should raise ValueError
    with pytest.raises(ValueError, match="At least one report must be provided"):
        compile_final_report(
            [],
            output_html=output_html,
            output_pdf=output_pdf,
            template_dir=TEMPLATE_DIR,
        )


def test_compile_final_report_single_report(tmp_path: Path):
    """Test compilation works with just one report."""
    # Setup: Create single report
    ar1_html = tmp_path / "ar1" / "report.html"
    _create_sample_report_html(ar1_html, "ar-1", "AR-1: Solo Analysis")

    reports = [
        ReportDescriptor(
            report_id="AR-1",
            title="AR-1: Solo Analysis",
            html_path=ar1_html,
        )
    ]

    output_html = tmp_path / "final_report.html"
    output_pdf = tmp_path / "final_report.pdf"

    # Execute: Compile
    result = compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    # Verify: Compilation succeeds with single report
    assert output_html.exists()
    if WEASYPRINT_AVAILABLE:
        assert output_pdf.exists()
    assert len(result.included_reports) == 1
    assert result.included_reports[0] == "AR-1"


def test_compile_final_report_creates_output_directory(tmp_path: Path):
    """Test that compilation creates output directory if it doesn't exist."""
    # Setup: Create report
    ar1_html = tmp_path / "ar1" / "report.html"
    _create_sample_report_html(ar1_html, "ar-1", "AR-1: Test")

    reports = [ReportDescriptor("AR-1", "AR-1: Test", ar1_html)]

    # Setup: Output in non-existent nested directory
    deep_path = tmp_path / "level1" / "level2" / "level3" / "reports"
    output_html = deep_path / "final_report.html"
    output_pdf = deep_path / "final_report.pdf"

    # Verify: Directory doesn't exist yet
    assert not deep_path.exists()

    # Execute: Compile
    compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    # Verify: Directory was created and files written
    assert deep_path.exists()
    assert output_html.exists()
    if WEASYPRINT_AVAILABLE:
        assert output_pdf.exists()


def test_compile_final_report_all_seven_analyses(tmp_path: Path):
    """Test compilation with all seven AR analyses."""
    # Setup: Create all seven reports
    report_configs = [
        ("AR-1", "AR-1: Gaze Duration Analysis"),
        ("AR-2", "AR-2: Gaze Transitions"),
        ("AR-3", "AR-3: Social Gaze Triplets"),
        ("AR-4", "AR-4: Dwell Time Analysis"),
        ("AR-5", "AR-5: Developmental Trajectory"),
        ("AR-6", "AR-6: Learning & Habituation"),
        ("AR-7", "AR-7: Event Dissociation"),
    ]

    reports = []
    for report_id, title in report_configs:
        html_path = tmp_path / report_id.lower() / "report.html"
        _create_sample_report_html(html_path, report_id.lower(), title)
        reports.append(ReportDescriptor(report_id, title, html_path))

    output_html = tmp_path / "reports" / "final_report.html"
    output_pdf = tmp_path / "reports" / "final_report.pdf"

    # Execute: Compile
    result = compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
        extra_context={
            "executive_summary": "Comprehensive analysis of infant event representation across seven analytical requirements."
        },
    )

    # Verify: All reports included
    assert len(result.included_reports) == 7
    assert set(result.included_reports) == {
        "AR-1",
        "AR-2",
        "AR-3",
        "AR-4",
        "AR-5",
        "AR-6",
        "AR-7",
    }

    # Verify: HTML contains all sections
    html_content = output_html.read_text(encoding="utf-8")
    for report_id, title in report_configs:
        assert title in html_content
        assert f'id="{report_id.lower()}"' in html_content

    # Verify: PDF generated successfully if WeasyPrint available
    if WEASYPRINT_AVAILABLE:
        assert output_pdf.exists()
        pdf_size = output_pdf.stat().st_size
        assert pdf_size > 50000  # Should be reasonably sized with 7 reports


def test_compile_final_report_html_special_characters(tmp_path: Path):
    """Test compilation handles HTML special characters correctly."""
    # Setup: Create report with special characters
    ar1_html = tmp_path / "ar1" / "report.html"
    content = """
    <html><body>
        <h1>AR-1: Test &amp; Analysis</h1>
        <p>Testing <strong>bold</strong> and <em>italic</em> text.</p>
        <p>Mathematical notation: α = 0.05, β > 0.1</p>
        <code>function_name(arg1, arg2)</code>
    </body></html>
    """
    ar1_html.parent.mkdir(parents=True, exist_ok=True)
    ar1_html.write_text(content, encoding="utf-8")

    reports = [ReportDescriptor("AR-1", "AR-1: Test & Analysis", ar1_html)]

    output_html = tmp_path / "final_report.html"
    output_pdf = tmp_path / "final_report.pdf"

    # Execute: Compile
    compile_final_report(
        reports,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    # Verify: Special characters preserved in HTML
    html_content = output_html.read_text(encoding="utf-8")
    assert "&amp;" in html_content
    assert "<strong>bold</strong>" in html_content
    assert "α = 0.05" in html_content

    # Verify: PDF renders without errors if WeasyPrint available
    if WEASYPRINT_AVAILABLE:
        assert output_pdf.exists()
