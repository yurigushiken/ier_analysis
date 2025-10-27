"""AR-2 Gaze Transition analysis module."""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pandas as pd

from src.reporting import visualizations
from src.reporting.report_generator import render_report

LOGGER = logging.getLogger("ier.analysis.ar2")

ONSCREEN_EXCLUDE: Iterable[str] = ("off_screen",)
RESULT_DIR = Path("results/AR2_Gaze_Transitions")


def _load_gaze_events(config: Dict[str, Any]) -> pd.DataFrame:
    processed_dir = Path(config["paths"]["processed_data"])
    child_path = processed_dir / "gaze_events_child.csv"
    default_path = processed_dir / "gaze_events.csv"

    if child_path.exists():
        path = child_path
    elif default_path.exists():
        path = default_path
    else:
        raise FileNotFoundError("No gaze events file found for AR-2 analysis")

    LOGGER.info("Loading gaze events from %s", path)
    return pd.read_csv(path)


def _filter_valid_gaze_events(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["aoi_category"].isin(ONSCREEN_EXCLUDE)].copy()


def _compute_transitions(df: pd.DataFrame) -> pd.DataFrame:
    df_sorted = df.sort_values(["participant_id", "trial_number", "gaze_onset_time"])
    transitions = []

    for (participant, trial), group in df_sorted.groupby(["participant_id", "trial_number"], sort=False):
        prev_row = None
        for _, row in group.iterrows():
            if prev_row is not None and prev_row["aoi_category"] != row["aoi_category"]:
                transitions.append(
                    {
                        "participant_id": participant,
                        "trial_number": trial,
                        "condition": row["condition_name"],
                        "age_group": row.get("age_group", "unknown"),
                        "from_aoi": prev_row["aoi_category"],
                        "to_aoi": row["aoi_category"],
                    }
                )
            prev_row = row

    return pd.DataFrame(transitions)


def _build_probability_tables(transitions: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    overall_counts = (
        transitions.groupby(["from_aoi", "to_aoi"], as_index=False).size().rename(columns={"size": "count"})
    )
    overall_pivot = overall_counts.pivot_table(
        index="from_aoi", columns="to_aoi", values="count", aggfunc="sum", fill_value=0
    )
    overall_probs = overall_pivot.div(overall_pivot.sum(axis=1), axis=0).fillna(0)

    by_condition: Dict[str, pd.DataFrame] = {}
    for condition, subset in transitions.groupby("condition"):
        counts = subset.groupby(["from_aoi", "to_aoi"], as_index=False).size().rename(columns={"size": "count"})
        pivot = counts.pivot_table(index="from_aoi", columns="to_aoi", values="count", aggfunc="sum", fill_value=0)
        probs = pivot.div(pivot.sum(axis=1), axis=0).fillna(0)
        by_condition[condition] = probs

    return overall_probs, by_condition


def _save_tables(overall: pd.DataFrame, by_condition: Dict[str, pd.DataFrame], output_dir: Path) -> Dict[str, Any]:
    tables_context = []

    overall_csv = output_dir / "transition_matrix_overall.csv"
    overall.to_csv(overall_csv)
    tables_context.append(
        {
            "title": "Overall Transition Probabilities",
            "html": overall.to_html(classes="table table-striped", float_format="{:.3f}".format),
        }
    )

    for condition, matrix in by_condition.items():
        file_path = output_dir / f"transition_matrix_{condition}.csv"
        matrix.to_csv(file_path)
        tables_context.append(
            {
                "title": f"Transition Probabilities – {condition}",
                "html": matrix.to_html(classes="table table-striped", float_format="{:.3f}".format),
            }
        )

    return {
        "tables": tables_context,
        "csv_paths": [overall_csv] + [output_dir / f"transition_matrix_{c}.csv" for c in by_condition.keys()],
    }


def _generate_graphs(overall: pd.DataFrame, output_dir: Path) -> Dict[str, Any]:
    transitions_mapping: Dict[Tuple[str, str], float] = {}
    node_durations: Dict[str, float] = defaultdict(float)

    for from_aoi in overall.index:
        for to_aoi in overall.columns:
            weight = float(overall.loc[from_aoi, to_aoi])
            if weight > 0:
                transitions_mapping[(from_aoi, to_aoi)] = weight
        node_durations[from_aoi] += overall.loc[from_aoi].sum()

    figure_path = output_dir / "transition_graph_overall.png"
    visualizations.directed_graph(
        transitions_mapping,
        node_durations,
        title="Gaze Transition Graph (Overall)",
        output_path=figure_path,
    )

    return {"graph_figures": [{"path": str(figure_path), "caption": "Overall transition probabilities"}]}


def _render_report(context: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    html_path = output_dir / "report.html"
    pdf_path = output_dir / "report.pdf"
    render_report(
        template_name="ar2_template.html",
        context=context,
        output_html=html_path,
        output_pdf=pdf_path,
    )
    return {
        "report_id": "AR-2",
        "title": "Gaze Transition Analysis",
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
    }


def run(*, config: Dict[str, Any]) -> Dict[str, Any]:
    LOGGER.info("Starting AR-2 gaze transition analysis")

    try:
        df = _load_gaze_events(config)
    except FileNotFoundError as exc:
        LOGGER.warning("Skipping AR-2 analysis: %s", exc)
        return {
            "report_id": "AR-2",
            "title": "Gaze Transition Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    if df.empty:
        LOGGER.warning("Gaze events file is empty; skipping AR-2 analysis")
        return {
            "report_id": "AR-2",
            "title": "Gaze Transition Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    valid_df = _filter_valid_gaze_events(df)
    transitions = _compute_transitions(valid_df)
    if transitions.empty:
        LOGGER.warning("No transitions detected; skipping AR-2 report generation")
        return {
            "report_id": "AR-2",
            "title": "Gaze Transition Analysis",
            "html_path": "",
            "pdf_path": "",
        }

    overall_probs, condition_probs = _build_probability_tables(transitions)

    output_dir = Path(config["paths"]["results"]) / "AR2_Gaze_Transitions"
    output_dir.mkdir(parents=True, exist_ok=True)

    tables_context = _save_tables(overall_probs, condition_probs, output_dir)
    figures_context = _generate_graphs(overall_probs, output_dir)

    context = {
        "summary_text": "Transition probabilities between AOIs aggregated across conditions.",
        "methods_text": "Transitions derived from consecutive gaze events within trials; probabilities computed per source AOI.",
        "transition_tables": tables_context["tables"],
        "graph_figures": figures_context["graph_figures"],
        "statistics_table": "<p>Statistical tests not yet implemented.</p>",
        "interpretation_text": "Transitions highlight common gaze paths between faces and objects.",
        "conditions": sorted(condition_probs.keys()),
        "age_groups": sorted(transitions["age_group"].dropna().unique()),
    }

    metadata = _render_report(context, output_dir)

    LOGGER.info("AR-2 analysis completed; report generated at %s", metadata["html_path"])
    return metadata
