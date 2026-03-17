from __future__ import annotations

from pathlib import Path
import sys


def app_base_dir() -> Path:
    """Return writable app directory near executable/script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent
