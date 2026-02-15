"""Clock interface used by schedulers and simulations."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Clock interface for wall or simulated time."""

    def now(self) -> datetime:
        """Return the current time."""

    def sleep(self, seconds: float) -> None:
        """Advance time by the given seconds (or sleep in real time)."""

    def sleep_for_logical(self, seconds: float) -> None:
        """Advance the clock by logical seconds."""
