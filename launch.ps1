param(
    [string]$EnvName = "docling"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "[INFO] 工作目录: $PWD"
Write-Host "[INFO] 目标 conda 环境: $EnvName"

function Resolve-CondaCommand {
    $cmd = Get-Command conda -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $candidates = @(
        "$env:USERPROFILE\anaconda3\condabin\conda.bat",
        "$env:USERPROFILE\miniconda3\condabin\conda.bat",
        "C:\ProgramData\anaconda3\condabin\conda.bat",
        "C:\ProgramData\miniconda3\condabin\conda.bat",
        "$env:USERPROFILE\anaconda3\Scripts\conda.exe",
        "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
        "C:\ProgramData\anaconda3\Scripts\conda.exe",
        "C:\ProgramData\miniconda3\Scripts\conda.exe"
    )

    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            return $path
        }
    }

    return $null
}

$condaCmd = Resolve-CondaCommand
if (-not $condaCmd) {
    Write-Host "[ERROR] 未找到 conda 命令（conda.bat/conda.exe）。"
    Write-Host "[TIP] 请确认 Anaconda/Miniconda 已安装，或将 condabin/Scripts 加入 PATH。"
    Read-Host "按回车退出"
    exit 1
}

Write-Host "[INFO] 使用 conda: $condaCmd"

$envList = & $condaCmd env list 2>&1 | Out-String
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] 执行 conda env list 失败。"
    Write-Host $envList
    Read-Host "按回车退出"
    exit 1
}

if ($envList -notmatch "(?m)^\s*\*?\s*$([regex]::Escape($EnvName))\s+") {
    Write-Host "[ERROR] conda 环境不存在: $EnvName"
    Write-Host "[INFO] 当前可用环境:"
    Write-Host $envList
    Read-Host "按回车退出"
    exit 1
}

& $condaCmd run -n $EnvName python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] 启动失败。"
    Write-Host "[TIP] 请手工测试: conda run -n $EnvName python main.py"
    Read-Host "按回车退出"
    exit 1
}
