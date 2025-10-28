from __future__ import annotations

import pytest
from pathlib import Path

from src.reporting.report_generator import HTML, render_report

pytest.importorskip("jinja2")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "templates"


@pytest.mark.skipif(HTML is None, reason="WeasyPrint not installed")
def test_render_report(tmp_path: Path):
    output_html = tmp_path / "report.html"
    output_pdf = tmp_path / "report.pdf"
    context = {
        "report_title": "Test Report",
        "total_participants": 10,
        "participants_included": 8,
        "participants_excluded": 2,
        "total_gaze_fixations": 100,
        "conditions": ["GIVE", "HUG"],
        "exclusions": [],
        "min_gaze_frames": 3,
        "alpha": 0.05,
        "descriptive_stats_table": "<table><tr><td>Example</td></tr></table>",
        "figure_duration_by_condition": "figure1.png",
        "error_bar_type": "SEM",
        "significance_marker": "",
        "ttest_p": 0.04,
        "ttest_df": 20,
        "ttest_statistic": 2.5,
        "cohens_d": 0.5,
        "ci_lower": 0.1,
        "ci_upper": 0.9,
        "significant_condition": "GIVE",
        "other_condition": "HUG",
        "p_comparison": "<",
        "figure_duration_by_age": "figure2.png",
        "anova_results_table": "<table><tr><td>ANOVA</td></tr></table>",
        "anova_p": 0.07,
        "anova_df1": 2,
        "anova_df2": 18,
        "anova_f_statistic": 3.2,
        "eta_squared": 0.12,
        "assumptions_violated": False,
        "assumptions_violated_message": "",
        "interpretation_text": "Interpretation",
        "comparison_to_gordon": "Comparison",
        "limitations": "Limitations",
        "participant_summary_table": "<table></table>",
        "assumptions_table": "<table></table>",
        "logs_summary": "Warning: insufficient sample size",
        "figures": [],
        "tables": [],
    }

    asset = render_report(
        template_name="ar1_template.html",
        context=context,
        output_html=output_html,
        output_pdf=output_pdf,
        template_dir=TEMPLATE_DIR,
    )

    assert output_html.exists()
    assert output_pdf.exists()
    assert asset.html_path == output_html
    assert asset.pdf_path == output_pdf

    html_content = output_html.read_text(encoding="utf-8")
    assert "Warning: insufficient sample size" in html_content
