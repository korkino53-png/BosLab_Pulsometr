from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import threading
import time
from typing import Dict

from bleak import BleakScanner


HR_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"


@dataclass
class DeviceView:
    name: str
    address: str
    rssi: int | None
    is_hr_candidate: bool
    last_seen: float = field(default_factory=time.time)
    test_status: str = "not_tested"


class BleScannerService:
    def __init__(self) -> None:
        self._devices: Dict[str, DeviceView] = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._pause = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._pause.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.5)

    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        self._pause.clear()

    def clear(self) -> None:
        with self._lock:
            self._devices.clear()

    def update_test_status(self, address: str, status: str) -> None:
        with self._lock:
            if address in self._devices:
                self._devices[address].test_status = status

    def snapshot(self) -> list[DeviceView]:
        with self._lock:
            rows = list(self._devices.values())
        rows.sort(key=lambda d: (not d.is_hr_candidate, -(d.rssi or -999), d.name.lower()))
        return rows

    def _run(self) -> None:
        asyncio.run(self._scan_loop())

    async def _scan_loop(self) -> None:
        while not self._stop.is_set():
            if self._pause.is_set():
                await asyncio.sleep(0.1)
                continue
            devices = await BleakScanner.discover(timeout=1.0, return_adv=True)
            now = time.time()
            with self._lock:
                for _, (dev, adv) in devices.items():
                    name = dev.name or adv.local_name or "Unknown"
                    uuids = [u.lower() for u in (adv.service_uuids or [])]
                    is_hr = "hr" in name.lower() or HR_SERVICE in uuids
                    self._devices[dev.address] = DeviceView(
                        name=name,
                        address=dev.address,
                        rssi=adv.rssi,
                        is_hr_candidate=is_hr,
                        last_seen=now,
                        test_status=self._devices.get(dev.address, DeviceView(name, dev.address, adv.rssi, is_hr)).test_status,
                    )
            await asyncio.sleep(0.05)
