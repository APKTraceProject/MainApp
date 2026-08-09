import tkinter.filedialog as filedialog
import customtkinter as ctk

from core.config import NATIVE_ENGINE_OPTIONS

from ..ui import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)


def native_engine_hint(engine: str) -> str:
    """Helper text describing the path expected for the selected engine."""
    if (engine or "").strip().lower() == "radare2":
        return "Path to the Radare2 executable (r2 or r2.exe)."
    return "Path to the Ghidra headless analyzer script or executable (e.g. analyzeHeadless.bat)."


def build_settings_page(app):
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
    page.grid_columnconfigure(0, weight=1)
    page.grid_rowconfigure(1, weight=1)

    header_frame = ctk.CTkFrame(page, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 15))
    ctk.CTkLabel(header_frame, text="⚙️ Settings", font=("Arial", 26, "bold"), text_color=COLOR_ACCENT_TEXT).pack(side="left")

    body = ctk.CTkScrollableFrame(page, fg_color="transparent")
    body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))

    current_paths = app.config.get("paths", {}) or {}
    current_api = app.config.get("api", {}) or {}

    # --- Tool paths section ---
    paths_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    paths_card.pack(fill="x", pady=(0, 15), padx=5)
    ctk.CTkLabel(paths_card, text="TOOL PATHS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

    path_fields = [
        ("output_dir", "Output Directory", "dir"),
        ("apktool_path", "Apktool Path (.jar / executable)", "file"),
        ("jadx_path", "Jadx Path (executable / bat)", "file"),
        ("native_engine_path", "Native Engine Path", "file"),
    ]

    app.settings_path_entries = {}
    for key, label, kind in path_fields:
        if key == "native_engine_path":
            _build_engine_selector(app, paths_card, current_paths)

        row = ctk.CTkFrame(paths_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(row, text=label, font=("Arial", 13), text_color=COLOR_TEXT, width=210, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(row, fg_color=COLOR_SURFACE_HOVER, border_width=0, height=35)
        entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        entry.insert(0, current_paths.get(key, "") or "")

        ctk.CTkButton(
            row,
            text="Browse",
            width=90,
            height=35,
            fg_color=COLOR_SURFACE_HOVER,
            hover_color="#3D3E4A",
            command=lambda e=entry, k=kind: browse_path(e, k),
        ).pack(side="left")

        app.settings_path_entries[key] = entry

        if key == "native_engine_path":
            app.settings_engine_hint_lbl = ctk.CTkLabel(
                paths_card,
                text=native_engine_hint(app.settings_engine_combo.get()),
                font=("Arial", 11),
                text_color=COLOR_TEXT_MUTED,
            )
            app.settings_engine_hint_lbl.pack(anchor="w", padx=20, pady=(0, 4))

    paths_card_spacer = ctk.CTkFrame(paths_card, fg_color="transparent", height=5)
    paths_card_spacer.pack(fill="x")

    # --- AI API section ---
    api_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
    api_card.pack(fill="x", pady=(0, 15), padx=5)
    ctk.CTkLabel(api_card, text="AI API SETTINGS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

    api_fields = [
        ("provider", "Provider (e.g. openai, anthropic)", ""),
        ("model", "Model Name", ""),
        ("api_key", "API Key", "•"),
    ]

    app.settings_api_entries = {}
    for key, label, show_char in api_fields:
        row = ctk.CTkFrame(api_card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(row, text=label, font=("Arial", 13), text_color=COLOR_TEXT, width=210, anchor="w").pack(side="left")

        entry = ctk.CTkEntry(row, fg_color=COLOR_SURFACE_HOVER, border_width=0, height=35, show=show_char)
        entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        entry.insert(0, current_api.get(key, "") or "")

        app.settings_api_entries[key] = entry

    api_card_spacer = ctk.CTkFrame(api_card, fg_color="transparent", height=5)
    api_card_spacer.pack(fill="x", pady=(0, 10))

    # --- Save button + status ---
    save_row = ctk.CTkFrame(body, fg_color="transparent")
    save_row.pack(fill="x", pady=(5, 20), padx=5)

    app.settings_status_lbl = ctk.CTkLabel(save_row, text="", font=("Arial", 12), text_color=COLOR_TEXT_MUTED)
    app.settings_status_lbl.pack(side="left")

    ctk.CTkButton(
        save_row,
        text="💾 Save Settings",
        height=40,
        width=160,
        fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER,
        command=app.save_settings,
    ).pack(side="right")

    return page


def _build_engine_selector(app, paths_card, current_paths):
    engine_row = ctk.CTkFrame(paths_card, fg_color="transparent")
    engine_row.pack(fill="x", padx=20, pady=6)

    ctk.CTkLabel(
        engine_row,
        text="Native Analysis Engine",
        font=("Arial", 13),
        text_color=COLOR_TEXT,
        width=210,
        anchor="w",
    ).pack(side="left")

    current = str(current_paths.get("native_engine", "ghidra") or "ghidra").strip().lower()
    if current not in NATIVE_ENGINE_OPTIONS:
        current = "ghidra"

    app.settings_engine_combo = ctk.CTkComboBox(
        engine_row,
        values=NATIVE_ENGINE_OPTIONS,
        state="readonly",
        height=35,
        fg_color=COLOR_SURFACE_HOVER,
        border_width=0,
        dropdown_fg_color=COLOR_SURFACE_HOVER,
        dropdown_hover_color=COLOR_ACCENT,
        command=lambda _choice: _update_engine_hint(app),
    )
    app.settings_engine_combo.set(current)
    app.settings_engine_combo.pack(side="left", fill="x", expand=True, padx=(10, 10))


def _update_engine_hint(app):
    if getattr(app, "settings_engine_hint_lbl", None) is not None:
        app.settings_engine_hint_lbl.configure(
            text=native_engine_hint(app.settings_engine_combo.get())
        )


def browse_path(entry_widget: ctk.CTkEntry, kind: str):
    path = (
        filedialog.askdirectory(title="Select Directory")
        if kind == "dir"
        else filedialog.askopenfilename(title="Select File")
    )
    if path:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, path)


def save_settings(app):
    new_paths = {key: entry.get().strip() for key, entry in app.settings_path_entries.items()}
    new_paths["native_engine"] = app.settings_engine_combo.get().strip().lower()
    new_api = {key: entry.get().strip() for key, entry in app.settings_api_entries.items()}
    updated_config = {"paths": new_paths, "api": new_api}

    if app.save_config_fn is None:
        app.settings_status_lbl.configure(text="⚠️ Save handler not available.", text_color=COLOR_DANGER)
        return

    try:
        app.save_config_fn(updated_config)
    except Exception as exc:  # noqa: BLE001
        app.settings_status_lbl.configure(text=f"❌ Failed to save: {exc}", text_color=COLOR_DANGER)
        return

    app.config = updated_config
    app.settings_status_lbl.configure(text="✅ Settings saved.", text_color=COLOR_SUCCESS)