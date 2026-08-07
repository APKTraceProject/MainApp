import customtkinter as ctk

from ..ui import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_SURFACE,
    COLOR_SURFACE_HOVER,
)


def build_chat_page(app):
    page = ctk.CTkFrame(app.main_container, fg_color="transparent")
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

    add_chat_bubble(chat_history, "🤖 Hello! I'm your AI assistant. Load an APK and ask me anything about it.", is_ai=True)

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


def add_chat_bubble(parent_frame, text, is_ai=True):
    color = COLOR_SURFACE_HOVER if is_ai else "#312061"
    align = "w" if is_ai else "e"

    msg_frame = ctk.CTkFrame(parent_frame, fg_color=color, corner_radius=10)
    msg_frame.pack(anchor=align, pady=10, padx=10, fill="x", expand=False)

    lbl = ctk.CTkLabel(msg_frame, text=text, justify="left", font=("Arial", 13), text_color="white", wraplength=700)
    lbl.pack(padx=20, pady=12, anchor="w")