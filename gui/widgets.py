from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import customtkinter as ctk


def get_object_value(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:
    """Read a value from a dictionary, SQLite row, or object."""

    try:
        return obj[key]

    except (KeyError, TypeError, IndexError):
        return getattr(
            obj,
            key,
            default,
        )


def get_event_date(event: Any) -> Any:
    """Return an event's date or timestamp."""

    return getattr(
        event,
        "date",
        getattr(
            event,
            "timestamp",
            "",
        ),
    )


def get_event_sort_value(
    event: Any,
) -> datetime:
    """Return a value that can safely sort tracking events."""

    value = get_event_date(event)
    parsed = parse_datetime(value)

    if parsed is not None:
        return parsed.astimezone(timezone.utc)

    return datetime.min.replace(
        tzinfo=timezone.utc
    )


def parse_datetime(
    value: Any,
) -> datetime | None:
    """Convert supported tracking timestamps into datetime objects."""

    if isinstance(value, datetime):
        parsed = value

    else:
        text = str(value).strip()

        if not text:
            return None

        normalized = text.replace(
            "Z",
            "+00:00",
        )

        try:
            parsed = datetime.fromisoformat(
                normalized
            )

        except ValueError:
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
            ]

            parsed = None

            for date_format in formats:
                try:
                    parsed = datetime.strptime(
                        text,
                        date_format,
                    )
                    break

                except ValueError:
                    continue

            if parsed is None:
                return None

    # Older events or future carrier integrations may still
    # provide timezone-naive timestamps. UTC acts as a safe
    # fallback, although GlobKurier timestamps become aware
    # inside carriers/globkurier.py.
    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed


def format_date(
    value: Any,
) -> str:
    """Format a tracking timestamp for display."""

    parsed = parse_datetime(value)

    if parsed is None:
        return str(value)

    return parsed.strftime(
        "%B %d, %Y at %I:%M %p"
    )


def format_elapsed(
    value: Any,
) -> str:
    """Return a human-readable time since a tracking event."""

    event_time = parse_datetime(value)

    if event_time is None:
        return ""

    now = datetime.now(timezone.utc)

    elapsed = (
        now
        - event_time.astimezone(timezone.utc)
    )

    total_seconds = max(
        0,
        int(elapsed.total_seconds()),
    )

    days, remaining_seconds = divmod(
        total_seconds,
        86_400,
    )

    hours, remaining_seconds = divmod(
        remaining_seconds,
        3_600,
    )

    minutes = remaining_seconds // 60

    if days == 1:
        return (
            f"1 day {hours}h {minutes}m ago"
        )

    if days > 1:
        return (
            f"{days} days {hours}h {minutes}m ago"
        )

    if hours > 0:
        return (
            f"{hours}h {minutes}m ago"
        )

    if minutes > 0:
        return f"{minutes}m ago"

    return "Less than a minute ago"


def format_tracking_result(
    result: Any,
) -> str:
    """Format the newest event for a package card."""

    events = list(
        getattr(
            result,
            "events",
            [],
        )
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

        date = get_event_date(
            latest_event
        )

        pieces = [
            str(name),
        ]

        if location:
            pieces.append(
                str(location)
            )

        if date:
            pieces.append(
                format_date(date)
            )

            elapsed_text = format_elapsed(
                date
            )

            if elapsed_text:
                pieces.append(
                    "Last update: "
                    f"{elapsed_text}"
                )

        return "\n".join(pieces)

    status = getattr(
        result,
        "status",
        None,
    )

    if status:
        return str(status)

    return "No tracking events were returned."


class TimelineEventCard(ctk.CTkFrame):
    """Display one tracking event inside the timeline."""

    def __init__(
        self,
        master: Any,
        event: Any,
        is_latest: bool = False,
    ) -> None:
        super().__init__(master)

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        marker = ctk.CTkLabel(
            self,
            text=(
                "●"
                if is_latest
                else "○"
            ),
            font=ctk.CTkFont(
                size=22
            ),
            width=34,
        )

        marker.grid(
            row=0,
            column=0,
            rowspan=4,
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

        date = get_event_date(
            event
        )

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

        detail_parts: list[str] = []

        if location:
            detail_parts.append(
                str(location)
            )

        if date:
            detail_parts.append(
                format_date(date)
            )

        details_label = ctk.CTkLabel(
            self,
            text=" • ".join(
                detail_parts
            ),
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

        next_row = 2

        if is_latest and date:
            elapsed_text = format_elapsed(
                date
            )

            if elapsed_text:
                elapsed_label = ctk.CTkLabel(
                    self,
                    text=(
                        "Last update: "
                        f"{elapsed_text}"
                    ),
                    anchor="w",
                    justify="left",
                    font=ctk.CTkFont(
                        size=13,
                        weight="bold",
                    ),
                )

                elapsed_label.grid(
                    row=next_row,
                    column=1,
                    padx=(4, 16),
                    pady=2,
                    sticky="ew",
                )

                next_row += 1

        if description:
            description_label = ctk.CTkLabel(
                self,
                text=str(description),
                anchor="w",
                justify="left",
                wraplength=500,
            )

            description_label.grid(
                row=next_row,
                column=1,
                padx=(4, 16),
                pady=(2, 13),
                sticky="ew",
            )