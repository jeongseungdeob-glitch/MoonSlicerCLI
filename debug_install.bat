@echo on
title CIA Roblox Executor - Debug Installer
color 0C

echo.
echo ========================================
echo   CIA Roblox Executor v1.0
echo   DEBUG Installer
echo ========================================
echo.

echo [DEBUG] Starting debug installation...
echo [DEBUG] Current directory: %CD%
echo [DEBUG] Current user: %USERNAME%
echo [DEBUG] Current time: %TIME%
echo.

echo [DEBUG] Step 1: Checking administrator privileges...
net session >nul 2>&1
echo [DEBUG] net session exit code: %errorLevel%
if %errorLevel% == 0 (
    echo [DEBUG] Running as administrator
) else (
    echo [DEBUG] Not running as administrator
)

echo.
echo [DEBUG] Step 2: Checking Windows version...
ver
echo [DEBUG] ver command completed

echo.
echo [DEBUG] Step 3: Checking Python...
python --version
echo [DEBUG] python --version exit code: %errorLevel%

echo.
echo [DEBUG] Step 4: Checking if requirements.txt exists...
if exist requirements.txt (
    echo [DEBUG] requirements.txt found
    dir requirements.txt
) else (
    echo [DEBUG] requirements.txt NOT found
    echo [DEBUG] Current directory contents:
    dir
)

echo.
echo [DEBUG] Step 5: Testing pip...
pip --version
echo [DEBUG] pip --version exit code: %errorLevel%

echo.
echo [DEBUG] Step 6: Testing Ollama...
ollama --version
echo [DEBUG] ollama --version exit code: %errorLevel%

echo.
echo [DEBUG] Installation check complete.
echo [DEBUG] Press any key to continue with actual installation...
pause

echo.
echo [DEBUG] Starting actual installation...
echo.

:: Now try the actual installation
echo [DEBUG] Installing Python dependencies...
pip install -r requirements.txt
echo [DEBUG] pip install exit code: %errorLevel%

echo.
echo [DEBUG] Creating directories...
if not exist "logs" mkdir logs
if not exist "sandboxed_scripts" mkdir sandboxed_scripts
if not exist "backups" mkdir backups
if not exist "temp" mkdir temp

echo [DEBUG] Installation complete.
echo [DEBUG] Press any key to exit...
pause