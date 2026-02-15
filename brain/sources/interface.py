"""Observation source interface for synthetic and replay backends."""

from __future__ import annotations

from collections.abc import Generator
from typing import Protocol

from brain.contracts import DeviceStatusV1, ObservationV1


class ObservationSource(Protocol):
    """Unified source interface for observation streams.

    Implementations must:
    - Emit ordered observations
    - Be deterministic for fixed inputs (e.g., seed or static file)
    - Return None at end-of-stream
    """

    def next_observation(
        self,
    ) -> tuple[ObservationV1, DeviceStatusV1] | None:
        """Return the next observation and device status, or None at EOF."""


def iter_observations(
    source: ObservationSource,
) -> Generator[tuple[ObservationV1, DeviceStatusV1], None, None]:
    """Yield observations until the source is exhausted."""
    while True:
        item = source.next_observation()
        if item is None:
            return
        yield item
