"""Tests for OrderedSet construction, __contains__, and __len__ (signature from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestConstruct:
    """__init__(self, initial_items: Sequence) -> None"""

    def test_empty_from_list(self):
        s = OrderedSet([])
        assert len(s) == 0
        assert list(s) == []

    def test_empty_from_tuple(self):
        s = OrderedSet(())
        assert len(s) == 0

    def test_from_list_no_duplicates(self):
        s = OrderedSet([3, 1, 2])
        assert len(s) == 3
        assert list(s) == [3, 1, 2]

    def test_from_list_with_duplicates_preserves_order(self):
        s = OrderedSet([1, 2, 1, 3, 2, 1])
        assert len(s) == 3
        assert list(s) == [1, 2, 3]

    def test_from_tuple(self):
        s = OrderedSet((5, 4, 5, 6))
        assert len(s) == 3
        assert list(s) == [5, 4, 6]

    def test_from_range(self):
        s = OrderedSet(range(3))
        assert len(s) == 3
        assert list(s) == [0, 1, 2]

    def test_from_set_order_arbitrary(self):
        s = OrderedSet({1, 2, 3})
        assert len(s) == 3
        assert set(s) == {1, 2, 3}

    def test_from_string_single_chars(self):
        s = OrderedSet("aba")
        assert len(s) == 2
        assert list(s) == ["a", "b"]

    def test_from_generator(self):
        s = OrderedSet(x for x in [2, 1, 2, 3])
        assert len(s) == 3
        assert list(s) == [2, 1, 3]


class TestContains:
    """__contains__(self, item: Item) -> bool"""

    def test_contains_present(self):
        s = OrderedSet([1, 2, 3])
        assert 1 in s
        assert 2 in s
        assert 3 in s

    def test_contains_absent(self):
        s = OrderedSet([1, 2, 3])
        assert 0 not in s
        assert 4 not in s

    def test_contains_after_add(self):
        s = OrderedSet([1])
        assert 2 not in s
        s.add(2)
        assert 2 in s

    def test_contains_after_remove(self):
        s = OrderedSet([1, 2])
        s.remove(1)
        assert 1 not in s
        assert 2 in s

    def test_contains_empty(self):
        s = OrderedSet([])
        assert 1 not in s

    def test_contains_hashable_types(self):
        s = OrderedSet([(1, 2), "a", frozenset([1])])
        assert (1, 2) in s
        assert "a" in s
        assert frozenset([1]) in s
