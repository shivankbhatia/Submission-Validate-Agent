#!/bin/bash
# Start the FastAPI backend server

echo "Starting API Server on http://localhost:8000..."
echo ""

uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
