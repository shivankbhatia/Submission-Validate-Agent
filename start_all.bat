@echo off
REM Start both API and Frontend servers

echo ============================================================
echo   Starting Agentic Evaluator Application
echo ============================================================
echo.

REM Check if API is already running
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo Warning: Port 8000 is already in use!
    echo Please stop the existing process or use a different port.
    echo.
    pause
    exit /b 1
)

echo Step 1: Starting API Server on http://localhost:8000...
echo.
start "API Server" cmd /k "uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a bit for API to start
timeout /t 3 /nobreak > nul

echo Step 2: Starting Frontend on http://localhost:5173...
echo.
start "Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak > nul

echo.
echo ============================================================
echo   Application Started Successfully!
echo ============================================================
echo.
echo   API Server:  http://localhost:8000/docs
echo   Frontend:    http://localhost:5173
echo.
echo   Two new windows have been opened:
echo   - API Server (Backend)
echo   - Frontend (React App)
echo.
echo   Press Ctrl+C in each window to stop the servers.
echo ============================================================
echo.

pause
