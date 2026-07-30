@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ========================================
echo  API Explorer - Dependency Installer
echo ========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0

echo [1] Checking Python on PATH...
python --version
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Python is available
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Python not found on PATH
    set /a FAIL_COUNT+=1
)

echo.
echo [2] Checking pip availability...
pip --version
if %ERRORLEVEL% EQU 0 (
    echo   [OK] pip is available
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] pip not found on PATH
    set /a FAIL_COUNT+=1
)

echo.
echo [3] Installing requirements from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Requirements installed successfully
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] Failed to install requirements
    set /a FAIL_COUNT+=1
)

echo.
echo [4] Checking PyInstaller...
pyinstaller --version
if %ERRORLEVEL% EQU 0 (
    echo   [OK] PyInstaller is installed
    set /a PASS_COUNT+=1
) else (
    echo   PyInstaller not found. Installing...
    pip install pyinstaller
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] PyInstaller installed successfully
        set /a PASS_COUNT+=1
    ) else (
        echo   [FAIL] Failed to install PyInstaller
        set /a FAIL_COUNT+=1
    )
)

echo.
echo ========================================
echo  Summary: !PASS_COUNT! passed, !FAIL_COUNT! failed
echo ========================================

if !FAIL_COUNT! GTR 0 (
    echo WARNING: Some checks failed. Review output above.
) else (
    echo All dependencies are ready.
)

endlocal