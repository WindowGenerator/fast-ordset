#!/usr/bin/env bash

set -eou pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common_env.sh"

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-target}"

rm -f ${CARGO_TARGET_DIR}/wheels/*.whl

uv sync --all-extras
uv run maturin build --profile=dev

uv pip install ${CARGO_TARGET_DIR}/wheels/*.whl

uv run pytest -v tests
