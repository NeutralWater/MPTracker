from __future__ import annotations

from typing import Any, Callable

import customtkinter as ctk
from tkinter import messagebox

from database import add_package


class AddPackageDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master: Any,
        on_package_added: Callable[[], None],
    ) -> None:
        super().__init__(master)

        self.on_package_added = on_package_added

        self.title("Add Package")
        self.geometry("470x280")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)

        self._create_layout()

    def _create_layout(self) -> None:
        title_label = ctk.CTkLabel(
            self,
            text="Add a package",
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            padx=24,
            pady=(24, 16),
            sticky="w",
        )

        self.tracking_entry = ctk.CTkEntry(
            self,
            placeholder_text=(
                "Tracking number, e.g. GK12345678"
            ),
        )
        self.tracking_entry.grid(
            row=1,
            column=0,
            padx=24,
            pady=8,
            sticky="ew",
        )

        self.nickname_entry = ctk.CTkEntry(
            self,
            placeholder_text="Nickname (optional)",
        )
        self.nickname_entry.grid(
            row=2,
            column=0,
            padx=24,
            pady=8,
            sticky="ew",
        )

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        button_frame.grid(
            row=3,
            column=0,
            padx=24,
            pady=(18, 24),
            sticky="e",
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            fg_color="transparent",
            border_width=1,
            command=self.destroy,
        )
        cancel_button.grid(
            row=0,
            column=0,
            padx=(0, 8),
        )

        add_button = ctk.CTkButton(
            button_frame,
            text="Add Package",
            width=120,
            command=self.add_new_package,
        )
        add_button.grid(
            row=0,
            column=1,
        )

        self.tracking_entry.focus_set()
        self.bind(
            "<Return>",
            lambda _event: self.add_new_package(),
        )

    def add_new_package(self) -> None:
        tracking_number = (
            self.tracking_entry
            .get()
            .strip()
        )

        nickname = (
            self.nickname_entry
            .get()
            .strip()
        )

        if not tracking_number:
            messagebox.showwarning(
                "Missing Tracking Number",
                "Enter a tracking number first.",
                parent=self,
            )
            return

        try:
            add_package(
                tracking_number=tracking_number,
                carrier="globkurier",
                nickname=nickname,
            )

        except TypeError:
            try:
                add_package(
                    tracking_number,
                    "globkurier",
                    nickname,
                )

            except Exception as error:
                messagebox.showerror(
                    "Could Not Add Package",
                    str(error),
                    parent=self,
                )
                return

        except Exception as error:
            messagebox.showerror(
                "Could Not Add Package",
                str(error),
                parent=self,
            )
            return

        self.destroy()
        self.on_package_added()