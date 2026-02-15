"""Time-based ring buffer for bounded state history."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean, pstdev
from typing import Callable, Deque, Generic, Iterable, Optional, TypeVar

T = TypeVar("T")


@dataclass
class BufferStats:
    """Summary stats for numeric series."""

    count: int
    minimum: Optional[float]
    maximum: Optional[float]
    mean: Optional[float]
    std: Optional[float]


class TimeRingBuffer(Generic[T]):
    """Ring buffer that retains items within a time window."""

    def __init__(
        self, max_hours: float, timestamp_getter: Callable[[T], datetime]
    ) -> None:
        if max_hours <= 0:
            raise ValueError("max_hours must be positive")
        self._max_hours = max_hours
        self._timestamp_getter = timestamp_getter
        self._items: Deque[T] = deque()

    def __len__(self) -> int:
        return len(self._items)

    def append(self, item: T) -> None:
        timestamp = self._timestamp_getter(item)
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        self._items.append(item)
        self._prune(timestamp)

    def _prune(self, now: datetime) -> None:
        cutoff = now - timedelta(hours=self._max_hours)
        while self._items:
            oldest = self._items[0]
            if self._timestamp_getter(oldest) >= cutoff:
                break
            self._items.popleft()

    def items(self) -> list[T]:
        return list(self._items)

    def get_since(self, cutoff: datetime) -> list[T]:
        return [item for item in self._items if self._timestamp_getter(item) >= cutoff]

    def get_last_n_hours(self, hours: float, now: Optional[datetime] = None) -> list[T]:
        if hours <= 0:
            return []
        if not self._items:
            return []
        if now is None:
            now = self._timestamp_getter(self._items[-1])
        cutoff = now - timedelta(hours=hours)
        return self.get_since(cutoff)

    def get_stats(self, value_getter: Callable[[T], float]) -> BufferStats:
        values = [value_getter(item) for item in self._items]
        if not values:
            return BufferStats(count=0, minimum=None, maximum=None, mean=None, std=None)
        if len(values) == 1:
            return BufferStats(
                count=1,
                minimum=values[0],
                maximum=values[0],
                mean=values[0],
                std=0.0,
            )
        return BufferStats(
            count=len(values),
            minimum=min(values),
            maximum=max(values),
            mean=mean(values),
            std=pstdev(values),
        )
