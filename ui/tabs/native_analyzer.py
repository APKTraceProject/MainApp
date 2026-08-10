"""
Native Analyzer results tab.

Renders the structured JSON report produced by Native-Analyzer (Ghidra / Radare2).
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT_BORDER,
    COLOR_ACCENT_SURFACE,
    COLOR_ACCENT_TEXT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)

UNKNOWN = "N/A"

COLOR_CRITICAL = "#800020"  # Dark Red / Burgundy
COLOR_HIGH = "#E53935"      # Bright Red
COLOR_MEDIUM = "#FF8C00"    # Orange
COLOR_LOW = "#009688"       # Green / Teal
COLOR_INFO = COLOR_SURFACE_HOVER
COLOR_UNKNOWN = COLOR_SURFACE_HOVER
COLOR_WARNING = COLOR_MEDIUM

SEVERITY_BADGE_COLORS = {
    "CRITICAL": COLOR_CRITICAL,
    "HIGH": COLOR_HIGH,
    "MEDIUM": COLOR_MEDIUM,
    "LOW": COLOR_LOW,
    "INFO": COLOR_INFO,
    "UNKNOWN": COLOR_UNKNOWN,
}


def default_native_report() -> Dict[str, Any]:
    return {
        "summary": {
            "analysis_engine": "ghidra",
            "total_targets_scanned": 0,
            "total_findings": 0,
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "by_confidence": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "by_category": {},
            "abi_resolution": {
                "primary_abi": UNKNOWN,
                "associated_abis": [],
                "deduplication_enabled": True,
            },
        },
        "targets": [],
    }


def normalize_native_report(report: Any) -> Dict[str, Any]:
    """Normalize and merge raw scanner data and AI analysis into a safe UI structure.

    Extracts technical metrics from raw_data/report.json and text summaries from ai_native_analysis.json,
    matching findings via finding_id.
    """
    ai_report: Dict[str, Any] = {}
    raw_report: Dict[str, Any] = {}

    # 1. Resolve input object if passed directly from run_native_analysis dict
    if isinstance(report, dict):
        if "ai_report" in report or "raw_report" in report:
            ai_report = report.get("ai_report") if isinstance(report.get("ai_report"), dict) else {}
            raw_report = report.get("raw_report") if isinstance(report.get("raw_report"), dict) else {}
        elif "executive_overview" in report or "targets" in report:
            ai_report = report
        elif "summary" in report:
            raw_report = report

    # 2. Disk Fallback: Try loading from native_analysis_output directory or project root
    base_dir = Path(__file__).resolve().parent.parent.parent
    if not ai_report:
        for possible_path in [
            base_dir / "output" / "native_analysis_output" / "ai_native_analysis.json",
            base_dir / "Native-analysis.example.json",
        ]:
            if possible_path.exists():
                try:
                    with open(possible_path, "r", encoding="utf-8") as f:
                        ai_report = json.load(f)
                        break
                except Exception:
                    pass

    if not raw_report:
        possible_raw = base_dir / "output" / "native_analysis_output" / "raw_data" / "report.json"
        if possible_raw.exists():
            try:
                with open(possible_raw, "r", encoding="utf-8") as f:
                    raw_report = json.load(f)
            except Exception:
                pass

    if not ai_report and not raw_report:
        return default_native_report()

    # 3. Index AI Report data by finding_id, function_name, and file_name
    ai_findings_by_id: Dict[str, Dict[str, Any]] = {}
    ai_functions_by_name: Dict[str, Dict[str, Any]] = {}
    ai_targets_by_file: Dict[str, Dict[str, Any]] = {}

    for t in ai_report.get("targets", []):
        if not isinstance(t, dict):
            continue
        file_name = t.get("file_name", "libnative.so")
        ai_targets_by_file[file_name] = t

        for fn in t.get("functions", []):
            if not isinstance(fn, dict):
                continue
            fn_name = fn.get("function_name", UNKNOWN)
            ai_functions_by_name[fn_name] = fn

            for f in fn.get("findings", []):
                if isinstance(f, dict) and "finding_id" in f:
                    ai_findings_by_id[f["finding_id"]] = f

    # 4. Extract Executive Overview
    exec_overview = str(
        ai_report.get("executive_overview")
        or ai_report.get("overview")
        or raw_report.get("overall_assessment", {}).get("summary")
        or ""
    )

    # 5. Extract Raw Summary & Metrics
    raw_summary = raw_report.get("summary") if isinstance(raw_report.get("summary"), dict) else {}
    raw_sev = raw_summary.get("by_severity") if isinstance(raw_summary.get("by_severity"), dict) else {}

    by_severity = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    # Count findings dynamically if missing from raw summary
    all_raw_targets = raw_report.get("targets", [])
    if not isinstance(all_raw_targets, list) or not all_raw_targets:
        # Fallback to AI report targets if raw_report targets are missing
        all_raw_targets = ai_report.get("targets", [])

    targets_normalized = []
    total_findings_count = 0

    for target in all_raw_targets:
        if not isinstance(target, dict):
            continue

        file_name = str(target.get("file_name") or "libfoo.so")
        ai_t = ai_targets_by_file.get(file_name, {})

        apk_rel_path = str(target.get("apk_relative_path") or f"lib/{target.get('abi_architecture', 'arm64-v8a')}/{file_name}")
        abi_arch = str(target.get("abi_architecture") or "arm64-v8a")
        sha256 = str(target.get("sha256") or "N/A")
        file_overview = str(ai_t.get("file_overview") or target.get("file_overview") or "")

        target_summary_raw = target.get("target_summary") if isinstance(target.get("target_summary"), dict) else {}
        attack_metrics = target_summary_raw.get("attack_surface_metrics") if isinstance(target_summary_raw.get("attack_surface_metrics"), dict) else {}
        if not attack_metrics and "attack_surface_metrics" in target:
            attack_metrics = target["attack_surface_metrics"] if isinstance(target["attack_surface_metrics"], dict) else {}

        functions_raw = target.get("functions", [])
        functions_normalized = []

        for fn in functions_raw if isinstance(functions_raw, list) else []:
            if not isinstance(fn, dict):
                continue

            fn_name = str(fn.get("function_name") or UNKNOWN)
            ai_fn = ai_functions_by_name.get(fn_name, {})

            symbol_address = str(fn.get("symbol_address") or ai_fn.get("symbol_address") or UNKNOWN)
            is_exported_jni = bool(fn.get("is_exported_jni", True if "Java_" in fn_name else False))
            fn_overview = str(ai_fn.get("function_overview") or fn.get("function_overview") or "")
            fn_source_code = fn.get("source_code") or ai_fn.get("source_code") or []

            findings_raw = fn.get("findings", [])
            findings_normalized = []

            for f in findings_raw if isinstance(findings_raw, list) else []:
                if not isinstance(f, dict):
                    continue

                fid = str(f.get("finding_id") or "FINDING")
                ai_f = ai_findings_by_id.get(fid, {})

                title = str(ai_f.get("title") or f.get("title") or f.get("rule_name") or "Native Vulnerability")
                ai_explanation = str(
                    ai_f.get("ai_explanation")
                    or ai_f.get("description")
                    or f.get("description")
                    or f.get("details")
                    or "No detailed explanation provided."
                )

                cwe_id = str(f.get("cwe_id") or f.get("rule_id") or ai_f.get("cwe_id") or "")
                severity_val = str(f.get("severity") or ai_f.get("severity") or f.get("importance") or "LOW").upper()
                if severity_val not in SEVERITY_BADGE_COLORS:
                    severity_val = "LOW"

                by_severity[severity_val] = by_severity.get(severity_val, 0) + 1
                total_findings_count += 1

                trigger = str(f.get("trigger_line") or f.get("line_number") or f.get("line") or UNKNOWN)
                source_code = f.get("source_code") or fn_source_code or []

                # Extract Remediation
                rem_data = ai_f.get("remediation") or f.get("remediation")
                recommendation = ""
                fixed_code_snippet = ""

                if isinstance(rem_data, dict):
                    recommendation = str(rem_data.get("recommendation") or "")
                    fixed_code_snippet = str(rem_data.get("fixed_code_snippet") or "")
                elif isinstance(rem_data, str):
                    recommendation = rem_data

                if not recommendation:
                    recommendation = f"Review native C/C++ code for {cwe_id or 'memory handling'}. Ensure strict input validation."

                findings_normalized.append({
                    "finding_id": fid,
                    "title": title,
                    "cwe_id": cwe_id,
                    "severity": severity_val,
                    "trigger_line": trigger,
                    "ai_explanation": ai_explanation,
                    "source_code": source_code,
                    "recommendation": recommendation,
                    "fixed_code_snippet": fixed_code_snippet,
                    "function_name": fn_name,
                    "symbol_address": symbol_address,
                })

            functions_normalized.append({
                "function_name": fn_name,
                "symbol_address": symbol_address,
                "is_exported_jni": is_exported_jni,
                "function_overview": fn_overview,
                "source_code": fn_source_code,
                "findings": findings_normalized,
            })

        total_scanned_fn = attack_metrics.get("total_functions_scanned", len(functions_normalized))
        exported_fn = attack_metrics.get("exported_jni_functions", sum(1 for fn in functions_normalized if fn["is_exported_jni"]))
        vuln_fn = attack_metrics.get("vulnerable_jni_functions", sum(1 for fn in functions_normalized if fn["findings"]))

        targets_normalized.append({
            "file_name": file_name,
            "file_overview": file_overview,
            "apk_relative_path": apk_rel_path,
            "abi_architecture": abi_arch,
            "sha256": sha256,
            "attack_surface_metrics": {
                "total_functions_scanned": total_scanned_fn,
                "exported_jni_functions": exported_fn,
                "vulnerable_jni_functions": vuln_fn,
            },
            "functions": functions_normalized,
        })

    if total_findings_count == 0 and raw_sev:
        for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            by_severity[k] = int(raw_sev.get(k, 0))
        total_findings_count = sum(by_severity.values())

    summary = {
        "analysis_engine": str(raw_summary.get("analysis_engine") or "GHIDRA / RADARE2"),
        "total_targets_scanned": len(targets_normalized),
        "total_findings": total_findings_count,
        "by_severity": by_severity,
        "abi_resolution": {
            "primary_abi": str(raw_summary.get("abi_resolution", {}).get("primary_abi") or "arm64-v8a"),
            "associated_abis": [],
        },
    }

    return {
        "executive_overview": exec_overview,
        "summary": summary,
        "targets": targets_normalized,
    }


def build_native_analyzer_page(app):
    """Build the layout for Native Libraries analysis results."""
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(page, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
    ctk.CTkLabel(
        header,
        text="⌨️ Native Libraries Analysis",
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

    # Scrollable body
    body = ctk.CTkScrollableFrame(page, fg_color="transparent")
    body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

    app.native_widgets = {}

    # 1. Summary Card
    summary_card = ctk.CTkFrame(
        body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER
    )
    summary_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(
        summary_card, text="NATIVE ANALYSIS SUMMARY", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED
    ).pack(anchor="w", padx=20, pady=(15, 10))

    grid_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
    grid_frame.pack(fill="x", padx=20, pady=(0, 10))

    # Metrics grid
    metrics_defs = [
        ("Analysis Engine:", "engine_lbl"),
        ("Primary ABI:", "abi_lbl"),
        ("Targets Scanned:", "targets_count_lbl"),
        ("Total Vulnerabilities:", "findings_count_lbl"),
    ]

    metrics_widgets = {}
    for i, (label_text, widget_key) in enumerate(metrics_defs):
        r, c = divmod(i, 2)
        ctk.CTkLabel(
            grid_frame, text=f"{label_text} ", font=("Arial", 13, "bold"), text_color=COLOR_TEXT_MUTED
        ).grid(row=r, column=c * 2, sticky="w", pady=4, padx=(0, 5))

        val_lbl = ctk.CTkLabel(grid_frame, text="—", font=("Arial", 13, "bold"), text_color=COLOR_TEXT)
        val_lbl.grid(row=r, column=c * 2 + 1, sticky="w", pady=4, padx=(0, 30))
        metrics_widgets[widget_key] = val_lbl

    app.native_widgets["metrics"] = metrics_widgets

    # Severity distribution row
    sev_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
    sev_frame.pack(fill="x", padx=20, pady=(5, 15))

    ctk.CTkLabel(
        sev_frame, text="Severity Breakout:", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED
    ).pack(side="left", padx=(0, 15))

    sev_badges = {}
    for sev_name in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        badge = ctk.CTkLabel(
            sev_frame,
            text=f" {sev_name}: 0 ",
            font=("Arial", 11, "bold"),
            fg_color=SEVERITY_BADGE_COLORS[sev_name],
            text_color="#FFFFFF",
            corner_radius=4,
        )
        badge.pack(side="left", padx=5)
        sev_badges[sev_name] = badge

    app.native_widgets["sev_badges"] = sev_badges

    # 2. Dynamic Targets Container
    targets_container = ctk.CTkFrame(body, fg_color="transparent")
    targets_container.pack(fill="x")

    app.native_widgets["targets_container"] = targets_container
    app.native_widgets["target_frames"] = []

    # Initialize empty state
    update_native_analyzer_page(app, default_native_report())

    return page


def _bind_click_recursive(widget, callback):
    try:
        widget.bind("<Button-1>", lambda e: callback())
    except Exception:
        pass
    for child in widget.winfo_children():
        _bind_click_recursive(child, callback)


def _setup_accordion(header_frame, toggle_lbl, body_frame, is_expanded=False, fill="x", padx=15, pady=(0, 10)):
    state = {"expanded": is_expanded}

    def toggle():
        state["expanded"] = not state["expanded"]
        if state["expanded"]:
            toggle_lbl.configure(text="▼")
            body_frame.pack(fill=fill, padx=padx, pady=pady)
        else:
            toggle_lbl.configure(text="▶")
            body_frame.pack_forget()

    _bind_click_recursive(header_frame, toggle)
    if not is_expanded:
        body_frame.pack_forget()
    else:
        body_frame.pack(fill=fill, padx=padx, pady=pady)


def _clear_target_frames(app) -> None:
    for frame in app.native_widgets.get("target_frames", []):
        frame.destroy()
    app.native_widgets["target_frames"] = []


def update_native_analyzer_page(app, report: Optional[Dict[str, Any]]) -> None:
    """Update the Native Analyzer results page with merged dual-source data."""
    if not getattr(app, "native_widgets", None):
        return

    normalized = normalize_native_report(report)
    summary = normalized["summary"]
    metrics = app.native_widgets["metrics"]

    metrics["engine_lbl"].configure(text=summary["analysis_engine"])
    metrics["abi_lbl"].configure(text=summary["abi_resolution"]["primary_abi"])
    metrics["targets_count_lbl"].configure(text=str(summary["total_targets_scanned"]))
    metrics["findings_count_lbl"].configure(
        text=str(summary["total_findings"]),
        text_color=COLOR_DANGER if summary["total_findings"] > 0 else COLOR_SUCCESS,
    )

    sev_counts = summary["by_severity"]
    for sev_name, badge in app.native_widgets["sev_badges"].items():
        count = sev_counts.get(sev_name, 0)
        badge.configure(text=f" {sev_name}: {count} ")

    _clear_target_frames(app)
    container = app.native_widgets["targets_container"]

    # Render Executive Overview Banner if present
    exec_overview = normalized.get("executive_overview")
    if exec_overview:
        overview_card = ctk.CTkFrame(
            container, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_ACCENT_BORDER
        )
        overview_card.pack(fill="x", pady=(0, 15), padx=5)
        app.native_widgets["target_frames"].append(overview_card)

        head = ctk.CTkFrame(overview_card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            head,
            text="📋 EXECUTIVE OVERVIEW",
            font=("Arial", 14, "bold"),
            text_color=COLOR_ACCENT_TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            overview_card,
            text=exec_overview,
            font=("Arial", 12),
            text_color=COLOR_TEXT,
            anchor="w",
            justify="left",
            wraplength=900,
        ).pack(fill="x", padx=20, pady=(5, 15))

    targets = normalized["targets"]
    if not targets:
        no_data_card = ctk.CTkFrame(
            container, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER
        )
        no_data_card.pack(fill="x", pady=10, padx=5)
        app.native_widgets["target_frames"].append(no_data_card)

        ctk.CTkLabel(
            no_data_card,
            text="No native libraries analyzed yet — run 'Native Libraries' scan on the Dashboard.",
            font=("Arial", 14),
            text_color=COLOR_TEXT_MUTED,
        ).pack(pady=30, padx=20)
        return

    # Render each target binary (Level 1 Accordion)
    for t_idx, target in enumerate(targets):
        target_card = ctk.CTkFrame(
            container, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER
        )
        target_card.pack(fill="x", pady=(0, 15), padx=5)
        app.native_widgets["target_frames"].append(target_card)

        total_target_findings = sum(len(fn.get("findings", [])) for fn in target.get("functions", []))

        # Level 1 Accordion Header
        target_header = ctk.CTkFrame(target_card, fg_color="transparent", cursor="hand2")
        target_header.pack(fill="x", padx=15, pady=12)

        left_target_head = ctk.CTkFrame(target_header, fg_color="transparent")
        left_target_head.pack(side="left", fill="x", expand=True)

        target_toggle_lbl = ctk.CTkLabel(
            left_target_head,
            text="▶",
            font=("Arial", 14, "bold"),
            text_color=COLOR_ACCENT_TEXT,
            width=20,
        )
        target_toggle_lbl.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left_target_head,
            text=f"📦 {target['file_name']}",
            font=("Arial", 16, "bold"),
            text_color=COLOR_TEXT,
            anchor="w",
        ).pack(side="left")

        right_target_head = ctk.CTkFrame(target_header, fg_color="transparent")
        right_target_head.pack(side="right")

        finding_badge_color = COLOR_DANGER if total_target_findings > 0 else COLOR_SUCCESS
        ctk.CTkLabel(
            right_target_head,
            text=f" {total_target_findings} Findings ",
            font=("Arial", 11, "bold"),
            fg_color=finding_badge_color,
            text_color="#FFFFFF",
            corner_radius=4,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkLabel(
            right_target_head,
            text=f" ABI: {target['abi_architecture']} ",
            font=("Arial", 11, "bold"),
            fg_color=COLOR_ACCENT_SURFACE,
            text_color=COLOR_ACCENT_TEXT,
            corner_radius=4,
        ).pack(side="right")

        # Level 1 Accordion Body
        target_body = ctk.CTkFrame(target_card, fg_color="transparent")

        # Target Overview / Path
        meta_frame = ctk.CTkFrame(target_body, fg_color="transparent")
        meta_frame.pack(fill="x", padx=15, pady=(0, 8))

        sha_text = f"SHA256: {target['sha256'][:16]}..." if target['sha256'] != "N/A" else "SHA256: N/A"
        ctk.CTkLabel(
            meta_frame,
            text=f"Path: {target['apk_relative_path']}  |  {sha_text}",
            font=("Consolas", 11),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w")

        if target.get("file_overview"):
            ctk.CTkLabel(
                target_body,
                text=f"📝 File Overview: {target['file_overview']}",
                font=("Arial", 12, "italic"),
                text_color=COLOR_ACCENT_TEXT,
                anchor="w",
                justify="left",
                wraplength=880,
            ).pack(fill="x", padx=15, pady=(0, 10))

        # Metrics bar
        m = target["attack_surface_metrics"]
        metrics_bar = ctk.CTkFrame(
            target_body, fg_color=COLOR_BG, corner_radius=6, border_width=1, border_color=COLOR_BORDER
        )
        metrics_bar.pack(fill="x", padx=15, pady=(0, 12))

        metrics_text = (
            f"Scanned Functions: {m['total_functions_scanned']}   •   "
            f"Exported JNI Functions: {m['exported_jni_functions']}   •   "
            f"Vulnerable JNI Functions: {m['vulnerable_jni_functions']}"
        )
        ctk.CTkLabel(
            metrics_bar,
            text=metrics_text,
            font=("Arial", 12, "bold"),
            text_color=COLOR_DANGER if m['vulnerable_jni_functions'] > 0 else COLOR_TEXT,
        ).pack(padx=15, pady=8, anchor="w")

        # Render Functions (Level 2 Accordion)
        functions = target.get("functions", [])
        if not functions:
            ok_box = ctk.CTkFrame(target_body, fg_color="transparent")
            ok_box.pack(fill="x", padx=15, pady=(0, 12))
            ctk.CTkLabel(
                ok_box,
                text="✅ No security vulnerabilities detected in this library.",
                font=("Arial", 13),
                text_color=COLOR_SUCCESS,
            ).pack(anchor="w")
        else:
            for fn in functions:
                fn_card = ctk.CTkFrame(
                    target_body, fg_color=COLOR_BG, corner_radius=8, border_width=1, border_color=COLOR_BORDER
                )
                fn_card.pack(fill="x", padx=15, pady=(0, 12))

                fn_findings = fn.get("findings", [])
                fn_findings_count = len(fn_findings)

                # Level 2 Accordion Header
                fn_header = ctk.CTkFrame(fn_card, fg_color="transparent", cursor="hand2")
                fn_header.pack(fill="x", padx=12, pady=10)

                left_fn_head = ctk.CTkFrame(fn_header, fg_color="transparent")
                left_fn_head.pack(side="left", fill="x", expand=True)

                fn_toggle_lbl = ctk.CTkLabel(
                    left_fn_head,
                    text="▶",
                    font=("Arial", 12, "bold"),
                    text_color=COLOR_ACCENT_TEXT,
                    width=18,
                )
                fn_toggle_lbl.pack(side="left", padx=(0, 6))

                ctk.CTkLabel(
                    left_fn_head,
                    text=f"⚙️ Function: {fn['function_name']}",
                    font=("Arial", 14, "bold"),
                    text_color=COLOR_TEXT,
                    anchor="w",
                ).pack(side="left")

                right_fn_head = ctk.CTkFrame(fn_header, fg_color="transparent")
                right_fn_head.pack(side="right")

                fn_badge_color = COLOR_DANGER if fn_findings_count > 0 else COLOR_SUCCESS
                ctk.CTkLabel(
                    right_fn_head,
                    text=f" {fn_findings_count} Findings ",
                    font=("Arial", 10, "bold"),
                    fg_color=fn_badge_color,
                    text_color="#FFFFFF",
                    corner_radius=4,
                ).pack(side="right", padx=(8, 0))

                if fn.get("is_exported_jni"):
                    ctk.CTkLabel(
                        right_fn_head,
                        text=" EXPORTED JNI ",
                        font=("Arial", 10, "bold"),
                        fg_color=COLOR_ACCENT_SURFACE,
                        text_color=COLOR_ACCENT_TEXT,
                        corner_radius=4,
                    ).pack(side="right", padx=(8, 0))

                ctk.CTkLabel(
                    right_fn_head,
                    text=f"Address: {fn['symbol_address']}",
                    font=("Consolas", 11),
                    text_color=COLOR_TEXT_MUTED,
                ).pack(side="right")

                # Level 2 Accordion Body
                fn_body = ctk.CTkFrame(fn_card, fg_color="transparent")

                if fn.get("function_overview"):
                    ctk.CTkLabel(
                        fn_body,
                        text=f"💬 Function Overview: {fn['function_overview']}",
                        font=("Arial", 12),
                        text_color=COLOR_TEXT,
                        anchor="w",
                        justify="left",
                        wraplength=850,
                    ).pack(fill="x", padx=12, pady=(0, 10))

                # Render Findings under Function (Level 3 Accordion)
                if not fn_findings:
                    ctk.CTkLabel(
                        fn_body,
                        text="✅ No vulnerability findings for this function.",
                        font=("Arial", 12),
                        text_color=COLOR_SUCCESS,
                    ).pack(anchor="w", padx=12, pady=(0, 10))
                else:
                    for f_idx, f in enumerate(fn_findings):
                        finding_card = ctk.CTkFrame(
                            fn_body,
                            fg_color=COLOR_SURFACE,
                            corner_radius=6,
                            border_width=1,
                            border_color=COLOR_ACCENT_BORDER if f["severity"] in ["CRITICAL", "HIGH"] else COLOR_BORDER,
                        )
                        finding_card.pack(fill="x", padx=12, pady=(0, 10))

                        # Level 3 Accordion Header (Closed State)
                        f_header = ctk.CTkFrame(finding_card, fg_color="transparent", cursor="hand2")
                        f_header.pack(fill="x", padx=12, pady=8)

                        left_f_head = ctk.CTkFrame(f_header, fg_color="transparent")
                        left_f_head.pack(side="left", fill="x", expand=True)

                        f_toggle_lbl = ctk.CTkLabel(
                            left_f_head,
                            text="▶",
                            font=("Arial", 11, "bold"),
                            text_color=COLOR_ACCENT_TEXT,
                            width=16,
                        )
                        f_toggle_lbl.pack(side="left", padx=(0, 6))

                        cwe_prefix = f"[{f['cwe_id']}] " if f.get("cwe_id") else ""
                        ctk.CTkLabel(
                            left_f_head,
                            text=f"#{f_idx + 1:02d} [{f['finding_id']}] {cwe_prefix}{f['title']}",
                            font=("Arial", 13, "bold"),
                            text_color=COLOR_TEXT,
                            anchor="w",
                            justify="left",
                            wraplength=600,
                        ).pack(side="left", fill="x", expand=True)

                        badge_color = SEVERITY_BADGE_COLORS.get(f["severity"], COLOR_UNKNOWN)
                        ctk.CTkLabel(
                            f_header,
                            text=f" {f['severity']} ",
                            font=("Arial", 11, "bold"),
                            fg_color=badge_color,
                            text_color="#FFFFFF",
                            corner_radius=4,
                        ).pack(side="right")

                        # Level 3 Accordion Body (Expanded State)
                        f_body = ctk.CTkFrame(finding_card, fg_color="transparent")

                        # Technical Line Trigger
                        ctk.CTkLabel(
                            f_body,
                            text=f"Target Line / Trigger: {f['trigger_line']}",
                            font=("Consolas", 11),
                            text_color=COLOR_TEXT_MUTED,
                        ).pack(anchor="w", padx=12, pady=(0, 8))

                        # AI Explanation Box
                        exp_box = ctk.CTkFrame(
                            f_body,
                            fg_color="#181D28",
                            corner_radius=6,
                            border_width=1,
                            border_color="#2A3346",
                        )
                        exp_box.pack(fill="x", padx=12, pady=(0, 10))

                        ctk.CTkLabel(
                            exp_box,
                            text="🤖 AI VULNERABILITY EXPLANATION",
                            font=("Arial", 11, "bold"),
                            text_color=COLOR_ACCENT_TEXT,
                            anchor="w",
                        ).pack(anchor="w", padx=12, pady=(8, 4))

                        ctk.CTkLabel(
                            exp_box,
                            text=f["ai_explanation"],
                            font=("Arial", 12),
                            text_color=COLOR_TEXT,
                            anchor="w",
                            justify="left",
                            wraplength=800,
                        ).pack(anchor="w", padx=12, pady=(0, 8), fill="x")

                        # Decompiled Context Code Snippet
                        code_lines = f.get("source_code") or []
                        if isinstance(code_lines, str):
                            code_lines = code_lines.splitlines()

                        if code_lines:
                            ctk.CTkLabel(
                                f_body,
                                text="Decompiled Source Code Context:",
                                font=("Arial", 11, "bold"),
                                text_color=COLOR_TEXT_MUTED,
                            ).pack(anchor="w", padx=12, pady=(0, 4))

                            snippet_box = ctk.CTkTextbox(
                                f_body,
                                height=60 if len(code_lines) <= 3 else 90,
                                fg_color=COLOR_BG,
                                font=("Consolas", 11),
                                text_color=COLOR_TEXT,
                                border_width=1,
                                border_color=COLOR_BORDER,
                            )
                            snippet_box.pack(fill="x", padx=12, pady=(0, 10))
                            snippet_box.insert("end", "\n".join(str(line) for line in code_lines))
                            snippet_box.configure(state="disabled")

                        # Remediation Box
                        rem_card = ctk.CTkFrame(
                            f_body,
                            fg_color="#122619",
                            corner_radius=6,
                            border_width=1,
                            border_color=COLOR_SUCCESS,
                        )
                        rem_card.pack(fill="x", padx=12, pady=(0, 10))

                        ctk.CTkLabel(
                            rem_card,
                            text="💡 REMEDIATION RECOMMENDATION",
                            font=("Arial", 11, "bold"),
                            text_color=COLOR_SUCCESS,
                            anchor="w",
                        ).pack(anchor="w", padx=12, pady=(8, 4))

                        ctk.CTkLabel(
                            rem_card,
                            text=f["recommendation"],
                            font=("Arial", 12),
                            text_color=COLOR_TEXT,
                            anchor="w",
                            justify="left",
                            wraplength=800,
                        ).pack(anchor="w", padx=12, pady=(0, 8), fill="x")

                        if f.get("fixed_code_snippet"):
                            ctk.CTkLabel(
                                rem_card,
                                text="Suggested Code Fix:",
                                font=("Arial", 11, "bold"),
                                text_color=COLOR_SUCCESS,
                            ).pack(anchor="w", padx=12, pady=(0, 4))

                            fix_box = ctk.CTkTextbox(
                                rem_card,
                                height=50 if len(f["fixed_code_snippet"].splitlines()) <= 2 else 80,
                                fg_color="#0A180E",
                                font=("Consolas", 11),
                                text_color="#81C784",
                                border_width=1,
                                border_color="#1B4D27",
                            )
                            fix_box.pack(fill="x", padx=12, pady=(0, 10))
                            fix_box.insert("end", f["fixed_code_snippet"])
                            fix_box.configure(state="disabled")

                        _setup_accordion(f_header, f_toggle_lbl, f_body, is_expanded=False, fill="x", padx=0, pady=(0, 5))

                _setup_accordion(fn_header, fn_toggle_lbl, fn_body, is_expanded=False, fill="x", padx=0, pady=(0, 10))

        _setup_accordion(target_header, target_toggle_lbl, target_body, is_expanded=False, fill="x", padx=15, pady=(0, 15))
