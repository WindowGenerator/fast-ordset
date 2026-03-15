"""Tests for copy (signature: copy(self) -> OrderedSet)."""
import pytest

from fast_ordset import OrderedSet


class TestCopy:
    """copy(self) -> OrderedSet"""

    def test_copy_empty(self):
        s = OrderedSet([])
        c = s.copy()
        assert c is not s
        assert list(c) == []
        assert len(c) == 0

    def test_copy_non_empty(self):
        s = OrderedSet([1, 2, 3])
        c = s.copy()
        assert c is not s
        assert list(c) == [1, 2, 3]
        assert list(s) == [1, 2, 3]

    def test_copy_is_independent(self):
        s = OrderedSet([1, 2, 3])
        c = s.copy()
        s.add(4)
        assert 4 not in c
        assert list(c) == [1, 2, 3]
        c.remove(2)
        assert 2 in s
        assert list(s) == [1, 2, 3, 4]

    def test_copy_return_type(self):
        s = OrderedSet([1])
        c = s.copy()
        assert type(c) is type(s)
        assert isinstance(c, OrderedSet)
