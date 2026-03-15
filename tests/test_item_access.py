"""Tests for OrderedSet __getitem__ (signature: __getitem__(self, index: int) -> Item)."""
import pytest

from fast_ordset import OrderedSet


class TestGetItem:
    """__getitem__(self, index: int) -> Item"""

    def test_positive_index(self):
        s = OrderedSet([10, 20, 30])
        assert s[0] == 10
        assert s[1] == 20
        assert s[2] == 30

    def test_negative_index(self):
        s = OrderedSet([10, 20, 30])
        assert s[-1] == 30
        assert s[-2] == 20
        assert s[-3] == 10

    def test_single_element(self):
        s = OrderedSet([42])
        assert s[0] == 42
        assert s[-1] == 42

    def test_index_out_of_range_positive(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(IndexError, match="index out of range"):
            _ = s[3]
        with pytest.raises(IndexError, match="index out of range"):
            _ = s[10]

    def test_index_out_of_range_negative(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(IndexError, match="index out of range"):
            _ = s[-4]
        with pytest.raises(IndexError, match="index out of range"):
            _ = s[-100]

    def test_empty_set_index_error(self):
        s = OrderedSet([])
        with pytest.raises(IndexError):
            _ = s[0]
        with pytest.raises(IndexError):
            _ = s[-1]

    def test_slice_not_supported_raises_type_error(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(TypeError, match="indices must be integers"):
            _ = s[1:2]

    def test_non_integer_index_type_error(self):
        s = OrderedSet([1, 2, 3])
        with pytest.raises(TypeError, match="indices must be integers"):
            _ = s["0"]
        with pytest.raises(TypeError):
            _ = s[None]
        with pytest.raises(TypeError):
            _ = s[1.0]
