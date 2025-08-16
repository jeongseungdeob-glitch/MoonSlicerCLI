@echo off
title Directory Checker
color 0B

echo.
echo ========================================
echo   CIA Roblox Executor - Directory Check
echo ========================================
echo.

echo [INFO] Current directory: %CD%
echo.

echo [INFO] Checking for required files...
echo.

if exist "gui.py" (
    echo [OK] gui.py found
) else (
    echo [MISSING] gui.py not found
)

if exist "main.py" (
    echo [OK] main.py found
) else (
    echo [MISSING] main.py not found
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [MISSING] requirements.txt not found
)

if exist "README.md" (
    echo [OK] README.md found
) else (
    echo [MISSING] README.md not found
)

echo.
echo [INFO] All files in current directory:
dir /b

echo.
echo ========================================
echo   Instructions
echo ========================================
echo.
echo If you see [MISSING] for requirements.txt:
echo 1. Make sure you're in the CIA Roblox Executor folder
echo 2. The folder should contain gui.py, main.py, requirements.txt
echo 3. Run install.bat from this directory
echo.
echo If you're not in the right directory:
echo 1. Navigate to the CIA Roblox Executor folder
echo 2. Run this check again
echo.
echo Press any key to exit...
pause >nul