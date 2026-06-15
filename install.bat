@echo off
chcp 65001 >nul
title 校园广播系统 V5.4 一键部署

echo ==========================================
echo   校园智能广播定时系统 V5.4
echo   一键部署脚本
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [提示] 建议以管理员身份运行(右键-以管理员身份运行)
    echo         NTP校时需要管理员权限才能校准系统时间
    echo.
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.9+
    echo        下载地址: https://www.python.org/downloads/
    echo        安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python已安装
python --version
echo.

REM 安装依赖
echo [1/3] 安装Python依赖...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [重试] 逐个安装...
    python -m pip install flask flask-apscheduler pygame ntplib openpyxl
)
echo [OK] 依赖安装完成
echo.

REM 初始化
echo [2/3] 初始化系统...
python -c "from models import init_db; init_db(); print('[OK] 数据库已初始化')"
echo.

REM 询问开机自启
echo [3/3] 开机自启动设置
echo   1. 是 - 系统登录后自动启动（推荐服务器使用）
echo   2. 否 - 手动启动
set /p choice="请选择 (1/2): "

if "%choice%"=="1" (
    set "SCRIPT_DIR=%~dp0"
    set "VBS_FILE=%SCRIPT_DIR%start_hidden.vbs"
    echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
    echo WshShell.Run "pythonw.exe ""%SCRIPT_DIR%run.py""", 0, False >> "%VBS_FILE%"
    set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    copy "%VBS_FILE%" "%STARTUP_FOLDER%\校园广播系统.vbs" >nul 2>&1
    if errorlevel 1 (
        echo [警告] 无法添加开机启动，请手动设置
    ) else (
        echo [OK] 已设置开机自启动
    )
)

echo.
echo ==========================================
echo   部署完成! V5.4
echo.
echo   启动方式:
echo   1. 双击 run.py
echo   2. 命令行: python run.py
echo   3. 后台运行: start_hidden.vbs (双击，无窗口)
echo.
echo   访问地址:
echo   http://localhost:8787
echo   手机访问: http://[电脑IP]:8787
echo.
echo   首次使用:
echo   1. 进入「节假日」→ 同步节假日
echo   2. 进入「课表管理」→ 编辑打铃任务
echo   3. 进入「系统设置」→ 配置钉钉/NTP
echo ==========================================
pause
