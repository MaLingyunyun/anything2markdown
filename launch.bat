@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM 默认环境名，也支持 launch.bat your_env
set "DEFAULT_CONDA_ENV_NAME=docling"
set "CONDA_ENV_NAME=%~1"
if not defined CONDA_ENV_NAME set "CONDA_ENV_NAME=%DEFAULT_CONDA_ENV_NAME%"

cd /d "%~dp0"

REM 按你的建议：统一通过 PowerShell 启动（PowerShell 里 conda 往往可用）
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch.ps1" -EnvName "%CONDA_ENV_NAME%"
if errorlevel 1 (
    echo.
    echo [ERROR] PowerShell 启动失败。
    pause
    exit /b 1
)

endlocal
