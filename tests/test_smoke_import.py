"""
Smoke tests for basic package import and structure.

Validates that the brain package is properly structured and importable.
"""

import sys
from pathlib import Path


def test_import_brain_package():
    """Test that brain package is importable."""
    try:
        import brain
        assert brain is not None
        assert hasattr(brain, "__version__")
    except ImportError as e:
        raise AssertionError(f"Failed to import brain package: {e}")


def test_brain_package_location():
    """Test that brain package is located in the correct directory."""
    import brain
    
    brain_path = Path(brain.__file__).parent
    assert brain_path.name == "brain"
    assert brain_path.exists()
    

def test_brain_init_has_version():
    """Test that brain.__init__ defines version."""
    import brain
    
    assert hasattr(brain, "__version__")
    assert isinstance(brain.__version__, str)
    assert len(brain.__version__) > 0
