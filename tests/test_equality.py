"""Tests for OrderedSet __eq__ (signature: __eq__(self, value: Sequence, /) -> bool)."""
import pytest

from fast_ordset import OrderedSet


class TestEq:
    """__eq__(self, value: Sequence, /) -> bool"""

    def test_equal_same_order_list(self):
        s = OrderedSet([1, 2, 3])
        assert s == [1, 2, 3]
        assert s == (1, 2, 3)

    def test_equal_ordered_set(self):
        a = OrderedSet([1, 2, 3])
        b = OrderedSet([1, 2, 3])
        assert a == b
        assert a == list(b)

    def test_not_equal_different_order(self):
        s = OrderedSet([1, 2, 3])
        assert s != [1, 3, 2]
        assert s != (3, 2, 1)

    def test_not_equal_different_length(self):
        s = OrderedSet([1, 2, 3])
        assert s != [1, 2]
        assert s != [1, 2, 3, 4]

    def test_not_equal_different_elements(self):
        s = OrderedSet([1, 2, 3])
        assert s != [1, 2, 4]
        assert s != []

    def test_empty_equal(self):
        s = OrderedSet([])
        assert s == []
        assert s == ()
        assert s == OrderedSet([])

    def test_single_element(self):
        s = OrderedSet([42])
        assert s == [42]
        assert s != [41]
        assert s != [42, 43]

    def test_eq_with_iterable(self):
        s = OrderedSet([1, 2])
        assert s == (1, 2)
        assert s == range(1, 3)  # range is sequence in Python 3
