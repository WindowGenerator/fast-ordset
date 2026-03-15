#!/usr/bin/env bash
set -eou pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_env.sh"

uv run maturin develop --release
uv run pytest benchmarks/test_memory.py -v -s
