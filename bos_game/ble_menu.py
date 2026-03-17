from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pygame

from .ble_diagnostics import DiagnosticResult, run_diagnostics
from .ble_scanner import BleScannerService


@dataclass
class BleSelection:
    mode: str
    address: str = ""
    name: str = ""
    test_status: str = "not_tested"


STATUS_TEXT = {
    "not_tested": "не тестировалось",
    "ok": "OK",
    "hr_only": "только ЧСС",
    "unfit": "не годен",
    "connection_error": "ошибка подключения",
}


def ble_menu(screen: pygame.Surface) -> BleSelection | None:
    scanner = BleScannerService()
    scanner.start()
    font = pygame.font.SysFont("Consolas", 20)
    title_font = pygame.font.SysFont("Segoe UI", 28)
    selected = 0
    only_hr = False
    info = "Сканирование BLE..."

    while True:
        devices = scanner.snapshot()
        if only_hr:
            devices = [d for d in devices if d.is_hr_candidate]
        if devices:
            selected = max(0, min(selected, len(devices) - 1))
        else:
            selected = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                scanner.stop()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected -= 1
                elif event.key == pygame.K_f:
                    only_hr = not only_hr
                elif event.key == pygame.K_r:
                    scanner.clear()
                    info = "Список очищен, идет новый скан"
                elif event.key == pygame.K_d:
                    scanner.stop()
                    return BleSelection(mode="demo")
                elif event.key == pygame.K_ESCAPE:
                    scanner.stop()
                    return BleSelection(mode="demo")
                elif event.key == pygame.K_RETURN and devices:
                    d = devices[selected]
                    scanner.stop()
                    return BleSelection(mode="ble", address=d.address, name=d.name, test_status=d.test_status)
                elif event.key == pygame.K_t and devices:
                    d = devices[selected]
                    scanner.pause()
                    result: DiagnosticResult = asyncio.run(run_diagnostics(d.address))
                    scanner.resume()
                    scanner.update_test_status(d.address, result.status)
                    info = result.message

        screen.fill((10, 10, 16))
        screen.blit(title_font.render("BLE меню", True, (240, 240, 255)), (20, 14))
        hint = "↑/↓ W/S навигация | Enter выбрать | T тест | F фильтр | R перескан | D demo"
        screen.blit(font.render(hint, True, (180, 180, 190)), (20, 54))
        screen.blit(font.render(info, True, (198, 210, 230)), (20, 82))

        y = 120
        for i, d in enumerate(devices[:20]):
            marker = ">" if i == selected else " "
            tag = "HR" if d.is_hr_candidate else "BLE"
            status = STATUS_TEXT.get(d.test_status, d.test_status)
            row = f"{marker} {d.name[:18]:18} {d.address:20} RSSI:{str(d.rssi):>4} {tag:3} [{status}]"
            color = (245, 245, 255) if i == selected else (160, 175, 188)
            screen.blit(font.render(row, True, color), (20, y))
            y += 26

        if not devices:
            screen.blit(font.render("Нет устройств пока...", True, (180, 180, 200)), (20, y + 10))

        pygame.display.flip()
