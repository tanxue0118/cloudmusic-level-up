@echo off
chcp 65001 >nul
title 网易云登录工具
cd /d "%~dp0"

echo ============================================
echo  网易云登录工具
echo  登录后自动同步到你的服务器
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8 或更高版本。
    pause
    exit /b 1
)

if not exist config.json (
    echo [错误] 未找到 config.json
    echo 请复制 config.example.json 为 config.json，并填入你的服务器信息。
    pause
    exit /b 1
)

py -c "import playwright, paramiko, requests" >nul 2>nul
if errorlevel 1 (
    echo 正在安装依赖，请稍候…
    py -m pip install playwright paramiko requests
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络。
        pause
        exit /b 1
    )
    echo 正在准备浏览器内核…
    py -m playwright install msedge
)

py browser_login.py
echo.
pause
