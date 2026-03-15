"""Tests for symmetric_difference, __xor__, symmetric_difference_update, __ixor__."""
import pytest

from fast_ordset import OrderedSet


class TestSymmetricDifference:
    """symmetric_difference(self, other_items: Sequence) -> OrderedSet"""

    def test_symmetric_difference_both_sides(self):
        a = OrderedSet([1, 2, 3])
        b = a.symmetric_difference([2, 3, 4])
        assert set(b) == {1, 4}
        assert len(b) == 2
        assert list(a) == [1, 2, 3]

    def test_symmetric_difference_with_ordered_set(self):
        a = OrderedSet([1, 2])
        other = OrderedSet([2, 3])
        b = a.symmetric_difference(other)
        assert set(b) == {1, 3}
        assert len(b) == 2

    def test_symmetric_difference_with_set(self):
        a = OrderedSet([1, 2])
        b = a.symmetric_difference({2, 3})
        assert set(b) == {1, 3}

    def test_symmetric_difference_empty_other(self):
        a = OrderedSet([1, 2, 3])
        b = a.symmetric_difference([])
        assert list(b) == [1, 2, 3]

    def test_symmetric_difference_empty_self(self):
        a = OrderedSet([])
        b = a.symmetric_difference([1, 2])
        assert list(b) == [1, 2]

    def test_symmetric_difference_no_overlap(self):
        a = OrderedSet([1, 2])
        b = a.symmetric_difference([3, 4])
        assert set(b) == {1, 2, 3, 4}
        assert len(b) == 4

    def test_symmetric_difference_full_overlap(self):
        a = OrderedSet([1, 2])
        b = a.symmetric_difference([1, 2])
        assert list(b) == []


class TestXor:
    """__xor__(self, other_items: Union[OrderedSet, Set]) -> OrderedSet"""

    def test_xor_with_list(self):
        a = OrderedSet([1, 2])
        b = a ^ [2, 3]
        assert set(b) == {1, 3}

    def test_xor_with_ordered_set(self):
        a = OrderedSet([1, 2])
        b = a ^ OrderedSet([2, 3])
        assert set(b) == {1, 3}

    def test_xor_with_set(self):
        a = OrderedSet([1, 2])
        b = a ^ {2, 3}
        assert set(b) == {1, 3}


class TestSymmetricDifferenceUpdate:
    """symmetric_difference_update(self, other_items: Sequence) -> None"""

    def test_symmetric_difference_update_with_list(self):
        a = OrderedSet([1, 2, 3])
        a.symmetric_difference_update([2, 3, 4])
        assert set(a) == {1, 4}
        assert len(a) == 2

    def test_symmetric_difference_update_with_ordered_set(self):
        a = OrderedSet([1, 2])
        a.symmetric_difference_update(OrderedSet([2, 3]))
        assert set(a) == {1, 3}


class TestIxor:
    """__ixor__(self, other_items: Union[OrderedSet, Set]) -> None"""

    def test_ixor_with_list(self):
        a = OrderedSet([1, 2])
        a ^= [2, 3]
        assert set(a) == {1, 3}

    def test_ixor_with_ordered_set(self):
        a = OrderedSet([1, 2])
        a ^= OrderedSet([2, 3])
        assert set(a) == {1, 3}

    def test_ixor_with_set(self):
        a = OrderedSet([1, 2])
        a ^= {2, 3}
        assert set(a) == {1, 3}
