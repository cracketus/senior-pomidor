"""Hardware adapter interface, registry, and built-in driver implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol

from brain.contracts import ActionV1
from brain.contracts.action_v1 import ActionType


@dataclass(frozen=True)
class HardwareDispatchResult:
    """Result from dispatching a validated action to an actuator backend."""

    accepted: bool
    command: str
    duration_seconds: float | None
    adapter_name: str
    retryable: bool = False
    error_class: str | None = None
    details: str | None = None

    def __post_init__(self) -> None:
        if not self.command:
            raise ValueError("command must be non-empty")
        if not self.adapter_name:
            raise ValueError("adapter_name must be non-empty")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0")
        if self.accepted and self.retryable:
            raise ValueError("accepted results cannot be retryable")
        if self.accepted and self.error_class is not None:
            raise ValueError("accepted results cannot include error_class")


class HardwareAdapter(Protocol):
    """Abstraction for actuator command dispatch backends."""

    @property
    def adapter_name(self) -> str:
        """Stable adapter identity used in logs and observability."""

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        """Dispatch an action and return deterministic execution metadata."""


class HardwareStubAdapter:
    """Deterministic no-op adapter that mimics hardware command routing."""

    _COMMAND_MAP = {
        ActionType.WATER.value: "WATER_PULSE",
        ActionType.LIGHT.value: "SET_LIGHT",
        ActionType.FAN.value: "SET_FAN",
        ActionType.CO2.value: "CO2_INJECT",
        ActionType.CIRCULATE.value: "SET_CIRCULATION",
    }

    @property
    def adapter_name(self) -> str:
        return "hardware_stub"

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        command = self._COMMAND_MAP.get(str(action.action_type), "UNKNOWN")
        return HardwareDispatchResult(
            accepted=True,
            command=command,
            duration_seconds=action.duration_seconds,
            adapter_name=self.adapter_name,
            details=f"hardware_stub_dispatched_at={now.isoformat()}",
        )


class ProductionScaffoldAdapter:
    """
    Production-intended adapter scaffold.

    TODO(stage-5+): replace deterministic no-op dispatch path with real hardware driver I/O.
    """

    _COMMAND_MAP = {
        ActionType.WATER.value: "ACTUATOR_WATER_PULSE",
        ActionType.LIGHT.value: "ACTUATOR_LIGHT_SET",
        ActionType.FAN.value: "ACTUATOR_FAN_SET",
        ActionType.CO2.value: "ACTUATOR_CO2_INJECT",
        ActionType.CIRCULATE.value: "ACTUATOR_CIRCULATION_SET",
    }

    @property
    def adapter_name(self) -> str:
        return "production_scaffold"

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        command = self._COMMAND_MAP.get(str(action.action_type), "ACTUATOR_UNKNOWN")
        return HardwareDispatchResult(
            accepted=True,
            command=command,
            duration_seconds=action.duration_seconds,
            adapter_name=self.adapter_name,
            details=(
                "TODO: wire production device transport; "
                f"scaffold_dispatched_at={now.isoformat()}"
            ),
        )


class FlakyStubAdapter:
    """Deterministic flaky adapter used to exercise runtime retry behavior."""

    def __init__(self) -> None:
        self._dispatch_calls = 0

    @property
    def adapter_name(self) -> str:
        return "flaky_stub"

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        self._dispatch_calls += 1
        if self._dispatch_calls % 2 == 1:
            return HardwareDispatchResult(
                accepted=False,
                command="TRANSIENT_IO",
                duration_seconds=action.duration_seconds,
                adapter_name=self.adapter_name,
                retryable=True,
                error_class="transient_io",
                details=f"flaky_stub_transient_failure_at={now.isoformat()}",
            )
        return HardwareDispatchResult(
            accepted=True,
            command="FLAKY_RECOVERED_DISPATCH",
            duration_seconds=action.duration_seconds,
            adapter_name=self.adapter_name,
            details=f"flaky_stub_recovered_at={now.isoformat()}",
        )


HardwareAdapterFactory = Callable[[], HardwareAdapter]

_ADAPTER_FACTORIES: dict[str, HardwareAdapterFactory] = {
    "hardware_stub": HardwareStubAdapter,
    "production_scaffold": ProductionScaffoldAdapter,
    "flaky_stub": FlakyStubAdapter,
}


def register_hardware_adapter(name: str, factory: HardwareAdapterFactory) -> None:
    """Register a hardware adapter factory by stable name."""
    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("adapter name must be non-empty")
    _ADAPTER_FACTORIES[normalized] = factory


def available_hardware_adapters() -> tuple[str, ...]:
    """Return sorted registered adapter names."""
    return tuple(sorted(_ADAPTER_FACTORIES))


def get_hardware_adapter_factory(name: str) -> HardwareAdapterFactory:
    """Lookup adapter factory by name."""
    normalized = name.strip().lower()
    try:
        return _ADAPTER_FACTORIES[normalized]
    except KeyError as exc:
        known = ", ".join(available_hardware_adapters())
        raise ValueError(f"unknown hardware adapter '{name}'; known: {known}") from exc


def create_hardware_adapter(name: str) -> HardwareAdapter:
    """Create an adapter instance from the registry."""
    return get_hardware_adapter_factory(name)()
