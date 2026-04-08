from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InputItem:
    src_path: Path
    root_dir: Path


def collect_files(paths: list[Path], recursive: bool, supported_exts: set[str]) -> tuple[list[InputItem], list[Path]]:
    files: list[InputItem] = []
    unsupported: list[Path] = []

    for item in paths:
        if not item.exists():
            unsupported.append(item)
            continue

        if item.is_file():
            ext = item.suffix.lower()
            if ext in supported_exts:
                files.append(InputItem(src_path=item, root_dir=item.parent))
            else:
                unsupported.append(item)
            continue

        pattern = "**/*" if recursive else "*"
        for p in item.glob(pattern):
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            if ext in supported_exts:
                files.append(InputItem(src_path=p, root_dir=item))
            else:
                unsupported.append(p)

    files = sorted(files, key=lambda x: str(x.src_path).lower())
    unsupported = sorted(set(unsupported), key=lambda p: str(p).lower())
    return files, unsupported


def build_output_path(src_file: Path, root_dir: Path, output_dir: Path) -> Path:
    rel_path = src_file.relative_to(root_dir)
    return (output_dir / rel_path).with_suffix(".md")
