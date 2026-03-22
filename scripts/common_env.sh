#!/usr/bin/env bash
# Common build/env flags for release benchmarks. Source from benchmark_*.sh:
#   set -eou pipefail
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/common_env.sh"

export UNSAFE_PYO3_BUILD_FREE_THREADED=1
export UNSAFE_PYO3_SKIP_VERSION_CHECK=1
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Apply clang/lld optimizations only on Linux (skip Windows MSVC and macOS ld64)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    export CC="${CC:-clang}"
    export LD="${LD:-lld}"
    
    export CFLAGS="-Os -fstrict-aliasing"
    export RUSTFLAGS="-C linker=${CC} -C link-arg=-fuse-ld=${LD}"
fi
