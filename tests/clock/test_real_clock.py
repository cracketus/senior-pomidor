"""Tests for RealClock."""

from brain.clock import RealClock


def test_real_clock_monotonicity():
    clock = RealClock()
    first = clock.now()
    clock.sleep(0.01)
    second = clock.now()
    assert second >= first
