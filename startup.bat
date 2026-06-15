@echo off
chcp 65001 >nul
title 校园广播系统 - 开机自启设置

echo ==========================================
echo   校园广播系统 - 开机自启动配置
echo ==========================================
echo.
echo 此脚本将设置系统在 Windows 登录后自动启动。
echo 即使断电重启，系统也会在登录后自动运行。
echo.

set "SCRIPT_DIR=%~dp0"
set "VBS_FILE=%SCRIPT_DIR%start_hidden.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

if not exist "%STARTUP_FOLDER%" mkdir "%STARTUP_FOLDER%" 2>nul

copy /Y "%VBS_FILE%" "%STARTUP_FOLDER%\校园广播系统.vbs" >nul 2>&1

if errorlevel 1 (
    echo [失败] 无法复制到启动文件夹
    echo 请手动将 start_hidden.vbs 复制到:
    echo %STARTUP_FOLDER%
    echo 并重命名为 "校园广播系统.vbs"
) else (
    echo [成功] 已配置开机自启动
    echo 位置: %STARTUP_FOLDER%\校园广播系统.vbs
    echo.
    echo 下次 Windows 登录后系统将自动运行。
)

echo.
echo ==========================================
echo   配置 NTP 时间自动同步
echo ==========================================
echo.

w32tm /config /manualpeerlist:ntp.aliyun.com /syncfromflags:manual /reliable:yes /update >nul 2>&1
if errorlevel 1 (
    echo [提示] NTP时间服务配置需要管理员权限
    echo 请右键此脚本 -- 以管理员身份运行，以启用高精度时间同步
    echo （不影响打铃功能，但系统时间偏差会累积）
) else (
    net stop w32time >nul 2>&1
    net start w32time >nul 2>&1
    w32tm /resync >nul 2>&1
    echo [成功] NTP时间服务已配置
    echo 系统将自动与 ntp.aliyun.com 同步时间
    echo 精度可达 0.01 秒以内
)

echo.
pause
