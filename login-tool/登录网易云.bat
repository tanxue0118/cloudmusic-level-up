@echo off
title 网易云登录工具
cd /d "%~dp0"

echo ============================================
echo  网易云登录工具
echo  登录后自动同步到服务器
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3。
    pause
    exit /b 1
)

py -c "import playwright, paramiko, requests" >nul 2>nul
if errorlevel 1 (
    echo 正在安装依赖，请稍候...
    py -m pip install playwright paramiko requests
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络。
        pause
        exit /b 1
    )
    py -m playwright install
)

py browser_login.py
echo.
pause
