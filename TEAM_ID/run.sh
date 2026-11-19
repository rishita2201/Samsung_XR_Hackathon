#!/usr/bin/env bash
# Official Samsung XR Hackathon Track 4 Execution Contract
# Usage: ./run.sh <video.mp4> <out.json>
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <video.mp4> <out.json>" >&2
    exit 2
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Discover Python 3 executable
PYTHON_CMD=""
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif [ -f "$DIR/../venv/bin/python" ]; then
    PYTHON_CMD="$DIR/../venv/bin/python"
else
    echo "ERROR: Python 3 executable not found in PATH." >&2
    exit 1
fi

exec "$PYTHON_CMD" "$DIR/code/run_pipeline.py" \
     --video "$1" \
     --out "$2" \
     --weights "$DIR/weights" \
     --classes "$DIR/weights/supported_classes.json"
