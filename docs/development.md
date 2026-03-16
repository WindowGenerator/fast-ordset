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

```bash
./scripts/build.sh
```

## Tests

- **Unit tests** (in `tests/`):
  ```bash
  ./scripts/debug.sh
  ```

See [scripts](scripts.md).

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

**Add it**

## Releasing

**Add it**

## Docs

- [Scripts](scripts.md) — `scripts/*` usage and environment.
- [Benchmarks](benchmarks.md) — how to run and interpret time/memory benchmarks.
