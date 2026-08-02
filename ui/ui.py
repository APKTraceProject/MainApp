import platform
import tkinter.filedialog as filedialog
import customtkinter as ctk

# Set general appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def emoji_font(size):
    """
    Pick a font family per-OS that actually ships full-color emoji glyphs.
    Tk only renders emoji in color if the font family itself is a color-emoji
    font; a generic family like "Arial" falls back to a black-and-white
    symbol glyph (or nothing) on most systems.
    """
    system = platform.system()
    if system == "Windows":
        family = "Segoe UI Emoji"
    elif system == "Darwin":
        family = "Apple Color Emoji"
    else:
        family = "Noto Color Emoji"
    return (family, size)


# Fonts used for icons vs text are kept separate on purpose
ICON_FONT_SIDEBAR = emoji_font(15)
TEXT_FONT_SIDEBAR = ("Arial", 14)
ICON_FONT_ROW = emoji_font(17)
TITLE_FONT_ROW = ("Arial", 14, "bold")

# Shared palette so colors stay consistent across the whole app
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
COLOR_DISABLED = "#33343E"


class SidebarButton(ctk.CTkFrame):
    """Custom sidebar button with a fixed-width icon column so icon and text align perfectly."""
    def __init__(self, master, icon, text, command, **kwargs):
        super().__init__(master, corner_radius=6, cursor="hand2", **kwargs)
        self.command = command

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
        if not self.is_active:
            self.configure(fg_color=self.hover_fg)

    def on_leave(self, event):
        if not self.is_active:
            self.configure(fg_color=self.default_fg)

    def on_click(self, event):
        self.command()

    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self.configure(fg_color=self.active_fg)
            self.lbl.configure(text_color=COLOR_ACCENT_TEXT)
        else:
            self.configure(fg_color=self.default_fg)
            self.lbl.configure(text_color=COLOR_TEXT)


class ClickableRow(ctk.CTkFrame):
    """Custom frame for dashboard results list with a fixed-width icon column for perfect alignment."""
    def __init__(self, master, icon, title, desc, command, is_ai=False, **kwargs):
        super().__init__(master, corner_radius=8, cursor="hand2", **kwargs)
        self.command = command

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
        self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        self.configure(fg_color=self.default_color)

    def on_click(self, event):
        self.command()


class AndroidAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Android Analyzer AI")
        self.geometry("1250x800")
        self.minsize(1000, 700)

        self.pages = {}
        self.nav_btns = {}
        self.scan_mode_btns = {}

        self.current_scan_mode = "Manifest"
        self.loaded_apk_path = None

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
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLOR_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=25, pady=(22, 10))
        ctk.CTkLabel(brand_frame, text="🛡️", font=emoji_font(20)).pack(side="left")
        ctk.CTkLabel(brand_frame, text="Android Analyzer", font=("Arial", 15, "bold"), text_color=COLOR_TEXT).pack(side="left", padx=(8, 0))
        ctk.CTkFrame(sidebar, fg_color=COLOR_BORDER, height=1).pack(fill="x", padx=25, pady=(4, 0))

        # MAIN Category
        ctk.CTkLabel(sidebar, text="MAIN", text_color=COLOR_TEXT_MUTED, font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(20, 8))

        self.create_nav_btn(sidebar, "🏠", "Dashboard", "Dashboard")
        self.create_nav_btn(sidebar, "💬", "AI Assistant", "AI Assistant")
        self.create_nav_btn(sidebar, "⚙️", "API Settings", "API Settings")

        # SCAN MODES Category
        ctk.CTkLabel(sidebar, text="SCAN MODES", text_color=COLOR_TEXT_MUTED, font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(20, 8))

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
            self.create_scan_mode_btn(sidebar, icon, mode_name)

    def create_nav_btn(self, parent, icon, text, page_name):
        """Helper to create main navigation buttons"""
        btn = SidebarButton(parent, icon, text, command=lambda: self.show_page(page_name))
        btn.pack(fill="x", padx=20, pady=2)
        self.nav_btns[page_name] = btn

    def create_scan_mode_btn(self, parent, icon, mode_name):
        """Helper to create scan mode selection buttons"""
        btn = SidebarButton(parent, icon, mode_name, command=lambda: self.set_scan_mode(mode_name))
        btn.pack(fill="x", padx=20, pady=2)
        self.scan_mode_btns[mode_name] = btn

    def set_scan_mode(self, mode_name):
        """Select scan mode without changing tabs"""
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
        self.pages["API Settings"] = self.build_placeholder_page("API Settings")

        self.pages["Manifest"] = self.build_placeholder_page("Manifest Analysis Results")
        self.pages["Java / Kotlin"] = self.build_placeholder_page("Java / Kotlin Analysis Results")
        self.pages["Native Libraries"] = self.build_placeholder_page("Native Libraries Analysis Results")
        self.pages["Strings"] = self.build_placeholder_page("Strings & Secrets Results")
        self.pages["Permissions"] = self.build_placeholder_page("Permissions Usage Results")
        self.pages["Resources"] = self.build_placeholder_page("Resources Results")
        self.pages["Full AI Analysis"] = self.build_placeholder_page("Full AI Security Assessment Results")

    def build_dashboard(self):
        """Build the main dashboard view"""
        page = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

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
            command=lambda: print(f"Running scan with mode: {self.current_scan_mode}"),
        )
        self.start_btn.pack(side="right", padx=20)
        ctk.CTkButton(
            self.apk_frame,
            text="Choose File",
            height=40,
            fg_color=COLOR_SURFACE_HOVER,
            hover_color="#3D3E4A",
            command=self.choose_apk_file,
        ).pack(side="right", padx=10)

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
            ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold"), text_color=COLOR_TEXT).pack(pady=5)
            ctk.CTkLabel(card, text=sub, font=("Arial", 11), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 15))

        res_lbl = ctk.CTkLabel(page, text="Analysis Results (Click to view tab)", font=("Arial", 14, "bold"), text_color=COLOR_ACCENT_TEXT)
        res_lbl.pack(anchor="w", padx=30, pady=(25, 10))

        list_frame = ctk.CTkFrame(page, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=30)

        results_data = [
            ("📄", "Manifest", "Package info, components, permissions and configuration", "Manifest"),
            ("☕", "Java / Kotlin", "Decompiled source code analysis and security checks", "Java / Kotlin"),
            ("⌨️", "Native Libraries", "Ghidra & Radare2 analysis of native libraries", "Native Libraries"),
            ("🔤", "Strings", "Important strings, URLs, IPs and hidden data", "Strings"),
            ("🛡️", "Permissions", "Check how dangerous permissions are used in code", "Permissions"),
            ("📁", "Resources", "Resource files and asset analysis", "Resources"),
        ]

        for icon, title, desc, target_page in results_data:
            ClickableRow(
                list_frame,
                icon,
                title,
                desc,
                command=lambda tp=target_page: self.show_page(tp),
            ).pack(fill="x", pady=6)

        ClickableRow(
            list_frame,
            "✨",
            "Full AI Analysis",
            "Overall evaluation and recommendations by AI",
            command=lambda: self.show_page("Full AI Analysis"),
            is_ai=True,
        ).pack(fill="x", pady=(15, 30))

        return page

    def choose_apk_file(self):
        """Let the user pick a real .apk file"""
        path = filedialog.askopenfilename(title="Select an APK file", filetypes=[("APK files", "*.apk")])
        if not path:
            return
        self.loaded_apk_path = path
        file_name = path.split("/")[-1].split("\\")[-1]
        self.apk_name_lbl.configure(text=file_name)
        self.apk_path_lbl.configure(text=path)
        self.apk_icon_lbl.configure(text="🤖", fg_color=COLOR_ACCENT)
        self.start_btn.configure(state="normal")

    def build_chat_page(self):
        """Build the dedicated full-page AI Assistant chat tab"""
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
        """Helper to add chat bubbles with proper text wrapping"""
        color = COLOR_SURFACE_HOVER if is_ai else "#312061"
        align = "w" if is_ai else "e"

        msg_frame = ctk.CTkFrame(parent_frame, fg_color=color, corner_radius=10)
        msg_frame.pack(anchor=align, pady=10, padx=10, fill="x", expand=False)

        lbl = ctk.CTkLabel(msg_frame, text=text, justify="left", font=("Arial", 13), text_color="white", wraplength=700)
        lbl.pack(padx=20, pady=12, anchor="w")

    def build_placeholder_page(self, title):
        """Build placeholder pages for specific result tabs"""
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
        """Manage main view navigation"""
        for name, btn in self.nav_btns.items():
            btn.set_active(name == page_name)

        for page in self.pages.values():
            page.grid_forget()

        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")