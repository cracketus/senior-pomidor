"""Tests for deterministic retry/backoff policy."""

import pytest

from brain.executor import RetryPolicyConfig


def test_backoff_sequence_is_deterministic():
    policy = RetryPolicyConfig(
        max_attempts=4,
        base_backoff_seconds=10.0,
        backoff_multiplier=2.0,
        max_backoff_seconds=25.0,
    )
    assert policy.backoff_seconds_for_retry(1) == 10.0
    assert policy.backoff_seconds_for_retry(2) == 20.0
    assert policy.backoff_seconds_for_retry(3) == 25.0


def test_retryable_error_class_membership():
    policy = RetryPolicyConfig(retryable_error_classes=("timeout", "transient_io"))
    assert policy.is_retryable_error_class("timeout") is True
    assert policy.is_retryable_error_class("fatal_config") is False
    assert policy.is_retryable_error_class(None) is False


def test_invalid_policy_configuration_raises():
    with pytest.raises(ValueError):
        RetryPolicyConfig(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicyConfig(base_backoff_seconds=-1.0)
    with pytest.raises(ValueError):
        RetryPolicyConfig(backoff_multiplier=0.5)
