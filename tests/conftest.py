"""Shared pytest configuration and fixtures for fast_ordset tests."""
import pytest

try:
    from fast_ordset import OrderedSet
except ImportError:
    pytest.skip(
        "fast_ordset not installed. Run: maturin develop (from project root, with venv active)",
        allow_module_level=True,
    )


@pytest.fixture
def ordered_set():
    """Return the OrderedSet class (for tests that need the type)."""
    return OrderedSet


@pytest.fixture
def empty():
    """Return an empty OrderedSet."""
    return OrderedSet([])


@pytest.fixture
def three_items():
    """Return an OrderedSet containing [1, 2, 3]."""
    return OrderedSet([1, 2, 3])
