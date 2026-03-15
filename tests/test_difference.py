"""Tests for difference, __sub__, difference_update, __isub__ (signatures from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestDifference:
    """difference(self, other_items: Sequence) -> OrderedSet"""

    def test_difference_with_list(self):
        a = OrderedSet([1, 2, 3])
        b = a.difference([2])
        assert list(b) == [1, 3]
        assert list(a) == [1, 2, 3]

    def test_difference_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        other = OrderedSet([2])
        b = a.difference(other)
        assert list(b) == [1, 3]

    def test_difference_with_set(self):
        a = OrderedSet([1, 2, 3])
        b = a.difference({2})
        assert list(b) == [1, 3]

    def test_difference_empty_other(self):
        a = OrderedSet([1, 2, 3])
        b = a.difference([])
        assert list(b) == [1, 2, 3]

    def test_difference_all_removed(self):
        a = OrderedSet([1, 2])
        b = a.difference([1, 2])
        assert list(b) == []

    def test_difference_none_removed(self):
        a = OrderedSet([1, 2, 3])
        b = a.difference([0, 4])
        assert list(b) == [1, 2, 3]


class TestSub:
    """__sub__(self, items: Union[OrderedSet, Set]) -> OrderedSet"""

    def test_sub_with_list(self):
        a = OrderedSet([1, 2, 3])
        b = a - [2]
        assert list(b) == [1, 3]

    def test_sub_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        other = OrderedSet([2])
        b = a - other
        assert list(b) == [1, 3]

    def test_sub_with_set(self):
        a = OrderedSet([1, 2, 3])
        b = a - {2}
        assert list(b) == [1, 3]


class TestDifferenceUpdate:
    """difference_update(self, other_items: Sequence) -> None"""

    def test_difference_update_with_list(self):
        a = OrderedSet([1, 2, 3])
        a.difference_update([2])
        assert list(a) == [1, 3]

    def test_difference_update_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        a.difference_update(OrderedSet([2]))
        assert list(a) == [1, 3]

    def test_difference_update_empty_other(self):
        a = OrderedSet([1, 2, 3])
        a.difference_update([])
        assert list(a) == [1, 2, 3]


class TestIsub:
    """__isub__(self, items: Union[OrderedSet, Set]) -> None"""

    def test_isub_with_list(self):
        a = OrderedSet([1, 2, 3])
        a -= [2]
        assert list(a) == [1, 3]

    def test_isub_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        a -= OrderedSet([2])
        assert list(a) == [1, 3]

    def test_isub_with_set(self):
        a = OrderedSet([1, 2, 3])
        a -= {2}
        assert list(a) == [1, 3]
