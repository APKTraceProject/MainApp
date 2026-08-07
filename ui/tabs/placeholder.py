import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
    COLOR_TEXT_MUTED,
)


def build_placeholder_page(app, title):
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
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
        command=lambda: app.show_page("Dashboard"),
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