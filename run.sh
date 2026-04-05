#!/usr/bin/env bash
set -e
 
ROOT="$(cd "$(dirname "$0")" && pwd)"
 
echo "[run.sh] Starting CanSat ground station..."

# Launch Dashboard
cd "$ROOT/InfoDisplay_Dashboard"
uv run main.py &
DASHBOARD_PID=$!
echo "[run.sh] Dashboard started (PID $DASHBOARD_PID) → http://localhost:4000"
 
# Launch Ground Receiver
cd "$ROOT"
uv run ground.py &
GROUND_PID=$!
echo "[run.sh] Ground receiver started (PID $GROUND_PID)"
 
# Shutdown Handler
cleanup() {
    echo ""
    echo "[run.sh] Shutting down..."
    kill $DASHBOARD_PID 2>/dev/null
    kill $GROUND_PID    2>/dev/null
    wait $DASHBOARD_PID 2>/dev/null
    wait $GROUND_PID    2>/dev/null
    echo "[run.sh] Done."
    exit 0
}
 
trap cleanup SIGINT SIGTERM

# Wait for processes to finish
wait $DASHBOARD_PID $GROUND_PID
