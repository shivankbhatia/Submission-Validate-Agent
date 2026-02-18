#!/bin/bash
# Start both API and Frontend servers

echo "============================================================"
echo "  Starting Agentic Evaluator Application"
echo "============================================================"
echo ""

# Check if API is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠ Warning: Port 8000 is already in use!"
    echo "Please stop the existing process or use a different port."
    echo ""
    exit 1
fi

echo "Step 1: Starting API Server on http://localhost:8000..."
echo ""

# Start API in background
gnome-terminal -- bash -c "uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload; exec bash" 2>/dev/null ||
xterm -e "uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload" 2>/dev/null ||
(uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload &)

# Wait a bit for API to start
sleep 3

echo "Step 2: Starting Frontend on http://localhost:5173..."
echo ""

# Start Frontend in background
gnome-terminal -- bash -c "cd frontend && npm run dev; exec bash" 2>/dev/null ||
xterm -e "cd frontend && npm run dev" 2>/dev/null ||
(cd frontend && npm run dev &)

sleep 3

echo ""
echo "============================================================"
echo "  Application Started Successfully!"
echo "============================================================"
echo ""
echo "  API Server:  http://localhost:8000/docs"
echo "  Frontend:    http://localhost:5173"
echo ""
echo "  Two new windows/processes have been started."
echo "  Use 'pkill -f uvicorn' to stop the API server."
echo "  Use 'pkill -f vite' to stop the frontend."
echo "============================================================"
echo ""
