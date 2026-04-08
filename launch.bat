@echo off
setlocal EnableExtensions
chcp 65001 >nul

title Anything2Markdown Launcher
cd /d "%~dp0"

REM 防闪退：始终在常驻 cmd 窗口执行
if /i not "%~1"=="--run" (
    start "Anything2Markdown" cmd /k "\"%~f0\" --run %~1"
    exit /b 0
)

REM ===== 可配置 =====
set "ENV_NAME=%~2"
if not defined ENV_NAME set "ENV_NAME=docling"
REM 如需手工指定解释器，取消下一行注释并填绝对路径
REM set "PYTHON_EXE=C:\Users\<you>\anaconda3\envs\docling\python.exe"
REM =================

echo [INFO] 工作目录: %cd%
echo [INFO] 目标环境: %ENV_NAME%

if not defined PYTHON_EXE (
    call :find_env_python "%ENV_NAME%"
)

if not defined PYTHON_EXE (
    echo [WARN] 未找到环境 python.exe，尝试 conda run...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch.ps1" -EnvName "%ENV_NAME%"
    if errorlevel 1 (
        echo [ERROR] 启动失败：既找不到环境 python.exe，也无法通过 conda run 启动。
        echo [TIP] 你可以在本文件中手工设置 PYTHON_EXE 后重试。
        pause
        exit /b 1
    )
    goto :done
)

echo [INFO] 使用解释器: %PYTHON_EXE%
"%PYTHON_EXE%" "%~dp0main.py"
if errorlevel 1 (
    echo [ERROR] 使用环境解释器启动失败：%PYTHON_EXE%
    pause
    exit /b 1
)

:done
echo [INFO] 启动流程结束。
pause
exit /b 0

:find_env_python
set "TARGET_ENV=%~1"
set "PYTHON_EXE="

if exist "%USERPROFILE%\anaconda3\envs\%TARGET_ENV%\python.exe" set "PYTHON_EXE=%USERPROFILE%\anaconda3\envs\%TARGET_ENV%\python.exe"
if not defined PYTHON_EXE if exist "%USERPROFILE%\miniconda3\envs\%TARGET_ENV%\python.exe" set "PYTHON_EXE=%USERPROFILE%\miniconda3\envs\%TARGET_ENV%\python.exe"
if not defined PYTHON_EXE if exist "C:\ProgramData\anaconda3\envs\%TARGET_ENV%\python.exe" set "PYTHON_EXE=C:\ProgramData\anaconda3\envs\%TARGET_ENV%\python.exe"
if not defined PYTHON_EXE if exist "C:\ProgramData\miniconda3\envs\%TARGET_ENV%\python.exe" set "PYTHON_EXE=C:\ProgramData\miniconda3\envs\%TARGET_ENV%\python.exe"

exit /b 0
