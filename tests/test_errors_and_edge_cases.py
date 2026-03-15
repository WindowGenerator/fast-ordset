"""Tests for error paths and edge cases (unhashable, non-iterable, etc.)."""
import pytest

from fast_ordset import OrderedSet


class TestUnhashableInContains:
    """__contains__ with unhashable item may raise TypeError."""

    def test_contains_unhashable_raises(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(TypeError):
            _ = [] in s
        with pytest.raises(TypeError):
            _ = {} in s


class TestUnhashableInAdd:
    """add() with unhashable item."""

    def test_add_unhashable_raises(self):
        s = OrderedSet([])
        with pytest.raises(TypeError):
            s.add([])
        with pytest.raises(TypeError):
            s.add({})


class TestUnhashableInInit:
    """__init__ with unhashable elements in sequence."""

    def test_init_unhashable_raises(self):
        with pytest.raises(TypeError):
            OrderedSet([[1], [2]])
        with pytest.raises(TypeError):
            OrderedSet([1, 2, [3]])


class TestUpdateNonIterable:
    """update() with non-iterable may raise."""

    def test_update_non_iterable_raises(self):
        s = OrderedSet([1])
        with pytest.raises(TypeError):
            s.update(42)
        with pytest.raises(TypeError):
            s.update(None)


class TestUnionNonIterable:
    """union() with non-iterable may raise."""

    def test_union_non_iterable_raises(self):
        s = OrderedSet([1])
        with pytest.raises(TypeError):
            s.union(42)


class TestEqNonSequence:
    """__eq__ with non-iterable value."""

    def test_eq_non_iterable_raises(self):
        s = OrderedSet([1, 2])
        with pytest.raises(TypeError):
            _ = s == 42


class TestInitNoArgs:
    """__init__ called with no arguments (optional behavior)."""

    def test_init_no_args_either_works_or_type_error(self):
        try:
            s = OrderedSet()
            assert len(s) == 0
            assert list(s) == []
        except TypeError:
            pass


class TestRemoveKeyErrorMessage:
    """remove() KeyError includes key repr."""

    def test_remove_key_error_repr(self):
        s = OrderedSet([1, 2])
        with pytest.raises(KeyError) as exc_info:
            s.remove(99)
        assert "99" in str(exc_info.value) or "99" in repr(exc_info.value)


class TestChainedOperations:
    """Chained in-place and binary operations."""

    def test_chain_union_then_difference(self):
        a = OrderedSet([1, 2, 3])
        b = a.union([4]).difference([2])
        assert set(b) == {1, 3, 4}

    def test_chain_in_place(self):
        a = OrderedSet([1, 2, 3])
        a.update([4])
        a.difference_update([2])
        assert list(a) == [1, 3, 4]
