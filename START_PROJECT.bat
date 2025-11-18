@echo off
echo ========================================
echo   GameVerse - Starting Project
echo ========================================
echo.

echo [1/2] Starting Backend (FastAPI)...
start cmd /k "cd /d %~dp0 && echo Starting FastAPI Backend... && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend (React)...
start cmd /k "cd /d %~dp0frontend && echo Starting React Frontend... && npm run dev"

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
pause >nul
