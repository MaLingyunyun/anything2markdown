from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.constants import DEFAULT_OUTPUT_DIR, SUPPORTED_EXTENSIONS
from core.processor import ConversionProcessor
from utils.file_scan import collect_files
from utils.logger import AppLogger

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
except Exception:  # noqa: BLE001
    DND_FILES = None
    TkinterDnD = None


class App:
    def __init__(self) -> None:
        if TkinterDnD:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("Anything2Markdown MVP")
        self.root.geometry("900x620")

        self.input_paths: list[Path] = []

        self.output_dir_var = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR.resolve()))
        self.recursive_var = tk.BooleanVar(value=True)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="就绪")
        self.summary_var = tk.StringVar(value="成功 0 | 失败 0 | 跳过 0")

        self.logger = AppLogger(self._append_log)

        self._build_ui()

    def _build_ui(self) -> None:
        frm_top = ttk.Frame(self.root, padding=10)
        frm_top.pack(fill=tk.X)

        ttk.Button(frm_top, text="添加文件", command=self._pick_files).pack(side=tk.LEFT)
        ttk.Button(frm_top, text="添加文件夹", command=self._pick_folder).pack(side=tk.LEFT, padx=8)
        ttk.Button(frm_top, text="清空列表", command=self._clear_inputs).pack(side=tk.LEFT)

        frm_opts = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        frm_opts.pack(fill=tk.X)

        ttk.Label(frm_opts, text="输出目录:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frm_opts, textvariable=self.output_dir_var).grid(row=0, column=1, sticky=tk.EW, padx=8)
        ttk.Button(frm_opts, text="选择", command=self._pick_output_dir).grid(row=0, column=2, sticky=tk.E)
        frm_opts.columnconfigure(1, weight=1)

        ttk.Checkbutton(frm_opts, text="递归扫描子文件夹", variable=self.recursive_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(frm_opts, text="覆盖已有 .md", variable=self.overwrite_var).grid(row=1, column=1, sticky=tk.W)

        drop_text = "拖拽文件/文件夹到这里"
        if not TkinterDnD:
            drop_text += "（未安装 tkinterdnd2，拖拽不可用）"
        self.drop_label = ttk.Label(self.root, text=drop_text, relief=tk.GROOVE, anchor=tk.CENTER)
        self.drop_label.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=12)

        if TkinterDnD and DND_FILES:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

        frm_mid = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        frm_mid.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(frm_mid, height=8)
        self.listbox.pack(fill=tk.X)

        self.progress = ttk.Progressbar(frm_mid, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(fill=tk.X, pady=8)

        self.log_text = tk.Text(frm_mid, height=16)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        frm_bottom = ttk.Frame(self.root, padding=10)
        frm_bottom.pack(fill=tk.X)
        ttk.Button(frm_bottom, text="开始转换", command=self._start_convert).pack(side=tk.LEFT)
        ttk.Label(frm_bottom, textvariable=self.status_var).pack(side=tk.LEFT, padx=12)
        ttk.Label(frm_bottom, textvariable=self.summary_var).pack(side=tk.RIGHT)

    def _on_drop(self, event) -> None:  # type: ignore[no-untyped-def]
        raw = self.root.tk.splitlist(event.data)
        paths = [Path(p.strip("{}")) for p in raw]
        self._add_inputs(paths)

    def _pick_files(self) -> None:
        files = filedialog.askopenfilenames(title="选择文件")
        self._add_inputs([Path(f) for f in files])

    def _pick_folder(self) -> None:
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            self._add_inputs([Path(folder)])

    def _pick_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir_var.set(folder)

    def _add_inputs(self, paths: list[Path]) -> None:
        added = 0
        for p in paths:
            if p not in self.input_paths:
                self.input_paths.append(p)
                self.listbox.insert(tk.END, str(p))
                added += 1
        self.logger.log(f"已加入 {added} 个输入项")

    def _clear_inputs(self) -> None:
        self.input_paths.clear()
        self.listbox.delete(0, tk.END)
        self.logger.log("输入列表已清空")

    def _append_log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def _set_progress(self, idx: int, total: int) -> None:
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = idx
        self.status_var.set(f"处理中 {idx}/{total}")

    def _start_convert(self) -> None:
        if not self.input_paths:
            messagebox.showwarning("提示", "请先添加文件或文件夹")
            return

        output_dir = Path(self.output_dir_var.get().strip())
        if not output_dir:
            messagebox.showwarning("提示", "请先选择输出目录")
            return

        self.progress["value"] = 0
        self.summary_var.set("成功 0 | 失败 0 | 跳过 0")
        self.status_var.set("准备扫描文件...")

        t = threading.Thread(target=self._run_convert, args=(output_dir,), daemon=True)
        t.start()

    def _run_convert(self, output_dir: Path) -> None:
        try:
            files, unsupported = collect_files(
                paths=self.input_paths,
                recursive=self.recursive_var.get(),
                supported_exts=SUPPORTED_EXTENSIONS,
            )

            for p in unsupported:
                self.logger.log(f"[不支持/不存在] {p}")

            if not files:
                self.status_var.set("无可处理文件")
                return

            self.logger.log(f"共扫描到 {len(files)} 个可处理文件")
            processor = ConversionProcessor(overwrite=self.overwrite_var.get(), logger=self.logger.log)

            def progress_cb(i: int, t: int) -> None:
                self.root.after(0, self._set_progress, i, t)

            stats = processor.convert(files, output_dir=output_dir, progress_cb=progress_cb)
            self.root.after(0, self._finish, stats.success, stats.failed, stats.skipped)
        except Exception as exc:  # noqa: BLE001
            self.logger.log(f"[致命错误] {exc}")
            self.status_var.set("执行失败")

    def _finish(self, success: int, failed: int, skipped: int) -> None:
        self.status_var.set("处理完成")
        self.summary_var.set(f"成功 {success} | 失败 {failed} | 跳过 {skipped}")
        self.logger.log("全部任务处理结束")

    def run(self) -> None:
        self.root.mainloop()
