from __future__ import annotations

from datetime import datetime
from typing import Any

import customtkinter as ctk


def get_object_value(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:
    """Read a value from a dictionary, sqlite row, or object."""

    try:
        return obj[key]
    except (KeyError, TypeError, IndexError):
        return getattr(obj, key, default)


def get_event_date(event: Any) -> Any:
    return getattr(
        event,
        "date",
        getattr(event, "timestamp", ""),
    )


def get_event_sort_value(event: Any) -> str:
    return str(get_event_date(event))


def format_date(value: Any) -> str:
    text = str(value)

    cleaned_text = (
        text.replace("Z", "")
        .split("+")[0]
    )

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]

    for date_format in formats:
        try:
            parsed = datetime.strptime(
                cleaned_text,
                date_format,
            )

            return parsed.strftime(
                "%B %d, %Y at %I:%M %p"
            )

        except ValueError:
            continue

    return text


def format_tracking_result(result: Any) -> str:
    events = list(
        getattr(result, "events", [])
    )

    if events:
        latest_event = max(
            events,
            key=get_event_sort_value,
        )

        name = getattr(
            latest_event,
            "name",
            getattr(
                latest_event,
                "status",
                "Unknown status",
            ),
        )

        location = getattr(
            latest_event,
            "location",
            "",
        )

        date = get_event_date(latest_event)

        pieces = [str(name)]

        if location:
            pieces.append(str(location))

        if date:
            pieces.append(format_date(date))

        return "\n".join(pieces)

    status = getattr(result, "status", None)

    if status:
        return str(status)

    return "No tracking events were returned."


class TimelineEventCard(ctk.CTkFrame):
    """Displays one tracking event inside the timeline."""

    def __init__(
        self,
        master: Any,
        event: Any,
        is_latest: bool = False,
    ) -> None:
        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)

        marker = ctk.CTkLabel(
            self,
            text="●" if is_latest else "○",
            font=ctk.CTkFont(size=22),
            width=34,
        )
        marker.grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(14, 6),
            pady=14,
            sticky="n",
        )

        name = getattr(
            event,
            "name",
            getattr(
                event,
                "status",
                "Unknown status",
            ),
        )

        location = getattr(
            event,
            "location",
            "",
        )

        date = get_event_date(event)

        description = getattr(
            event,
            "description",
            "",
        )

        name_label = ctk.CTkLabel(
            self,
            text=str(name),
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
            anchor="w",
            justify="left",
        )
        name_label.grid(
            row=0,
            column=1,
            padx=(4, 16),
            pady=(13, 2),
            sticky="ew",
        )

        detail_parts = []

        if location:
            detail_parts.append(str(location))

        if date:
            detail_parts.append(
                format_date(date)
            )

        details_label = ctk.CTkLabel(
            self,
            text=" • ".join(detail_parts),
            anchor="w",
            justify="left",
        )
        details_label.grid(
            row=1,
            column=1,
            padx=(4, 16),
            pady=2,
            sticky="ew",
        )

        if description:
            description_label = ctk.CTkLabel(
                self,
                text=str(description),
                anchor="w",
                justify="left",
                wraplength=500,
            )
            description_label.grid(
                row=2,
                column=1,
                padx=(4, 16),
                pady=(2, 13),
                sticky="ew",
            )