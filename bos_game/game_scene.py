from __future__ import annotations

from dataclasses import dataclass
import math
import random

import pygame

from .persistence import RecordState
from .tower_physics import Block, Debris, collapse_to_debris, is_unstable, placement_offset_from_bpm


@dataclass
class GameResult:
    best_height: int


class HeartRateSource:
    def __init__(self, mode: str = "demo") -> None:
        self.mode = mode
        self._t = 0.0

    def update(self, dt: float) -> float:
        if self.mode == "demo":
            self._t += dt
            return 76 + 10 * math.sin(self._t * 0.8) + random.uniform(-2.5, 2.5)
        return 82.0


def run_game(screen: pygame.Surface, hr_source: HeartRateSource, record: RecordState) -> GameResult:
    clock = pygame.time.Clock()
    w, h = screen.get_size()
    cube_size = 56
    base_y_world = h * 0.75
    blocks: list[Block] = [Block(x=w / 2, y=base_y_world, size=cube_size)]

    camera_y = 0.0
    target_camera_y = 0.0
    dropping_x = w / 2
    drop_y = -120.0
    drop_v = 0.0
    gravity = 820.0
    max_speed = 760.0

    collapse = False
    debris: list[Debris] = []
    show_message = False

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameResult(best_height=record.best_height)
            if show_message and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return GameResult(best_height=record.best_height)

        hr = hr_source.update(dt)

        if not collapse:
            drop_v = min(max_speed, drop_v + gravity * dt)
            drop_y += drop_v * dt
            top_block = blocks[-1]
            target_y = top_block.y - cube_size
            if drop_y >= target_y:
                drop_y = target_y
                placed_x = top_block.x + placement_offset_from_bpm(hr)
                blocks.append(Block(placed_x, target_y, cube_size))
                drop_y = target_y - 220
                drop_v = 0.0
                dropping_x = placed_x
                target_camera_y = max(0.0, target_y - h * 0.25)
                current_height = len(blocks) - 1
                record.best_height = max(record.best_height, current_height)
                if is_unstable(blocks):
                    collapse = True
                    debris = collapse_to_debris(blocks)

        camera_y += (target_camera_y - camera_y) * min(1.0, dt * 2.5)

        if collapse:
            settled = 0
            for d in debris:
                d.vy += gravity * dt
                d.x += d.vx * dt
                d.y += d.vy * dt
                d.vx *= 0.985
                d.vy *= 0.985
                if d.y >= base_y_world + 200:
                    d.y = base_y_world + 200
                    d.vx *= 0.7
                    d.vy = 0.0
                if abs(d.vx) < 4 and abs(d.vy) < 4:
                    settled += 1
            if debris and settled / len(debris) > 0.9:
                show_message = True

        screen.fill((11, 16, 28))
        pygame.draw.rect(screen, (30, 36, 52), (0, h - 60, w, 60))

        if not collapse:
            rect = pygame.Rect(dropping_x - cube_size / 2, drop_y - camera_y, cube_size, cube_size)
            pygame.draw.rect(screen, (238, 198, 99), rect)
            for b in blocks:
                r = pygame.Rect(b.x - b.size / 2, b.y - camera_y, b.size, b.size)
                pygame.draw.rect(screen, (102, 183, 255), r)
        else:
            for d in debris:
                r = pygame.Rect(d.x - cube_size / 2, d.y - camera_y, cube_size, cube_size)
                pygame.draw.rect(screen, (174, 112, 112), r)

        font = pygame.font.SysFont("Segoe UI", 24)
        screen.blit(font.render(f"ЧСС: {int(hr)}", True, (230, 235, 245)), (18, 12))
        screen.blit(font.render(f"Высота: {len(blocks)-1}", True, (230, 235, 245)), (18, 42))
        screen.blit(font.render(f"Рекорд: {record.best_height}", True, (230, 235, 245)), (18, 72))

        if show_message:
            msg = pygame.font.SysFont("Segoe UI", 34).render("Очень хорошо, но можно и лучше. Попробуем ещё раз?", True, (250, 250, 250))
            sub = font.render("Нажмите ПРОБЕЛ для перезапуска.", True, (250, 250, 250))
            screen.blit(msg, (max(10, w // 2 - msg.get_width() // 2), h // 2 - 40))
            screen.blit(sub, (max(10, w // 2 - sub.get_width() // 2), h // 2 + 10))

        pygame.display.flip()
