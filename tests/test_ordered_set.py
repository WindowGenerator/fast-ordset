#!/usr/bin/env python3
"""Smoke tests for fast_ordset.OrderedSet (run after maturin develop or pip install)."""
import sys

try:
    from fast_ordset import OrderedSet
except ImportError:
    print("Run: maturin develop  (from project root, with venv active)")
    print("  or: pip install .  (after maturin build)")
    sys.exit(1)

def test_basic():
    s = OrderedSet([])
    assert len(s) == 0
    s.add(1)
    s.add(2)
    s.add(1)
    assert len(s) == 2
    assert 1 in s
    assert 2 in s
    assert 3 not in s
    assert s[0] == 1
    assert s[1] == 2
    assert s[-1] == 2
    assert s[-2] == 1

def test_remove():
    s = OrderedSet([])
    s.add("a")
    s.add("b")
    s.remove("a")
    assert len(s) == 1
    assert "a" not in s
    assert "b" in s
    assert s[0] == "b"
    try:
        s.remove("x")
        assert False, "KeyError expected"
    except KeyError:
        pass

def test_update():
    s = OrderedSet([])
    s.add(1)
    s.update([2, 3, 1, 4])
    assert len(s) == 4
    assert list(s) == [1, 2, 3, 4]

def test_iter():
    s = OrderedSet([])
    s.add(10)
    s.add(20)
    assert list(iter(s)) == [10, 20]
    assert list(s) == [10, 20]

def test_pop():
    s = OrderedSet([])
    s.add("first")
    s.add("last")
    x = s.pop()
    assert x == "last"
    assert len(s) == 1
    assert s[0] == "first"
    y = s.pop()
    assert y == "first"
    assert len(s) == 0
    try:
        s.pop()
        assert False, "KeyError expected"
    except KeyError:
        pass

def test_difference():
    a = OrderedSet([])
    a.add(1)
    a.add(2)
    a.add(3)
    b = OrderedSet([])
    b.add(2)
    d = a.difference(b)
    assert list(d) == [1, 3]
    # other as iterable
    d2 = a.difference([2])
    assert list(d2) == [1, 3]

def test_intersection():
    a = OrderedSet([])
    a.add(1)
    a.add(2)
    a.add(3)
    b = OrderedSet([])
    b.add(2)
    b.add(3)
    i = a.intersection(b)
    assert list(i) == [2, 3]
    i2 = a.intersection([2, 3])
    assert list(i2) == [2, 3]

def test_symmetric_difference():
    a = OrderedSet([])
    a.add(1)
    a.add(2)
    b = OrderedSet([])
    b.add(2)
    b.add(3)
    sd = a.symmetric_difference(b)
    elems = list(sd)
    assert set(elems) == {1, 3}
    assert len(elems) == 2

def test_index_error():
    s = OrderedSet([])
    s.add(1)
    try:
        _ = s[10]
        assert False, "IndexError expected"
    except IndexError:
        pass
    try:
        _ = s["bad"]
        assert False, "TypeError expected"
    except TypeError:
        pass

if __name__ == "__main__":
    test_basic()
    test_remove()
    test_update()
    test_iter()
    test_pop()
    test_difference()
    test_intersection()
    test_symmetric_difference()
    test_index_error()
    print("All tests passed.")
