"""Tests for OrderedSet __iter__ and iteration (signature: __iter__(self) -> Iterator)."""
import pytest

from fast_ordset import OrderedSet


class TestIter:
    """__iter__(self) -> Iterator"""

    def test_iter_empty(self):
        s = OrderedSet([])
        assert list(s) == []
        assert list(iter(s)) == []

    def test_iter_order_preserved(self):
        s = OrderedSet([3, 1, 2])
        assert list(s) == [3, 1, 2]
        assert list(iter(s)) == [3, 1, 2]

    def test_iter_multiple_consumption(self):
        s = OrderedSet([1, 2, 3])
        assert list(s) == [1, 2, 3]
        assert list(s) == [1, 2, 3]

    def test_for_loop(self):
        s = OrderedSet(["a", "b", "c"])
        out = []
        for x in s:
            out.append(x)
        assert out == ["a", "b", "c"]

    def test_iterator_protocol_next(self):
        s = OrderedSet([10, 20])
        it = iter(s)
        assert next(it) == 10
        assert next(it) == 20
        with pytest.raises(StopIteration):
            next(it)

    def test_iterator_is_itself_iterable(self):
        s = OrderedSet([1, 2])
        it = iter(s)
        assert list(it) == [1, 2]
