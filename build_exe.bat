@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM 用法：build_exe.bat [env_name]
set "ENV_NAME=%~1"
if not defined ENV_NAME set "ENV_NAME=docling"

cd /d "%~dp0"

echo [INFO] 激活 conda 环境: %ENV_NAME%
call conda activate "%ENV_NAME%"
if errorlevel 1 (
    echo [ERROR] conda activate 失败: %ENV_NAME%
    pause
    exit /b 1
)

echo [INFO] 安装/升级打包依赖
python -m pip install -U pyinstaller
if errorlevel 1 (
    echo [ERROR] pyinstaller 安装失败
    pause
    exit /b 1
)

echo [INFO] 开始打包（onedir 更稳）
pyinstaller --noconfirm --clean --onedir --windowed --name Anything2Markdown main.py
if errorlevel 1 (
    echo [ERROR] 打包失败
    pause
    exit /b 1
)

echo [OK] 打包完成，输出目录: dist\Anything2Markdown\
echo [TIP] 请在目标机器先验证 OCR/ASR 是否可用。
pause
endlocal
