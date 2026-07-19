from __future__ import annotations

from typing import Any

import customtkinter as ctk


class SettingsWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: Any,
    ) -> None:
        super().__init__(master)

        self.title("MPTracker Settings")
        self.geometry("480x340")
        self.resizable(False, False)

        self.transient(master)
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(
                size=24,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            padx=24,
            pady=(24, 12),
            sticky="w",
        )

        appearance_label = ctk.CTkLabel(
            self,
            text="Appearance",
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        )
        appearance_label.grid(
            row=1,
            column=0,
            padx=24,
            pady=(12, 6),
            sticky="w",
        )

        self.appearance_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "Dark",
                "Light",
                "System",
            ],
            command=self.change_appearance,
        )
        self.appearance_menu.set("Dark")
        self.appearance_menu.grid(
            row=2,
            column=0,
            padx=24,
            pady=6,
            sticky="w",
        )

        coming_soon_label = ctk.CTkLabel(
            self,
            text=(
                "More settings coming later:\n"
                "• Automatic refresh interval\n"
                "• Notifications\n"
                "• Carrier preferences"
            ),
            justify="left",
            anchor="w",
        )
        coming_soon_label.grid(
            row=3,
            column=0,
            padx=24,
            pady=(24, 12),
            sticky="ew",
        )

    @staticmethod
    def change_appearance(
        selected_mode: str,
    ) -> None:
        ctk.set_appearance_mode(
            selected_mode.lower()
        )