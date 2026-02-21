"""Deterministic idempotency cache config for execution deduplication."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdempotencyConfig:
    """Configuration for in-memory idempotency-key retention."""

    ttl_seconds: int = 6 * 60 * 60
    max_entries: int = 4096

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")
        if self.max_entries <= 0:
            raise ValueError("max_entries must be > 0")
