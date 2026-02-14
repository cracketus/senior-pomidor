"""Tests for project metadata configuration.

Validates that pyproject.toml and project configuration target Python 3.11.
"""

import tomllib
from pathlib import Path


def get_pyproject_path() -> Path:
    current = Path(__file__).parent
    while current != current.parent:
        candidate = current.parent / "pyproject.toml"
        if candidate.exists():
            return candidate
        current = current.parent

    workspace_root = Path(__file__).parent.parent
    candidate = workspace_root / "pyproject.toml"
    if candidate.exists():
        return candidate

    raise FileNotFoundError("Could not find pyproject.toml")


def _load_pyproject(path: Path) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def test_python_version_target_is_311():
    pyproject = _load_pyproject(get_pyproject_path())
    requires_python = pyproject.get("project", {}).get("requires-python")
    assert requires_python is not None, "requires-python not set in pyproject.toml"
    assert "3.11" in requires_python, (
        f"Python 3.11 not found in requires-python: {requires_python}"
    )


def test_project_has_name():
    pyproject = _load_pyproject(get_pyproject_path())
    name = pyproject.get("project", {}).get("name")
    assert name is not None and len(name) > 0, "Project name missing or empty"


def test_project_has_version():
    pyproject = _load_pyproject(get_pyproject_path())
    version = pyproject.get("project", {}).get("version")
    assert version is not None and len(version) > 0, "Project version missing or empty"
