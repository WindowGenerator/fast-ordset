"""Tests for to_list (signature: to_list(self) -> List[Item])."""
import pytest

from fast_ordset import OrderedSet


class TestToList:
    """to_list(self) -> List[Item]"""

    def test_to_list_empty(self):
        s = OrderedSet([])
        result = s.to_list()
        assert result == []
        assert isinstance(result, list)

    def test_to_list_order_preserved(self):
        s = OrderedSet([3, 1, 2])
        assert s.to_list() == [3, 1, 2]

    def test_to_list_matches_list_of_self(self):
        s = OrderedSet([1, 2, 3, 2, 1])
        assert s.to_list() == list(s)

    def test_to_list_returns_new_list(self):
        s = OrderedSet([1, 2, 3])
        a = s.to_list()
        b = s.to_list()
        assert a == b
        assert a is not b

    def test_to_list_result_is_plain_list(self):
        s = OrderedSet([1])
        result = s.to_list()
        assert type(result) is list
        assert isinstance(result, list)

    def test_to_list_after_mutation(self):
        s = OrderedSet([1, 2, 3])
        lst = s.to_list()
        s.add(4)
        s.remove(2)
        assert lst == [1, 2, 3]
        assert s.to_list() == [1, 3, 4]

    def test_to_list_single_element(self):
        s = OrderedSet([42])
        assert s.to_list() == [42]

    def test_to_list_duplicates_removed_order_kept(self):
        s = OrderedSet([2, 1, 2, 3, 1, 3])
        assert s.to_list() == [2, 1, 3]

    def test_to_list_heterogeneous(self):
        s = OrderedSet(["a", 1, None, (1, 2)])
        result = s.to_list()
        assert result == ["a", 1, None, (1, 2)]
        assert isinstance(result, list)
