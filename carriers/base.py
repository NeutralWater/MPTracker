from abc import ABC, abstractmethod

from models import TrackingResult


class CarrierTracker(ABC):
    name: str

    @abstractmethod
    def supports(self, tracking_number: str) -> bool:
        """Return whether this tracker recognizes the number format."""
        raise NotImplementedError

    @abstractmethod
    def track(self, tracking_number: str) -> TrackingResult:
        """Retrieve and normalize shipment tracking information."""
        raise NotImplementedError