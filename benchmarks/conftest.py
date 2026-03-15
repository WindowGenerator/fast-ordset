"""Pytest configuration for benchmarks."""


def _get_memory_results():
    """Get MEMORY_RESULTS from test_memory module after tests have run."""
    import sys
    for modname, mod in list(sys.modules.items()):
        if "test_memory" in modname and mod is not None and hasattr(mod, "MEMORY_RESULTS"):
            return getattr(mod, "MEMORY_RESULTS", [])
    return []


def pytest_sessionfinish(session, exitstatus):
    """Print memory benchmark summary after test_memory runs."""
    MEMORY_RESULTS = _get_memory_results()
    if not MEMORY_RESULTS:
        return
    # Group by (group, n), then show each impl's peak MB
    from collections import defaultdict
    table = defaultdict(dict)  # (group, n) -> { impl_name: peak_mb }
    for group, impl_name, n, peak_mb in MEMORY_RESULTS:
        key = (group, n)
        table[key][impl_name] = peak_mb
    groups = sorted(set(g for g, _ in table))
    print("\n" + "=" * 72)
    print("Memory (space) benchmark summary – peak process RSS (MB)")
    print("=" * 72)
    for group in groups:
        rows = [(n, data) for (g, n), data in sorted(table.items()) if g == group]
        if not rows:
            continue
        print(f"\n  {group}")
        print("  " + "-" * 60)
        for n, data in rows:
            n_str = str(n) if n else "0"
            parts = [f"{impl}: {peak_mb:.4f} MB" for impl, peak_mb in sorted(data.items())]
            print(f"    n={n_str:>6}  " + "  |  ".join(parts))
    print("\n" + "=" * 72)
