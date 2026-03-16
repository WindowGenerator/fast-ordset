#!/usr/bin/env bash
set -eou pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/build.sh"

uv run pytest benchmarks/test_performance.py --benchmark-only --benchmark-autosave