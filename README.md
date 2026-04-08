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

先把 `launch.bat` 里的 `CONDA_ENV_NAME` 改成你的环境名（默认 `docling`）。  
新版 `launch.bat` 已改为 `conda run -n ... python main.py`，并自动探测常见 `conda.bat` 路径，避免双击时 `conda activate` 失效导致闪退。
先把 `launch.bat` 里的 `CONDA_ENV_NAME` 改成你的环境名（默认 `docling`）。

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

不建议一开始就追求“完全独立 exe”，原因：
- `docling` 依赖链较大，PyInstaller 首次打包成本高。
- ASR/OCR 组件在不同机器兼容性差异明显。

建议顺序：
1. **先用 conda 环境 + launch.bat 稳定跑通（本仓库已完成）。**
2. 再尝试 `pyinstaller --onedir main.py`（优先 `onedir`，别先用 `onefile`）。
3. 针对缺失动态库逐步加 `--hidden-import` / `--collect-all`。

## 10. MVP 限制 / TODO

- GUI 当前不做任务暂停/恢复（MVP刻意简化）。
- 大文件批处理时，日志较多是预期行为。
- 如果你希望后续加“每个文件耗时统计、失败重试、导出报告 CSV”，可以在现结构上直接扩展。

## 11. 常见问题：双击 launch.bat 闪退

如果仍闪退，请按顺序检查：
1. 打开 `launch.bat`，确认 `CONDA_ENV_NAME` 和你的环境名一致。  
2. 在终端执行：`conda run -n 你的环境名 python main.py`，看是否有明确报错。  
3. 若提示找不到 `conda.bat`，把 `anaconda3\\condabin` 或 `miniconda3\\condabin` 加到系统 PATH。  
4. 若 GUI 打开失败，检查当前环境是否安装 `tkinterdnd2`（拖拽可选，不影响按钮选择方式）。
