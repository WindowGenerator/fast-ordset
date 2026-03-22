# AGENTS.md

AI agent guide for the `fast-ordset` project. This document describes the project architecture, key components, and how to make effective contributions.

## Project Overview

**fast-ordset** is a high-performance ordered set implementation for Python built with Rust (PyO3) and backed by the [indexmap](https://docs.rs/indexmap/) crate. It provides Python's standard set operations while maintaining insertion order and supporting direct index access.

### Key Characteristics

- **Language**: Rust + Python bindings via PyO3
- **Core Data Structure**: `indexmap::IndexSet<PyHashable>`
- **Concurrency**: Thread-safe using `Mutex` (no GIL dependency)
- **GIL Model**: Free-threaded (declares `gil_used = false`)
- **Min Python**: 3.9, Max Python: 3.14
- **Version**: 0.4.0 (MIT licensed)

### Main Features

- All standard set operations: union, intersection, difference, symmetric_difference
- Index-based access: `s[0]`, `s[-1]`, iteration in insertion order
- Mutators: `add()`, `remove()`, `pop(index)`, `update()`, `clear()`
- Set operations work with any iterable (not just OrderedSet)
- Performance optimizations for large sets (2-10× faster than `ordered-set` on key operations)

---

## Architecture Overview

### Project Structure

```
src/                    # Rust implementation
├── lib.rs             # Module entry point, PyO3 module definition
├── ordered_set.rs     # Core OrderedSet class (374 lines)
├── hash.rs            # PyHashable wrapper and hashing strategy
pysrc/
└── fast_ordset/       # Python package metadata
    ├── __init__.py
    └── __init__.pyi   # Type stubs for IDE support
tests/                 # 12 pytest test modules covering all operations
benchmarks/            # Performance and memory benchmarks
docs/                  # development.md, benchmarks.md, scripts.md
scripts/               # Bash build/test helpers
```

### High-Level Data Flow

```
Python API (OrderedSet class)
         ↓
PyO3 Binding Layer (pymethods)
         ↓
OrderedSet struct - Mutex<IndexSet<PyHashable>>
         ↓
PyHashable (cached hash + Py<PyAny>)
         ↓
indexmap::IndexSet (core ordered HashMap)
```

---

## Core Components

### 1. `src/lib.rs`

**Responsibility**: Module initialization and export

```rust
#[pymodule(gil_used = false)]
fn fast_ordset(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OrderedSet>()?;
    m.add_class::<OrderedSetIterator>()?;
    Ok(())
}
```

- Exports `OrderedSet` and `OrderedSetIterator` classes
- Declares `gil_used = false` for free-threaded Python compatibility
- No public Rust API; only Python-facing types are exported

### 2. `src/ordered_set.rs` (Core Implementation - 374 lines)

**Responsibility**: Main `OrderedSet` class with all Python dunder methods and set operations

Key elements:

- **Data Container**: `Mutex<IndexSet<PyHashable>>` 
  - `Mutex` instead of `RefCell` because GIL is not guaranteed
  - `IndexSet` maintains insertion order + fast lookup
  
- **`lock_inner()` Helper**: Safely acquires mutex lock with poison recovery
  - If a previous lock holder panicked, recovers from poison without propagating panic
  - Trades consistency for crash-safety in multi-threaded contexts

- **Core Methods**:
  - `__init__`: Initialize from optional sequence
  - `__contains__`: Fast O(1) membership test via hash lookup
  - `__getitem__`: Index access (includes negative indices)
  - `__iter__`: Returns `OrderedSetIterator` 
  - `add()`, `remove()`, `pop()`, `clear()`: Mutators
  - `copy()`: Shallow clone via cloning inner IndexSet
  - Set operations: `union()`, `intersection()`, `difference()`, `symmetric_difference()` + in-place variants

- **Critical Detail**: `__iter__` holds an unsafe reference to self
  ```rust
  OrderedSetIterator {
      set: unsafe { Py::from_borrowed_ptr(py, slf.as_ptr()) },
      index: 0,
  }
  ```
  Guarantees set stays alive during iteration.

### 3. `src/hash.rs` (Hash Strategy - 90 lines)

**Responsibility**: Efficient Python object hashing for IndexSet

Two types:

- **`PyHashable`**: Owned variant (holds `Py<PyAny>` + cached hash)
  - Used as keys in IndexSet
  - `Clone` and `PartialEq` require GIL acquisition (touches `PyAny`)
  
- **`PyHashableRef<'a>`**: Borrowed variant for lookups
  - Used in `__contains__`, `remove()`, etc.
  - Zero-copy; no GIL needed during lookup
  - Implements `Hash` by hashing the cached `isize` hash value

**Key Optimization**:
```rust
// Direct hash lookup without cloning
pub fn lookup<'a>(hash_val: isize, obj: &'a Bound<'a, PyAny>) -> PyHashableRef<'a> {
    PyHashableRef { hash_val, obj }
}
```

Allows set operations to avoid cloning Python objects when just checking membership.

### 4. `OrderedSetIterator` Class

**Responsibility**: Python iterator protocol

```rust
#[pyclass]
pub struct OrderedSetIterator {
    set: Py<OrderedSet>,      // Owns reference, keeps set alive
    index: usize,              // Current position
}
```

- Holds `Py<OrderedSet>` to prevent set from being garbage collected during iteration
- Implements `__iter__` (returns self) and `__next__` (increment and yield)

---

## Build & Test Workflow

### Build

```bash
./scripts/build.sh
# or directly:
uv sync --all-extras
uv run maturin develop --release
```

- Uses **maturin** to compile Rust → Python extension (.so/.pyd)
- Python source from `pysrc/` is bundled
- `--release` flag essential for performance testing

### Testing

**Unit tests** (12 modules in `tests/`):
```bash
./scripts/debug.sh
# or:
pytest tests/
```

Test coverage areas:
- Construction and containment
- Copy semantics
- All set operations (union, intersection, difference, symmetric_difference)
- Item access and iteration
- Mutators (add, remove, pop)
- Representation and equality
- Edge cases and error handling

**Benchmarks**:
```bash
./scripts/benchmark_time.sh   # Timing benchmarks
./scripts/benchmark_mem.sh    # Memory consumption
pytest benchmarks/ --benchmark-only
```

Compares against `ordered-set` (pure Python reference impl).

---

## Performance Characteristics

### Strengths (vs ordered-set)

| Operation | Speedup | Notes |
|-----------|---------|-------|
| Construction (n=10k) | **2.7×** | IndexSet overhead minimal |
| `__getitem__` (1k accesses) | **10×** | Direct array access vs iteration |
| `pop()` / `remove()` | **2.5-3.5×** | shift_remove optimized |
| `copy()` | **9.5×** | Clone vs rebuild |
| `union()` / `update()` | **2×** | Rust set ops |
| `symmetric_difference()` | **3.8×** | Built-in XOR logic |

### Weaknesses

| Operation | Slowdown | Notes |
|-----------|----------|-------|
| `__iter__` → list | **7.8× slower** | Must call Python repr/clone per element |
| Tight contains loops (1k) | **1.26× slower** | GIL overhead in lookups |

**Bottom Line**: Rust version excels at mutations and index access; Python version still better for pure iteration. Trade-off: threading support vs iteration speed.

---

## Threading & GIL

### Design Principles

1. **No GIL Required**: Declared `gil_used = false` in module definition
2. **Thread-Safe**: Uses `Mutex<T>` instead of `RefCell<T>`
3. **Poison Recovery**: If a thread panics while holding lock, next lock holder recovers gracefully

### Practical Implications

- Safe to use in free-threaded Python (3.13+ with `PYTHON_GIL=0`)
- Concurrent operations on different OrderedSet instances are truly parallel
- Operations on same set are serialized by mutex (expected for set semantics)

```rust
fn lock_inner(set: &OrderedSet) -> MutexGuard<'_, IndexSet<PyHashable>> {
    set.inner.lock().unwrap_or_else(|e| e.into_inner())  // Poison recovery
}
```

---

## Key Implementation Decisions

### 1. Hash Caching

Hashes are computed once in Python (`item.hash()?`) and stored in `PyHashable`. This is critical because:
- Python hash values are stable within a process
- Avoids repeated GIL-requiring calls during set ops
- IndexSet hashing uses the cached `isize`

### 2. Mutex over RefCell

**Why not RefCell?**
- RefCell requires single-threaded access (panics on violation)
- OrderedSet must work in true multi-threaded contexts
- Mutex allows parallel access from different threads

**Cost**: Extra synchronization overhead even in single-threaded cases.

### 3. IndexSet vs HashMap + Vec

IndexSet is a hybrid data structure:
- Maintains insertion order (like Vec)
- Provides O(1) lookup (like HashMap)
- Better cache locality than separate Vec + HashMap
- Built for exactly this use case

### 4. shift_remove vs swap_remove

Used `shift_remove()` (maintains order, O(n)) over `swap_remove()` (O(1), loses order).
Trade-off: Order preservation is part of the API contract.

---

## Adding Features: Quick Checklist

When adding a new method or operation:

1. **Implement in Rust** (`src/ordered_set.rs`)
   - Use `#[pymethods]` for Python-facing methods
   - Use `lock_inner(self)` for mutex access
   - Handle Python exceptions properly

2. **Update Type Stubs** (`pysrc/fast_ordset/__init__.pyi`)
   - Add method signature for IDE autocomplete

3. **Write Tests** (`tests/test_*.py`)
   - Follow existing patterns
   - Test edge cases (empty set, single element, large sets)
   - Test with various Python types (int, str, tuple, etc.)

4. **Benchmark** (if performance-sensitive)
   - Add to `benchmarks/test_performance.py`
   - Compare vs `ordered-set`
   - Profile with release build

5. **Update Docs** (`docs/`)
   - Add to benchmarks.md if performance-relevant
   - Update development.md if architectural change

---

## Known Limitations & TODOs

### From docs/development.md

```
## Code quality
**Add it**

## Releasing
**Add it**
```

These sections need implementation:
- Static analysis / linting setup (clippy for Rust, pylint/mypy for Python)
- Release checklist, versioning strategy, PyPI publishing workflow

### Performance Bottlenecks

1. **Iteration + Python calls**: Each element needs `repr()`, `clone()` to move to Python
   - Mitigation: Use indexing or batch operations when performance-critical
   
2. **Mutex contention**: Single lock for entire set
   - Implication: Won't scale super-linearly in multi-threaded scenarios
   
3. **Hash conflicts**: Birthday problem with Python hash collisions
   - Standard IndexSet handling, not a bug, but causes rehashing

---

## Common Patterns in Codebase

### Pattern 1: Acquire Lock + Operate

```rust
let inner = lock_inner(self);
inner.contains(&lookup)
```

Most operations follow this: acquire once, use immutably.

### Pattern 2: Lookup Key Without Cloning

```rust
let hash_val = item.hash()?;
let lookup = PyHashable::lookup(hash_val, item);
lock_inner(self).contains(&lookup)  // No clone
```

Used when checking membership but not inserting.

### Pattern 3: Clone Owned + Create New Py Reference

```rust
let elem = inner
    .get_index(idx)
    .map(|k| k.obj.clone_ref(py))
    .ok_or_else(|| PyIndexError::new_err("..."))?;
Ok(elem.bind(py).clone())
```

For returning items to Python layer.

### Pattern 4: Error Handling with PyResult

```rust
fn remove(&self, item: &Bound<'_, PyAny>) -> PyResult<()> {
    let hash_val = item.hash()?;  // ? propagates PyErr
    let lookup = PyHashable::lookup(hash_val, item);
    let removed = lock_inner(self).shift_remove(&lookup);
    if removed {
        Ok(())
    } else {
        Err(PyKeyError::new_err(...))
    }
}
```

All Rust methods return `PyResult<T>` to propagate Python exceptions.

---

## Debugging Tips for Agents

### Rust Compilation Errors

```bash
cargo build --lib 2>&1 | head -20
# or for detailed error context:
./scripts/build.sh
```

### Test Failures

```bash
# Run specific test module
pytest tests/test_ordered_set.py -v

# Run with Python debugger (slower)
pytest tests/test_ordered_set.py --pdb
```

### Memory Issues

- Check `nsys profile` output from `./scripts/benchmark_mem.sh`
- Look for unwanted clones in tight loops (review `PyHashable::clone` calls)

### Multi-threading Bugs

- Use Python with free-threaded build: `python3.13t`
- Test with `threading.Thread` / `multiprocessing`
- Check for unexpected exceptions from poison recovery

---

## File Dependencies Graph

```
lib.rs
  ├─ ordered_set.rs (defines OrderedSet, OrderedSetIterator)
  └─ hash.rs (defines PyHashable, PyHashableRef)

ordered_set.rs
  └─ hash.rs (uses PyHashable)

pyproject.toml
  └─ src/lib.rs (compiles to fast_ordset module)

pysrc/fast_ordset/__init__.pyi
  └─ (types OrderedSet, OrderedSetIterator from Rust)

tests/test_*.py
  └─ (imports OrderedSet from fast_ordset)

benchmarks/test_*.py
  └─ (imports OrderedSet, compares with ordered_set)
```

---

## How AI Agents Can Contribute

### Low Complexity

1. **Add code quality sections** to `docs/development.md`
   - Define clippy + rustfmt rules
   - Add Python linting (mypy, ruff)
   - Setup CI/CD if not exists

2. **Add release process** to `docs/development.md`
   - Version bumping strategy
   - Changelog format
   - PyPI upload steps

3. **Expand benchmarks** with additional operations or data sizes
   - Add `n=100k, 1M` scale tests
   - Benchmark on different CPU types
   - Profile memory allocation patterns

### Medium Complexity

1. **Optimize iteration** (current 7.8× slowdown vs ordered-set)
   - Profile Python object creation in `__iter__` path
   - Consider batch retrieval API
   - Possible: implement `__getitem__` slice support

2. **Add `isdisjoint()` method** (standard set operation)
   - Write Rust implementation using IndexSet iterator
   - Add tests and benchmarks
   - Update type stubs

3. **Stats/introspection API**
   - `OrderedSet.capacity()` to expose internal storage size
   - `OrderedSet.hash_stats()` to diagnose collision rates
   - Useful for optimization and education

### High Complexity

1. **Custom hash function support**
   - Allow users to provide Python hash wrapper
   - Trade-off: loss of GIL-free guarantee
   - Requires redesign of PyHashable storage

2. **Persistent/snapshot API**
   - Serialize to bytes (pickle-compatible)
   - Would need custom PyO3 serialization
   - Benchmark memory format efficiency

3. **Parallel set operations** (for large sets in free-threaded Python)
   - Use rayon for parallel union/intersection
   - Careful: must preserve order deterministically
   - Benchmark to verify benefit

---

## Resources

- [PyO3 Guide](https://pyo3.rs/) - Python bindings framework
- [indexmap docs](https://docs.rs/indexmap/) - Rust implementation details
- Python Set API: [docs.python.org/3/library/stdtypes.html#set-types](https://docs.python.org/3/library/stdtypes.html#set-types)
- [Maturin Docs](https://www.maturin.rs/) - Build system for extension
- Project Benchmarks: `docs/benchmarks.md` (detailed timing breakdown)

---

## Questions or Issues?

Check these in order:
1. **Build fails**: `./scripts/build.sh` with full output
2. **Test fails**: Run failing test with `-vvs` flag
3. **Unclear semantics**: Check `tests/test_ordered_set.py` for examples
4. **Performance question**: See `docs/benchmarks.md` for baseline comparisons
