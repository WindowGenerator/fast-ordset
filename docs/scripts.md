# Scripts

Scripts in `scripts/` automate build, test, and benchmark workflows. They use a shared environment (see `common_env.sh`) and assume Bash.

## common_env.sh

**Purpose:** Shared environment for release benchmarks and debug builds. Source this from other scripts; do not run directly.

## debug.sh

**Purpose:** Build in dev profile, install the wheel, and run unit tests.

## benchmark_time.sh

**Purpose:** Run **time** (performance) benchmarks and optionally save results.

## benchmark_mem.sh

**Purpose:** Run **memory** benchmarks (peak process RSS).
