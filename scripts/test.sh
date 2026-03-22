#!/usr/bin/env bash
set -eou pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_env.sh"

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-target}"

# Ensure dependencies are synced
echo "=== Syncing dependencies ==="
uv sync --all-extras

# Build the project
echo ""
echo "=== Building project ==="
uv run maturin develop --release

# Run unit tests
echo ""
echo "=== Running tests with coverage ==="
    uv run pytest --cov=pysrc --cov-report=term-missing tests/

echo ""
echo "✓ All tests passed!"
