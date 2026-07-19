from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests

from carriers.base import CarrierTracker
from models import TrackingEvent, TrackingResult


class GlobKurierError(Exception):
    """Raised when GlobKurier tracking fails."""


class GlobKurierTracker(CarrierTracker):
    name = "GlobKurier"

    BASE_URL = "https://api.globkurier.pl/v1/order/tracking"

    # GlobKurier returns timestamps without a UTC offset.
    # Treat those timestamps as GlobKurier's local Polish time.
    API_TIMEZONE = ZoneInfo("Europe/Warsaw")

    def supports(self, tracking_number: str) -> bool:
        normalized = self._normalize_number(tracking_number)

        return (
            normalized.startswith("GK")
            and len(normalized) > 2
        )

    def track(
        self,
        tracking_number: str,
    ) -> TrackingResult:
        normalized = self._normalize_number(
            tracking_number
        )

        if not self.supports(normalized):
            raise ValueError(
                "GlobKurier order numbers must begin "
                "with 'GK'."
            )

        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "orderNumber": normalized,
                },
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en",
                    "User-Agent": "MPTracker/0.1",
                },
                timeout=15,
            )

            response.raise_for_status()

        except requests.Timeout as exc:
            raise GlobKurierError(
                "GlobKurier took too long to respond."
            ) from exc

        except requests.HTTPError as exc:
            status_code = exc.response.status_code

            if status_code == 404:
                raise GlobKurierError(
                    "No GlobKurier shipment found for "
                    f"{normalized}."
                ) from exc

            raise GlobKurierError(
                "GlobKurier returned HTTP "
                f"{status_code}."
            ) from exc

        except requests.RequestException as exc:
            raise GlobKurierError(
                "Could not connect to GlobKurier."
            ) from exc

        try:
            data: dict[str, Any] = response.json()

        except requests.JSONDecodeError as exc:
            raise GlobKurierError(
                "GlobKurier returned an invalid response."
            ) from exc

        latest = data.get("latestStatus")

        if not isinstance(latest, dict):
            raise GlobKurierError(
                "GlobKurier returned no current "
                "shipment status."
            )

        events = [
            self._parse_event(event)
            for event in data.get("statuses", [])
            if isinstance(event, dict)
        ]

        events.sort(
            key=lambda event: event.timestamp
        )

        return TrackingResult(
            carrier=self.name,
            tracking_number=normalized,
            status=str(
                latest.get(
                    "type",
                    "UNKNOWN",
                )
            ),
            status_name=str(
                latest.get(
                    "name",
                    "Unknown",
                )
            ),
            events=events,
        )

    @classmethod
    def _parse_event(
        cls,
        data: dict[str, Any],
    ) -> TrackingEvent:
        raw_date = data.get("date")

        try:
            timestamp = datetime.strptime(
                str(raw_date),
                "%Y-%m-%d %H:%M:%S",
            )

        except (TypeError, ValueError) as exc:
            raise GlobKurierError(
                "Invalid event date returned: "
                f"{raw_date!r}"
            ) from exc

        # datetime.strptime creates a timezone-naive datetime.
        # Attach GlobKurier's timezone so elapsed-time math
        # handles UTC offsets and daylight saving time correctly.
        timestamp = timestamp.replace(
            tzinfo=cls.API_TIMEZONE
        )

        return TrackingEvent(
            status=str(
                data.get(
                    "type",
                    "UNKNOWN",
                )
            ),
            name=str(
                data.get(
                    "name",
                    "Unknown",
                )
            ),
            description=data.get("description"),
            location=data.get("location"),
            timestamp=timestamp,
            tracking_number=data.get("number"),
        )

    @staticmethod
    def _normalize_number(
        tracking_number: str,
    ) -> str:
        return "".join(
            tracking_number.upper().split()
        )