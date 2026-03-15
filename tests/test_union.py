"""Tests for union, __or__, __ior__ (signatures from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestUnion:
    """union(self, items: Sequence) -> OrderedSet"""

    def test_union_with_list(self):
        a = OrderedSet([1, 2, 3])
        b = a.union([2, 3, 4])
        assert list(b) == [1, 2, 3, 4]
        assert list(a) == [1, 2, 3]

    def test_union_with_ordered_set(self):
        a = OrderedSet([1, 2])
        other = OrderedSet([2, 3])
        b = a.union(other)
        assert list(b) == [1, 2, 3]
        assert list(a) == [1, 2]

    def test_union_with_set(self):
        a = OrderedSet([1, 2])
        b = a.union({2, 3})
        assert set(b) == {1, 2, 3}
        assert len(b) == 3

    def test_union_empty_other(self):
        a = OrderedSet([1, 2, 3])
        b = a.union([])
        assert list(b) == [1, 2, 3]

    def test_union_empty_self(self):
        a = OrderedSet([])
        b = a.union([1, 2])
        assert list(b) == [1, 2]


class TestOr:
    """__or__(self, items: Union[OrderedSet, Set]) -> OrderedSet"""

    def test_or_with_list(self):
        a = OrderedSet([1, 2])
        b = a | [2, 3]
        assert list(b) == [1, 2, 3]
        assert list(a) == [1, 2]

    def test_or_with_ordered_set(self):
        a = OrderedSet([1, 2])
        other = OrderedSet([2, 3])
        b = a | other
        assert list(b) == [1, 2, 3]

    def test_or_with_set(self):
        a = OrderedSet([1, 2])
        b = a | {2, 3}
        assert set(b) == {1, 2, 3}


class TestIor:
    """__ior__(self, items: Union[OrderedSet, Set]) -> None (in-place)"""

    def test_ior_with_list(self):
        a = OrderedSet([1, 2])
        a |= [2, 3, 4]
        assert list(a) == [1, 2, 3, 4]

    def test_ior_with_ordered_set(self):
        a = OrderedSet([1, 2])
        a |= OrderedSet([2, 3])
        assert list(a) == [1, 2, 3]

    def test_ior_with_set(self):
        a = OrderedSet([1, 2])
        a |= {2, 3}
        assert set(a) == {1, 2, 3}
        assert len(a) == 3
