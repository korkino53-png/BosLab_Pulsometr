from __future__ import annotations

import pygame

from bos_game.ble_menu import ble_menu
from bos_game.game_scene import HeartRateSource, run_game
from bos_game.persistence import load_record, load_settings, save_record, save_settings
from bos_game.settings import open_centered_window, resolution_menu


def main() -> int:
    pygame.init()
    settings = load_settings()

    res = resolution_menu((settings.width, settings.height))
    if res is None:
        return 0

    settings.width, settings.height = res.width, res.height
    save_settings(settings)

    screen = open_centered_window(settings.width, settings.height)

    selected = ble_menu(screen)
    if selected is None:
        return 0

    settings.last_mode = selected.mode
    settings.last_ble_address = selected.address
    settings.last_ble_name = selected.name
    settings.last_test_status = selected.test_status
    save_settings(settings)

    record = load_record()
    source = HeartRateSource(mode="demo" if selected.mode != "ble" else "ble")
    result = run_game(screen, source, record)
    record.best_height = max(record.best_height, result.best_height)
    save_record(record)

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
