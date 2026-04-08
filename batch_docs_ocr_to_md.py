"""兼容旧用法：命令行批量处理文档/OCR文件。"""

from pathlib import Path

from core.constants import DOC_EXTENSIONS
from core.processor import ConversionProcessor
from utils.file_scan import collect_files

INPUT_DIR = Path(r"D:\ALM_OUT\文档及图片OCR转md\ocr_input")
OUTPUT_DIR = Path(r"D:\ALM_OUT\文档及图片OCR转md\ocr_md_output")
RECURSIVE = True
OVERWRITE = False


def main() -> None:
    print("开始批量转换文档为 Markdown...")
    print(f"输入目录：{INPUT_DIR}")
    print(f"输出目录：{OUTPUT_DIR}")
    files, unsupported = collect_files([INPUT_DIR], recursive=RECURSIVE, supported_exts=DOC_EXTENSIONS)

    for path in unsupported:
        print(f"[不支持/不存在] {path}")

    if not files:
        print("没有找到可处理的文件。")
        return

    converter = ConversionProcessor(overwrite=OVERWRITE, logger=print)
    stats = converter.convert(files, OUTPUT_DIR, lambda i, t: None)

    print("-" * 60)
    print("处理结束")
    print(f"成功：{stats.success}")
    print(f"失败：{stats.failed}")
    print(f"跳过：{stats.skipped}")


if __name__ == "__main__":
    main()
