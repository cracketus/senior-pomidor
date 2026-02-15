"""Tests for SyntheticSource behavior."""

from datetime import datetime, timezone

from brain.sources import SyntheticConfig, SyntheticSource


def test_seeded_generation_is_deterministic():
    config = SyntheticConfig(seed=123, count=3)
    src_a = SyntheticSource(config)
    src_b = SyntheticSource(config)

    seq_a = [src_a.next_observation() for _ in range(3)]
    seq_b = [src_b.next_observation() for _ in range(3)]

    assert [a[0].model_dump() for a in seq_a] == [
        b[0].model_dump() for b in seq_b
    ]
    assert [a[1].model_dump() for a in seq_a] == [
        b[1].model_dump() for b in seq_b
    ]


def test_diurnal_cycle_affects_output():
    midnight = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    noon = datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc)

    config_night = SyntheticConfig(
        seed=1,
        count=1,
        start_time=midnight,
        noise_air_temperature=0.0,
        noise_air_humidity=0.0,
        noise_light_intensity=0.0,
        diurnal_light_amp=1.0,
    )
    config_day = SyntheticConfig(
        seed=1,
        count=1,
        start_time=noon,
        noise_air_temperature=0.0,
        noise_air_humidity=0.0,
        noise_light_intensity=0.0,
        diurnal_light_amp=1.0,
    )

    night_obs, _ = SyntheticSource(config_night).next_observation()
    day_obs, _ = SyntheticSource(config_day).next_observation()

    assert day_obs.light_intensity > night_obs.light_intensity


def test_scenario_injection_changes_signal():
    def scenario_hook(obs, device, rng, step_index):
        return (
            obs.model_copy(update={"air_temperature": 35.0}),
            device,
        )

    config = SyntheticConfig(
        seed=5,
        count=1,
        scenarios=[scenario_hook],
        noise_air_temperature=0.0,
    )
    obs, _ = SyntheticSource(config).next_observation()
    assert obs.air_temperature == 35.0


def test_observations_match_observation_v1_schema():
    config = SyntheticConfig(seed=99, count=5)
    source = SyntheticSource(config)
    for _ in range(5):
        obs, device = source.next_observation()
        assert obs.schema_version == "observation_v1"
        assert device.schema_version == "device_status_v1"
