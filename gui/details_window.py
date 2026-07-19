from __future__ import annotations

import threading
from typing import Any

import customtkinter as ctk

from gui.widgets import (
    TimelineEventCard,
    get_event_sort_value,
)


class DetailsWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: Any,
        tracker: Any,
        tracking_number: str,
        display_name: str,
    ) -> None:
        super().__init__(master)

        self.tracker = tracker
        self.tracking_number = tracking_number
        self.display_name = display_name

        self.title(
            f"{display_name} - Tracking Details"
        )
        self.geometry("680x620")
        self.minsize(520, 420)

        self.transient(master)
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_layout()
        self.load_tracking_history()

    def _create_layout(self) -> None:
        title_label = ctk.CTkLabel(
            self,
            text=f"📦 {self.display_name}",
            font=ctk.CTkFont(
                size=24,
                weight="bold",
            ),
            anchor="w",
        )
        title_label.grid(
            row=0,
            column=0,
            padx=24,
            pady=(22, 2),
            sticky="ew",
        )

        number_label = ctk.CTkLabel(
            self,
            text=self.tracking_number,
            anchor="w",
        )
        number_label.grid(
            row=1,
            column=0,
            padx=24,
            pady=(0, 12),
            sticky="ew",
        )

        self.timeline_frame = (
            ctk.CTkScrollableFrame(
                self,
                label_text="Tracking Timeline",
            )
        )
        self.timeline_frame.grid(
            row=2,
            column=0,
            padx=24,
            pady=(8, 24),
            sticky="nsew",
        )
        self.timeline_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.loading_label = ctk.CTkLabel(
            self.timeline_frame,
            text="Loading tracking history...",
            font=ctk.CTkFont(size=16),
        )
        self.loading_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=40,
        )

    def load_tracking_history(self) -> None:
        thread = threading.Thread(
            target=self._load_worker,
            daemon=True,
        )
        thread.start()

    def _load_worker(self) -> None:
        try:
            result = self.tracker.track(
                self.tracking_number
            )

            events = list(
                getattr(result, "events", [])
            )

            events.sort(
                key=get_event_sort_value,
                reverse=True,
            )

            self.after(
                0,
                lambda: self.display_events(events),
            )

        except Exception as error:
            error_text = (
                "Could not load tracking history:"
                f"\n\n{error}"
            )

            self.after(
                0,
                lambda: self.loading_label.configure(
                    text=error_text
                ),
            )

    def display_events(
        self,
        events: list[Any],
    ) -> None:
        if self.loading_label.winfo_exists():
            self.loading_label.destroy()

        if not events:
            empty_label = ctk.CTkLabel(
                self.timeline_frame,
                text=(
                    "No tracking events "
                    "were returned."
                ),
            )
            empty_label.grid(
                row=0,
                column=0,
                padx=20,
                pady=40,
            )
            return

        for index, event in enumerate(events):
            event_card = TimelineEventCard(
                self.timeline_frame,
                event,
                is_latest=index == 0,
            )
            event_card.grid(
                row=index,
                column=0,
                padx=8,
                pady=7,
                sticky="ew",
            )