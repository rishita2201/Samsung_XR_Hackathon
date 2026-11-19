#!/usr/bin/env bash
set -e
echo "===================================================================="
echo " MOMENTIQ - Intelligent First-Person Video Understanding & Highlights"
echo " Samsung XR Hackathon 2026 - Track 4"
echo "===================================================================="
echo ""

DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_CMD="python"
if [ -f "$DIR/venv/bin/python" ]; then
    PYTHON_CMD="$DIR/venv/bin/python"
fi

echo "Starting MOMENTIQ unified server (API + Frontend) on port 8000..."
echo "Open your browser to: http://127.0.0.1:8000"
echo ""

cd "$DIR/backend"
"$PYTHON_CMD" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

