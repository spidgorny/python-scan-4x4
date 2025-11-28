#!/bin/bash
# Start the web interface

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

echo "Starting A4 Scanner Web Interface..."
echo ""

uv run python app.py
