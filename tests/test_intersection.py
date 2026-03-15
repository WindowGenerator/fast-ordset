"""Tests for intersection, __and__, intersection_update, __iand__ (signatures from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestIntersection:
    """intersection(self, other_items: Sequence) -> OrderedSet"""

    def test_intersection_with_list(self):
        a = OrderedSet([1, 2, 3])
        b = a.intersection([2, 3])
        assert list(b) == [2, 3]
        assert list(a) == [1, 2, 3]

    def test_intersection_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        other = OrderedSet([2, 3, 4])
        b = a.intersection(other)
        assert list(b) == [2, 3]

    def test_intersection_with_set(self):
        a = OrderedSet([1, 2, 3])
        b = a.intersection({2, 3})
        assert set(b) == {2, 3}
        assert len(b) == 2

    def test_intersection_empty_other(self):
        a = OrderedSet([1, 2, 3])
        b = a.intersection([])
        assert list(b) == []

    def test_intersection_no_overlap(self):
        a = OrderedSet([1, 2])
        b = a.intersection([3, 4])
        assert list(b) == []

    def test_intersection_order_from_self(self):
        a = OrderedSet([3, 1, 2])
        b = a.intersection([1, 2])
        assert list(b) == [1, 2]


class TestAnd:
    """__and__(self, other_items: Sequence) -> OrderedSet"""

    def test_and_with_list(self):
        a = OrderedSet([1, 2, 3])
        b = a & [2, 3]
        assert list(b) == [2, 3]

    def test_and_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        b = a & OrderedSet([2, 3])
        assert list(b) == [2, 3]

    def test_and_with_set(self):
        a = OrderedSet([1, 2, 3])
        b = a & {2, 3}
        assert set(b) == {2, 3}


class TestIntersectionUpdate:
    """intersection_update(self, other_items: Sequence) -> None"""

    def test_intersection_update_with_list(self):
        a = OrderedSet([1, 2, 3])
        a.intersection_update([2, 3])
        assert list(a) == [2, 3]

    def test_intersection_update_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        a.intersection_update(OrderedSet([2]))
        assert list(a) == [2]

    def test_intersection_update_empty_other(self):
        a = OrderedSet([1, 2, 3])
        a.intersection_update([])
        assert list(a) == []


class TestIand:
    """__iand__(self, other_items: Sequence) -> OrderedSet (stub) / in-place in impl"""

    def test_iand_with_list(self):
        a = OrderedSet([1, 2, 3])
        a &= [2, 3]
        assert list(a) == [2, 3]

    def test_iand_with_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        a &= OrderedSet([2, 3])
        assert list(a) == [2, 3]

    def test_iand_with_set(self):
        a = OrderedSet([1, 2, 3])
        a &= {2}
        assert list(a) == [2]
