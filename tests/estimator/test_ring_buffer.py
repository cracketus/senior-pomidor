"""Tests for TimeRingBuffer."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from brain.estimator.ring_buffer import TimeRingBuffer


@dataclass
class Sample:
    timestamp: datetime
    value: float


def test_ring_buffer_overwrites_oldest():
    buffer = TimeRingBuffer(1.0, lambda item: item.timestamp)
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    buffer.append(Sample(now - timedelta(hours=2), 1.0))
    buffer.append(Sample(now - timedelta(minutes=30), 2.0))
    assert len(buffer) == 1
    assert buffer.items()[0].value == 2.0


def test_get_last_n_hours():
    buffer = TimeRingBuffer(5.0, lambda item: item.timestamp)
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    buffer.append(Sample(now - timedelta(hours=3), 1.0))
    buffer.append(Sample(now - timedelta(hours=1), 2.0))
    buffer.append(Sample(now, 3.0))

    last_hour = buffer.get_last_n_hours(1.0, now=now)
    assert [item.value for item in last_hour] == [2.0, 3.0]


def test_get_stats():
    buffer = TimeRingBuffer(5.0, lambda item: item.timestamp)
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    buffer.append(Sample(now - timedelta(minutes=30), 1.0))
    buffer.append(Sample(now - timedelta(minutes=20), 3.0))
    buffer.append(Sample(now - timedelta(minutes=10), 5.0))

    stats = buffer.get_stats(lambda item: item.value)
    assert stats.count == 3
    assert stats.minimum == 1.0
    assert stats.maximum == 5.0
    assert stats.mean == 3.0
    assert stats.std is not None and stats.std > 0
