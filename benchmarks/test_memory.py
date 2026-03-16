"""
Uses process RSS (resident set size) so that memory from both Python and native
(Rust) code is included. tracemalloc only tracks Python's allocator and would
miss almost all allocations from a Rust extension.
Requires psutil (pip install -e '.[dev]').
"""
import gc

import pytest

try:
    import psutil
except ImportError:
    psutil = None

if psutil is None:
    pytest.skip(
        "psutil required for memory benchmarks. Install with: pip install -e '.[dev]'",
        allow_module_level=True,
    )

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

# Collected memory results: list of (group, impl_name, n, peak_bytes)
MEMORY_RESULTS = []


@pytest.fixture(params=[name for name, _ in _IMPLS], ids=[name for name, _ in _IMPLS])
def impl(request):
    d = dict(_IMPLS)
    return request.param, d[request.param]


def _make_list(n):
    return list(range(n))


def _get_rss_bytes():
    """Current process resident set size in bytes (includes Python + native/Rust)."""
    return psutil.Process().memory_info().rss


def _measure_peak_mb(operation, rounds=3):
    """Run operation rounds times, return max RSS in MB (process memory, incl. native)."""
    peak_bytes = 0
    for _ in range(rounds):
        gc.collect()
        start_rss = _get_rss_bytes()
        operation()
        rss = _get_rss_bytes() - start_rss
        gc.collect()
        if rss > peak_bytes:
            peak_bytes = rss
    return peak_bytes / (1024 * 1024)


def _record(group, impl_name, n, peak_mb):
    MEMORY_RESULTS.append((group, impl_name, n, peak_mb))


# --- Construction ---


@pytest.mark.benchmark(group="memory_construction")
def test_memory_construction_empty(impl):
    """Peak memory: construct empty OrderedSet."""
    name, OrderedSetCls = impl
    peak_mb = _measure_peak_mb(lambda: OrderedSetCls())
    _record("construction_empty", name, 0, peak_mb)


@pytest.mark.benchmark(group="memory_construction")
@pytest.mark.parametrize("n", [1_000, 10_000, 50_000], ids=lambda x: f"n={x}")
def test_memory_construction_from_list(impl, n):
    """Peak memory: construct OrderedSet from list of n integers."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    peak_mb = _measure_peak_mb(lambda: OrderedSetCls(data))
    _record("construction_from_list", name, n, peak_mb)


# --- add() ---


@pytest.mark.benchmark(group="memory_add")
@pytest.mark.parametrize("n", [1_000, 10_000, 50_000], ids=lambda x: f"n={x}")
def test_memory_add_loop(impl, n):
    """Peak memory: add n items one by one to an empty set."""
    name, OrderedSetCls = impl

    def run():
        s = OrderedSetCls()
        for i in range(n):
            s.add(i)
        return s

    peak_mb = _measure_peak_mb(run)
    _record("add_loop", name, n, peak_mb)


# --- copy ---


@pytest.mark.benchmark(group="memory_copy")
@pytest.mark.parametrize("n", [1_000, 10_000, 50_000], ids=lambda x: f"n={x}")
def test_memory_copy(impl, n):
    """Peak memory: copy a set of n elements."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    peak_mb = _measure_peak_mb(lambda: s.copy())
    _record("copy", name, n, peak_mb)


# --- union ---


@pytest.mark.benchmark(group="memory_union")
@pytest.mark.parametrize("n", [1_000, 10_000], ids=lambda x: f"n={x}")
def test_memory_union(impl, n):
    """Peak memory: union with a list of ~n elements (50% overlap)."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    peak_mb = _measure_peak_mb(lambda: a.union(other))
    _record("union", name, n, peak_mb)


# --- difference ---


@pytest.mark.benchmark(group="memory_difference")
@pytest.mark.parametrize("n", [1_000, 10_000], ids=lambda x: f"n={x}")
def test_memory_difference(impl, n):
    """Peak memory: difference with a list."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    peak_mb = _measure_peak_mb(lambda: a.difference(other))
    _record("difference", name, n, peak_mb)


# --- intersection ---


@pytest.mark.benchmark(group="memory_intersection")
@pytest.mark.parametrize("n", [1_000, 10_000], ids=lambda x: f"n={x}")
def test_memory_intersection(impl, n):
    """Peak memory: intersection with a list."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    peak_mb = _measure_peak_mb(lambda: a.intersection(other))
    _record("intersection", name, n, peak_mb)


# --- symmetric_difference ---


@pytest.mark.benchmark(group="memory_symmetric_difference")
@pytest.mark.parametrize("n", [1_000, 10_000], ids=lambda x: f"n={x}")
def test_memory_symmetric_difference(impl, n):
    """Peak memory: symmetric_difference with a list."""
    name, OrderedSetCls = impl
    a = OrderedSetCls(_make_list(n))
    other = list(range(n // 2, n + n // 2))
    peak_mb = _measure_peak_mb(lambda: a.symmetric_difference(other))
    _record("symmetric_difference", name, n, peak_mb)


# --- iteration to list ---


@pytest.mark.benchmark(group="memory_iteration")
@pytest.mark.parametrize("n", [1_000, 10_000, 50_000], ids=lambda x: f"n={x}")
def test_memory_iteration_to_list(impl, n):
    """Peak memory: iterate and collect into list."""
    name, OrderedSetCls = impl
    data = _make_list(n)
    s = OrderedSetCls(data)
    peak_mb = _measure_peak_mb(lambda: list(s))
    _record("iteration_to_list", name, n, peak_mb)
