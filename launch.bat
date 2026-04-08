@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM 既支持默认环境，也支持 launch.bat your_env
set "ENV_NAME=%~1"
if not defined ENV_NAME set "ENV_NAME=docling"

cd /d "%~dp0"

echo [INFO] 工作目录: %cd%
echo [INFO] 激活 conda 环境: %ENV_NAME%

call conda activate "%ENV_NAME%"
if errorlevel 1 (
    echo [ERROR] conda activate 失败，请检查环境名: %ENV_NAME%
    pause
    exit /b 1
)

python main.py
if errorlevel 1 (
    echo [ERROR] 程序运行失败，请检查依赖或报错日志。
    pause
    exit /b 1
)

endlocal
