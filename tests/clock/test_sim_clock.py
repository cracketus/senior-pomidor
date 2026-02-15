"""Tests for SimClock."""

from datetime import datetime, timedelta, timezone

from brain.clock import SimClock


def test_sim_clock_advances_by_scale():
    start = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    clock = SimClock(time_scale=120.0, start_time=start)

    clock.sleep(1.5)

    assert clock.now() == start + timedelta(seconds=180)
