@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Anything2Markdown Launcher

REM ==========================
REM 可修改：你的 conda 环境名
set "CONDA_ENV_NAME=docling"
REM ==========================

REM 切换到当前 bat 所在目录
cd /d "%~dp0"

echo [INFO] 工作目录: %cd%
echo [INFO] 目标 conda 环境: %CONDA_ENV_NAME%

REM 优先使用已在 PATH 中的 conda.bat
set "CONDA_BAT="
for /f "delims=" %%i in ('where conda.bat 2^>nul') do (
    set "CONDA_BAT=%%i"
    goto :found_conda
)

REM 兜底：常见 Anaconda/Miniconda 安装路径
if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "C:\ProgramData\anaconda3\condabin\conda.bat" set "CONDA_BAT=C:\ProgramData\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "C:\ProgramData\miniconda3\condabin\conda.bat" set "CONDA_BAT=C:\ProgramData\miniconda3\condabin\conda.bat"

:found_conda
if not defined CONDA_BAT (
    echo [ERROR] 未找到 conda.bat。请检查 Anaconda/Miniconda 是否安装，或把 condabin 加入 PATH。
    echo [TIP] 例如：C:\Users\你的用户名\anaconda3\condabin
    pause
    exit /b 1
)

echo [INFO] 使用 conda: %CONDA_BAT%

REM 使用 conda run 避免双击场景下 activate 失效导致闪退
call "%CONDA_BAT%" run -n "%CONDA_ENV_NAME%" python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] 启动失败。
    echo [TIP] 先在命令行测试：conda run -n %CONDA_ENV_NAME% python main.py
    pause
    exit /b 1
)

endlocal
