from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable


@dataclass
class AppLogger:
    sink: Callable[[str], None]

    def log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.sink(f"[{ts}] {message}")
