from __future__ import annotations

from typing import Any, Callable, Sequence

import customtkinter as ctk
from tkinter import ttk

# Dolce Neves palette
BG_DEEP = "#F7F0E8"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E8C8D0"
HEADER_BG = "#FAE8EC"
FIELD_BG = "#FAF4F0"

ACCENT = "#C96B7A"
TEXT_PRIMARY = "#3D2314"
TEXT_SECONDARY = "#7A4A55"
TEXT_MUTED = "#C0A0A8"

COLOR_GREEN = "#2E9B6A"
COLOR_RED = "#D45050"
COLOR_BLUE = "#4A8FC4"
COLOR_ORANGE = "#D4842A"
COLOR_PURPLE = "#9A6CC8"


def _card(parent: Any, **kw: Any) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=CARD_BG,
        corner_radius=12,
        border_width=1,
        border_color=CARD_BORDER,
        **kw,
    )


def _entry(parent: Any, **kw: Any) -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent,
        fg_color=FIELD_BG,
        border_color=CARD_BORDER,
        text_color=TEXT_PRIMARY,
        **kw,
    )


def _combo(parent: Any, values: Sequence[str], **kw: Any) -> ctk.CTkComboBox:
    return ctk.CTkComboBox(
        parent,
        values=list(values),
        fg_color=FIELD_BG,
        border_color=CARD_BORDER,
        button_color=CARD_BORDER,
        button_hover_color="#E0B8C2",
        text_color=TEXT_PRIMARY,
        dropdown_fg_color=CARD_BG,
        dropdown_text_color=TEXT_PRIMARY,
        dropdown_hover_color="#FAE8EC",
        **kw,
    )


def _btn_accent(parent: Any, text: str, command: Callable[..., Any], **kw: Any) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=ACCENT,
        hover_color="#A84F5E",
        text_color="#FFFFFF",
        height=30,
        corner_radius=20,
        font=ctk.CTkFont(size=12, weight="bold"),
        **kw,
    )


def _btn_ghost(parent: Any, text: str, command: Callable[..., Any], **kw: Any) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=FIELD_BG,
        hover_color="#F2D5DC",
        border_color=CARD_BORDER,
        border_width=1,
        text_color=TEXT_SECONDARY,
        height=30,
        corner_radius=20,
        font=ctk.CTkFont(size=12),
        **kw,
    )


def _btn_danger(parent: Any, text: str, command: Callable[..., Any], **kw: Any) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="#FAE8EC",
        hover_color="#F2D5DC",
        border_color=CARD_BORDER,
        border_width=1,
        text_color=ACCENT,
        height=30,
        corner_radius=20,
        font=ctk.CTkFont(size=12),
        **kw,
    )


def _sep(parent: Any, **kw: Any) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, fg_color=CARD_BORDER, height=1, **kw)


def _treeview_style(name: str, rowheight: int = 30) -> str:
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        f"{name}.Treeview",
        background=CARD_BG,
        foreground=TEXT_PRIMARY,
        rowheight=rowheight,
        fieldbackground=CARD_BG,
        borderwidth=0,
    )
    style.map(f"{name}.Treeview", background=[("selected", "#F2D5DC")])
    style.configure(
        f"{name}.Treeview.Heading",
        background=HEADER_BG,
        foreground=TEXT_SECONDARY,
        relief="flat",
        font=("Roboto", 10, "bold"),
    )
    style.map(f"{name}.Treeview.Heading", background=[("active", "#F2D5DC")])
    return f"{name}.Treeview"


def _optmenu(parent: Any, values: Sequence[str], **kw: Any) -> ctk.CTkOptionMenu:
    return ctk.CTkOptionMenu(
        parent,
        values=list(values),
        fg_color=FIELD_BG,
        button_color=CARD_BORDER,
        button_hover_color="#E0B8C2",
        text_color=TEXT_PRIMARY,
        dropdown_fg_color=CARD_BG,
        dropdown_text_color=TEXT_PRIMARY,
        dropdown_hover_color="#FAE8EC",
        **kw,
    )
