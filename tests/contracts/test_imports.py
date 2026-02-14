"""Tests for __init__.py of contracts module."""

import pytest

from brain.contracts import ActionV1, AnomalyV1, SensorHealthV1, StateV1


def test_all_contracts_are_importable():
    """Verify all contract models can be imported from brain.contracts."""
    assert StateV1 is not None
    assert ActionV1 is not None
    assert AnomalyV1 is not None
    assert SensorHealthV1 is not None
