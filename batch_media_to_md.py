from pathlib import Path
import traceback

from docling.datamodel import asr_model_specs
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import AsrPipelineOptions
from docling.document_converter import AudioFormatOption, DocumentConverter
from docling.pipeline.asr_pipeline import AsrPipeline


# ========= 这里改成你的输入/输出文件夹 =========
INPUT_DIR = Path(r"D:\ALM_OUT\音视频转md\media_input")
OUTPUT_DIR = Path(r"D:\ALM_OUT\音视频转md\media_md_output")
# ===========================================

# 支持的音频 + 视频格式
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac",
    ".mp4", ".avi", ".mov"
}

# 是否递归扫描子文件夹
RECURSIVE = True

# 如果 md 已存在，是否覆盖
OVERWRITE = False


def build_converter() -> DocumentConverter:
    pipeline_options = AsrPipelineOptions()
    pipeline_options.asr_options = asr_model_specs.WHISPER_TURBO

    converter = DocumentConverter(
        format_options={
            InputFormat.AUDIO: AudioFormatOption(
                pipeline_cls=AsrPipeline,
                pipeline_options=pipeline_options,
            )
        }
    )
    return converter


def find_media_files(input_dir: Path) -> list[Path]:
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

        if result.status != ConversionStatus.SUCCESS:
            print(f"[失败] 状态异常：{src_file} -> {result.status}")
            return False

        md_text = result.document.export_to_markdown()
        dst_file.write_text(md_text, encoding="utf-8")

        print(f"[完成] {dst_file}")
        return True

    except Exception as e:
        print(f"[报错] {src_file}")
        print(f"原因：{e}")
        traceback.print_exc()
        return False


def main():
    print("开始批量转换音频/视频为 Markdown...")
    print(f"输入目录：{INPUT_DIR}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("-" * 60)

    media_files = find_media_files(INPUT_DIR)

    if not media_files:
        print("没有找到可处理的音频或视频文件。")
        return

    print(f"共找到 {len(media_files)} 个文件。")
    print("-" * 60)

    converter = build_converter()

    success_count = 0
    fail_count = 0

    for src_file in media_files:
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