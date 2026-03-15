"""Tests for add, remove, pop, clear, update (signatures from __init__.pyi)."""
import pytest

from fast_ordset import OrderedSet


class TestAdd:
    """add(self, item: Item) -> None"""

    def test_add_to_empty(self):
        s = OrderedSet([])
        s.add(1)
        assert list(s) == [1]
        assert len(s) == 1

    def test_add_duplicate_no_effect(self):
        s = OrderedSet([1, 2])
        s.add(1)
        assert list(s) == [1, 2]
        assert len(s) == 2

    def test_add_new_at_end(self):
        s = OrderedSet([1, 2])
        s.add(3)
        assert list(s) == [1, 2, 3]


class TestRemove:
    """remove(self, item: Item) -> None"""

    def test_remove_present(self):
        s = OrderedSet([1, 2, 3])
        s.remove(2)
        assert list(s) == [1, 3]
        assert len(s) == 2

    def test_remove_first(self):
        s = OrderedSet([1, 2, 3])
        s.remove(1)
        assert list(s) == [2, 3]

    def test_remove_last(self):
        s = OrderedSet([1, 2, 3])
        s.remove(3)
        assert list(s) == [1, 2]

    def test_remove_absent_raises_key_error(self):
        s = OrderedSet([1, 2])
        with pytest.raises(KeyError):
            s.remove(3)
        with pytest.raises(KeyError):
            s.remove("x")

    def test_remove_from_single(self):
        s = OrderedSet([1])
        s.remove(1)
        assert len(s) == 0
        assert list(s) == []


class TestPop:
    """pop(self, index: int) -> Item (implementation default index=-1)"""

    def test_pop_default_last(self):
        s = OrderedSet([1, 2, 3])
        x = s.pop()
        assert x == 3
        assert list(s) == [1, 2]

    def test_pop_explicit_minus_one(self):
        s = OrderedSet([1, 2, 3])
        x = s.pop(-1)
        assert x == 3
        assert list(s) == [1, 2]

    def test_pop_zero(self):
        s = OrderedSet([1, 2, 3])
        x = s.pop(0)
        assert x == 1
        assert list(s) == [2, 3]

    def test_pop_middle(self):
        s = OrderedSet([1, 2, 3])
        x = s.pop(1)
        assert x == 2
        assert list(s) == [1, 3]

    def test_pop_negative_index(self):
        s = OrderedSet([1, 2, 3])
        x = s.pop(-2)
        assert x == 2
        assert list(s) == [1, 3]

    def test_pop_empty_raises_key_error(self):
        s = OrderedSet([])
        with pytest.raises(KeyError, match="pop from an empty set"):
            s.pop()

    def test_pop_index_out_of_range_raises_index_error(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(IndexError, match="pop index out of range"):
            s.pop(10)
        with pytest.raises(IndexError, match="pop index out of range"):
            s.pop(-10)

    def test_pop_single_element(self):
        s = OrderedSet([42])
        assert s.pop() == 42
        assert len(s) == 0


class TestClear:
    """clear(self) -> None"""

    def test_clear_non_empty(self):
        s = OrderedSet([1, 2, 3])
        s.clear()
        assert len(s) == 0
        assert list(s) == []

    def test_clear_empty(self):
        s = OrderedSet([])
        s.clear()
        assert len(s) == 0


class TestUpdate:
    """update(self, items: Sequence) -> None"""

    def test_update_with_list(self):
        s = OrderedSet([1])
        s.update([2, 3, 1, 4])
        assert len(s) == 4
        assert list(s) == [1, 2, 3, 4]

    def test_update_with_tuple(self):
        s = OrderedSet([1])
        s.update((2, 3))
        assert list(s) == [1, 2, 3]

    def test_update_empty_sequence(self):
        s = OrderedSet([1, 2])
        s.update([])
        assert list(s) == [1, 2]

    def test_update_from_empty_set(self):
        s = OrderedSet([])
        s.update([1, 2, 3])
        assert list(s) == [1, 2, 3]

    def test_update_preserves_order_new_at_end(self):
        s = OrderedSet([1, 2])
        s.update([3, 2, 4])
        assert list(s) == [1, 2, 3, 4]
