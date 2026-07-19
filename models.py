from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrackingEvent:
    status: str
    name: str
    description: str | None
    location: str | None
    timestamp: datetime
    tracking_number: str | None = None


@dataclass
class TrackingResult:
    carrier: str
    tracking_number: str
    status: str
    status_name: str
    events: list[TrackingEvent] = field(default_factory=list)

    @property
    def delivered(self) -> bool:
        return self.status.upper() == "DELIVERED"