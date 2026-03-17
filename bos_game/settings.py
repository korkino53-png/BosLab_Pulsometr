from __future__ import annotations

import os
from dataclasses import dataclass

import pygame


RESOLUTIONS = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080)]


@dataclass
class ResolutionChoice:
    width: int
    height: int


def open_centered_window(width: int, height: int) -> pygame.Surface:
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    return pygame.display.set_mode((width, height))


def resolution_menu(initial: tuple[int, int]) -> ResolutionChoice | None:
    idx = RESOLUTIONS.index(initial) if initial in RESOLUTIONS else 0
    screen = open_centered_window(800, 500)
    font = pygame.font.SysFont("Segoe UI", 34)
    small = pygame.font.SysFont("Segoe UI", 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(RESOLUTIONS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(RESOLUTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    w, h = RESOLUTIONS[idx]
                    return ResolutionChoice(w, h)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, (w, h) in enumerate(RESOLUTIONS):
                    rect = pygame.Rect(220, 120 + i * 80, 360, 60)
                    if rect.collidepoint(mx, my):
                        return ResolutionChoice(w, h)

        screen.fill((15, 15, 22))
        title = font.render("Выбор разрешения", True, (236, 236, 250))
        screen.blit(title, (220, 36))
        hint = small.render("↑/↓, W/S, Enter/Space, мышь", True, (178, 178, 190))
        screen.blit(hint, (190, 84))
        for i, (w, h) in enumerate(RESOLUTIONS):
            rect = pygame.Rect(220, 120 + i * 80, 360, 60)
            selected = i == idx
            pygame.draw.rect(screen, (70, 90, 150) if selected else (34, 38, 48), rect, border_radius=8)
            txt = font.render(f"{w}x{h}", True, (255, 255, 255))
            screen.blit(txt, (rect.x + 90, rect.y + 12))

        pygame.display.flip()
