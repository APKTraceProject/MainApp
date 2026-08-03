import platform
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import tkinter.filedialog as filedialog
import customtkinter as ctk

# Set general appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def emoji_font(size):
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
    def __init__(self, master, icon, text, command, **kwargs):
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
    def __init__(self, master, icon, title, desc, command, is_ai=False, **kwargs):
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
        self.icon_lbl.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(16, 0), pady=(12, 12))

        self.title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=TITLE_FONT_ROW,
            text_color=title_color,
            fg_color="transparent",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=1, sticky="sw", padx=(4, 10), pady=(12, 2))

        self.desc_lbl = ctk.CTkLabel(
            self,
            text=desc,
            font=("Arial", 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color="transparent",
            anchor="w",
        )
        self.desc_lbl.grid(row=1, column=1, sticky="nw", padx=(4, 10), pady=(0, 12))

        status_text = "✨ View  ˅" if is_ai else "− Results  ˅"
        status_color = COLOR_ACCENT_TEXT if is_ai else COLOR_TEXT_MUTED
        self.status_lbl = ctk.CTkLabel(
            self,
            text=status_text,
            font=("Arial", 12),
            text_color=status_color,
            fg_color="transparent",
        )
        self.status_lbl.grid(row=0, column=2, rowspan=2, padx=20, pady=15, sticky="e")

        for widget in [self, self.icon_lbl, self.title_lbl, self.desc_lbl, self.status_lbl]:
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

        # Config + analysis/save callables are injected from main.py, which owns
        # all business logic (config file, path validation, running the tools).
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
        self.settings_path_entries = {}
        self.settings_api_entries = {}

        self.current_scan_mode = "Manifest"
        self.loaded_apk_path = None
        self.analysis_results = None
        self.is_analyzing = False

        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main Content
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_content()

        # Default view
        self.show_page("Dashboard")
        self.set_scan_mode("Manifest")

    def create_sidebar(self):
        """Create the left navigation menu"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=25, pady=(22, 10))
        ctk.CTkLabel(brand_frame, text="🛡️", font=emoji_font(20)).pack(side="left")
        ctk.CTkLabel(brand_frame, text="Android Analyzer", font=("Arial", 15, "bold"), text_color=COLOR_TEXT).pack(side="left", padx=(8, 0))
        ctk.CTkFrame(self.sidebar, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=25, pady=(4, 0))

        # MAIN Category
        ctk.CTkLabel(self.sidebar, text="MAIN", text_color=COLOR_TEXT_MUTED, font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(20, 8))

        self.create_nav_btn(self.sidebar, "🏠", "Dashboard", "Dashboard")
        self.create_nav_btn(self.sidebar, "💬", "AI Assistant", "AI Assistant")
        self.create_nav_btn(self.sidebar, "⚙️", "Settings", "Settings")

        # SCAN MODES Category
        ctk.CTkLabel(self.sidebar, text="SCAN MODES", text_color=COLOR_TEXT_MUTED, font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(20, 8))

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

    def create_nav_btn(self, parent, icon, text, page_name):
        btn = SidebarButton(parent, icon, text, command=lambda: self.show_page(page_name))
        btn.pack(fill="x", padx=20, pady=2)
        self.nav_btns[page_name] = btn

    def create_scan_mode_btn(self, parent, icon, mode_name):
        btn = SidebarButton(parent, icon, mode_name, command=lambda: self.set_scan_mode(mode_name))
        btn.pack(fill="x", padx=20, pady=2)
        self.scan_mode_btns[mode_name] = btn

    def set_scan_mode(self, mode_name):
        if self.is_analyzing:
            return
        self.current_scan_mode = mode_name
        for name, btn in self.scan_mode_btns.items():
            btn.set_active(name == mode_name)

        if hasattr(self, "mode_indicator_lbl"):
            self.mode_indicator_lbl.configure(text=f"Active Scan Mode: {mode_name}")

    def create_main_content(self):
        """Create the central container holding all pages"""
        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.pages["Dashboard"] = self.build_dashboard()
        self.pages["AI Assistant"] = self.build_chat_page()
        self.pages["Settings"] = self.build_settings_page()

        # Manifest page is built ONCE as an empty skeleton and updated in place
        # whenever an analysis finishes (see update_manifest_page). It is never
        # torn down and rebuilt, so it stays visible - just empty - even if no
        # scan has run yet.
        self.pages["Manifest"] = self.build_manifest_page()
        self.pages["Java / Kotlin"] = self.build_placeholder_page("Java / Kotlin Analysis Results")
        self.pages["Native Libraries"] = self.build_placeholder_page("Native Libraries Analysis Results")
        self.pages["Strings"] = self.build_placeholder_page("Strings & Secrets Results")
        self.pages["Permissions"] = self.build_placeholder_page("Permissions Usage Results")
        self.pages["Resources"] = self.build_placeholder_page("Resources Results")
        self.pages["Full AI Analysis"] = self.build_placeholder_page("Full AI Security Assessment Results")

    def build_dashboard(self):
        """Build the main dashboard view"""
        page = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

        # APK Load Header Box
        self.apk_frame = ctk.CTkFrame(
            page,
            fg_color=COLOR_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self.apk_frame.pack(fill="x", padx=30, pady=(30, 15))

        self.apk_icon_lbl = ctk.CTkLabel(
            self.apk_frame,
            text="📦",
            font=emoji_font(26),
            fg_color=COLOR_DISABLED,
            text_color="white",
            corner_radius=8,
            width=56,
            height=56,
        )
        self.apk_icon_lbl.pack(side="left", padx=20, pady=20)

        info_frame = ctk.CTkFrame(self.apk_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="y", pady=20)
        self.apk_name_lbl = ctk.CTkLabel(
            info_frame,
            text="No APK selected",
            font=("Arial", 16, "bold"),
            text_color=COLOR_TEXT,
        )
        self.apk_name_lbl.pack(anchor="w")
        self.apk_path_lbl = ctk.CTkLabel(
            info_frame,
            text='Click "Choose File" to load an .apk for analysis',
            font=("Arial", 12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.apk_path_lbl.pack(anchor="w")

        self.start_btn = ctk.CTkButton(
            self.apk_frame,
            text="▶ Start Analysis",
            height=40,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            state="disabled",
            command=self.start_analysis_process,
        )
        self.start_btn.pack(side="right", padx=20)

        self.choose_btn = ctk.CTkButton(
            self.apk_frame,
            text="Choose File",
            height=40,
            fg_color=COLOR_SURFACE_HOVER,
            hover_color="#3D3E4A",
            command=self.choose_apk_file,
        )
        self.choose_btn.pack(side="right", padx=10)

        # Progress / Status Frame (Hidden initially)
        self.progress_frame = ctk.CTkFrame(
            page,
            fg_color=COLOR_ACCENT_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_ACCENT_BORDER,
        )

        self.progress_status_lbl = ctk.CTkLabel(
            self.progress_frame,
            text="⏳ Starting analysis...",
            font=("Arial", 13, "bold"),
            text_color=COLOR_ACCENT_TEXT,
        )
        self.progress_status_lbl.pack(anchor="w", padx=20, pady=(12, 6))

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=10,
            corner_radius=5,
            progress_color=COLOR_ACCENT_TEXT,
            fg_color=COLOR_SURFACE,
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 15))
        self.progress_bar.set(0)

        # Active Scan Mode Indicator
        mode_banner = ctk.CTkFrame(
            page,
            fg_color=COLOR_ACCENT_SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_ACCENT_BORDER,
        )
        mode_banner.pack(fill="x", padx=30, pady=(5, 10))
        self.mode_indicator_lbl = ctk.CTkLabel(
            mode_banner,
            text=f"Active Scan Mode: {self.current_scan_mode}",
            font=("Arial", 13, "bold"),
            text_color=COLOR_ACCENT_TEXT,
        )
        self.mode_indicator_lbl.pack(padx=20, pady=12, anchor="w")

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

            self.dashboard_cards[title] = (val_lbl, sub_lbl)

        res_lbl = ctk.CTkLabel(page, text="Analysis Results (Click to view tab)", font=("Arial", 14, "bold"), text_color=COLOR_ACCENT_TEXT)
        res_lbl.pack(anchor="w", padx=30, pady=(25, 10))

        self.list_frame = ctk.CTkFrame(page, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=30)

        results_data = [
            ("📄", "Manifest", "Package info, components, permissions and configuration", "Manifest"),
            ("☕", "Java / Kotlin", "Decompiled source code analysis and security checks", "Java / Kotlin"),
            ("⌨️", "Native Libraries", "Ghidra & Radare2 analysis of native libraries", "Native Libraries"),
            ("🔤", "Strings", "Important strings, URLs, IPs and hidden data", "Strings"),
            ("🛡️", "Permissions", "Check how dangerous permissions are used in code", "Permissions"),
            ("📁", "Resources", "Resource files and asset analysis", "Resources"),
        ]

        self.result_rows = []
        for icon, title, desc, target_page in results_data:
            row = ClickableRow(
                self.list_frame,
                icon,
                title,
                desc,
                command=lambda tp=target_page: self.show_page(tp),
            )
            row.pack(fill="x", pady=6)
            self.result_rows.append(row)

        ai_row = ClickableRow(
            self.list_frame,
            "✨",
            "Full AI Analysis",
            "Overall evaluation and recommendations by AI",
            command=lambda: self.show_page("Full AI Analysis"),
            is_ai=True,
        )
        ai_row.pack(fill="x", pady=(15, 30))
        self.result_rows.append(ai_row)

        return page

    def choose_apk_file(self):
        if self.is_analyzing:
            return
        path = filedialog.askopenfilename(title="Select an APK file", filetypes=[("APK files", "*.apk")])
        if not path:
            return
        self.loaded_apk_path = path
        file_name = Path(path).name
        self.apk_name_lbl.configure(text=file_name)
        self.apk_path_lbl.configure(text=path)
        self.apk_icon_lbl.configure(text="🤖", fg_color=COLOR_ACCENT)
        self.start_btn.configure(state="normal")

    def toggle_ui_interactivity(self, enabled: bool):
        """Enable or disable all navigation/actions during scanning"""
        self.is_analyzing = not enabled
        state = "normal" if enabled else "disabled"

        self.start_btn.configure(state=state)
        self.choose_btn.configure(state=state)

        for btn in self.nav_btns.values():
            btn.set_enabled(enabled)
        for btn in self.scan_mode_btns.values():
            btn.set_enabled(enabled)
        for row in self.result_rows:
            row.set_enabled(enabled)

    def start_analysis_process(self):
        """Initiate analysis thread if Manifest mode is active"""
        if not self.loaded_apk_path:
            return

        if self.current_scan_mode == "Manifest":
            self.toggle_ui_interactivity(False)
            self.progress_frame.pack(fill="x", padx=30, pady=(10, 15), before=self.mode_indicator_lbl.master)
            self.progress_bar.set(0.05)
            self.progress_status_lbl.configure(text="⚙️ Initializing analysis engine...")

            # Run in worker thread to prevent UI freezing
            threading.Thread(target=self._run_manifest_analysis_thread, daemon=True).start()
        else:
            print(f"[*] Scan mode '{self.current_scan_mode}' is not yet connected.")

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

        self.analysis_results = report
        self.update_dashboard_cards(report)
        self.update_manifest_page(report)

        # Switch to Manifest tab upon completion
        self.show_page("Manifest")

    def update_dashboard_cards(self, report: dict):
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
            if title in self.dashboard_cards:
                val_lbl, sub_lbl = self.dashboard_cards[title]
                val_lbl.configure(text=val)
                if title == "Risk Level":
                    val_lbl.configure(text_color=risk[1])
                sub_lbl.configure(text=sub)

    # ------------------------------------------------------------------ #
    # Manifest page: built ONCE (empty), then only its widgets are updated
    # ------------------------------------------------------------------ #
    def build_manifest_page(self):
        """Build the Manifest Analysis tab's full layout, empty from the start.

        All the cards/sections a completed scan would fill in are already
        present here (just showing placeholder values). update_manifest_page()
        later fills in the same widgets in place - the page itself is never
        rebuilt, so nothing "appears" only after clicking Analyze.
        """
        page = ctk.CTkFrame(self.main_container, fg_color="transparent")
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
            command=lambda: self.show_page("Dashboard"),
        ).pack(side="right")

        # Scrollable Body Container
        body = ctk.CTkScrollableFrame(page, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

        self.manifest_widgets = {}

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

        self.manifest_widgets["metadata"] = {}
        for i, label in enumerate(metadata_labels):
            r, c = divmod(i, 2)
            lbl_widget = ctk.CTkLabel(grid_frame, text=f"{label} ", font=("Arial", 13, "bold"), text_color=COLOR_TEXT_MUTED)
            lbl_widget.grid(row=r, column=c * 2, sticky="w", pady=4, padx=(0, 5))

            val_widget = ctk.CTkLabel(grid_frame, text="—", font=("Arial", 13), text_color=COLOR_TEXT)
            val_widget.grid(row=r, column=c * 2 + 1, sticky="w", pady=4, padx=(0, 30))
            self.manifest_widgets["metadata"][label] = val_widget

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

        self.manifest_widgets["flags"] = {}
        for i, (flag_name, flag_desc) in enumerate(flags_defs):
            f_lbl = ctk.CTkLabel(flags_grid, text=flag_name, font=("Arial", 13, "bold"), text_color=COLOR_TEXT)
            f_lbl.grid(row=i, column=0, sticky="w", pady=6)

            badge = ctk.CTkLabel(flags_grid, text=" UNSPECIFIED ", font=("Arial", 11, "bold"), fg_color=COLOR_SURFACE_HOVER, corner_radius=4)
            badge.grid(row=i, column=1, sticky="w", padx=15, pady=6)

            d_lbl = ctk.CTkLabel(flags_grid, text=flag_desc, font=("Arial", 12), text_color=COLOR_TEXT_MUTED)
            d_lbl.grid(row=i, column=2, sticky="w", pady=6)

            self.manifest_widgets["flags"][flag_name] = badge

        # 3. Permissions Section
        perms_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        perms_card.pack(fill="x", pady=(0, 15), padx=5)

        perms_title_lbl = ctk.CTkLabel(perms_card, text="DECLARED PERMISSIONS (0)", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED)
        perms_title_lbl.pack(anchor="w", padx=20, pady=(15, 10))

        perms_box = ctk.CTkTextbox(perms_card, height=130, fg_color=COLOR_BG, font=("Consolas", 12), text_color=COLOR_ACCENT_TEXT)
        perms_box.pack(fill="x", padx=20, pady=(0, 15))
        perms_box.insert("end", "No data yet — select an APK on Dashboard and run 'Manifest' analysis.")
        perms_box.configure(state="disabled")

        self.manifest_widgets["perms_title"] = perms_title_lbl
        self.manifest_widgets["perms_box"] = perms_box

        # 4. Components Section
        comps_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        comps_card.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(comps_card, text="MANIFEST COMPONENTS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

        tabview = ctk.CTkTabview(comps_card, fg_color=COLOR_BG)
        tabview.pack(fill="x", padx=20, pady=(0, 15))

        self.manifest_widgets["comp_boxes"] = {}
        for c_type in ["activities", "services", "receivers", "providers"]:
            tab = tabview.add(c_type.capitalize())

            box = ctk.CTkTextbox(tab, height=150, fg_color="transparent", font=("Consolas", 12), text_color=COLOR_TEXT)
            box.pack(fill="both", expand=True)
            box.insert("end", "No data yet.")
            box.configure(state="disabled")

            self.manifest_widgets["comp_boxes"][c_type] = box

        return page

    def update_manifest_page(self, report: dict):
        """Fill in the already-built Manifest page with results from a completed scan."""
        widgets = self.manifest_widgets
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

    # ------------------------------------------------------------------ #
    # Settings page (renamed from "API Settings"): manages the 4 shared
    # tool paths AND the API section, both persisted through save_config_fn
    # ------------------------------------------------------------------ #
    def build_settings_page(self):
        page = ctk.CTkFrame(self.main_container, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="⚙️ Settings", font=("Arial", 26, "bold"), text_color=COLOR_ACCENT_TEXT).pack(side="left")

        body = ctk.CTkScrollableFrame(page, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))

        current_paths = self.config.get("paths", {}) or {}
        current_api = self.config.get("api", {}) or {}

        # --- Tool paths section ---
        paths_card = ctk.CTkFrame(body, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_BORDER)
        paths_card.pack(fill="x", pady=(0, 15), padx=5)
        ctk.CTkLabel(paths_card, text="TOOL PATHS", font=("Arial", 12, "bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=20, pady=(15, 10))

        path_fields = [
            ("output_dir", "Output Directory", "dir"),
            ("apktool_path", "Apktool Path (.jar / executable)", "file"),
            ("jadx_path", "Jadx Path (executable / bat)", "file"),
            ("ghidra_path", "Ghidra Path (script / executable)", "file"),
        ]

        self.settings_path_entries = {}
        for key, label, kind in path_fields:
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
                command=lambda e=entry, k=kind: self._browse_path(e, k),
            ).pack(side="left")

            self.settings_path_entries[key] = entry

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

        self.settings_api_entries = {}
        for key, label, show_char in api_fields:
            row = ctk.CTkFrame(api_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(row, text=label, font=("Arial", 13), text_color=COLOR_TEXT, width=210, anchor="w").pack(side="left")

            entry = ctk.CTkEntry(row, fg_color=COLOR_SURFACE_HOVER, border_width=0, height=35, show=show_char)
            entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
            entry.insert(0, current_api.get(key, "") or "")

            self.settings_api_entries[key] = entry

        api_card_spacer = ctk.CTkFrame(api_card, fg_color="transparent", height=5)
        api_card_spacer.pack(fill="x", pady=(0, 10))

        # --- Save button + status ---
        save_row = ctk.CTkFrame(body, fg_color="transparent")
        save_row.pack(fill="x", pady=(5, 20), padx=5)

        self.settings_status_lbl = ctk.CTkLabel(save_row, text="", font=("Arial", 12), text_color=COLOR_TEXT_MUTED)
        self.settings_status_lbl.pack(side="left")

        ctk.CTkButton(
            save_row,
            text="💾 Save Settings",
            height=40,
            width=160,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            command=self.save_settings,
        ).pack(side="right")

        return page

    def _browse_path(self, entry_widget: ctk.CTkEntry, kind: str):
        path = (
            filedialog.askdirectory(title="Select Directory")
            if kind == "dir"
            else filedialog.askopenfilename(title="Select File")
        )
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def save_settings(self):
        new_paths = {key: entry.get().strip() for key, entry in self.settings_path_entries.items()}
        new_api = {key: entry.get().strip() for key, entry in self.settings_api_entries.items()}
        updated_config = {"paths": new_paths, "api": new_api}

        if self.save_config_fn is None:
            self.settings_status_lbl.configure(text="⚠️ Save handler not available.", text_color=COLOR_DANGER)
            return

        try:
            self.save_config_fn(updated_config)
        except Exception as exc:  # noqa: BLE001
            self.settings_status_lbl.configure(text=f"❌ Failed to save: {exc}", text_color=COLOR_DANGER)
            return

        self.config = updated_config
        self.settings_status_lbl.configure(text="✅ Settings saved.", text_color=COLOR_SUCCESS)

    def build_chat_page(self):
        page = ctk.CTkFrame(self.main_container, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text="💬 AI Assistant Chat", font=("Arial", 26, "bold"), text_color=COLOR_ACCENT_TEXT).pack(side="left")

        chat_box = ctk.CTkFrame(
            page,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        chat_box.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        chat_box.grid_columnconfigure(0, weight=1)
        chat_box.grid_rowconfigure(0, weight=1)

        chat_history = ctk.CTkScrollableFrame(chat_box, fg_color="transparent")
        chat_history.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        self.add_chat_bubble(chat_history, "🤖 Hello! I'm your AI assistant. Load an APK and ask me anything about it.", is_ai=True)

        input_frame = ctk.CTkFrame(chat_box, fg_color="transparent", height=80)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=15)

        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your question about the APK here...",
            fg_color=COLOR_SURFACE_HOVER,
            border_width=0,
            height=45,
            font=("Arial", 13),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=100,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
        )
        send_btn.pack(side="right")

        return page

    def add_chat_bubble(self, parent_frame, text, is_ai=True):
        color = COLOR_SURFACE_HOVER if is_ai else "#312061"
        align = "w" if is_ai else "e"

        msg_frame = ctk.CTkFrame(parent_frame, fg_color=color, corner_radius=10)
        msg_frame.pack(anchor=align, pady=10, padx=10, fill="x", expand=False)

        lbl = ctk.CTkLabel(msg_frame, text=text, justify="left", font=("Arial", 13), text_color="white", wraplength=700)
        lbl.pack(padx=20, pady=12, anchor="w")

    def build_placeholder_page(self, title):
        page = ctk.CTkFrame(self.main_container, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 15))
        ctk.CTkLabel(header_frame, text=title, font=("Arial", 26, "bold"), text_color=COLOR_ACCENT_TEXT).pack(side="left")

        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Dashboard",
            width=160,
            height=35,
            fg_color=COLOR_SURFACE_HOVER,
            hover_color="#3D3E4A",
            command=lambda: self.show_page("Dashboard"),
        )
        back_btn.pack(side="right")

        content_box = ctk.CTkFrame(
            page,
            fg_color=COLOR_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        content_box.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))

        ctk.CTkLabel(
            content_box,
            text=f"No data yet — run an analysis to populate '{title}'.",
            font=("Arial", 15),
            text_color=COLOR_TEXT_MUTED,
        ).pack(expand=True)

        return page

    def show_page(self, page_name):
        if self.is_analyzing and page_name != "Dashboard":
            return

        for name, btn in self.nav_btns.items():
            btn.set_active(name == page_name)

        for page in self.pages.values():
            page.grid_forget()

        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")