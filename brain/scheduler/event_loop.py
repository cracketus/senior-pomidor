"""Event loop for periodic tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, List

from brain.clock import Clock


@dataclass
class PeriodicTask:
    interval_seconds: float
    callback: Callable[[datetime], None]
    next_run: datetime
    order: int
    name: str | None = None


class Scheduler:
    """Deterministic scheduler driven by an injected clock."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._tasks: List[PeriodicTask] = []
        self._order = 0
        self._stop = False

    def schedule_every(
        self, interval_seconds: float, callback: Callable[[datetime], None], name: str | None = None
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        now = self._clock.now()
        next_run = now + timedelta(seconds=interval_seconds)
        task = PeriodicTask(
            interval_seconds=interval_seconds,
            callback=callback,
            next_run=next_run,
            order=self._order,
            name=name,
        )
        self._order += 1
        self._tasks.append(task)

    def shutdown(self) -> None:
        """Request the scheduler to stop after the current task."""
        self._stop = True

    def run(self, duration_seconds: float) -> None:
        """Run scheduled tasks for the given logical duration."""
        if duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        start = self._clock.now()
        end = start + timedelta(seconds=duration_seconds)

        if not self._tasks:
            self._clock.sleep_for_logical(duration_seconds)
            return

        while not self._stop:
            now = self._clock.now()
            next_run = min(task.next_run for task in self._tasks)
            if next_run > end:
                self._clock.sleep_for_logical((end - now).total_seconds())
                break
            if next_run > now:
                self._clock.sleep_for_logical((next_run - now).total_seconds())
                now = self._clock.now()

            due = [task for task in self._tasks if task.next_run <= now]
            due.sort(key=lambda task: (task.next_run, task.order))

            for task in due:
                task.callback(now)
                task.next_run = task.next_run + timedelta(
                    seconds=task.interval_seconds
                )
                if self._stop:
                    break
