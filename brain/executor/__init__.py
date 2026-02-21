"""Executor implementations for simulation and hardware dispatch foundations."""

from .hardware_adapter import (
    FlakyStubAdapter,
    HardwareDispatchResult,
    HardwareStubAdapter,
    ProductionScaffoldAdapter,
    available_hardware_adapters,
    create_hardware_adapter,
    get_hardware_adapter_factory,
    register_hardware_adapter,
)
from .hardware_executor import HardwareExecutor
from .hardware_state_machine import (
    ExecutorRuntimeState,
    HardwareExecutionStateMachine,
    StateMachineConfig,
    StateTransition,
)
from .mock_executor import MockExecutor
from .retry_policy import RetryPolicyConfig

__all__ = [
    "HardwareDispatchResult",
    "HardwareExecutor",
    "ExecutorRuntimeState",
    "FlakyStubAdapter",
    "HardwareExecutionStateMachine",
    "ProductionScaffoldAdapter",
    "StateMachineConfig",
    "StateTransition",
    "HardwareStubAdapter",
    "MockExecutor",
    "available_hardware_adapters",
    "create_hardware_adapter",
    "get_hardware_adapter_factory",
    "register_hardware_adapter",
    "RetryPolicyConfig",
]
