# Anything2Markdown (MVP)

基于你现有 `docling` 脚本重构的**本地 GUI 批量转 Markdown 工具**（Windows 优先）。

## 1. 本版目标

第一版只聚焦可用性：
- 拖入文件/文件夹
- 自动识别格式并批量转换
- 输出 `.md`
- 显示进度、日志、成功/失败/跳过统计
- 尽量复用你已有 Docling OCR/ASR 配置

## 2. 目录结构

```text
anything2markdown/
├─ main.py                         # GUI 入口
├─ batch_docs_ocr_to_md.py         # 旧脚本兼容入口（已复用新核心）
├─ batch_media_to_md.py            # 旧脚本兼容入口（已复用新核心）
├─ requirements.txt
├─ launch.bat                      # Windows 一键启动（激活 conda + 打开 GUI）
├─ core/
│  ├─ constants.py
│  └─ processor.py                 # 统一分发 + 转换流程
├─ converters/
│  ├─ doc_converter.py             # PDF/IMAGE OCR + 表格配置
│  └─ media_converter.py           # ASR + 视频 fallback(ffmpeg)
├─ gui/
│  └─ main_window.py               # Tkinter GUI
└─ utils/
   ├─ file_scan.py                 # 递归扫描/输出路径映射
   └─ logger.py
```

## 3. 支持格式

### 文档 / OCR
- PDF
- PNG / JPG / JPEG / TIF / TIFF / BMP / WEBP
- DOCX / PPTX / XLSX
- HTML / HTM
- MD / MARKDOWN
- CSV
- ADOC / ASCIIDOC
- TEX / LATEX

### 音视频
- MP3 / WAV / M4A / AAC / OGG / FLAC
- MP4 / AVI / MOV

## 4. 关键复用（保留你的原能力）

文档/OCR链路保留：
- `do_ocr = True`
- `do_table_structure = True`
- `TableStructureOptions(do_cell_matching=True)`
- `RapidOcrOptions(force_full_page_ocr=True)`

音视频链路保留：
- ASR pipeline
- `asr_model_specs.WHISPER_TURBO`

## 5. 视频稳定性策略（新增）

考虑到不同机器上视频直转的稳定性差异：
1. 先尝试 `docling` 直接转换视频。
2. 如果失败且检测到 `ffmpeg`，自动 fallback：先抽取 WAV，再走 ASR。
3. 如果失败且没有 `ffmpeg`，日志中明确提示原因。

> 这样比“假设 mp4/avi/mov 都能稳定直转”更稳。

## 6. 在现有 conda 环境中运行

### 方式 A（推荐）：双击 `launch.bat`

默认使用 `docling` 环境；你可以命令行传参：`launch.bat 你的环境名`。  
`launch.bat` 现在直接执行：`conda activate <env> && python main.py`。  
你已经把 conda 配好了，这种方式最直观、最好维护。

### 方式 B：命令行

```bash
conda activate docling
cd /d D:\ALM_OUT\音视频转md
python main.py
```

## 7. 安装依赖

在你的 conda 环境中执行：

```bash
pip install -r requirements.txt
```

> `tkinter` 在大多数 Windows Python/conda 中自带；
> 如果拖拽不可用，先安装 `tkinterdnd2`。

## 8. 旧脚本兼容

你原来的两个脚本仍然可运行：
- `python batch_docs_ocr_to_md.py`
- `python batch_media_to_md.py`

但内部已复用统一核心逻辑，减少重复代码。

## 9. 打包建议（第二阶段）

可以直接打包成 exe（推荐先 `onedir` 方案）。  
我已经提供 `build_exe.bat`，会自动：
1. 激活 conda 环境  
2. 安装/升级 pyinstaller  
3. 执行 `pyinstaller --onedir --windowed --name Anything2Markdown main.py`

使用方式：
```bash
build_exe.bat
# 或指定环境
build_exe.bat docling
```

产物目录：
- `dist/Anything2Markdown/Anything2Markdown.exe`

说明：
- `onedir` 比 `onefile` 更稳（尤其是 docling 这类依赖较重场景）。
- 若你后续确认稳定，再尝试 onefile。

## 10. MVP 限制 / TODO

- GUI 当前不做任务暂停/恢复（MVP刻意简化）。
- 大文件批处理时，日志较多是预期行为。
- 如果你希望后续加“每个文件耗时统计、失败重试、导出报告 CSV”，可以在现结构上直接扩展。

## 11. 常见问题：双击 launch.bat 闪退

如果仍闪退，请按顺序检查：
1. 打开 `launch.bat`，确认环境名（默认 `docling`）与你本机一致，或命令行执行 `launch.bat your_env`。  
2. 在终端手工执行：`conda activate 你的环境名 && python main.py`，确认环境可正常运行。  
3. 若 GUI 打开失败，检查当前环境是否安装 `tkinterdnd2`（拖拽可选，不影响按钮选择方式）。

## 12. 常见问题：CMD 中 conda 不可用

你当前已修复此问题。若后续再次出现，请先执行：
```bash
conda init cmd.exe
```
然后重新打开 CMD。
