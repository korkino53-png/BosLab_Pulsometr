from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass
class Block:
    x: float
    y: float
    size: int


@dataclass
class Debris:
    x: float
    y: float
    vx: float
    vy: float
    settled: bool = False


def placement_offset_from_bpm(bpm: float) -> float:
    calm = max(0.0, min(1.0, (100.0 - bpm) / 40.0))
    jitter = (1.0 - calm) * 28.0
    return random.uniform(-jitter, jitter)


def center_of_mass_x(blocks: list[Block], from_idx: int = 0) -> float:
    subset = blocks[from_idx:] if blocks else []
    if not subset:
        return 0.0
    return sum(b.x for b in subset) / len(subset)


def is_unstable(blocks: list[Block], support_margin: float = 20.0) -> bool:
    if len(blocks) < 3:
        return False
    base = blocks[0]
    com = center_of_mass_x(blocks, from_idx=max(0, len(blocks) // 3))
    return abs(com - base.x) > support_margin


def collapse_to_debris(blocks: list[Block]) -> list[Debris]:
    debris: list[Debris] = []
    for b in blocks:
        debris.append(
            Debris(
                x=b.x,
                y=b.y,
                vx=random.uniform(-180, 180),
                vy=random.uniform(-260, -80),
            )
        )
    return debris
