"""
mainapp/ui/setup_wizard.py

Configuration window shown by the startup flow (core.launcher.launch_app)
whenever config.json is missing, invalid, or incomplete. Collects the
required tool paths, writes the validated configuration to config.json,
and then closes itself so the app can open the real UI.

The config is written through `on_complete` (normally core.config.save_config).
If no callback is supplied the wizard falls back to that same writer, so
completing the wizard always persists a valid config.json.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

import tkinter.filedialog as filedialog
import customtkinter as ctk

from core.config import API_KEYS, NATIVE_ENGINE_OPTIONS, save_config as default_save_config

from .ui import (
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def native_engine_hint(engine: str) -> str:
    """Helper text describing the path expected for the selected engine."""
    if (engine or "").strip().lower() == "radare2":
        return "Path to the Radare2 executable (r2 or r2.exe)."
    return "Path to the Ghidra headless analyzer script or executable (e.g. analyzeHeadless.bat)."


class SetupWizard(ctk.CTk):
    """Collects the 4 required tool paths on first run."""

    # (config key, display label, "dir" or "file", helper text)
    FIELDS = [
        (
            "output_dir",
            "Output Directory",
            "dir",
            "apktool_output, jadx_output and ghidra_output will be created inside this folder.",
        ),
        (
            "apktool_path",
            "Apktool Path (.jar or executable)",
            "file",
            "Path to apktool.jar or the apktool executable/bat script.",
        ),
        (
            "jadx_path",
            "Jadx Path (executable/bat)",
            "file",
            "Path to the jadx or jadx.bat executable.",
        ),
        (
            "native_engine_path",
            "Native Engine Path",
            "file",
            native_engine_hint("ghidra"),
        ),
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None, on_complete: Optional[Callable[[Dict[str, Any]], None]] = None):
        super().__init__()

        self.title("APKTrace - Initial Setup")
        self.geometry("720x600")
        self.minsize(680, 540)

        self.config_data: Dict[str, Any] = config or {"paths": {}, "api": {}}
        self.on_complete = (
            on_complete if on_complete is not None else default_save_config
        )
        self.entries: Dict[str, ctk.CTkEntry] = {}
        self.completed = False

        self._build_ui()

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))
        ctk.CTkLabel(
            header, text="🛡️ Welcome to APKTrace", font=("Arial", 22, "bold"), text_color=COLOR_ACCENT_TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Before you start, please provide the required tool paths below.",
            font=("Arial", 13),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        body = ctk.CTkScrollableFrame(
            self, fg_color=COLOR_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_BORDER
        )
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 10))

        existing_paths = self.config_data.get("paths", {}) or {}
        self._native_engine_hint_lbl: Optional[ctk.CTkLabel] = None

        for key, label, kind, hint in self.FIELDS:
            if key == "native_engine_path":
                self._build_engine_selector(body, existing_paths)

            field_frame = ctk.CTkFrame(body, fg_color="transparent")
            field_frame.pack(fill="x", padx=20, pady=(15, 5))

            ctk.CTkLabel(field_frame, text=label, font=("Arial", 14, "bold"), text_color=COLOR_TEXT).pack(anchor="w")

            if key == "native_engine_path":
                self._native_engine_hint_lbl = ctk.CTkLabel(
                    field_frame,
                    text=native_engine_hint(self.engine_combo.get()),
                    font=("Arial", 11),
                    text_color=COLOR_TEXT_MUTED,
                )
                self._native_engine_hint_lbl.pack(anchor="w", pady=(0, 6))
            else:
                ctk.CTkLabel(field_frame, text=hint, font=("Arial", 11), text_color=COLOR_TEXT_MUTED).pack(
                    anchor="w", pady=(0, 6)
                )

            input_row = ctk.CTkFrame(field_frame, fg_color="transparent")
            input_row.pack(fill="x")

            entry = ctk.CTkEntry(input_row, fg_color=COLOR_SURFACE_HOVER, border_width=0, height=38)
            entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            entry.insert(0, existing_paths.get(key, "") or "")

            browse_btn = ctk.CTkButton(
                input_row,
                text="Browse",
                width=90,
                height=38,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_HOVER,
                command=lambda e=entry, k=kind: self._browse(e, k),
            )
            browse_btn.pack(side="left")

            self.entries[key] = entry

        self.status_lbl = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color=COLOR_DANGER)
        self.status_lbl.grid(row=2, column=0, sticky="w", padx=35, pady=(0, 5))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 25))

        ctk.CTkButton(
            footer,
            text="Save & Continue",
            height=42,
            width=180,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self._on_save,
        ).pack(side="right")

    # ------------------------------------------------------------------ #
    def _build_engine_selector(self, body: ctk.CTkScrollableFrame, existing_paths: Dict[str, Any]):
        engine_frame = ctk.CTkFrame(body, fg_color="transparent")
        engine_frame.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            engine_frame, text="Native Analysis Engine", font=("Arial", 14, "bold"), text_color=COLOR_TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            engine_frame,
            text="Choose the engine used to analyze native libraries (Ghidra or Radare2).",
            font=("Arial", 11),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 6))

        current = str(existing_paths.get("native_engine", "ghidra") or "ghidra").strip().lower()
        if current not in NATIVE_ENGINE_OPTIONS:
            current = "ghidra"

        self.engine_combo = ctk.CTkComboBox(
            engine_frame,
            values=NATIVE_ENGINE_OPTIONS,
            state="readonly",
            height=38,
            fg_color=COLOR_SURFACE_HOVER,
            border_width=0,
            dropdown_fg_color=COLOR_SURFACE_HOVER,
            dropdown_hover_color=COLOR_ACCENT,
            command=lambda _choice: self._update_native_engine_hint(),
        )
        self.engine_combo.set(current)
        self.engine_combo.pack(fill="x")

    def _update_native_engine_hint(self):
        if self._native_engine_hint_lbl is not None:
            self._native_engine_hint_lbl.configure(
                text=native_engine_hint(self.engine_combo.get())
            )

    # ------------------------------------------------------------------ #
    def _browse(self, entry_widget: ctk.CTkEntry, kind: str):
        path = (
            filedialog.askdirectory(title="Select Directory")
            if kind == "dir"
            else filedialog.askopenfilename(title="Select File")
        )
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def _on_save(self):
        values = {key: entry.get().strip() for key, entry in self.entries.items()}
        values["native_engine"] = self.engine_combo.get().strip().lower()
        if values["native_engine"] not in NATIVE_ENGINE_OPTIONS:
            self.status_lbl.configure(text="❌ 'Native Analysis Engine' is invalid.")
            return

        for key, label, kind, _hint in self.FIELDS:
            value = values.get(key, "")
            if not value:
                self.status_lbl.configure(text=f"❌ '{label}' is required.")
                return
            if kind == "file" and not Path(value).expanduser().exists():
                self.status_lbl.configure(text=f"❌ '{label}' does not point to an existing file.")
                return

        # Build a structurally valid config: the collected paths plus the
        # existing API settings normalized to strings (empty when absent).
        # This guarantees `save_config` always persists a valid config.json.
        raw_api = self.config_data.get("api") or {}
        if not isinstance(raw_api, dict):
            raw_api = {}
        updated_config: Dict[str, Any] = {
            "paths": values,
            "api": {key: str(raw_api.get(key, "") or "") for key in API_KEYS},
        }

        if self.on_complete is not None:
            try:
                self.on_complete(updated_config)
            except Exception as exc:  # noqa: BLE001
                self.status_lbl.configure(text=f"❌ Failed to save configuration: {exc}")
                return

        self.config_data = updated_config
        self.completed = True
        self.status_lbl.configure(text="✅ Saved.", text_color=COLOR_SUCCESS)
        self.destroy()