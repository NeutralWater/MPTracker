from __future__ import annotations

import threading
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from carriers.globkurier import GlobKurierTracker
from database import (
    get_active_packages,
    initialize_database,
)
from gui.add_package_dialog import AddPackageDialog
from gui.package_card import PackageCard
from gui.settings_window import SettingsWindow


class MPTrackerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("MPTracker")
        self.geometry("760x600")
        self.minsize(620, 450)

        initialize_database()

        self.tracker = GlobKurierTracker()
        self.package_cards: list[PackageCard] = []

        self._create_layout()
        self.load_packages()

    def _create_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        header_frame.grid(
            row=0,
            column=0,
            padx=24,
            pady=(20, 10),
            sticky="ew",
        )
        header_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        title_label = ctk.CTkLabel(
            header_frame,
            text="MPTracker",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        settings_button = ctk.CTkButton(
            header_frame,
            text="⚙",
            width=42,
            command=self.open_settings,
        )
        settings_button.grid(
            row=0,
            column=1,
            padx=(8, 8),
        )

        add_button = ctk.CTkButton(
            header_frame,
            text="+ Add Package",
            width=120,
            command=self.open_add_dialog,
        )
        add_button.grid(
            row=0,
            column=2,
            padx=(0, 8),
        )

        self.refresh_button = ctk.CTkButton(
            header_frame,
            text="Refresh All",
            width=110,
            command=self.refresh_all_packages,
        )
        self.refresh_button.grid(
            row=0,
            column=3,
        )

        self.package_container = (
            ctk.CTkScrollableFrame(
                self,
                label_text="Active Packages",
            )
        )
        self.package_container.grid(
            row=1,
            column=0,
            padx=24,
            pady=(10, 16),
            sticky="nsew",
        )
        self.package_container.grid_columnconfigure(
            0,
            weight=1,
        )

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
        )
        self.status_label.grid(
            row=2,
            column=0,
            padx=24,
            pady=(0, 12),
            sticky="ew",
        )

    def clear_package_cards(self) -> None:
        self.package_cards.clear()

        for widget in (
            self.package_container
            .winfo_children()
        ):
            widget.destroy()

    def load_packages(self) -> None:
        self.clear_package_cards()

        try:
            packages = get_active_packages()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                "Could not load packages:"
                f"\n\n{error}",
            )
            return

        if not packages:
            empty_label = ctk.CTkLabel(
                self.package_container,
                text=(
                    "No active packages yet.\n"
                    "Press + Add Package to begin"
                ),
                font=ctk.CTkFont(size=17),
            )
            empty_label.grid(
                row=0,
                column=0,
                padx=20,
                pady=50,
            )

            self.set_status(
                "No active packages."
            )
            return

        for index, package in enumerate(packages):
            card = PackageCard(
                master=self.package_container,
                package=package,
                tracker=self.tracker,
                status_callback=self.set_status,
                remove_callback=self.load_packages,
            )
            card.grid(
                row=index,
                column=0,
                padx=8,
                pady=8,
                sticky="ew",
            )

            self.package_cards.append(card)

        self.set_status(
            f"Loaded {len(packages)} package(s)."
        )

    def open_add_dialog(self) -> None:
        AddPackageDialog(
            master=self,
            on_package_added=(
                self._after_package_added
            ),
        )

    def _after_package_added(self) -> None:
        self.set_status("Package added.")
        self.load_packages()

    def open_settings(self) -> None:
        SettingsWindow(self)

    def refresh_all_packages(self) -> None:
        if not self.package_cards:
            self.set_status(
                "There are no packages to refresh."
            )
            return

        self.refresh_button.configure(
            state="disabled",
            text="Refreshing...",
        )

        self.set_status(
            "Refreshing all packages..."
        )

        thread = threading.Thread(
            target=self._refresh_all_worker,
            daemon=True,
        )
        thread.start()

    def _refresh_all_worker(self) -> None:
        for card in self.package_cards:
            try:
                result = self.tracker.track(
                    card.tracking_number
                )

                from gui.widgets import (
                    format_tracking_result,
                )

                status_text = (
                    format_tracking_result(result)
                )

                self.after(
                    0,
                    lambda current_card=card,
                    text=status_text:
                    current_card
                    .tracking_status_label
                    .configure(text=text),
                )

            except Exception as error:
                error_text = (
                    f"Tracking error: {error}"
                )

                self.after(
                    0,
                    lambda current_card=card,
                    text=error_text:
                    current_card
                    .tracking_status_label
                    .configure(text=text),
                )

        self.after(
            0,
            self._finish_refresh_all,
        )

    def _finish_refresh_all(self) -> None:
        self.refresh_button.configure(
            state="normal",
            text="Refresh All",
        )

        self.set_status(
            "Finished refreshing packages."
        )

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)