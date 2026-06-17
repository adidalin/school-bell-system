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
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_VBS=%STARTUP_FOLDER%\SchoolBell.vbs"

if not exist "%STARTUP_FOLDER%" mkdir "%STARTUP_FOLDER%" 2>nul

powershell -Command "$d='%SCRIPT_DIR:\=\\%'; $v='%STARTUP_VBS%'; $c='Set WshShell = CreateObject(\"WScript.Shell\")'+[char]13+[char]10+'WshShell.CurrentDirectory = \"'+$d+'\"'+[char]13+[char]10+'WshShell.Run \"pythonw.exe run.py\",0,False'; Set-Content -Path $v -Value $c -Encoding Default"

if errorlevel 1 (
    echo [FAIL] Cannot create startup file
    echo Please manually create a shortcut:
    echo   Target: pythonw.exe
    echo   Start in: %SCRIPT_DIR%
    echo   Save to: %STARTUP_FOLDER%
) else (
    echo [ OK ] Autostart configured
    echo Path: %STARTUP_VBS%
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
