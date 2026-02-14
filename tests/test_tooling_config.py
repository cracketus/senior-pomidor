"""
Tests for tooling configuration.

Validates that pytest and ruff are properly configured in pyproject.toml.
"""

import tomllib
from pathlib import Path


def get_pyproject_path():
    """Get the path to pyproject.toml."""
    # Start from this file's directory and walk up to find pyproject.toml
    current = Path(__file__).parent
    while current != current.parent:
        pyproject = current.parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject
        current = current.parent

    # Fallback: check directly in workspace root
    workspace_root = Path(__file__).parent.parent
    pyproject = workspace_root / "pyproject.toml"
    if pyproject.exists():
        return pyproject

    raise FileNotFoundError("Could not find pyproject.toml")


def test_pyproject_contains_pytest_and_ruff_sections():
    """Test that pyproject.toml has pytest and ruff tool configuration."""
    pyproject_path = get_pyproject_path()

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    tools = pyproject.get("tool", {})

    # Check pytest configuration
    assert "pytest" in tools, "pytest.ini_options not configured in pyproject.toml"
    pytest_config = tools.get("pytest", {})
    assert "ini_options" in pytest_config, "pytest.ini_options section missing"

    # Check ruff configuration
    assert "ruff" in tools, "ruff not configured in pyproject.toml"
    ruff_config = tools.get("ruff", {})
    assert "line-length" in ruff_config, "ruff line-length not configured"


def test_pytest_is_in_dev_dependencies():
    """Test that pytest and pytest-cov are in dev dependencies."""
    pyproject_path = get_pyproject_path()

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
    dev_deps = optional_deps.get("dev", [])

    # Check that pytest is in dev dependencies
    pytest_found = any("pytest" in dep for dep in dev_deps)
    assert pytest_found, f"pytest not found in dev dependencies: {dev_deps}"

    # Check that pytest-cov is in dev dependencies
    cov_found = any("pytest-cov" in dep for dep in dev_deps)
    assert cov_found, f"pytest-cov not found in dev dependencies: {dev_deps}"


def test_ruff_is_in_dev_dependencies():
    """Test that ruff is in dev dependencies."""
    pyproject_path = get_pyproject_path()

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
    dev_deps = optional_deps.get("dev", [])

    # Check that ruff is in dev dependencies
    ruff_found = any("ruff" in dep for dep in dev_deps)
    assert ruff_found, f"ruff not found in dev dependencies: {dev_deps}"


def test_coverage_configuration_exists():
    """Test that coverage tool is configured."""
    pyproject_path = get_pyproject_path()

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    tools = pyproject.get("tool", {})
    assert "coverage" in tools, "coverage tool not configured in pyproject.toml"

    coverage_config = tools.get("coverage", {})
    assert "run" in coverage_config, "coverage.run section missing"
    assert "report" in coverage_config, "coverage.report section missing"
