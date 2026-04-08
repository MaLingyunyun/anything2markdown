from pathlib import Path
import traceback

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableStructureOptions,
    RapidOcrOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    ImageFormatOption,
    ConversionStatus,
)

# ========= 这里改成你的输入/输出文件夹 =========
INPUT_DIR = Path(r"D:\ALM_OUT\文档及图片OCR转md\ocr_input")
OUTPUT_DIR = Path(r"D:\ALM_OUT\文档及图片OCR转md\ocr_md_output")
# ===========================================

# 是否递归扫描子文件夹
RECURSIVE = True

# 如果输出 md 已存在，是否覆盖
OVERWRITE = False

# 支持的输入格式
SUPPORTED_EXTENSIONS = {
    # OCR 重点格式
    ".pdf",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",

    # 常规解析格式
    ".docx", ".pptx", ".xlsx",
    ".html", ".htm",
    ".md", ".markdown",
    ".csv",
    ".adoc", ".asciidoc",
    ".tex", ".latex",
}


def build_pdf_like_pipeline() -> PdfPipelineOptions:
    """
    给 PDF / 图片共用的一套 OCR 配置。
    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options = TableStructureOptions(
        do_cell_matching=True
    )

    # 默认使用 RapidOCR，Win11 上更省事
    pipeline_options.ocr_options = RapidOcrOptions(
        force_full_page_ocr=True
    )
    return pipeline_options


def build_converter() -> DocumentConverter:
    """
    构建 Docling 转换器：
    - PDF / IMAGE 强制 OCR
    - 其他支持格式走默认解析
    """
    pdf_like_options = build_pdf_like_pipeline()

    converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.XLSX,
            InputFormat.HTML,
            InputFormat.MD,
            InputFormat.CSV,
            InputFormat.ASCIIDOC,
            InputFormat.LATEX,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_like_options
            ),
            InputFormat.IMAGE: ImageFormatOption(
                pipeline_options=pdf_like_options
            ),
        },
    )
    return converter


def find_input_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在：{input_dir}")

    pattern = "**/*" if RECURSIVE else "*"
    files = [
        p for p in input_dir.glob(pattern)
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)


def build_output_path(src_file: Path, input_dir: Path, output_dir: Path) -> Path:
    rel_path = src_file.relative_to(input_dir)
    return (output_dir / rel_path).with_suffix(".md")


def convert_one_file(converter: DocumentConverter, src_file: Path, dst_file: Path) -> bool:
    try:
        dst_file.parent.mkdir(parents=True, exist_ok=True)

        if dst_file.exists() and not OVERWRITE:
            print(f"[跳过] 已存在：{dst_file}")
            return True

        print(f"[处理中] {src_file}")

        result = converter.convert(src_file)

        if result.status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS}:
            print(f"[失败] 状态异常：{src_file} -> {result.status}")
            if getattr(result, "errors", None):
                print(f"[错误详情] {result.errors}")
            return False

        md_text = result.document.export_to_markdown()
        dst_file.write_text(md_text, encoding="utf-8")

        if result.status == ConversionStatus.PARTIAL_SUCCESS:
            print(f"[部分成功] {dst_file}")
        else:
            print(f"[完成] {dst_file}")

        return True

    except Exception as e:
        print(f"[报错] {src_file}")
        print(f"原因：{e}")
        traceback.print_exc()
        return False


def main():
    print("开始批量转换文档为 Markdown...")
    print(f"输入目录：{INPUT_DIR}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("-" * 60)

    files = find_input_files(INPUT_DIR)

    if not files:
        print("没有找到可处理的文件。")
        return

    print(f"共找到 {len(files)} 个文件。")
    print("-" * 60)

    converter = build_converter()

    success_count = 0
    fail_count = 0

    for src_file in files:
        dst_file = build_output_path(src_file, INPUT_DIR, OUTPUT_DIR)
        ok = convert_one_file(converter, src_file, dst_file)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print("-" * 60)
    print("处理结束")
    print(f"成功：{success_count}")
    print(f"失败：{fail_count}")


if __name__ == "__main__":
    main()