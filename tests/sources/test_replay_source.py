"""Tests for ReplaySource behavior."""

import json
from datetime import datetime, timezone

import pytest

from brain.sources import ReplaySource


def _make_payload(index: int) -> dict:
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    return {
        "observation": {
            "schema_version": "observation_v1",
            "timestamp": (now).isoformat(),
            "soil_moisture_p1": 0.4 + index * 0.01,
            "soil_moisture_p2": 0.5 + index * 0.01,
            "air_temperature": 20.0 + index,
            "air_humidity": 55.0,
            "co2_ppm": 410.0,
            "light_intensity": 250.0,
        },
        "device_status": {
            "schema_version": "device_status_v1",
            "timestamp": (now).isoformat(),
            "light_on": True,
            "fans_on": False,
            "heater_on": False,
            "pump_on": False,
            "co2_on": False,
            "mcu_connected": True,
            "mcu_uptime_seconds": 60 * index,
            "mcu_reset_count": 0,
            "light_intensity_setpoint": 250.0,
            "pump_pulse_count": 0,
        },
    }


def test_reads_jsonl_in_order(tmp_path):
    path = tmp_path / "obs.jsonl"
    lines = [json.dumps(_make_payload(i)) for i in range(3)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    source = ReplaySource(str(path))
    seq = [source.next_observation() for _ in range(3)]
    assert [s[0].air_temperature for s in seq] == [20.0, 21.0, 22.0]


def test_returns_none_after_eof(tmp_path):
    path = tmp_path / "obs.jsonl"
    path.write_text(json.dumps(_make_payload(0)) + "\n", encoding="utf-8")
    source = ReplaySource(str(path))
    assert source.next_observation() is not None
    assert source.next_observation() is None
    assert source.next_observation() is None


def test_malformed_line_policy(tmp_path, caplog):
    path = tmp_path / "obs.jsonl"
    lines = [
        json.dumps(_make_payload(0)),
        "{not-json}",
        json.dumps(_make_payload(1)),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    source = ReplaySource(str(path), malformed_policy="skip")
    with caplog.at_level("WARNING"):
        first = source.next_observation()
        second = source.next_observation()
    assert first is not None
    assert second is not None
    assert any("Malformed JSONL" in rec.message for rec in caplog.records)

    source_fail = ReplaySource(str(path), malformed_policy="fail_fast")
    assert source_fail.next_observation() is not None
    with pytest.raises(ValueError):
        source_fail.next_observation()
