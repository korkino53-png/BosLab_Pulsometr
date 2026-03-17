from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any

from .runtime_helpers import app_base_dir


SETTINGS_FILE = "bos_settings.json"
RECORD_FILE = "bos_record.json"


@dataclass
class AppSettings:
    width: int = 1280
    height: int = 720
    last_ble_address: str = ""
    last_ble_name: str = ""
    last_mode: str = "demo"
    last_test_status: str = "not_tested"


@dataclass
class RecordState:
    best_height: int = 0


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings() -> AppSettings:
    raw = _read_json(app_base_dir() / SETTINGS_FILE)
    return AppSettings(
        width=int(raw.get("width", 1280)),
        height=int(raw.get("height", 720)),
        last_ble_address=str(raw.get("last_ble_address", "")),
        last_ble_name=str(raw.get("last_ble_name", "")),
        last_mode=str(raw.get("last_mode", "demo")),
        last_test_status=str(raw.get("last_test_status", "not_tested")),
    )


def save_settings(settings: AppSettings) -> None:
    _write_json(app_base_dir() / SETTINGS_FILE, asdict(settings))


def load_record() -> RecordState:
    raw = _read_json(app_base_dir() / RECORD_FILE)
    return RecordState(best_height=int(raw.get("best_height", 0)))


def save_record(record: RecordState) -> None:
    _write_json(app_base_dir() / RECORD_FILE, asdict(record))
