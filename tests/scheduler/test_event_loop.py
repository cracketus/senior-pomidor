"""Tests for scheduler event loop."""

from datetime import datetime, timedelta, timezone

from brain.clock import SimClock
from brain.scheduler import Scheduler


def test_periodic_task_execution_order():
    start = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    clock = SimClock(time_scale=60.0, start_time=start)
    scheduler = Scheduler(clock)
    events: list[str] = []

    scheduler.schedule_every(10.0, lambda now: events.append("a"))
    scheduler.schedule_every(15.0, lambda now: events.append("b"))

    scheduler.run(duration_seconds=30.0)

    assert events == ["a", "b", "a", "a", "b"]


def test_two_hour_logical_cycle_completion():
    start = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    clock = SimClock(time_scale=120.0, start_time=start)
    scheduler = Scheduler(clock)
    ticks: list[datetime] = []

    scheduler.schedule_every(7200.0, lambda now: ticks.append(now))

    scheduler.run(duration_seconds=24 * 3600)

    assert len(ticks) == 12
    assert ticks[-1] == start + timedelta(hours=24)


def test_graceful_shutdown():
    start = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    clock = SimClock(time_scale=10.0, start_time=start)
    scheduler = Scheduler(clock)
    calls: list[str] = []

    def stop_task(_now):
        calls.append("stop")
        scheduler.shutdown()

    scheduler.schedule_every(5.0, stop_task)
    scheduler.schedule_every(5.0, lambda now: calls.append("other"))

    scheduler.run(duration_seconds=60.0)

    assert calls == ["stop"]
