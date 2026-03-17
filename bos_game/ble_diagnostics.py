from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bleak import BleakClient


HR_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"
HR_MEASUREMENT = "00002a37-0000-1000-8000-00805f9b34fb"


@dataclass
class DiagnosticResult:
    status: str
    bpm_seen: bool
    rr_seen: bool
    message: str


def parse_hr_measurement(payload: bytearray) -> tuple[int | None, bool]:
    if not payload:
        return None, False
    flags = payload[0]
    is_16 = bool(flags & 0x01)
    rr_present = bool(flags & 0x10)
    idx = 1
    bpm = None
    if is_16 and len(payload) >= 3:
        bpm = int.from_bytes(payload[idx:idx + 2], "little")
        idx += 2
    elif len(payload) >= 2:
        bpm = payload[idx]
        idx += 1
    if flags & 0x08:
        idx += 2
    if flags & 0x06:
        idx += 2
    has_rr = rr_present and len(payload) >= idx + 2
    return bpm, has_rr


async def run_diagnostics(address: str, timeout_s: float = 8.0) -> DiagnosticResult:
    bpm_seen = False
    rr_seen = False

    def on_measurement(_: int, data: bytearray) -> None:
        nonlocal bpm_seen, rr_seen
        bpm, has_rr = parse_hr_measurement(data)
        if bpm is not None:
            bpm_seen = True
        if has_rr:
            rr_seen = True

    try:
        async with BleakClient(address) as client:
            services = await client.get_services()
            if HR_SERVICE not in {s.uuid.lower() for s in services}:
                return DiagnosticResult("unfit", False, False, "Нет стандартного HR сервиса 0x180D")
            chars = {c.uuid.lower() for s in services for c in s.characteristics}
            if HR_MEASUREMENT not in chars:
                return DiagnosticResult("unfit", False, False, "Нет характеристики 0x2A37")

            await client.start_notify(HR_MEASUREMENT, on_measurement)
            started = asyncio.get_running_loop().time()
            while asyncio.get_running_loop().time() - started < timeout_s:
                await asyncio.sleep(0.2)
                if bpm_seen and rr_seen:
                    break
            await client.stop_notify(HR_MEASUREMENT)
    except Exception as exc:
        return DiagnosticResult("connection_error", False, False, f"Ошибка подключения: {exc}")

    if bpm_seen and rr_seen:
        return DiagnosticResult("ok", True, True, "OK: BPM и RR получены")
    if bpm_seen:
        return DiagnosticResult("hr_only", True, False, "Только ЧСС: RR не обнаружены")
    return DiagnosticResult("unfit", False, False, "Поток BPM не получен")
