@echo off
setlocal

REM 修改为你的 conda 环境名
set CONDA_ENV_NAME=docling

REM 进入当前 bat 所在目录
cd /d %~dp0

REM 初始化 conda 命令
call conda activate %CONDA_ENV_NAME%
if errorlevel 1 (
    echo [ERROR] conda activate failed. 请检查环境名: %CONDA_ENV_NAME%
    pause
    exit /b 1
)

python main.py
if errorlevel 1 (
    echo [ERROR] 程序运行失败，请查看报错日志。
    pause
    exit /b 1
)

endlocal
