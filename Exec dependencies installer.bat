@echo off
title CIA Roblox Executor - Dependencies Installer
color 0A

echo.
echo ========================================
echo   CIA Roblox Executor v1.0
echo   Automated Dependencies Installer
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator. Some installations may fail.
    echo Please run this script as administrator for best results.
    pause
)

echo.
echo [STEP 1/6] Checking system requirements...
echo.

:: Check Windows version
ver | findstr /i "10\.0\|11\.0" >nul
if %errorLevel% == 0 (
    echo [✓] Windows 10/11 detected
) else (
    echo [✗] Windows 10/11 required
    echo Please upgrade to Windows 10 or 11
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Python is already installed
    python --version
) else (
    echo [✗] Python not found. Installing Python 3.11...
    
    :: Download Python installer
    echo Downloading Python 3.11...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python_installer.exe'}"
    
    if exist python_installer.exe (
        echo Installing Python...
        python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        del python_installer.exe
        
        :: Refresh environment variables
        call refreshenv.cmd 2>nul || (
            echo Refreshing environment variables...
            set PATH=%PATH%;C:\Python311;C:\Python311\Scripts
        )
        
        echo [✓] Python installed successfully
    ) else (
        echo [✗] Failed to download Python
        echo Please install Python 3.11+ manually from https://python.org
        pause
        exit /b 1
    )
)

echo.
echo [STEP 2/6] Installing Python dependencies...
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install Python packages
echo Installing Python packages...
pip install -r requirements.txt

if %errorLevel% == 0 (
    echo [✓] Python dependencies installed successfully
) else (
    echo [✗] Failed to install Python dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo [STEP 3/6] Installing Ollama...
echo.

:: Check if Ollama is already installed
ollama --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Ollama is already installed
    ollama --version
) else (
    echo [✗] Ollama not found. Installing Ollama...
    
    :: Download Ollama installer
    echo Downloading Ollama...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.msi' -OutFile 'ollama_installer.msi'}"
    
    if exist ollama_installer.msi (
        echo Installing Ollama...
        msiexec /i ollama_installer.msi /quiet
        del ollama_installer.msi
        
        :: Wait for installation
        timeout /t 10 /nobreak >nul
        
        echo [✓] Ollama installed successfully
    ) else (
        echo [✗] Failed to download Ollama
        echo Please install Ollama manually from https://ollama.ai
        pause
        exit /b 1
    )
)

echo.
echo [STEP 4/6] Starting Ollama service...
echo.

:: Start Ollama service
echo Starting Ollama service...
start /B ollama serve

:: Wait for service to start
echo Waiting for Ollama service to start...
timeout /t 15 /nobreak >nul

:: Test Ollama connection
echo Testing Ollama connection...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Ollama service is running
) else (
    echo [✗] Ollama service failed to start
    echo Please start Ollama manually: ollama serve
)

echo.
echo [STEP 5/6] Downloading AI models...
echo.

:: Create models directory
if not exist "models" mkdir models

:: Download AI models
echo Downloading Mistral model...
ollama pull mistral:7b-instruct-q4_0

echo Downloading DeepSeek model...
ollama pull deepseek-coder:6.7b-instruct-q4_0

echo Downloading StarCoder2 model...
ollama pull starcoder2:7b-q4_0

echo [✓] AI models downloaded successfully

echo.
echo [STEP 6/6] Creating project structure...
echo.

:: Create necessary directories
if not exist "logs" mkdir logs
if not exist "sandboxed_scripts" mkdir sandboxed_scripts
if not exist "backups" mkdir backups
if not exist "temp" mkdir temp

:: Create initial configuration
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
)

echo [✓] Project structure created

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo [✓] Python 3.11+ installed
echo [✓] Python dependencies installed
echo [✓] Ollama installed and running
echo [✓] AI models downloaded
echo [✓] Project structure created
echo.
echo Next steps:
echo 1. Run: python gui.py (for GUI mode)
echo 2. Run: python main.py --help (for CLI mode)
echo.
echo For support, check the README.md file
echo.
pause