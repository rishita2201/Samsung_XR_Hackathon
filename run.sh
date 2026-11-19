#!/usr/bin/env bash
# Official Samsung Track 4 Run Script
# Usage: ./run.sh <video.mp4> <out.json>
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <video.mp4> <out.json>" >&2
    exit 2
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/TEAM_ID/run.sh" "$1" "$2"
