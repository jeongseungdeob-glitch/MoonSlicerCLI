@echo off
title CIA Roblox Executor - Simple Installer
color 0A

echo.
echo ========================================
echo   CIA Roblox Executor v1.0
echo   Simple Dependencies Installer
echo ========================================
echo.

echo [INFO] Starting installation...
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator
    echo Some installations may fail. Consider running as administrator.
    echo.
)

echo.
echo [STEP 1/5] Checking Windows version...
echo.

:: Simple Windows version check
ver >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Windows version check passed
) else (
    echo [ERROR] Windows version check failed
    pause
    exit /b 1
)

echo.
echo [STEP 2/5] Checking Python installation...
echo.

:: Check Python
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [WARNING] Python not found
    echo Please install Python 3.11+ from https://python.org
    echo Then run this installer again.
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 3/5] Installing Python dependencies...
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing Python packages...
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo [OK] Python dependencies installed
    ) else (
        echo [ERROR] Failed to install Python dependencies
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
) else (
    echo [ERROR] requirements.txt not found
    echo Please ensure you're running this from the correct directory.
    pause
    exit /b 1
)

echo.
echo [STEP 4/5] Checking Ollama...
echo.

:: Check Ollama
ollama --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ollama is installed
    ollama --version
) else (
    echo [WARNING] Ollama not found
    echo Please install Ollama from https://ollama.ai
    echo Then run this installer again.
    echo.
    pause
    exit /b 1
)

echo.
echo [STEP 5/5] Creating project structure...
echo.

:: Create directories
if not exist "logs" mkdir logs
if not exist "sandboxed_scripts" mkdir sandboxed_scripts
if not exist "backups" mkdir backups
if not exist "temp" mkdir temp

echo [OK] Project directories created

:: Create default config if it doesn't exist
if not exist "config.yaml" (
    echo Creating default configuration...
    echo # CIA Roblox Executor Configuration > config.yaml
    echo # Generated automatically by installer >> config.yaml
    echo. >> config.yaml
    echo executor: >> config.yaml
    echo   name: CIA Roblox Executor >> config.yaml
    echo   version: 1.0.0 >> config.yaml
    echo   max_execution_time: 30 >> config.yaml
    echo   enable_sandbox: true >> config.yaml
    echo   enable_bypass: true >> config.yaml
    echo [OK] Default configuration created
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo [OK] Python dependencies installed
echo [OK] Project structure created
echo [OK] Configuration file created
echo.
echo Next steps:
echo 1. Start Ollama: ollama serve
echo 2. Download AI models: ollama pull mistral:7b-instruct-q4_0
echo 3. Run the application: python gui.py
echo.
echo For help, check README.md
echo.
echo Press any key to exit...
pause >nul