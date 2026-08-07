import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT_TEXT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)


def build_manifest_page(app):
    """Build the Manifest Analysis tab's full layout, empty from the start."""
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(page, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
    ctk.CTkLabel(header, text="📄 Manifest Analysis", font=("Arial", 24, "bold"), text_color=COLOR_ACCENT_TEXT).pack(side="left")
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

    app.manifest_widgets = {}

    # 1. Package & App Overview Section
    info_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    info_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(info_card, text="APPLICATION METADATA", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

    grid_frame = ctk.CTkFrame(info_card, fg_color="transparent")
    grid_frame.pack(fill="x", padx=20, pady=(0, 15))

    metadata_labels = [
        "Package Name:",
        "Version Name:",
        "Version Code:",
        "Min SDK:",
        "Target SDK:",
        "Shared User ID:",
    ]

    app.manifest_widgets["metadata"] = {}
    for i, label in enumerate(metadata_labels):
        r, c = divmod(i, 2)
        lbl_widget = ctk.CTkLabel(grid_frame, text=f"{label} ", font=("Arial", 13, "bold"), text_color=COLOR_TEXT_MUTED)
        lbl_widget.grid(row=r, column=c * 2, sticky="w", pady=4, padx=(0, 5))

        val_widget = ctk.CTkLabel(grid_frame, text="—", font=("Arial", 13), text_color=COLOR_TEXT)
        val_widget.grid(row=r, column=c * 2 + 1, sticky="w", pady=4, padx=(0, 30))
        app.manifest_widgets["metadata"][label] = val_widget

    # 2. Security Flags Section
    flags_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    flags_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(flags_card, text="SECURITY FLAGS & CONFIGURATIONS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

    flags_grid = ctk.CTkFrame(flags_card, fg_color="transparent")
    flags_grid.pack(fill="x", padx=20, pady=(0, 15))

    flags_defs = [
        ("Debuggable", "High Risk: Code can be attached to a debugger"),
        ("Allow Backup", "Medium Risk: Application data can be extracted via ADB"),
        ("Cleartext Traffic", "HTTP unencrypted traffic permitted"),
        ("Test Only", "Test mode flag enabled"),
    ]

    app.manifest_widgets["flags"] = {}
    for i, (flag_name, flag_desc) in enumerate(flags_defs):
        f_lbl = ctk.CTkLabel(flags_grid, text=flag_name, font=("Arial", 13, "bold"), text_color=COLOR_TEXT)
        f_lbl.grid(row=i, column=0, sticky="w", pady=6)

        badge = ctk.CTkLabel(flags_grid, text=" UNSPECIFIED ", font=("Arial", 11, "bold"), fg_color=COLOR_SURFACE_HOVER, corner_radius=4)
        badge.grid(row=i, column=1, sticky="w", padx=15, pady=6)

        d_lbl = ctk.CTkLabel(flags_grid, text=flag_desc, font=("Arial", 12), text_color=COLOR_TEXT_MUTED)
        d_lbl.grid(row=i, column=2, sticky="w", pady=6)

        app.manifest_widgets["flags"][flag_name] = badge

    # 3. Permissions Section
    perms_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    perms_card.pack(fill="x", pady=(0, 15), padx=5)

    perms_title_lbl = ctk.CTkLabel(perms_card, text="DECLARED PERMISSIONS (0)", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED)
    perms_title_lbl.pack(anchor="w", padx=20, pady=(15, 10))

    perms_box = ctk.CTkTextbox(perms_card, height=130, fg_color=COLOR_BG, font=("Consolas", 12), text_color=COLOR_ACCENT_TEXT)
    perms_box.pack(fill="x", padx=20, pady=(0, 15))
    perms_box.insert("end", "No data yet — select an APK on Dashboard and run 'Manifest' analysis.")
    perms_box.configure(state="disabled")

    app.manifest_widgets["perms_title"] = perms_title_lbl
    app.manifest_widgets["perms_box"] = perms_box

    # 4. Components Section
    comps_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    comps_card.pack(fill="x", pady=(0, 15), padx=5)

    ctk.CTkLabel(comps_card, text="MANIFEST COMPONENTS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

    tabview = ctk.CTkTabview(comps_card, fg_color=COLOR_BG)
    tabview.pack(fill="x", padx=20, pady=(0, 15))

    app.manifest_widgets["comp_boxes"] = {}
    for c_type in ["activities", "services", "receivers", "providers"]:
        tab = tabview.add(c_type.capitalize())

        box = ctk.CTkTextbox(tab, height=150, fg_color="transparent", font=("Consolas", 12), text_color=COLOR_TEXT)
        box.pack(fill="both", expand=True)
        box.insert("end", "No data yet.")
        box.configure(state="disabled")

        app.manifest_widgets["comp_boxes"][c_type] = box

    return page


def update_manifest_page(app, report: dict):
    """Fill in the already-built Manifest page with results from a completed scan."""
    widgets = app.manifest_widgets
    if not widgets:
        return

    manifest = report.get("manifest", {})
    sdk_info = manifest.get("sdk", {})
    sec_flags = manifest.get("security_flags", {})

    # 1. Metadata
    metadata_values = {
        "Package Name:": manifest.get("package_name", "N/A"),
        "Version Name:": manifest.get("version_name", "N/A"),
        "Version Code:": str(manifest.get("version_code", "N/A")),
        "Min SDK:": str(sdk_info.get("min_sdk", "N/A")),
        "Target SDK:": str(sdk_info.get("target_sdk", "N/A")),
        "Shared User ID:": str(manifest.get("shared_user_id") or "None"),
    }
    for label, val in metadata_values.items():
        widget = widgets["metadata"].get(label)
        if widget:
            widget.configure(text=val)

    # 2. Security flags
    flags_map = {
        "Debuggable": sec_flags.get("debuggable"),
        "Allow Backup": sec_flags.get("allow_backup"),
        "Cleartext Traffic": sec_flags.get("uses_cleartext_traffic"),
        "Test Only": sec_flags.get("test_only"),
    }
    for flag_name, flag_val in flags_map.items():
        badge = widgets["flags"].get(flag_name)
        if not badge:
            continue
        is_bad = flag_val is True and flag_name in ["Debuggable", "Allow Backup", "Cleartext Traffic"]
        badge_color = COLOR_DANGER if is_bad else COLOR_SURFACE_HOVER
        badge_text = "TRUE" if flag_val else ("FALSE" if flag_val is False else "UNSPECIFIED")
        badge.configure(text=f" {badge_text} ", fg_color=badge_color)

    # 3. Permissions
    perms = manifest.get("permissions", [])
    widgets["perms_title"].configure(text=f"DECLARED PERMISSIONS ({len(perms)})")

    perms_box = widgets["perms_box"]
    perms_box.configure(state="normal")
    perms_box.delete("1.0", "end")
    if perms:
        for p in perms:
            perms_box.insert("end", f"• {p.get('name')}\n")
    else:
        perms_box.insert("end", "No permissions declared.")
    perms_box.configure(state="disabled")

    # 4. Components
    comps = manifest.get("components", {})
    for c_type, box in widgets["comp_boxes"].items():
        box.configure(state="normal")
        box.delete("1.0", "end")
        c_list = comps.get(c_type, [])
        if c_list:
            for item in c_list:
                exp = " [EXPORTED]" if item.get("exported") else ""
                box.insert("end", f"• {item.get('name')}{exp}\n")
        else:
            box.insert("end", f"No {c_type} found.")
        box.configure(state="disabled")