@echo off
setlocal

cd /d "%~dp0"

for /f "usebackq delims=" %%v in (`type VERSION`) do set VERSION=%%v

echo Building api-explorer version %VERSION%...

pyinstaller --noconfirm ^
    --name api-explorer-%VERSION% ^
    --add-data "data;data" ^
    --add-data "static;static" ^
    --distpath=dist ^
    --workpath=build ^
    app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Build completed. Output is in dist\api-explorer-%VERSION%\
) else (
    echo.
    echo FAILURE: Build failed with error code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

endlocal