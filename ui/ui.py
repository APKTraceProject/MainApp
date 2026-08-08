import platform
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import tkinter.filedialog as filedialog
import customtkinter as ctk

# Set general appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def emoji_font(size: int):
    """Pick a font family per-OS that actually ships full-color emoji glyphs."""
    system = platform.system()
    if system == "Windows":
        family = "Segoe UI Emoji"
    elif system == "Darwin":
        family = "Apple Color Emoji"
    else:
        family = "Noto Color Emoji"
    return (family, size)


# Fonts
ICON_FONT_SIDEBAR = emoji_font(15)
TEXT_FONT_SIDEBAR = ("Arial", 14)
ICON_FONT_ROW = emoji_font(17)
TITLE_FONT_ROW = ("Arial", 14, "bold")

# Shared Palette
COLOR_BG = "#13141B"
COLOR_SIDEBAR = "#181920"
COLOR_SURFACE = "#1E1F28"
COLOR_SURFACE_HOVER = "#2B2C36"
COLOR_BORDER = "#2A2B36"
COLOR_ACCENT = "#4F3C96"
COLOR_ACCENT_HOVER = "#644DBA"
COLOR_ACCENT_TEXT = "#A984FF"
COLOR_ACCENT_SURFACE = "#1D1A31"
COLOR_ACCENT_BORDER = "#3D2D63"
COLOR_TEXT = "#DCE0E5"
COLOR_TEXT_MUTED = "gray"
COLOR_DISABLED = "#252630"
COLOR_SUCCESS = "#28A745"
COLOR_DANGER = "#DC3545"


class SidebarButton(ctk.CTkFrame):
    """Custom sidebar button with a fixed-width icon column."""

    def __init__(self, master, icon: str, text: str, command: Callable, **kwargs):
        super().__init__(master, corner_radius=6, cursor="hand2", **kwargs)
        self.command = command
        self.is_disabled = False

        self.default_fg = "transparent"
        self.hover_fg = COLOR_SURFACE_HOVER
        self.active_fg = COLOR_ACCENT_BORDER
        self.is_active = False

        self.configure(fg_color=self.default_fg, height=38)
        self.grid_propagate(False)

        self.grid_columnconfigure(0, weight=0, minsize=34)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.icon_lbl = ctk.CTkLabel(
            self,
            text=icon,
            font=ICON_FONT_SIDEBAR,
            fg_color="transparent",
            anchor="center",
            width=34,
        )
        self.icon_lbl.grid(row=0, column=0, sticky="nsw", padx=(12, 0), pady=0)

        self.lbl = ctk.CTkLabel(
            self,
            text=text,
            font=TEXT_FONT_SIDEBAR,
            text_color=COLOR_TEXT,
            fg_color="transparent",
            anchor="w",
        )
        self.lbl.grid(row=0, column=1, sticky="nsew", padx=(2, 12), pady=0)

        for widget in [self, self.icon_lbl, self.lbl]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)

    def on_enter(self, event):
        if not self.is_active and not self.is_disabled:
            self.configure(fg_color=self.hover_fg)

    def on_leave(self, event):
        if not self.is_active and not self.is_disabled:
            self.configure(fg_color=self.default_fg)

    def on_click(self, event):
        if not self.is_disabled and self.command:
            self.command()

    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self.configure(fg_color=self.active_fg)
            self.lbl.configure(text_color=COLOR_ACCENT_TEXT)
        else:
            self.configure(fg_color=self.default_fg)
            self.lbl.configure(text_color=COLOR_TEXT)

    def set_enabled(self, enabled: bool):
        self.is_disabled = not enabled
        if self.is_disabled:
            self.configure(cursor="arrow", fg_color="transparent")
            self.lbl.configure(text_color=COLOR_TEXT_MUTED)
        else:
            self.configure(cursor="hand2")
            if self.is_active:
                self.set_active(True)
            else:
                self.lbl.configure(text_color=COLOR_TEXT)


