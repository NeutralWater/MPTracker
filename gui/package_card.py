from __future__ import annotations

import threading
from tkinter import messagebox
from typing import Any, Callable

import customtkinter as ctk

from database import remove_package
from gui.details_window import DetailsWindow
from gui.widgets import (
    format_tracking_result,
    get_object_value,
)


class PackageCard(ctk.CTkFrame):
    def __init__(
        self,
        master: Any,
        package: Any,
        tracker: Any,
        status_callback: Callable[[str], None] | None = None,
        remove_callback: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            master,
            cursor="hand2",
        )

        self.package = package
        self.tracker = tracker
        self.status_callback = status_callback
        self.remove_callback = remove_callback

        self.tracking_number = get_object_value(
            package,
            "tracking_number",
            "",
        )

        self.carrier = get_object_value(
            package,
            "carrier",
            "GlobKurier",
        )

        self.nickname = get_object_value(
            package,
            "nickname",
            "",
        )

        self.display_name = (
            self.nickname
            or self.tracking_number
        )

        self.grid_columnconfigure(0, weight=1)

        self._create_layout()
        self._bind_clicks()

        self.refresh()

    def _create_layout(self) -> None:
        self.name_label = ctk.CTkLabel(
            self,
            text=self.display_name,
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
            anchor="w",
            cursor="hand2",
        )
        self.name_label.grid(
            row=0,
            column=0,
            padx=16,
            pady=(14, 2),
            sticky="ew",
        )

        self.details_label = ctk.CTkLabel(
            self,
            text=(
                f"{self.carrier} • "
                f"{self.tracking_number}"
            ),
            anchor="w",
            cursor="hand2",
        )
        self.details_label.grid(
            row=1,
            column=0,
            padx=16,
            pady=(0, 5),
            sticky="ew",
        )

        self.tracking_status_label = ctk.CTkLabel(
            self,
            text="Checking current status...",
            anchor="w",
            justify="left",
            wraplength=500,
            cursor="hand2",
        )
        self.tracking_status_label.grid(
            row=2,
            column=0,
            padx=16,
            pady=(5, 14),
            sticky="ew",
        )

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        button_frame.grid(
            row=0,
            column=1,
            rowspan=3,
            padx=16,
            pady=16,
        )

        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh",
            width=90,
            command=self.refresh,
        )
        self.refresh_button.grid(
            row=0,
            column=0,
            pady=(0, 8),
        )

        self.remove_button = ctk.CTkButton(
            button_frame,
            text="Remove",
            width=90,
            fg_color="#9b2c2c",
            hover_color="#7f1d1d",
            command=self.confirm_remove,
        )
        self.remove_button.grid(
            row=1,
            column=0,
        )

    def _bind_clicks(self) -> None:
        clickable_widgets = [
            self,
            self.name_label,
            self.details_label,
            self.tracking_status_label,
        ]

        for widget in clickable_widgets:
            widget.bind(
                "<Button-1>",
                self._open_details,
            )

    def _open_details(
        self,
        _event: Any = None,
    ) -> None:
        DetailsWindow(
            master=self.winfo_toplevel(),
            tracker=self.tracker,
            tracking_number=self.tracking_number,
            display_name=self.display_name,
        )

    def confirm_remove(self) -> None:
        confirmed = messagebox.askyesno(
            "Remove Package",
            (
                f"Remove {self.display_name}?\n\n"
                "This will delete it from MPTracker."
            ),
            parent=self.winfo_toplevel(),
        )

        if not confirmed:
            return

        try:
            remove_package(self.tracking_number)

        except Exception as error:
            messagebox.showerror(
                "Could Not Remove Package",
                str(error),
                parent=self.winfo_toplevel(),
            )
            return

        if self.status_callback:
            self.status_callback(
                f"Removed {self.display_name}"
            )

        if self.remove_callback:
            self.remove_callback()
        else:
            self.destroy()

    def refresh(self) -> None:
        self.tracking_status_label.configure(
            text="Checking package..."
        )

        self.refresh_button.configure(
            state="disabled",
            text="Checking...",
        )

        thread = threading.Thread(
            target=self._refresh_worker,
            daemon=True,
        )
        thread.start()

    def _refresh_worker(self) -> None:
        try:
            result = self.tracker.track(
                self.tracking_number
            )

            status_text = format_tracking_result(
                result
            )

            self.after(
                0,
                lambda: self.tracking_status_label.configure(
                    text=status_text
                ),
            )

        except Exception as error:
            error_text = f"Tracking error: {error}"

            self.after(
                0,
                lambda: self.tracking_status_label.configure(
                    text=error_text
                ),
            )

        finally:
            self.after(
                0,
                lambda: self.refresh_button.configure(
                    state="normal",
                    text="Refresh",
                ),
            )

            if self.status_callback:
                self.after(
                    0,
                    lambda: self.status_callback(
                        f"Refreshed {self.display_name}"
                    ),
                )