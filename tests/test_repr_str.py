"""Tests for OrderedSet __repr__ and __str__ (signatures from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestRepr:
    """__repr__(self) -> str"""

    def test_repr_empty(self):
        s = OrderedSet([])
        assert repr(s) == "OrderedSet([])"

    def test_repr_single(self):
        s = OrderedSet([1])
        assert repr(s) == "OrderedSet([1])"

    def test_repr_several(self):
        s = OrderedSet([1, 2, 3])
        r = repr(s)
        assert r.startswith("OrderedSet([")
        assert r.endswith("])")
        assert "1" in r and "2" in r and "3" in r

    def test_repr_strings(self):
        s = OrderedSet(["a", "b"])
        r = repr(s)
        assert "'a'" in r and "'b'" in r


class TestStr:
    """__str__(self) -> str"""

    def test_str_equals_repr(self):
        s = OrderedSet([1, 2])
        assert str(s) == repr(s)

    def test_str_empty(self):
        s = OrderedSet([])
        assert str(s) == "OrderedSet([])"
