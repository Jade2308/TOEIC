#!/usr/bin/env bash
# ==============================================================================
# Autonomous TOEIC Crawler Pipeline Runner for Linux / Proxmox Ubuntu Server VM
# Outputs directly into ./data/exams and ./data/media (auto-discovered by web!)
# ==============================================================================
set -e

export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# Auto-detect Python virtual environment (Ubuntu VM venv first)
if [ -x "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/venv/bin/python"
elif [ -x "/opt/toeic/venv/bin/python" ]; then
    PYTHON_BIN="/opt/toeic/venv/bin/python"
elif [ -x "/opt/conda/envs/toeic-pipeline/bin/python" ]; then
    PYTHON_BIN="/opt/conda/envs/toeic-pipeline/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

TEST_DIR="$1"
if [ -z "$TEST_DIR" ]; then
    echo "Usage: ./crawler/run_crawler.sh <path_to_raw_test_dir> [extra_args...]"
    echo "Example: ./crawler/run_crawler.sh \"data/raw/TEST 5 - ETS 2023\" --device cpu"
    exit 1
fi

shift
EXTRA_ARGS="$@"

echo "=============================================================================="
echo " Starting Autonomous TOEIC Crawler Pipeline (100% Local Storage)"
echo " Test Dir: $TEST_DIR"
echo " Python  : $PYTHON_BIN"
echo "=============================================================================="

"$PYTHON_BIN" "$SCRIPT_DIR/main.py" --test-dir "$TEST_DIR" $EXTRA_ARGS
