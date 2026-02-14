"""
Tests for project metadata configuration.

Validates that pyproject.toml and project configuration target Python 3.11.
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


def test_python_version_target_is_311():
    """Test that project targets Python 3.11."""
    pyproject_path = get_pyproject_path()
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    
    # Check that requires-python is set correctly
    requires_python = pyproject.get("project", {}).get("requires-python")
    assert requires_python is not None, "requires-python not set in pyproject.toml"
    
    # Python 3.11 should be mentioned
    assert "3.11" in requires_python, f"Python 3.11 not found in requires-python: {requires_python}"


def test_project_has_name():
    """Test that project has a name."""
    pyproject_path = get_pyproject_path()
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    
    name = pyproject.get("project", {}).get("name")
    assert name is not None, "Project name not set"
    assert len(name) > 0, "Project name is empty"


def test_project_has_version():
    """Test that project has a version."""
    pyproject_path = get_pyproject_path()
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    
    version = pyproject.get("project", {}).get("version")
    assert version is not None, "Project version not set"
    assert len(version) > 0, "Project version is empty"
