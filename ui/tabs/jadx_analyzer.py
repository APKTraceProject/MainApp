"""
JADX Analyzer results tab.

This tab renders the structured JSON produced by the LLM after it analyzes
the Java/Kotlin source code extracted by the JADX Analyzer tool.

The tab never assumes a fixed number of findings and never interprets
Markdown: the JSON document described in `jadx_analysis.example.json`
is the only contract between the LLM and this UI. Every value is passed
through `normalize_jadx_report()` first, so missing or malformed data is
rendered as "UNKNOWN" instead of raising an exception.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT_BORDER,
    COLOR_ACCENT_SURFACE,
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)

UNKNOWN = "UNKNOWN"

# Colors used for the importance badge. MEDIUM has no matching constant in
# ui.py, so a local color is defined here rather than adding a new shared
# constant.
COLOR_WARNING = "#E0A73B"

IMPORTANCE_BADGE_COLORS = {
    "HIGH": COLOR_DANGER,
    "MEDIUM": COLOR_WARNING,
    "LOW": COLOR_SUCCESS,
    "UNKNOWN": COLOR_SURFACE_HOVER,
}


# ---------------------------------------------------------------------------
# Normalization / validation layer
# ---------------------------------------------------------------------------

def _default_section() -> Dict[str, Any]:
    """Placeholder section shown before any scan has produced real data."""
    return {
        "title": UNKNOWN,
        "code_lines": {"start": UNKNOWN, "end": UNKNOWN},
        "source_files": [UNKNOWN],
        "description": UNKNOWN,
        "importance": UNKNOWN,
    }


def _default_assessment() -> Dict[str, Any]:
    return {
        "summary": UNKNOWN,
        "recommendation": UNKNOWN,
        "suspicion": UNKNOWN,
    }


def default_jadx_report() -> Dict[str, Any]:
    """The empty-state report: exactly one UNKNOWN section, nothing else."""
    return {
        "analysis_type": "jadx_java_kotlin",
        "title": "JADX Analyzer",
        "overview": UNKNOWN,
        "sections": [_default_section()],
        "overall_assessment": _default_assessment(),
    }


def _normalize_section(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        return _default_section()

    title = raw.get("title") or UNKNOWN

    code_lines_raw = raw.get("code_lines")
    if isinstance(code_lines_raw, dict):
        start = code_lines_raw.get("start")
        end = code_lines_raw.get("end")
        start_str = str(start) if start is not None and start != "" else UNKNOWN
        end_str = str(end) if end is not None and end != "" else UNKNOWN
    else:
        start_str, end_str = UNKNOWN, UNKNOWN

    source_files_raw = raw.get("source_files")
    source_files: List[str] = []
    if isinstance(source_files_raw, list):
        source_files = [str(f) for f in source_files_raw if f]
    if not source_files:
        source_files = [UNKNOWN]

    description = raw.get("description") or UNKNOWN

    importance_raw = raw.get("importance")
    if isinstance(importance_raw, str) and importance_raw.upper() in IMPORTANCE_BADGE_COLORS:
        importance = importance_raw.upper()
    else:
        importance = UNKNOWN

    return {
        "title": str(title),
        "code_lines": {"start": start_str, "end": end_str},
        "source_files": source_files,
        "description": str(description),
        "importance": importance,
    }


def _normalize_assessment(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    return {
        "summary": raw.get("summary") or UNKNOWN,
        "recommendation": raw.get("recommendation") or UNKNOWN,
        "suspicion": raw.get("suspicion") or UNKNOWN,
    }


def normalize_jadx_report(report: Any) -> Dict[str, Any]:
    """Turn any raw LLM JSON dict into a UI-safe, fully-populated dict.

    This function never raises: unexpected input results in a safe
    UNKNOWN-filled structure instead of a crash.
    """
    if not isinstance(report, dict):
        return default_jadx_report()

    raw_sections = report.get("sections")
    if isinstance(raw_sections, list) and len(raw_sections) > 0:
        sections = [_normalize_section(s) for s in raw_sections]
    else:
        sections = [_default_section()]

    return {
        "analysis_type": report.get("analysis_type") or "jadx_java_kotlin",
        "title": report.get("title") or "JADX Analyzer",
        "overview": report.get("overview") or UNKNOWN,
        "sections": sections,
        "overall_assessment": _normalize_assessment(report.get("overall_assessment")),
    }


def load_jadx_report_from_file(path: str) -> Dict[str, Any]:
    """Optional helper: read a JADX/LLM analysis JSON file from disk.

    Returns a normalized report. If the file is missing or contains
    invalid JSON, the default UNKNOWN report is returned instead of
    raising, so callers can always safely pass the result straight to
    `update_jadx_analyzer_page`.
    """
    try:
        raw_text = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except (OSError, ValueError):
        return default_jadx_report()
    return normalize_jadx_report(data)


# ---------------------------------------------------------------------------
# Page construction
# ---------------------------------------------------------------------------

def build_jadx_analyzer_page(app):
    """Build the JADX Analyzer tab's full layout, pre-filled with the
    default UNKNOWN section so the page is never empty."""
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(page, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
    ctk.CTkLabel(
        header,
        text="☕ JADX Analyzer",
        font=("Arial", 24, "bold"),
        text_color=COLOR_ACCENT_TEXT,
    ).pack(side="left")
    ctk.CTkButton(
        header,
        text="← Back to Dashboard",
        width=150,
        height=35,
        fg_color=COLOR_SURFACE_HOVER,
        hover_color="#3D3E4A",
        command=lambda: app.show_page("Dashboard"),
    ).pack(side="right")

    # Scrollable Body Container
    body = ctk.CTkScrollableFrame(page, fg_color="transparent")
    body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

    app.jadx_widgets = {}

    # 1. Overview Section (static widgets, text is updated in place)
    overview_card = ctk.CTkFrame(
        body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER
    )
    overview_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(
        overview_card, text="ANALYSIS OVERVIEW", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED
    ).pack(anchor="w", padx=20, pady=(15, 5))

    overview_title_lbl = ctk.CTkLabel(
        overview_card, text="JADX Analyzer", font=("Arial", 16, "bold"), text_color=COLOR_TEXT, anchor="w", justify="left"
    )
    overview_title_lbl.pack(anchor="w", padx=20, pady=(0, 4), fill="x")

    overview_text_lbl = ctk.CTkLabel(
        overview_card,
        text=UNKNOWN,
        font=("Arial", 13),
        text_color=COLOR_TEXT_MUTED,
        anchor="w",
        justify="left",
        wraplength=980,
    )
    overview_text_lbl.pack(anchor="w", padx=20, pady=(0, 15), fill="x")

    app.jadx_widgets["overview_title"] = overview_title_lbl
    app.jadx_widgets["overview_text"] = overview_text_lbl

    # 2. Dynamic findings container (rebuilt on every update)
    sections_container = ctk.CTkFrame(body, fg_color="transparent")
    sections_container.pack(fill="x")

    app.jadx_widgets["sections_container"] = sections_container
    app.jadx_widgets["section_frames"] = []

    # 3. Overall Assessment Section (static widgets, text is updated in place)
    assessment_card = ctk.CTkFrame(
        body, fg_color=COLOR_ACCENT_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_ACCENT_BORDER
    )
    assessment_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(
        assessment_card, text="OVERALL ASSESSMENT", font=("Arial", 14, "bold"), text_color=COLOR_ACCENT_TEXT
    ).pack(anchor="w", padx=20, pady=(15, 10))

    assessment_widgets = {}
    for key, label in (
        ("summary", "SUMMARY"),
        ("recommendation", "RECOMMENDATION"),
        ("suspicion", "SUSPICION"),
    ):
        ctk.CTkLabel(
            assessment_card, text=label, font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=20, pady=(0, 4))

        value_lbl = ctk.CTkLabel(
            assessment_card,
            text=UNKNOWN,
            font=("Arial", 13),
            text_color=COLOR_TEXT,
            anchor="w",
            justify="left",
            wraplength=980,
        )
        is_last = key == "suspicion"
        value_lbl.pack(anchor="w", padx=20, pady=(0, 15 if is_last else 12), fill="x")
        assessment_widgets[key] = value_lbl

    app.jadx_widgets["assessment"] = assessment_widgets
    app.jadx_widgets["current_report"] = None

    # Populate the page with the empty-state (single UNKNOWN section) report.
    _render_report(app, default_jadx_report())

    return page


# ---------------------------------------------------------------------------
# Dynamic section rendering
# ---------------------------------------------------------------------------

def _clear_sections(app) -> None:
    for frame in app.jadx_widgets.get("section_frames", []):
        frame.destroy()
    app.jadx_widgets["section_frames"] = []


def _handle_remove_section(app, index: int) -> None:
    """Remove one finding section and re-render from the remaining data.

    If this was the last section, normalization automatically restores a
    single UNKNOWN placeholder section, so the page can never end up empty.
    """
    report = app.jadx_widgets.get("current_report") or default_jadx_report()
    sections = list(report.get("sections", []))
    if 0 <= index < len(sections):
        del sections[index]
    report = dict(report)
    report["sections"] = sections
    update_jadx_analyzer_page(app, report)


def _build_finding_card(app, container, index: int, section: Dict[str, Any]) -> None:
    """Create a single 'SECURITY FINDING' card from one normalized section."""
    card = ctk.CTkFrame(
        container, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER
    )
    card.pack(fill="x", pady=(0, 15), padx=5)
    app.jadx_widgets["section_frames"].append(card)

    # Header row: "SECURITY FINDING N" + importance badge
    header_row = ctk.CTkFrame(card, fg_color="transparent")
    header_row.pack(fill="x", padx=20, pady=(15, 5))

    ctk.CTkLabel(
        header_row,
        text=f"SECURITY FINDING {index + 1:02d}",
        font=("Arial", 12, "bold"),
        text_color=COLOR_TEXT_MUTED,
    ).pack(side="left")

    importance = section["importance"]
    badge_color = IMPORTANCE_BADGE_COLORS.get(importance, COLOR_SURFACE_HOVER)
    ctk.CTkLabel(
        header_row,
        text=f" {importance} ",
        font=("Arial", 11, "bold"),
        fg_color=badge_color,
        corner_radius=4,
    ).pack(side="right")

    # Title
    ctk.CTkLabel(
        card,
        text=section["title"],
        font=("Arial", 16, "bold"),
        text_color=COLOR_TEXT,
        anchor="w",
        justify="left",
        wraplength=940,
    ).pack(anchor="w", padx=20, pady=(0, 12), fill="x")

    # Start / End line grid
    lines_grid = ctk.CTkFrame(card, fg_color="transparent")
    lines_grid.pack(fill="x", padx=20, pady=(0, 12))

    ctk.CTkLabel(lines_grid, text="START LINE", font=("Arial", 11, "bold"), text_color=COLOR_TEXT_MUTED).grid(
        row=0, column=0, sticky="w", padx=(0, 60)
    )
    ctk.CTkLabel(lines_grid, text="END LINE", font=("Arial", 11, "bold"), text_color=COLOR_TEXT_MUTED).grid(
        row=0, column=1, sticky="w"
    )
    ctk.CTkLabel(
        lines_grid, text=str(section["code_lines"]["start"]), font=("Arial", 14), text_color=COLOR_ACCENT_TEXT
    ).grid(row=1, column=0, sticky="w", padx=(0, 60), pady=(2, 0))
    ctk.CTkLabel(
        lines_grid, text=str(section["code_lines"]["end"]), font=("Arial", 14), text_color=COLOR_ACCENT_TEXT
    ).grid(row=1, column=1, sticky="w", pady=(2, 0))

    # Source files / importance grid
    info_grid = ctk.CTkFrame(card, fg_color="transparent")
    info_grid.pack(fill="x", padx=20, pady=(0, 12))
    info_grid.grid_columnconfigure(0, weight=1)
    info_grid.grid_columnconfigure(1, weight=0)

    files_col = ctk.CTkFrame(info_grid, fg_color="transparent")
    files_col.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(files_col, text="SOURCE FILES", font=("Arial", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(
        anchor="w"
    )
    ctk.CTkLabel(
        files_col,
        text="\n".join(section["source_files"]),
        font=("Consolas", 12),
        text_color=COLOR_TEXT,
        anchor="w",
        justify="left",
    ).pack(anchor="w", pady=(2, 0))

    importance_col = ctk.CTkFrame(info_grid, fg_color="transparent")
    importance_col.grid(row=0, column=1, sticky="e", padx=(30, 0))
    ctk.CTkLabel(importance_col, text="IMPORTANCE", font=("Arial", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(
        anchor="w"
    )
    ctk.CTkLabel(importance_col, text=importance, font=("Arial", 13, "bold"), text_color=badge_color).pack(
        anchor="w", pady=(2, 0)
    )

    # Description
    ctk.CTkLabel(card, text="DESCRIPTION", font=("Arial", 11, "bold"), text_color=COLOR_TEXT_MUTED).pack(
        anchor="w", padx=20
    )
    ctk.CTkLabel(
        card,
        text=section["description"],
        font=("Arial", 13),
        text_color=COLOR_TEXT,
        anchor="w",
        justify="left",
        wraplength=940,
    ).pack(anchor="w", padx=20, pady=(2, 10), fill="x")

    # Remove control
    footer_row = ctk.CTkFrame(card, fg_color="transparent")
    footer_row.pack(fill="x", padx=20, pady=(0, 15))
    ctk.CTkButton(
        footer_row,
        text="Remove Section",
        width=140,
        height=30,
        fg_color=COLOR_SURFACE_HOVER,
        hover_color=COLOR_DANGER,
        command=lambda idx=index: _handle_remove_section(app, idx),
    ).pack(side="right")


def _render_report(app, normalized_report: Dict[str, Any]) -> None:
    """Render a fully normalized report into the already-built widgets."""
    app.jadx_widgets["current_report"] = normalized_report

    # Overview
    app.jadx_widgets["overview_title"].configure(text=normalized_report["title"])
    app.jadx_widgets["overview_text"].configure(text=normalized_report["overview"])

    # Findings (fully rebuilt: count is driven entirely by the JSON)
    _clear_sections(app)
    sections_container = app.jadx_widgets["sections_container"]
    for index, section in enumerate(normalized_report["sections"]):
        _build_finding_card(app, sections_container, index, section)

    # Overall assessment
    assessment = normalized_report["overall_assessment"]
    app.jadx_widgets["assessment"]["summary"].configure(text=assessment["summary"])
    app.jadx_widgets["assessment"]["recommendation"].configure(text=assessment["recommendation"])
    app.jadx_widgets["assessment"]["suspicion"].configure(text=assessment["suspicion"])


# ---------------------------------------------------------------------------
# Public update API
# ---------------------------------------------------------------------------

def update_jadx_analyzer_page(app, report: Optional[Dict[str, Any]]) -> None:
    """Rebuild the already-built JADX Analyzer page from an analysis dict.

    `report` is expected to follow the structure documented in
    `jadx_analysis.example.json`. Any missing or malformed field is safely
    replaced with UNKNOWN by `normalize_jadx_report`, so this function never
    raises because of incomplete LLM output.
    """
    if not getattr(app, "jadx_widgets", None):
        return
    normalized = normalize_jadx_report(report)
    _render_report(app, normalized)


def add_jadx_section(app, section_data: Dict[str, Any]) -> None:
    """Programmatically append one finding section and re-render."""
    report = app.jadx_widgets.get("current_report") or default_jadx_report()
    sections = list(report.get("sections", []))
    sections.append(section_data)
    report = dict(report)
    report["sections"] = sections
    update_jadx_analyzer_page(app, report)


def remove_jadx_section(app, index: int) -> None:
    """Programmatically remove one finding section by index and re-render."""
    _handle_remove_section(app, index)