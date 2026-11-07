#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Starting NexusOps Demo Server ==="
if [ ! -d ".venv" ]; then
  uv venv
  uv pip install fastapi "uvicorn[standard]"
fi

# Pastikan jika port 8765 masih dipakai oleh sesi sebelumnya, proses lama dihentikan otomatis
EXISTING_PID=$(lsof -ti:8765 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
  echo "Menghentikan proses server sebelumnya di port 8765 (PID: $EXISTING_PID)..."
  kill -9 $EXISTING_PID 2>/dev/null || true
  sleep 0.5
fi

echo "Running on http://127.0.0.1:8765"
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8765 --reload
