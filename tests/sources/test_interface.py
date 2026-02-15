"""Tests for observation source interface compliance."""

from datetime import datetime, timezone

from brain.contracts import DeviceStatusV1, ObservationV1
from brain.sources import ReplaySource, SyntheticConfig, SyntheticSource


def _make_replay_file(tmp_path):
    path = tmp_path / "obs.jsonl"
    payload = {
        "observation": {
            "schema_version": "observation_v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "soil_moisture_p1": 0.5,
            "soil_moisture_p2": 0.52,
            "air_temperature": 22.0,
            "air_humidity": 60.0,
            "co2_ppm": 420.0,
            "light_intensity": 300.0,
        },
        "device_status": {
            "schema_version": "device_status_v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "light_on": True,
            "fans_on": False,
            "heater_on": False,
            "pump_on": False,
            "co2_on": False,
            "mcu_connected": True,
            "mcu_uptime_seconds": 120,
            "mcu_reset_count": 0,
            "light_intensity_setpoint": 300.0,
            "pump_pulse_count": 0,
        },
    }
    path.write_text(__import__("json").dumps(payload) + "\n", encoding="utf-8")
    return path


def test_sources_implement_next_observation_contract(tmp_path):
    config = SyntheticConfig(count=1)
    synthetic = SyntheticSource(config)
    item = synthetic.next_observation()
    assert item is not None
    obs, device = item
    assert isinstance(obs, ObservationV1)
    assert isinstance(device, DeviceStatusV1)

    replay_path = _make_replay_file(tmp_path)
    replay = ReplaySource(str(replay_path))
    item = replay.next_observation()
    assert item is not None
    obs, device = item
    assert isinstance(obs, ObservationV1)
    assert isinstance(device, DeviceStatusV1)