class ClickableRow(ctk.CTkFrame):
    """Custom frame for dashboard results list."""

    def __init__(
        self,
        master,
        icon: str,
        title: str,
        desc: str,
        command: Callable,
        is_ai: bool = False,
        **kwargs,
    ):
        super().__init__(master, corner_radius=8, cursor="hand2", **kwargs)
        self.command = command
        self.is_disabled = False

        self.default_color = COLOR_ACCENT_SURFACE if is_ai else COLOR_SURFACE
        self.hover_color = "#2B254A" if is_ai else COLOR_SURFACE_HOVER
        self.configure(
            fg_color=self.default_color,
            border_width=1,
            border_color=COLOR_ACCENT_BORDER if is_ai else COLOR_BORDER,
        )

        self.grid_columnconfigure(0, weight=0, minsize=38)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_color = COLOR_ACCENT_TEXT if is_ai else COLOR_TEXT

        self.icon_lbl = ctk.CTkLabel(
            self,
            text=icon,
            font=ICON_FONT_ROW,
            fg_color="transparent",
            anchor="center",
            width=38,
        )
        self.icon_lbl.grid(
            row=0, column=0, rowspan=2, sticky="nsw", padx=(16, 0), pady=(12, 12)
        )

        self.title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=TITLE_FONT_ROW,
            text_color=title_color,
            fg_color="transparent",
            anchor="w",
        )
        self.title_lbl.grid(
            row=0, column=1, sticky="sw", padx=(4, 10), pady=(12, 2)
        )

        self.desc_lbl = ctk.CTkLabel(
            self,
            text=desc,
            font=("Arial", 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color="transparent",
            anchor="w",
        )
        self.desc_lbl.grid(
            row=1, column=1, sticky="nw", padx=(4, 10), pady=(0, 12)
        )

        status_text = "✨ View  ˅" if is_ai else "− Results  ˅"
        status_color = COLOR_ACCENT_TEXT if is_ai else COLOR_TEXT_MUTED
        self.status_lbl = ctk.CTkLabel(
            self,
            text=status_text,
            font=("Arial", 12),
            text_color=status_color,
            fg_color="transparent",
        )
        self.status_lbl.grid(
            row=0, column=2, rowspan=2, padx=20, pady=15, sticky="e"
        )

        for widget in [
            self,
            self.icon_lbl,
            self.title_lbl,
            self.desc_lbl,
            self.status_lbl,
        ]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)

    def on_enter(self, event):
        if not self.is_disabled:
            self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        if not self.is_disabled:
            self.configure(fg_color=self.default_color)

    def on_click(self, event):
        if not self.is_disabled and self.command:
            self.command()

    def set_enabled(self, enabled: bool):
        self.is_disabled = not enabled
        self.configure(cursor="hand2" if enabled else "arrow")


# Import tab builders and custom tab components from tabs package
from .tabs import (
    PermissionsTab,
    add_chat_bubble,
    browse_path,
    build_chat_page,
    build_dashboard,
    build_jadx_analyzer_page,
    build_manifest_page,
    build_placeholder_page,
    build_settings_page,
    save_settings,
    update_dashboard_cards,
    update_jadx_analyzer_page,
    update_manifest_page,
)


