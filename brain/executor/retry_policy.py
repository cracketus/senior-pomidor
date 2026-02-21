"""Deterministic retry/backoff policy for hardware execution."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicyConfig:
    """Retry policy configuration for adapter dispatch failures."""

    max_attempts: int = 3
    base_backoff_seconds: float = 30.0
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 5 * 60.0
    retryable_error_classes: tuple[str, ...] = (
        "transient_io",
        "timeout",
        "transport_unavailable",
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base_backoff_seconds < 0:
            raise ValueError("base_backoff_seconds must be >= 0")
        if self.backoff_multiplier < 1.0:
            raise ValueError("backoff_multiplier must be >= 1.0")
        if self.max_backoff_seconds < 0:
            raise ValueError("max_backoff_seconds must be >= 0")
        if self.base_backoff_seconds > self.max_backoff_seconds:
            raise ValueError("base_backoff_seconds cannot exceed max_backoff_seconds")

    def backoff_seconds_for_retry(self, retry_index: int) -> float:
        """
        Return deterministic backoff seconds for retry index.

        retry_index is 1-based for retry attempts after the initial dispatch.
        """
        if retry_index < 1:
            raise ValueError("retry_index must be >= 1")
        raw = self.base_backoff_seconds * (self.backoff_multiplier ** (retry_index - 1))
        return min(raw, self.max_backoff_seconds)

    def is_retryable_error_class(self, error_class: str | None) -> bool:
        if error_class is None:
            return False
        return error_class in self.retryable_error_classes
