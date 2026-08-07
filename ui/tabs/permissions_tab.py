from typing import Callable, Optional
import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT,
    COLOR_ACCENT_BORDER,
    COLOR_ACCENT_HOVER,
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


class PermissionsTab(ctk.CTkFrame):
    def __init__(self, master, on_back: Optional[Callable] = None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)

        self.on_back = on_back
        self.all_permissions = []

        # Grid configuration matching manifest page layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Build Header & Scrollable Body Container
        self._build_header()
        self._build_body()

    def _build_header(self):
        """Header structured exactly like Manifest page (Title Left, Back Button Right)."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))

        # Title on the left
        lbl_title = ctk.CTkLabel(
            header,
            text="🛡️ Permissions Analysis",
            font=("Arial", 24, "bold"),
            text_color=COLOR_ACCENT_TEXT,
        )
        lbl_title.pack(side="left")

        # Back to Dashboard button on the right
        btn_back = ctk.CTkButton(
            header,
            text="← Back to Dashboard",
            width=150,
            height=35,
            fg_color=COLOR_SURFACE_HOVER,
            hover_color="#3D3E4A",
            text_color=COLOR_TEXT,
            command=self._handle_back,
        )
        btn_back.pack(side="right")

    def _handle_back(self):
        """Return to Dashboard via callback or dynamic lookup."""
        if self.on_back:
            self.on_back()
        else:
            parent = self.master
            while parent and not hasattr(parent, "show_page"):
                parent = getattr(parent, "master", None)
            if parent and hasattr(parent, "show_page"):
                parent.show_page("Dashboard")

    def _build_body(self):
        """Scrollable Body Container containing analysis cards."""
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.body.grid_columnconfigure(0, weight=1)

        # 1. Summary Cards Section
        self._build_stat_cards()

        # 2. Search & Filter Bar Section
        self._build_search_filter_bar()

        # 3. Permissions List Section
        self._build_permissions_list()

    def _build_stat_cards(self):
        """Summary cards mimicking Application Metadata/Flags layout."""
        cards_card = ctk.CTkFrame(
            self.body,
            fg_color=COLOR_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        cards_card.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(
            cards_card,
            text="PERMISSIONS OVERVIEW",
            font=("Arial", 12, "bold"),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(15, 10))

        grid_frame = ctk.CTkFrame(cards_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20, pady=(0, 15))
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat_card")

        self.card_total_val = self._create_stat_card(
            grid_frame, col=0, title="TOTAL PERMISSIONS", icon="📜", color=COLOR_ACCENT_TEXT
        )
        self.card_danger_val = self._create_stat_card(
            grid_frame, col=1, title="DANGEROUS PERMISSIONS", icon="🚨", color=COLOR_DANGER
        )
        self.card_normal_val = self._create_stat_card(
            grid_frame, col=2, title="NORMAL / OTHER", icon="🛡️", color=COLOR_SUCCESS
        )

    def _create_stat_card(self, parent, col: int, title: str, icon: str, color: str):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BG,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=8,
        )
        card.grid(row=0, column=col, padx=6, pady=5, sticky="ew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=12)

        top_line = ctk.CTkFrame(content, fg_color="transparent")
        top_line.pack(fill="x")

        ctk.CTkLabel(
            top_line,
            text=title,
            font=("Arial", 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
        ).pack(side="left")

        ctk.CTkLabel(top_line, text=icon, font=("Arial", 13)).pack(side="right")

        val_lbl = ctk.CTkLabel(
            content,
            text="0",
            font=("Arial", 20, "bold"),
            text_color=color,
            anchor="w",
        )
        val_lbl.pack(anchor="w", pady=(4, 0))

        return val_lbl

    def _build_search_filter_bar(self):
        """Search box and segmented category button."""
        filter_card = ctk.CTkFrame(
            self.body,
            fg_color=COLOR_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        filter_card.pack(fill="x", pady=(0, 15), padx=5)

        bar_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        bar_frame.pack(fill="x", padx=20, pady=15)
        bar_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar_frame,
            placeholder_text="🔍 Search permission name or description...",
            fg_color=COLOR_BG,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT,
            placeholder_text_color=COLOR_TEXT_MUTED,
            height=36,
            corner_radius=6,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self._apply_filters)

        self.filter_segment = ctk.CTkSegmentedButton(
            bar_frame,
            values=["All", "Dangerous", "Normal"],
            command=self._apply_filters,
            fg_color=COLOR_BG,
            selected_color=COLOR_ACCENT,
            selected_hover_color=COLOR_ACCENT_HOVER,
            unselected_color=COLOR_BG,
            unselected_hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT,
            height=36,
            corner_radius=6,
        )
        self.filter_segment.set("All")
        self.filter_segment.grid(row=0, column=1, sticky="e")

    def _build_permissions_list(self):
        """Container card for detailed permission list."""
        self.list_card = ctk.CTkFrame(
            self.body,
            fg_color=COLOR_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self.list_card.pack(fill="x", pady=(0, 15), padx=5)

        self.list_title_lbl = ctk.CTkLabel(
            self.list_card,
            text="DETAILED PERMISSIONS LIST (0)",
            font=("Arial", 12, "bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        self.list_title_lbl.pack(anchor="w", padx=20, pady=(15, 10))

        self.items_container = ctk.CTkFrame(self.list_card, fg_color="transparent")
        self.items_container.pack(fill="x", padx=20, pady=(0, 15))

        self._show_empty_state("No data yet — select an APK on Dashboard and run 'Permissions' analysis.")

    def _show_empty_state(self, message: str):
        for widget in self.items_container.winfo_children():
            widget.destroy()

        empty_box = ctk.CTkFrame(
            self.items_container,
            fg_color=COLOR_BG,
            border_width=1,
            border_color=COLOR_BORDER,
            corner_radius=8,
        )
        empty_box.pack(fill="x", pady=10)

        ctk.CTkLabel(
            empty_box,
            text=message,
            font=("Consolas", 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=15, pady=15)

    def update_permissions_data(self, permissions_data: list):
        """Populate permissions data from report."""
        self.all_permissions = permissions_data or []

        total = len(self.all_permissions)
        dangerous = sum(
            1 for p in self.all_permissions if p.get("is_dangerous") or p.get("level") == "dangerous"
        )
        normal = total - dangerous

        self.card_total_val.configure(text=str(total))
        self.card_danger_val.configure(text=str(dangerous))
        self.card_normal_val.configure(text=str(normal))
        self.list_title_lbl.configure(text=f"DETAILED PERMISSIONS LIST ({total})")

        self._apply_filters()

    def _apply_filters(self, *args):
        if not self.all_permissions:
            return

        query = self.search_entry.get().strip().lower()
        category = self.filter_segment.get()

        filtered = []
        for p in self.all_permissions:
            name = p.get("name", "").lower()
            desc = p.get("description", "").lower()
            is_danger = p.get("is_dangerous") or p.get("level") == "dangerous"

            if category == "Dangerous" and not is_danger:
                continue
            if category == "Normal" and is_danger:
                continue
            if query and (query not in name and query not in desc):
                continue

            filtered.append(p)

        self._render_list(filtered)

    def _render_list(self, permissions_list: list):
        for widget in self.items_container.winfo_children():
            widget.destroy()

        if not permissions_list:
            self._show_empty_state("No permissions matching your filter criteria.")
            return

        for item in permissions_list:
            name = item.get("name", "UNKNOWN_PERMISSION")
            short_name = name.split(".")[-1]
            is_danger = item.get("is_dangerous") or item.get("level") == "dangerous"
            desc = item.get("description", "No detailed description available.")

            row = ctk.CTkFrame(
                self.items_container,
                fg_color=COLOR_ACCENT_SURFACE if is_danger else COLOR_BG,
                border_width=1,
                border_color=COLOR_ACCENT_BORDER if is_danger else COLOR_BORDER,
                corner_radius=6,
            )
            row.pack(fill="x", pady=3)
            row.grid_columnconfigure(1, weight=1)

            # Left Icon
            icon_symbol = "🚨" if is_danger else "🟢"
            ctk.CTkLabel(row, text=icon_symbol, font=("Arial", 14)).grid(
                row=0, column=0, rowspan=2, padx=(12, 8), pady=10, sticky="n"
            )

            # Permission Name & Details
            title_color = COLOR_DANGER if is_danger else COLOR_TEXT
            ctk.CTkLabel(
                row,
                text=short_name,
                font=("Arial", 13, "bold"),
                text_color=title_color,
                anchor="w",
            ).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(8, 2))

            full_desc = f"{name}\n{desc}" if desc else name
            ctk.CTkLabel(
                row,
                text=full_desc,
                font=("Consolas", 11),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
                justify="left",
            ).grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 8))

            # Right Badge
            badge_text = "DANGEROUS" if is_danger else "NORMAL"
            badge_color = COLOR_DANGER if is_danger else COLOR_SURFACE_HOVER
            badge = ctk.CTkLabel(
                row,
                text=f" {badge_text} ",
                font=("Arial", 10, "bold"),
                fg_color=badge_color,
                corner_radius=4,
            )
            badge.grid(row=0, column=2, padx=12, pady=10, sticky="e")