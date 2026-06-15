@echo off
title School Bell - Setup

echo ==========================================
echo   School Bell System - Autostart Setup
echo ==========================================
echo.
echo This will setup auto-start on Windows login.
echo System will auto-recover after power outage.
echo.

set "SCRIPT_DIR=%~dp0"
set "VBS_FILE=%SCRIPT_DIR%start_hidden.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

if not exist "%STARTUP_FOLDER%" mkdir "%STARTUP_FOLDER%" 2>nul

copy /Y "%VBS_FILE%" "%STARTUP_FOLDER%\SchoolBell.vbs" >nul 2>&1

if errorlevel 1 (
    echo [FAIL] Cannot copy to startup folder
    echo Please manually copy start_hidden.vbs to:
    echo %STARTUP_FOLDER%
    echo and rename to "SchoolBell.vbs"
) else (
    echo [ OK ] Autostart configured
    echo Path: %STARTUP_FOLDER%\SchoolBell.vbs
    echo.
    echo System will auto-run after next Windows login.
)

echo.
echo ==========================================
echo   NTP Time Sync Setup
echo ==========================================
echo.

w32tm /config /manualpeerlist:ntp.aliyun.com /syncfromflags:manual /reliable:yes /update >nul 2>&1
if errorlevel 1 (
    echo [INFO] NTP config needs Administrator
    echo Please right-click this BAT - Run as Administrator
    echo Calendar bell still works without it, but clock may drift.
) else (
    net stop w32time >nul 2>&1
    net start w32time >nul 2>&1
    w32tm /resync >nul 2>&1
    echo [ OK ] NTP time service configured
    echo System will auto-sync with ntp.aliyun.com
    echo Precision: ~0.01 seconds
)

echo.
pause
