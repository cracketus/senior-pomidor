"""Replay observation source from JSONL files."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, TextIO

from brain.contracts import DeviceStatusV1, ObservationV1

logger = logging.getLogger(__name__)


class ReplaySource:
    """Replay ObservationV1 + DeviceStatusV1 records from JSONL.

    Each JSONL line must be a JSON object with keys:
    - "observation": dict matching ObservationV1
    - "device_status": dict matching DeviceStatusV1
    """

    def __init__(
        self,
        path: str,
        malformed_policy: Literal["skip", "fail_fast"] = "skip",
    ) -> None:
        if malformed_policy not in {"skip", "fail_fast"}:
            raise ValueError(
                "malformed_policy must be 'skip' or 'fail_fast'"
            )
        self._path = Path(path)
        self._policy = malformed_policy
        self._handle: Optional[TextIO] = None
        self._line_no = 0

    def _ensure_open(self) -> None:
        if self._handle is None:
            self._handle = self._path.open("r", encoding="utf-8")

    @staticmethod
    def _parse_timestamp(value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value)
        return value

    def next_observation(
        self,
    ) -> tuple[ObservationV1, DeviceStatusV1] | None:
        self._ensure_open()
        assert self._handle is not None
        while True:
            line = self._handle.readline()
            if line == "":
                return None
            self._line_no += 1
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                observation_payload = payload["observation"]
                device_payload = payload["device_status"]
                if "timestamp" in observation_payload:
                    observation_payload["timestamp"] = self._parse_timestamp(
                        observation_payload["timestamp"]
                    )
                if "timestamp" in device_payload:
                    device_payload["timestamp"] = self._parse_timestamp(
                        device_payload["timestamp"]
                    )
                observation = ObservationV1(**observation_payload)
                device_status = DeviceStatusV1(**device_payload)
                return observation, device_status
            except Exception as exc:  # noqa: BLE001
                if self._policy == "fail_fast":
                    raise ValueError(
                        f"Malformed JSONL at line {self._line_no}"
                    ) from exc
                logger.warning(
                    "Malformed JSONL at line %s: %s",
                    self._line_no,
                    exc,
                )
                continue
