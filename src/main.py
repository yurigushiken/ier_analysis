"""Main entrypoint for the infant event representation analysis pipeline."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Iterable, List

from src.preprocessing.master_log_generator import generate_master_log
from src.reporting.compiler import CompiledReport, ReportDescriptor, compile_final_report
from src.utils.config import load_config
from src.utils.logging_config import setup_logging

ANALYSIS_SPECS: Iterable[tuple[str, str, str, str]] = (
    ("AR-1", "analysis.ar1_gaze_duration", "run", "Gaze Duration Analysis"),
    ("AR-2", "analysis.ar2_transitions", "run", "Gaze Transition Analysis"),
    ("AR-3", "analysis.ar3_social_triplets", "run", "Social Gaze Triplet Analysis"),
    ("AR-4", "analysis.ar4_dwell_times", "run", "Dwell Time Analysis"),
    ("AR-5", "analysis.ar5_development", "run", "Developmental Trajectory Analysis"),
    ("AR-6", "analysis.ar6_learning", "run", "Learning Across Trials"),
    ("AR-7", "analysis.ar7_dissociation", "run", "SHOW Dissociation Analysis"),
)


def run_preprocessing(config: dict[str, Any], logger) -> None:
    contract_path = Path("specs/001-infant-event-analysis/contracts/raw_data_schema.json")
    processed_dir = Path(config["paths"]["processed_data"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_child_dir = Path(config["paths"]["raw_data_child"])
    raw_adult_dir = Path(config["paths"]["raw_data_adult"])

    try:
        if raw_child_dir.exists():
            logger.info("Generating child gaze events log from %s", raw_child_dir)
            generate_master_log(
                raw_directories=[raw_child_dir],
                contract_path=contract_path,
                output_path=processed_dir / "gaze_events_child.csv",
                config=config,
            )
        else:
            logger.warning("Child data directory not found: %s", raw_child_dir)

        if raw_adult_dir.exists():
            logger.info("Generating adult gaze events log from %s", raw_adult_dir)
            generate_master_log(
                raw_directories=[raw_adult_dir],
                contract_path=contract_path,
                output_path=processed_dir / "gaze_events_adult.csv",
                config=config,
            )
        else:
            logger.info("Adult data directory not found (optional): %s", raw_adult_dir)
    except Exception:  # pragma: no cover - logged upstream
        logger.exception("Preprocessing failed")
        raise


def _normalize_report(report_id: str, result: Any, title: str) -> ReportDescriptor | None:
    if result is None:
        return None
    if isinstance(result, ReportDescriptor):
        return result
    if isinstance(result, dict):
        html_path = Path(result.get("html_path", ""))
        pdf_path_value = result.get("pdf_path")
        pdf_path = Path(pdf_path_value) if pdf_path_value else None
        return ReportDescriptor(
            report_id=result.get("report_id", report_id),
            title=result.get("title", title),
            html_path=html_path,
            pdf_path=pdf_path,
        )
    if isinstance(result, tuple) and len(result) >= 2:
        html_path = Path(result[0])
        pdf_path = Path(result[1]) if result[1] else None
        return ReportDescriptor(report_id=report_id, title=title, html_path=html_path, pdf_path=pdf_path)
    return None


def run_analysis_modules(config: dict[str, Any], logger) -> List[ReportDescriptor]:
    descriptors: List[ReportDescriptor] = []

    for report_id, module_path, entry_point, title in ANALYSIS_SPECS:
        try:
            module = importlib.import_module(f"src.{module_path}")
        except ModuleNotFoundError:
            logger.info("Skipping %s (%s) - module not yet implemented", report_id, module_path)
            continue

        if not hasattr(module, entry_point):
            logger.warning("Module %s missing entry point '%s'", module_path, entry_point)
            continue

        logger.info("Running analysis %s via %s.%s", report_id, module_path, entry_point)
        entry = getattr(module, entry_point)
        try:
            result = entry(config=config)
        except Exception:  # pragma: no cover - downstream specifics
            logger.exception("Analysis %s failed", report_id)
            continue

        descriptor = _normalize_report(report_id, result, title)
        if descriptor:
            descriptors.append(descriptor)
        else:
            logger.warning("Analysis %s did not return report metadata; skipping compilation entry", report_id)

    return descriptors


def compile_reports(descriptors: List[ReportDescriptor], config: dict[str, Any], logger) -> CompiledReport | None:
    if not descriptors:
        logger.info("No analysis reports ready; skipping final compilation")
        return None

    reports_dir = Path(config["paths"]["final_reports"])
    reports_dir.mkdir(parents=True, exist_ok=True)

    html_output = reports_dir / "final_report.html"
    pdf_output = reports_dir / "final_report.pdf"

    logger.info("Compiling final report with %d sections", len(descriptors))
    try:
        return compile_final_report(
            descriptors,
            output_html=html_output,
            output_pdf=pdf_output,
        )
    except RuntimeError as exc:
        logger.warning("Final report PDF generation skipped: %s", exc)
        return CompiledReport(
            html_path=html_output, pdf_path=pdf_output, included_reports=[d.report_id for d in descriptors]
        )


def main() -> None:
    config = load_config()
    logger = setup_logging(config)

    logger.info("Starting Infant Event Representation Analysis pipeline")

    run_preprocessing(config, logger)
    descriptors = run_analysis_modules(config, logger)
    compiled = compile_reports(descriptors, config, logger)

    if compiled:
        logger.info("Final report generated at %s", compiled.html_path)

    logger.info("Pipeline completed")


if __name__ == "__main__":
    main()
