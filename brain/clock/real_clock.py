"""Wall-clock implementation."""

from __future__ import annotations

import time
from datetime import datetime, timezone


class RealClock:
    """Clock backed by wall time."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def sleep(self, seconds: float) -> None:
        if seconds <= 0:
            return
        time.sleep(seconds)

    def sleep_for_logical(self, seconds: float) -> None:
        self.sleep(seconds)