class AndroidAnalyzerApp(ctk.CTk):

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        run_manifest_analysis: Optional[Callable] = None,
        run_java_analysis: Optional[Callable] = None,
        run_native_analysis: Optional[Callable] = None,
        save_config: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        super().__init__()

        self.config: Dict[str, Any] = config or {"paths": {}, "api": {}}
        self.run_manifest_analysis_fn = run_manifest_analysis
        self.run_java_analysis_fn = run_java_analysis
        self.run_native_analysis_fn = run_native_analysis
        self.save_config_fn = save_config

        self.title("Android Analyzer AI - APKTrace")
        self.geometry("1250x800")
        self.minsize(1000, 700)

        self.pages = {}
        self.nav_btns = {}
        self.scan_mode_btns = {}
        self.dashboard_cards = {}
        self.manifest_widgets = {}
        self.jadx_widgets = {}
        self.settings_path_entries = {}
        self.settings_api_entries = {}

        self.current_scan_mode = "Manifest"
        self.loaded_apk_path = None
        self.analysis_results = None
        self.is_analyzing = False

        self.grid_columnconfigure(0, weight=0)  # Sidebar column
        self.grid_columnconfigure(1, weight=1)  # Main Content column
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_content()

        # Initialization: set default scan mode to Manifest and open Dashboard
        self.set_scan_mode("Manifest")
        self.show_page("Dashboard")

    def create_sidebar(self):
        """Create the left navigation menu layout."""
        self.sidebar = ctk.CTkFrame(
            self, width=250, corner_radius=0, fg_color=COLOR_SIDEBAR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=25, pady=(22, 10))
        ctk.CTkLabel(brand_frame, text="🛡️", font=emoji_font(20)).pack(
            side="left"
        )
        ctk.CTkLabel(
            brand_frame,
            text="Android Analyzer",
            font=("Arial", 15, "bold"),
            text_color=COLOR_TEXT,
        ).pack(side="left", padx=(8, 0))
        ctk.CTkFrame(self.sidebar, fg_color=COLOR_BORDER, height=1).pack(
            fill="x", padx=25, pady=(4, 0)
        )

        # MAIN Category
        ctk.CTkLabel(
            self.sidebar,
            text="MAIN",
            text_color=COLOR_TEXT_MUTED,
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=25, pady=(20, 8))

        self.create_nav_btn(self.sidebar, "🏠", "Dashboard", "Dashboard")
        self.create_nav_btn(self.sidebar, "💬", "AI Assistant", "AI Assistant")
        self.create_nav_btn(self.sidebar, "⚙️", "Settings", "Settings")

        # SCAN MODES Category
        ctk.CTkLabel(
            self.sidebar,
            text="SCAN MODES",
            text_color=COLOR_TEXT_MUTED,
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=25, pady=(20, 8))

        modes_data = [
            ("📄", "Manifest"),
            ("☕", "Java / Kotlin"),
            ("⌨️", "Native Libraries"),
            ("🔤", "Strings"),
            ("🛡️", "Permissions"),
            ("📁", "Resources"),
            ("✨", "Full AI Analysis"),
        ]

        for icon, mode_name in modes_data:
            self.create_scan_mode_btn(self.sidebar, icon, mode_name)

    def create_nav_btn(self, parent, icon: str, text: str, page_name: str):
        """Create a navigation button for main tabs."""
        btn = SidebarButton(
            parent, icon, text, command=lambda: self.show_page(page_name)
        )
        btn.pack(fill="x", padx=20, pady=2)
        self.nav_btns[page_name] = btn

    def create_scan_mode_btn(self, parent, icon: str, mode_name: str):
        """Create a scan mode toggle button."""
        btn = SidebarButton(
            parent, icon, mode_name, command=lambda: self.set_scan_mode(mode_name)
        )
        btn.pack(fill="x", padx=20, pady=2)
        self.scan_mode_btns[mode_name] = btn

    def set_scan_mode(self, mode_name: str):
        """Select current scan mode without forcing a page switch."""
        if self.is_analyzing:
            return

        self.current_scan_mode = mode_name

        # Highlight selected scan mode button
        for name, btn in self.scan_mode_btns.items():
            btn.set_active(name == mode_name)

        # Update dashboard scan mode indicator if visible
        if hasattr(self, "mode_indicator_lbl") and self.mode_indicator_lbl:
            self.mode_indicator_lbl.configure(
                text=f"Active Scan Mode: {mode_name}"
            )

    def show_page(self, page_name: str):
        """Switch central view to the specified page/tab."""
        if self.is_analyzing and page_name != "Dashboard":
            return

        # Highlight selected main navigation button
        for name, btn in self.nav_btns.items():
            btn.set_active(name == page_name)

        # Hide all currently open pages
        for page in self.pages.values():
            page.grid_forget()

        # Display requested page
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")

    def create_main_content(self):
        """Initialize all central page containers."""
        self.main_container = ctk.CTkFrame(
            self, fg_color=COLOR_BG, corner_radius=0
        )
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Main pages
        self.pages["Dashboard"] = self.build_dashboard()
        self.pages["AI Assistant"] = self.build_chat_page()
        self.pages["Settings"] = self.build_settings_page()

        # Scan result pages
        self.pages["Manifest"] = self.build_manifest_page()
        self.pages["Java / Kotlin"] = self.build_jadx_analyzer_page()
        self.pages["Native Libraries"] = self.build_placeholder_page(
            "Native Libraries Analysis Results"
        )
        self.pages["Strings"] = self.build_placeholder_page(
            "Strings & Secrets Results"
        )

        # Full PermissionsTab custom component with back callback
        self.pages["Permissions"] = PermissionsTab(
            self.main_container, on_back=lambda: self.show_page("Dashboard")
        )

        self.pages["Resources"] = self.build_placeholder_page(
            "Resources Results"
        )
        self.pages["Full AI Analysis"] = self.build_placeholder_page(
            "Full AI Security Assessment Results"
        )

    def build_dashboard(self):
        return build_dashboard(self)

    def update_dashboard_cards(self, report: dict):
        return update_dashboard_cards(self, report)

    def choose_apk_file(self):
        if self.is_analyzing:
            return
        path = filedialog.askopenfilename(
            title="Select an APK file", filetypes=[("APK files", "*.apk")]
        )
        if not path:
            return
        self.loaded_apk_path = path
        file_name = Path(path).name
        self.apk_name_lbl.configure(text=file_name)
        self.apk_path_lbl.configure(text=path)
        self.apk_icon_lbl.configure(text="🤖", fg_color=COLOR_ACCENT)
        self.start_btn.configure(state="normal")

    def toggle_ui_interactivity(self, enabled: bool):
        """Enable or disable user interactions during active analysis."""
        self.is_analyzing = not enabled
        state = "normal" if enabled else "disabled"

        self.start_btn.configure(state=state)
        self.choose_btn.configure(state=state)

        for btn in self.nav_btns.values():
            btn.set_enabled(enabled)
        for btn in self.scan_mode_btns.values():
            btn.set_enabled(enabled)
        for row in getattr(self, "result_rows", []):
            row.set_enabled(enabled)

    def start_analysis_process(self):
        """Execute scan process for current mode."""
        if not self.loaded_apk_path:
            return

        if self.current_scan_mode == "Manifest":
            self.toggle_ui_interactivity(False)
            self.progress_frame.pack(
                fill="x",
                padx=30,
                pady=(10, 15),
                before=self.mode_indicator_lbl.master,
            )
            self.progress_bar.set(0.05)
            self.progress_status_lbl.configure(
                text="⚙️ Initializing analysis engine..."
            )

            threading.Thread(
                target=self._run_manifest_analysis_thread, daemon=True
            ).start()
        elif self.current_scan_mode == "Java / Kotlin":
            self.toggle_ui_interactivity(False)
            self.progress_frame.pack(
                fill="x",
                padx=30,
                pady=(10, 15),
                before=self.mode_indicator_lbl.master,
            )
            self.progress_bar.set(0.05)
            self.progress_status_lbl.configure(
                text="⚙️ Initializing analysis engine..."
            )

            threading.Thread(
                target=self._run_java_analysis_thread, daemon=True
            ).start()
        else:
            print(f"[*] Scan mode '{self.current_scan_mode}' is not yet connected.")

    def _run_java_analysis_thread(self):
        """Run the JADX -> LLM pipeline (Java/Kotlin scan mode)."""
        try:
            if self.run_java_analysis_fn is None:
                raise RuntimeError(
                    "Java/Kotlin analysis is not connected. Launch APKTrace via main.py so "
                    "the JADX Analyzer and the LLM analysis step get wired in."
                )

            report = self.run_java_analysis_fn(
                apk_path_str=self.loaded_apk_path,
                config=self.config,
                status_callback=self._update_progress_callback,
            )

            self.after(0, lambda: self._on_java_analysis_finished(report, None))
        except Exception as e:
            self.after(0, lambda: self._on_java_analysis_finished(None, str(e)))

    def _on_java_analysis_finished(self, report, error_msg):
        """Completion callback for the Java/Kotlin (JADX + LLM) scan mode.

        This is where the LLM's structured analysis JSON is handed to the
        JADX Analyzer tab.
        """
        self.toggle_ui_interactivity(True)
        self.progress_frame.pack_forget()

        if error_msg:
            self.progress_status_lbl.configure(text=f"❌ Error: {error_msg}")
            print(f"[ERROR] Java/Kotlin analysis failed: {error_msg}")
            return

        if not isinstance(report, dict):
            self.progress_status_lbl.configure(
                text="❌ Error: analyzer returned no usable data."
            )
            print(
                f"[ERROR] Java/Kotlin analysis returned an unexpected report type: {type(report)!r}"
            )
            return

        # <-- The JADX/LLM result is passed to the tab here.
        self.update_jadx_analyzer_page(report)

        # Show JADX Analyzer scan result page after completion
        self.show_page("Java / Kotlin")

    def _update_progress_callback(self, status_text: str, value: float):
        self.after(0, lambda: self._apply_progress_update(status_text, value))

    def _apply_progress_update(self, status_text: str, value: float):
        self.progress_status_lbl.configure(text=f"⚙️ {status_text}")
        self.progress_bar.set(value)

    def _run_manifest_analysis_thread(self):
        try:
            if self.run_manifest_analysis_fn is None:
                raise RuntimeError(
                    "Manifest analysis is not connected. Launch APKTrace via main.py so the "
                    "analyzer tools and config get wired in."
                )

            report = self.run_manifest_analysis_fn(
                apk_path_str=self.loaded_apk_path,
                config=self.config,
                status_callback=self._update_progress_callback,
            )

            self.after(0, lambda: self._on_analysis_finished(report, None))
        except Exception as e:
            self.after(0, lambda: self._on_analysis_finished(None, str(e)))

    def _on_analysis_finished(self, report, error_msg):
        self.toggle_ui_interactivity(True)
        self.progress_frame.pack_forget()

        if error_msg:
            self.progress_status_lbl.configure(text=f"❌ Error: {error_msg}")
            print(f"[ERROR] Analysis failed: {error_msg}")
            return

        if not isinstance(report, dict):
            self.progress_status_lbl.configure(
                text="❌ Error: analyzer returned no usable data."
            )
            print(
                f"[ERROR] Analysis returned an unexpected report type: {type(report)!r}"
            )
            return

        self.analysis_results = report
        self.update_dashboard_cards(report)
        self.update_manifest_page(report)

        # Pass permission data if available to PermissionsTab component
        if "permissions" in report and "Permissions" in self.pages:
            self.pages["Permissions"].update_permissions_data(
                report["permissions"]
            )

        # Show Manifest scan result page after completion
        self.show_page("Manifest")

    def build_manifest_page(self):
        return build_manifest_page(self)

    def update_manifest_page(self, report: dict):
        return update_manifest_page(self, report)

    def build_jadx_analyzer_page(self):
        return build_jadx_analyzer_page(self)

    def update_jadx_analyzer_page(self, report: dict):
        """Rebuild the JADX Analyzer tab from the LLM's structured analysis
        JSON. Call this once the Java/Kotlin analysis pipeline (JADX ->
        LLM) has produced its result dict, e.g. from a completion callback
        such as `_on_java_analysis_finished` below."""
        return update_jadx_analyzer_page(self, report)

    def build_settings_page(self):
        return build_settings_page(self)

    def _browse_path(self, entry_widget: ctk.CTkEntry, kind: str):
        return browse_path(entry_widget, kind)

    def save_settings(self):
        return save_settings(self)

    def build_chat_page(self):
        return build_chat_page(self)

    def add_chat_bubble(self, parent_frame, text: str, is_ai: bool = True):
        return add_chat_bubble(parent_frame, text, is_ai)

    def build_placeholder_page(self, title: str):
        return build_placeholder_page(self, title)