# fast-ordset

Ordered set for Python implemented in Rust (PyO3 + indexmap).

## Features

Same with the original set + pop(index: int) and remove(item)

`other` in set operations can be an `OrderedSet` or any iterable.

## Build and install

```bash
uv sync --all-extras
uv run maturin develop --release
```

## Usage

```python
from fast_ordset import OrderedSet

s = OrderedSet()
s.add(1)
s.add(2)
s.add(1)
assert len(s) == 2
assert 1 in s
assert s[0] == 1
assert s[-1] == 2
assert list(s) == [1, 2]

s.update([3, 2, 4])
s.remove(2)
x = s.pop()  # 4 (last inserted)
```

## Free-threaded Python (no-GIL)

The extension is built to be **thread-safe** and declares that it does not rely on the GIL (`gil_used = false`). You can use it with a free-threaded (no-GIL) Python build so that the interpreter does not re-enable the GIL when this module is imported.

- Use a **free-threaded** interpreter (e.g. the `t` variant of Python 3.13+, or start with `PYTHON_GIL=0`).
- Build the extension for that interpreter (e.g. `maturin build --release` with the correct Python).
- The same `OrderedSet` instance can then be used safely from multiple threads (e.g. via `threading` or `concurrent.futures`).

With a normal (GIL) build of Python, the extension still works as before; the GIL continues to serialize Python code, and the internal `Mutex` only matters if you release the GIL from Rust or use a free-threaded interpreter.

## Tests

```bash
./scripts/debug.sh
```

## Documentation

- [Scripts](docs/scripts.md) — build, test, and benchmark scripts
- [Benchmarks](docs/benchmarks.md) — performance and memory benchmarks
- [Development](docs/development.md) — setup, build, and contribution
