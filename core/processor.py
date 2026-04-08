from __future__ import annotations

import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from docling.datamodel.base_models import ConversionStatus

from converters.doc_converter import build_doc_converter
from converters.media_converter import build_media_converter, extract_video_audio, has_ffmpeg
from core.constants import DOC_EXTENSIONS, MEDIA_EXTENSIONS, VIDEO_EXTENSIONS
from utils.file_scan import InputItem, build_output_path


@dataclass
class ProcessStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0


class ConversionProcessor:
    def __init__(self, overwrite: bool, logger: Callable[[str], None]):
        self.overwrite = overwrite
        self.logger = logger
        self.doc_converter = build_doc_converter()
        self.media_converter = build_media_converter()
        self._ffmpeg_available = has_ffmpeg()

    def convert(self, items: list[InputItem], output_dir: Path, progress_cb: Callable[[int, int], None]) -> ProcessStats:
        stats = ProcessStats(total=len(items))

        for idx, item in enumerate(items, start=1):
            src_file = item.src_path
            dst_file = build_output_path(src_file, item.root_dir, output_dir)
            ok, skipped = self._convert_one(src_file, dst_file)
            if skipped:
                stats.skipped += 1
            elif ok:
                stats.success += 1
            else:
                stats.failed += 1
            progress_cb(idx, stats.total)

        return stats

    def _convert_one(self, src_file: Path, dst_file: Path) -> tuple[bool, bool]:
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            if dst_file.exists() and not self.overwrite:
                self.logger(f"[跳过] 已存在: {dst_file}")
                return True, True

            ext = src_file.suffix.lower()
            if ext in DOC_EXTENSIONS:
                return self._convert_via_docling(self.doc_converter, src_file, dst_file), False

            if ext in MEDIA_EXTENSIONS:
                # 视频经常依赖 ffmpeg。先直接尝试 docling；失败时再走 ffmpeg 抽音频 fallback。
                ok = self._convert_via_docling(self.media_converter, src_file, dst_file)
                if ok:
                    return True, False
                if ext in VIDEO_EXTENSIONS and self._ffmpeg_available:
                    self.logger(f"[提示] 视频转写 fallback: 先抽取音频再识别 -> {src_file.name}")
                    return self._convert_video_fallback(src_file, dst_file), False
                if ext in VIDEO_EXTENSIONS and not self._ffmpeg_available:
                    self.logger("[失败] 视频处理失败且未检测到 ffmpeg，无法执行 fallback。")
                return False, False

            self.logger(f"[失败] 不支持格式: {src_file}")
            return False, False

        except Exception as exc:
            self.logger(f"[报错] {src_file}\n原因: {exc}")
            self.logger(traceback.format_exc())
            return False, False

    def _convert_via_docling(self, converter, src_file: Path, dst_file: Path) -> bool:
        self.logger(f"[处理中] {src_file}")
        result = converter.convert(src_file)

        if result.status not in {ConversionStatus.SUCCESS, ConversionStatus.PARTIAL_SUCCESS}:
            self.logger(f"[失败] 状态异常: {src_file} -> {result.status}")
            if getattr(result, "errors", None):
                self.logger(f"[错误详情] {result.errors}")
            return False

        dst_file.write_text(result.document.export_to_markdown(), encoding="utf-8")
        if result.status == ConversionStatus.PARTIAL_SUCCESS:
            self.logger(f"[部分成功] {dst_file}")
        else:
            self.logger(f"[完成] {dst_file}")
        return True

    def _convert_video_fallback(self, src_file: Path, dst_file: Path) -> bool:
        with tempfile.TemporaryDirectory(prefix="a2m_") as tmp_dir:
            wav_path = Path(tmp_dir) / f"{src_file.stem}.wav"
            extract_video_audio(src_file, wav_path)
            return self._convert_via_docling(self.media_converter, wav_path, dst_file)
