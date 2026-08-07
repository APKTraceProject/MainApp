from pathlib import Path
import tkinter.filedialog as filedialog
import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT,
    COLOR_ACCENT_BORDER,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_SURFACE,
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_DISABLED,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    ClickableRow,
    emoji_font,
)


def build_dashboard(app):
    """Build the main dashboard view"""
    page = ctk.CTkScrollableFrame(app.main_container, fg_color="transparent")

    # APK Load Header Box
    app.apk_frame = ctk.CTkFrame(
        page,
        fg_color=COLOR_SURFACE,
        corner_radius=10,
        border_width=1,
        border_color=COLOR_BORDER,
    )
    app.apk_frame.pack(fill="x", padx=30, pady=(30, 15))

    app.apk_icon_lbl = ctk.CTkLabel(
        app.apk_frame,
        text="📦",
        font=emoji_font(26),
        fg_color=COLOR_DISABLED,
        text_color="white",
        corner_radius=8,
        width=56,
        height=56,
    )
    app.apk_icon_lbl.pack(side="left", padx=20, pady=20)

    info_frame = ctk.CTkFrame(app.apk_frame, fg_color="transparent")
    info_frame.pack(side="left", fill="y", pady=20)
    app.apk_name_lbl = ctk.CTkLabel(
        info_frame,
        text="No APK selected",
        font=("Arial", 16, "bold"),
        text_color=COLOR_TEXT,
    )
    app.apk_name_lbl.pack(anchor="w")
    app.apk_path_lbl = ctk.CTkLabel(
        info_frame,
        text='Click "Choose File" to load an .apk for analysis',
        font=("Arial", 12),
        text_color=COLOR_TEXT_MUTED,
    )
    app.apk_path_lbl.pack(anchor="w")

    app.start_btn = ctk.CTkButton(
        app.apk_frame,
        text="▶ Start Analysis",
        height=40,
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        state="disabled",
        command=app.start_analysis_process,
    )
    app.start_btn.pack(side="right", padx=20)

    app.choose_btn = ctk.CTkButton(
        app.apk_frame,
        text="Choose File",
        height=40,
        fg_color=COLOR_SURFACE_HOVER,
        hover_color="#3D3E4A",
        command=app.choose_apk_file,
    )
    app.choose_btn.pack(side="right", padx=10)

    # Progress / Status Frame (Hidden initially)
    app.progress_frame = ctk.CTkFrame(
        page,
        fg_color=COLOR_ACCENT_SURFACE,
        corner_radius=10,
        border_width=1,
        border_color=COLOR_ACCENT_BORDER,
    )

    app.progress_status_lbl = ctk.CTkLabel(
        app.progress_frame,
        text="⏳ Starting analysis...",
        font=("Arial", 13, "bold"),
        text_color=COLOR_ACCENT_TEXT,
    )
    app.progress_status_lbl.pack(anchor="w", padx=20, pady=(12, 6))

    app.progress_bar = ctk.CTkProgressBar(
        app.progress_frame,
        height=10,
        corner_radius=5,
        progress_color=COLOR_ACCENT_TEXT,
        fg_color=COLOR_SURFACE,
    )
    app.progress_bar.pack(fill="x", padx=20, pady=(0, 15))
    app.progress_bar.set(0)

    # Active Scan Mode Indicator
    mode_banner = ctk.CTkFrame(
        page,
        fg_color=COLOR_ACCENT_SURFACE,
        corner_radius=8,
        border_width=1,
        border_color=COLOR_ACCENT_BORDER,
    )
    mode_banner.pack(fill="x", padx=30, pady=(5, 10))
    app.mode_indicator_lbl = ctk.CTkLabel(
        mode_banner,
        text=f"Active Scan Mode: {app.current_scan_mode}",
        font=("Arial", 13, "bold"),
        text_color=COLOR_ACCENT_TEXT,
    )
    app.mode_indicator_lbl.pack(padx=20, pady=12, anchor="w")

    # Dashboard Summary Cards
    overview_lbl = ctk.CTkLabel(page, text="ANALYSIS OVERVIEW", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED)
    overview_lbl.pack(anchor="w", padx=30, pady=(15, 10))

    cards_frame = ctk.CTkFrame(page, fg_color="transparent")
    cards_frame.pack(fill="x", padx=25)

    cards_data = [
        ("Risk Level", "—", "Not analyzed yet"),
        ("Permissions", "—", "Not analyzed yet"),
        ("Activities", "—", "Not analyzed yet"),
        ("Services", "—", "Not analyzed yet"),
        ("Receivers", "—", "Not analyzed yet"),
        ("Native Libraries", "—", "Not analyzed yet"),
    ]

    for i, (title, val, sub) in enumerate(cards_data):
        cards_frame.grid_columnconfigure(i, weight=1)
        card = ctk.CTkFrame(
            cards_frame,
            fg_color=COLOR_SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(card, text=title, font=("Arial", 12), text_color=COLOR_TEXT_MUTED).pack(pady=(15, 0))
        val_lbl = ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold"), text_color=COLOR_TEXT)
        val_lbl.pack(pady=5)
        sub_lbl = ctk.CTkLabel(card, text=sub, font=("Arial", 11), text_color=COLOR_TEXT_MUTED)
        sub_lbl.pack(pady=(0, 15))

        app.dashboard_cards[title] = (val_lbl, sub_lbl)

    res_lbl = ctk.CTkLabel(page, text="Analysis Results (Click to view tab)", font=("Arial", 14, "bold"), text_color=COLOR_ACCENT_TEXT)
    res_lbl.pack(anchor="w", padx=30, pady=(25, 10))

    app.list_frame = ctk.CTkFrame(page, fg_color="transparent")
    app.list_frame.pack(fill="both", expand=True, padx=30)

    results_data = [
        ("📄", "Manifest", "Package info, components, permissions and configuration", "Manifest"),
        ("☕", "Java / Kotlin", "Decompiled source code analysis and security checks", "Java / Kotlin"),
        ("⌨️", "Native Libraries", "Ghidra & Radare2 analysis of native libraries", "Native Libraries"),
        ("🔤", "Strings", "Important strings, URLs, IPs and hidden data", "Strings"),
        ("🛡️", "Permissions", "Check how dangerous permissions are used in code", "Permissions"),
        ("📁", "Resources", "Resource files and asset analysis", "Resources"),
    ]

    app.result_rows = []
    for icon, title, desc, target_page in results_data:
        row = ClickableRow(
            app.list_frame,
            icon,
            title,
            desc,
            command=lambda tp=target_page: app.show_page(tp),
        )
        row.pack(fill="x", pady=6)
        app.result_rows.append(row)

    ai_row = ClickableRow(
        app.list_frame,
        "✨",
        "Full AI Analysis",
        "Overall evaluation and recommendations by AI",
        command=lambda: app.show_page("Full AI Analysis"),
        is_ai=True,
    )
    ai_row.pack(fill="x", pady=(15, 30))
    app.result_rows.append(ai_row)

    return page


def update_dashboard_cards(app, report: dict):
    manifest = report.get("manifest", {})
    components = report.get("component_summary", {})
    sec_flags = manifest.get("security_flags", {})

    # Calculate basic risk level
    perm_count = len(manifest.get("permissions", []))
    is_debuggable = sec_flags.get("debuggable", False)

    if is_debuggable or perm_count > 25:
        risk = ("HIGH", COLOR_DANGER)
    elif perm_count > 10:
        risk = ("MEDIUM", "#FFC107")
    else:
        risk = ("LOW", COLOR_SUCCESS)

    cards_mapping = {
        "Risk Level": (risk[0], f"Flags: Debuggable={is_debuggable}"),
        "Permissions": (str(perm_count), f"{len(manifest.get('custom_permissions', []))} custom permissions"),
        "Activities": (str(components.get("activities", 0)), f"Aliases: {components.get('activity_aliases', 0)}"),
        "Services": (str(components.get("services", 0)), "Background components"),
        "Receivers": (str(components.get("receivers", 0)), "Broadcast listeners"),
        "Native Libraries": (str(report.get("apk", {}).get("native_library_count", 0)), "Shared .so files"),
    }

    for title, (val, sub) in cards_mapping.items():
        if title in app.dashboard_cards:
            val_lbl, sub_lbl = app.dashboard_cards[title]
            val_lbl.configure(text=val)
            if title == "Risk Level":
                val_lbl.configure(text_color=risk[1])
            sub_lbl.configure(text=sub)