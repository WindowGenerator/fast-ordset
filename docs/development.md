# Development

## Prerequisites

- **Rust** (e.g. [rustup](https://rustup.rs/))
- **Python 3.10–3.14** (see `pyproject.toml` `requires-python`)
- **uv** (recommended) or **pip** + **maturin** for building

## Setup

```bash
# Clone and enter project
cd fast-ordset

# Create venv and install project + dev deps (with uv)
uv sync --all-extras

# Or with pip
pip install -e '.[dev]'
pip install maturin
```

## Build

| Goal | Command |
|------|--------|
| Debug (fast compile, slow runtime) | `maturin develop` or `uv run maturin develop` |
| Release (slow compile, fast runtime) | `maturin develop --release` |
| Wheel only | `maturin build --release` → `target/wheels/*.whl` |

For free-threaded (no-GIL) Python, set env (or use `scripts/common_env.sh`):

```bash
export UNSAFE_PYO3_BUILD_FREE_THREADED=1
export UNSAFE_PYO3_SKIP_VERSION_CHECK=1
maturin develop --release
```

## Tests

- **Unit tests** (in `tests/`):
  ```bash
  pytest tests -v
  # or
  uv run pytest tests -v
  ```
- **Quick dev loop** (debug build + tests):
  ```bash
  ./scripts/debug.sh
  ```

See [scripts](scripts.md) for `debug.sh`, `benchmark_time.sh`, `benchmark_mem.sh`.

## Benchmarks

- **Time:** `./scripts/benchmark_time.sh` or `pytest benchmarks/test_performance.py --benchmark-only`
- **Memory:** `./scripts/benchmark_mem.sh` or `pytest benchmarks/test_memory.py -v -s`

Use a release build before benchmarking. Details: [benchmarks](benchmarks.md).

## Project layout

| Path | Purpose |
|------|--------|
| `src/` | Rust crate (PyO3 extension): `lib.rs`, `ordered_set.rs`, `hash.rs` |
| `pysrc/` | Optional Python package content (see `[tool.maturin]` in `pyproject.toml`) |
| `tests/` | Pytest unit tests |
| `benchmarks/` | Pytest-based time and memory benchmarks |
| `scripts/` | Bash helpers for build, test, benchmarks |
| `docs/` | Documentation (scripts, benchmarks, development) |

## Code quality

- **Rust:** `cargo fmt`, `cargo clippy` (and `cargo test` for Rust tests if any).
- **Python:** Pytest for tests; coverage via `pytest-cov` (see `pyproject.toml` and `[tool.coverage.*]`).

## Releasing

1. Bump version in `pyproject.toml` and `Cargo.toml` if needed.
2. `maturin build --release` (optionally for multiple targets).
3. Publish wheels/sdist to PyPI (e.g. `twine upload target/wheels/*.whl` or use CI).

## Docs

- [Scripts](scripts.md) — `scripts/*` usage and environment.
- [Benchmarks](benchmarks.md) — how to run and interpret time/memory benchmarks.
