"""Simulated clock with deterministic progression."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class SimClock:
    """Clock that advances logical time by a scale factor."""

    def __init__(
        self,
        time_scale: float = 1.0,
        start_time: datetime | None = None,
    ) -> None:
        if time_scale <= 0:
            raise ValueError("time_scale must be positive")
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        if start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")
        self._time_scale = time_scale
        self._current_time = start_time

    @property
    def time_scale(self) -> float:
        return self._time_scale

    def now(self) -> datetime:
        return self._current_time

    def sleep(self, seconds: float) -> None:
        if seconds <= 0:
            return
        advance = seconds * self._time_scale
        self._current_time = self._current_time + timedelta(seconds=advance)

    def sleep_for_logical(self, seconds: float) -> None:
        if seconds <= 0:
            return
        self._current_time = self._current_time + timedelta(seconds=seconds)
