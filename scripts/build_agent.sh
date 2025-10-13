#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
AGENT_DIR="$ROOT_DIR/cgroup_agent"
BUILD_DIR="$ROOT_DIR/build"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake "$AGENT_DIR"
cmake --build . --config Release -j
echo "Built at $BUILD_DIR/safebox_cgroup"


