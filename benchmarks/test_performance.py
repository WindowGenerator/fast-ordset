"""
Performance tests comparing fast_ordset.OrderedSet with the ordered-set package.

Run with:
  pytest benchmarks/ --benchmark-only

For a fair comparison, use a release build of fast_ordset (faster than debug):
  maturin develop --release   # then run pytest as above

Optional:
  pytest benchmarks/ --benchmark-only -v
  pytest benchmarks/ --benchmark-only --benchmark-autosave
  pytest benchmarks/ --benchmark-only -k "construction or contains"
"""
import pytest

try:
    from fast_ordset import OrderedSet as FastOrderedSet
except ImportError:
    FastOrderedSet = None

try:
    from ordered_set import OrderedSet as RspeerOrderedSet
except ImportError:
    RspeerOrderedSet = None


def _impls():
    impls = []
    if FastOrderedSet is not None:
        impls.append(("fast_ordset", FastOrderedSet))
    if RspeerOrderedSet is not None:
        impls.append(("ordered_set", RspeerOrderedSet))
    return impls


_IMPLS = _impls()
if not _IMPLS:
    pytest.skip(
        "Need at least one of: fast_ordset, ordered-set. "
        "Install dev deps: pip install -e '.[dev]'",
        allow_module_level=True,
    )


@pytest.fixture(params=[name for name, _ in _IMPLS], ids=[name for name, _ in _IMPLS])
def impl(request):
    d = dict(_IMPLS)
    return request.param, d[request.param]


def _make_list(n):
    return list(range(n))


# --- Construction ---


@pytest.mark.benchmark(group="construction")
def test_bench_construction_empty(impl, benchmark):
    """Construct empty OrderedSet."""
    name, OrderedSetCls = impl
    benchmark(lambda: OrderedSetCls())


@pytest.mark.benchmark(group="construction")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_construction_from_list(impl, n, benchmark):
    """Construct OrderedSet from a list of n integers."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    benchmark(lambda: OrderedSetCls(data))


# --- add() ---


@pytest.mark.benchmark(group="add")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"add_{x}")
def test_bench_add_loop(impl, n, benchmark):
    """Add n items one by one to an empty set."""
    name, OrderedSetCls = impl

    def run():
        s = OrderedSetCls()
        for i in range(n):
            s.add(i)
        return s

    benchmark(run)


# --- Membership (in) ---


@pytest.mark.benchmark(group="contains")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_contains_present(impl, n, benchmark):
    """Membership test for item that is in the set."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    # middle element
    item = n // 2
    benchmark(lambda: item in s)


@pytest.mark.benchmark(group="contains")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_contains_absent(impl, n, benchmark):
    """Membership test for item not in the set."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    item = -1
    benchmark(lambda: item in s)


@pytest.mark.benchmark(group="contains")
@pytest.mark.parametrize("n", [1_000], ids=lambda x: f"n={x}")
def test_bench_contains_many_lookups(impl, n, benchmark):
    """Many membership checks (1000 lookups) on a set of size n."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    indices = [i % (n + 1) for i in range(1000)]  # mix of present and absent

    def run():
        for i in indices:
            _ = i in s

    benchmark(run)


# --- Iteration ---


@pytest.mark.benchmark(group="iteration")
@pytest.mark.parametrize("n", [50_000], ids=lambda x: f"n={x}")
def test_bench_iteration_to_list(impl, n, benchmark):
    """Iterate and collect into list."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    benchmark(lambda: list(s))


@pytest.mark.benchmark(group="to_list")
@pytest.mark.parametrize("n", [10_000, 50_000, 100_000], ids=lambda x: f"n={x}")
def test_bench_to_list(impl, n, benchmark):
    """Bulk to_list() (fast_ordset) vs list() (ordered_set). Best way to get a list per impl."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    if name == "fast_ordset":
        benchmark(lambda: s.to_list())
    else:
        benchmark(lambda: list(s))


# --- Index access __getitem__ ---


@pytest.mark.benchmark(group="getitem")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_getitem_middle(impl, n, benchmark):
    """Access element at middle index."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    idx = n // 2
    benchmark(lambda: s[idx])


@pytest.mark.benchmark(group="getitem")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_getitem_many(impl, n, benchmark):
    """Many index lookups (1000 accesses)."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    indices = [i % n for i in range(1000)]

    def run():
        for i in indices:
            _ = s[i]

    benchmark(run)


# --- remove ---


@pytest.mark.benchmark(group="remove")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_remove_one(impl, n, benchmark):
    """Remove one item from the set (middle)."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    item = n // 2

    def run():
        s = OrderedSetCls(data)
        s.remove(item)
        return s

    benchmark(run)


# --- pop ---


@pytest.mark.benchmark(group="pop")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_pop_end(impl, n, benchmark):
    """Pop one item from the end (default)."""
    name, OrderedSetCls = impl
    data = _make_list(n)

    def run():
        s = OrderedSetCls(data)
        s.pop()
        return s

    benchmark(run)


@pytest.mark.benchmark(group="pop")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_pop_middle(impl, n, benchmark):
    """Pop one item at middle index."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    idx = n // 2

    def run():
        s = OrderedSetCls(data)
        s.pop(idx)
        return s

    benchmark(run)


# --- Set operations ---


@pytest.mark.benchmark(group="union")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_union(impl, n, benchmark):
    """Union with another list (about same size, 50% overlap)."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    benchmark(lambda: a.union(other))


@pytest.mark.benchmark(group="update")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_update(impl, n, benchmark):
    """In-place update with another list (about same size, 50% overlap)."""
    name, OrderedSetCls = impl
    other = list(range(n // 2, n + n // 2))

    def run():
        s = OrderedSetCls(_make_list(n))
        s.update(other)
        return s

    benchmark(run)


@pytest.mark.benchmark(group="intersection")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_intersection(impl, n, benchmark):
    """Intersection with a list (about same size)."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    benchmark(lambda: a.intersection(other))


@pytest.mark.benchmark(group="intersection")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_intersection_update(impl, n, benchmark):
    """In-place intersection with a list (about same size)."""
    name, OrderedSetCls = impl
    other = list(range(n // 2, n + n // 2))

    def run():
        s = OrderedSetCls(_make_list(n))
        s.intersection_update(other)
        return s

    benchmark(run)


@pytest.mark.benchmark(group="difference")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_difference(impl, n, benchmark):
    """Difference with a list."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    benchmark(lambda: a.difference(other))


@pytest.mark.benchmark(group="difference")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_difference_update(impl, n, benchmark):
    """In-place difference with a list."""
    name, OrderedSetCls = impl
    other = list(range(n // 2, n + n // 2))

    def run():
        s = OrderedSetCls(_make_list(n))
        s.difference_update(other)
        return s

    benchmark(run)


@pytest.mark.benchmark(group="symmetric_difference")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_symmetric_difference(impl, n, benchmark):
    """Symmetric difference with a list (returns new set)."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    benchmark(lambda: a.symmetric_difference(other))


@pytest.mark.benchmark(group="symmetric_difference")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_symmetric_difference_update(impl, n, benchmark):
    """In-place symmetric difference with a list."""
    name, OrderedSetCls = impl
    other = list(range(n // 2, n + n // 2))

    def run():
        s = OrderedSetCls(_make_list(n))
        s.symmetric_difference_update(other)
        return s

    benchmark(run)


# --- copy ---


@pytest.mark.benchmark(group="copy")
@pytest.mark.parametrize("n", [10_000], ids=lambda x: f"n={x}")
def test_bench_copy(impl, n, benchmark):
    """Copy a set of n elements."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    benchmark(lambda: s.copy())
