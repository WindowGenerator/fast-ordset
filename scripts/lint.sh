#!/usr/bin/env bash
set -eou pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_env.sh"

echo "=== Running Python linting with mypy ==="
uvx mypy pysrc/fast_ordset --strict

echo ""
echo "=== Running Rust linting with Clippy ==="
cargo clippy --lib --all-targets -- -D warnings

echo ""
echo "✓ All lints passed!"
