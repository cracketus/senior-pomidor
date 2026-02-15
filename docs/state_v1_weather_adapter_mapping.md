# StateV1 to Weather Adapter Mapping

This document defines the deterministic bridge from flat `StateV1` to the
Stage 3 weather-adapter nested input schema.

Implementation: `brain/world_model/state_v1_weather_adapter_mapper.py`

## Target Schema

- `schema_version`: `weather_adapter_state_input_v1`
- `source_schema_version`: `state_v1`
- `timestamp`: timezone-aware ISO8601 datetime
- `confidence`: float in `[0, 1]`
- `env`: nested environment fields
- `soil`: nested soil fields and probes

## Field Mapping and Units

- `schema_version` <- constant `"weather_adapter_state_input_v1"`
- `source_schema_version` <- constant `"state_v1"`
- `timestamp` <- `StateV1.timestamp` (no conversion)
- `confidence` <- `StateV1.confidence` (no conversion)
- `env.air_temp_c` <- `StateV1.air_temperature` (Celsius, no conversion)
- `env.rh_pct` <- `StateV1.air_humidity` (percent, no conversion)
- `env.vpd_kpa` <- `StateV1.vpd` (kPa, no conversion)
- `env.co2_ppm` <- `StateV1.co2_ppm` (ppm, optional passthrough)
- `env.light_umol_m2_s` <- `StateV1.light_intensity` (umol/m^2/s, optional passthrough)
- `soil.avg_moisture_pct` <- `StateV1.soil_moisture_avg * 100`
- `soil.probes[0]` <- `StateV1.soil_moisture_p1 * 100` with `probe_id="p1"`
- `soil.probes[1]` <- `StateV1.soil_moisture_p2 * 100` with `probe_id="p2"` when present

## Validation Rules

Post-map validation is performed by constructing `WeatherAdapterStateInputV1`.
Validation enforces:

- required nested fields (`env`, `soil`, and at least one probe),
- numeric ranges (`rh_pct` in `[0,100]`, moisture in `[0,100]`, `vpd_kpa >= 0`),
- timezone-aware `timestamp`,
- bounded `confidence` in `[0,1]`.
