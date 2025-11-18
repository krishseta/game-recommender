@echo off
echo ========================================
echo   GameVerse - Installation Script
echo ========================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed successfully!
echo.

echo [2/3] Installing Node.js dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..
echo Node.js dependencies installed successfully!
echo.

echo [3/3] Running ETL Pipeline...
python etl.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to run ETL pipeline
    pause
    exit /b 1
)
echo.

echo [4/4] Training Semantic Search Engine...
python semantic_search.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to train search engine
    pause
    exit /b 1
)
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run START_PROJECT.bat to start both servers
echo 2. Open http://localhost:3000 in your browser
echo.
echo Or manually:
echo   Backend:  uvicorn main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
echo.
pause
