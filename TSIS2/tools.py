"""
tools.py  —  Drawing tool implementations for Paint TSIS 2
"""

import pygame
from collections import deque


# ── Flood Fill ────────────────────────────────────────────────────────────

def flood_fill(surface, x, y, fill_color):
    """BFS flood-fill on a pygame Surface."""
    w, h = surface.get_size()
    target = surface.get_at((x, y))[:3]
    fill   = fill_color[:3]
    if target == fill:
        return

    visited = set()
    queue   = deque()
    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cy < 0 or cx >= w or cy >= h:
            continue
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        queue.append((cx + 1, cy))
        queue.append((cx - 1, cy))
        queue.append((cx, cy + 1))
        queue.append((cx, cy - 1))


# ── Shape drawing helpers ─────────────────────────────────────────────────

def draw_rect(surface, color, start, end, size):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        pygame.draw.rect(surface, color, (x, y, w, h), size)


def draw_circle(surface, color, start, end, size):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    r  = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2
    if r > 0:
        pygame.draw.circle(surface, color, (cx, cy), r, size)


def draw_square(surface, color, start, end, size):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    x = start[0]
    y = start[1]
    pygame.draw.rect(surface, color, (x, y, side, side), size)


def draw_line(surface, color, start, end, size):
    pygame.draw.line(surface, color, start, end, size)


def draw_right_triangle(surface, color, start, end, size):
    p1 = start
    p2 = (start[0], end[1])
    p3 = end
    pygame.draw.polygon(surface, color, [p1, p2, p3], size)


def draw_equilateral_triangle(surface, color, start, end, size):
    import math
    base = abs(end[0] - start[0])
    p1 = (start[0], end[1])
    p2 = (end[0],   end[1])
    p3 = (start[0] + base // 2, int(end[1] - base * math.sqrt(3) / 2))
    pygame.draw.polygon(surface, color, [p1, p2, p3], size)


def draw_rhombus(surface, color, start, end, size):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    points = [
        (cx,         start[1]),
        (end[0],     cy),
        (cx,         end[1]),
        (start[0],   cy),
    ]
    pygame.draw.polygon(surface, color, points, size)