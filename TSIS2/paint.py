"""
Paint Application  —  TSIS 2
Run: python paint.py
Requires: pygame  (pip install pygame)
"""

import pygame
import sys
from datetime import datetime
from tools import (
    flood_fill, draw_rect, draw_circle, draw_square,
    draw_line, draw_right_triangle, draw_equilateral_triangle, draw_rhombus
)

# ── Constants ──────────────────────────────────────────────────────────────

WIDTH, HEIGHT = 1100, 700
TOOLBAR_W     = 160
CANVAS_RECT   = pygame.Rect(TOOLBAR_W, 0, WIDTH - TOOLBAR_W, HEIGHT)

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (200, 200, 200)
DGRAY  = (150, 150, 150)
LGRAY  = (230, 230, 230)

COLORS = [
    (0,   0,   0),   (255, 255, 255), (255, 0,   0),   (0,   200, 0),
    (0,   0,   255), (255, 255, 0),   (255, 165, 0),   (128, 0,   128),
    (0,   200, 200), (165, 42,  42),  (255, 182, 193), (128, 128, 128),
]

TOOLS = [
    "pencil", "line", "rect", "circle",
    "square", "rtriangle", "etriangle", "rhombus",
    "fill", "eraser", "text",
]

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}


# ── Button helper ──────────────────────────────────────────────────────────

class Button:
    def __init__(self, rect, label, color=LGRAY, text_color=BLACK):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.color      = color
        self.text_color = text_color

    def draw(self, surf, font, active=False):
        bg = DGRAY if active else self.color
        pygame.draw.rect(surf, bg, self.rect, border_radius=4)
        pygame.draw.rect(surf, DGRAY, self.rect, 1, border_radius=4)
        txt = font.render(self.label, True, self.text_color)
        r   = txt.get_rect(center=self.rect.center)
        surf.blit(txt, r)

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ── Main app ───────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paint — TSIS 2")

    font_sm = pygame.font.SysFont("segoeui", 13)
    font_md = pygame.font.SysFont("segoeui", 15, bold=True)
    font_tx = pygame.font.SysFont("segoeui", 22)

    # Canvas (separate surface so we can save cleanly)
    canvas = pygame.Surface((WIDTH - TOOLBAR_W, HEIGHT))
    canvas.fill(WHITE)

    # State
    tool        = "pencil"
    color       = BLACK
    brush_level = 2                     # 1/2/3
    drawing     = False
    start_pos   = None
    prev_pos    = None
    preview_buf = None                  # snapshot before live preview

    # Text tool state
    text_mode   = False
    text_pos    = None
    text_buf    = ""

    # ── Build toolbar buttons ──────────────────────────────────────────────
    bw, bh, bx = 136, 28, 12
    tool_buttons = {}
    labels = {
        "pencil":    "Pencil",     "line":      "Line",
        "rect":      "Rectangle",  "circle":    "Circle",
        "square":    "Square",     "rtriangle": "Right Tri",
        "etriangle": "Equil Tri",  "rhombus":   "Rhombus",
        "fill":      "Fill",       "eraser":    "Eraser",
        "text":      "Text",
    }
    for i, t in enumerate(TOOLS):
        by = 10 + i * 34
        tool_buttons[t] = Button((bx, by, bw, bh), labels[t])

    # Brush size buttons
    size_buttons = {
        k: Button((bx + (k-1)*46, 400, 42, 26), f"{'S' if k==1 else 'M' if k==2 else 'L'} ({BRUSH_SIZES[k]})")
        for k in (1, 2, 3)
    }

    # Color palette
    color_buttons = []
    for i, c in enumerate(COLORS):
        row, col = divmod(i, 3)
        cb = Button((bx + col*44, 450 + row*44, 40, 40), "", color=c)
        color_buttons.append((c, cb))

    def canvas_pos(screen_pos):
        return (screen_pos[0] - TOOLBAR_W, screen_pos[1])

    def in_canvas(pos):
        return CANVAS_RECT.collidepoint(pos)

    def get_brush():
        return BRUSH_SIZES[brush_level]

    def draw_shape_on(surf, t, s, e):
        sz = get_brush() if t != "eraser" else 1
        c  = WHITE if t == "eraser" else color
        if   t in ("pencil", "eraser"):
            pygame.draw.line(surf, c, s, e, get_brush() if t == "pencil" else 20)
        elif t == "line":      draw_line(surf, c, s, e, sz)
        elif t == "rect":      draw_rect(surf, c, s, e, sz)
        elif t == "circle":    draw_circle(surf, c, s, e, sz)
        elif t == "square":    draw_square(surf, c, s, e, sz)
        elif t == "rtriangle": draw_right_triangle(surf, c, s, e, sz)
        elif t == "etriangle": draw_equilateral_triangle(surf, c, s, e, sz)
        elif t == "rhombus":   draw_rhombus(surf, c, s, e, sz)

    # ── Main loop ──────────────────────────────────────────────────────────
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():

            # ── Quit ──
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Key ──
            if event.type == pygame.KEYDOWN:

                # Text tool typing
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        txt_surf = font_tx.render(text_buf, True, color)
                        canvas.blit(txt_surf, text_pos)
                        text_mode = False
                        text_buf  = ""
                        text_pos  = None
                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_buf  = ""
                        text_pos  = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buf = text_buf[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buf += event.unicode
                    continue

                # Ctrl+S — save
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name = f"canvas_{ts}.png"
                    pygame.image.save(canvas, name)
                    pygame.display.set_caption(f"Saved: {name}")

                # Brush size 1/2/3
                if event.key == pygame.K_1: brush_level = 1
                if event.key == pygame.K_2: brush_level = 2
                if event.key == pygame.K_3: brush_level = 3

            # ── Mouse down ──
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # Toolbar clicks
                for t, btn in tool_buttons.items():
                    if btn.hit(pos):
                        tool      = t
                        text_mode = False
                        text_buf  = ""

                for k, btn in size_buttons.items():
                    if btn.hit(pos):
                        brush_level = k

                for c, btn in color_buttons:
                    if btn.hit(pos):
                        color = c

                # Canvas clicks
                if in_canvas(pos):
                    cp = canvas_pos(pos)

                    if tool == "fill":
                        flood_fill(canvas, cp[0], cp[1], color)

                    elif tool == "text":
                        text_mode = True
                        text_pos  = cp
                        text_buf  = ""

                    else:
                        drawing     = True
                        start_pos   = cp
                        prev_pos    = cp
                        preview_buf = canvas.copy()

            # ── Mouse move ──
            if event.type == pygame.MOUSEMOTION:
                if drawing and in_canvas(event.pos):
                    cp = canvas_pos(event.pos)

                    if tool in ("pencil", "eraser"):
                        draw_shape_on(canvas, tool, prev_pos, cp)
                        prev_pos = cp

                    else:
                        # Live preview: restore snapshot then draw ghost
                        canvas.blit(preview_buf, (0, 0))
                        draw_shape_on(canvas, tool, start_pos, cp)

            # ── Mouse up ──
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and in_canvas(event.pos):
                    cp = canvas_pos(event.pos)
                    if tool not in ("pencil", "eraser", "fill", "text"):
                        canvas.blit(preview_buf, (0, 0))
                        draw_shape_on(canvas, tool, start_pos, cp)
                drawing     = False
                start_pos   = None
                preview_buf = None

        # ── Draw UI ───────────────────────────────────────────────────────
        screen.fill(GRAY)

        # Toolbar background
        pygame.draw.rect(screen, LGRAY, (0, 0, TOOLBAR_W, HEIGHT))
        pygame.draw.line(screen, DGRAY, (TOOLBAR_W, 0), (TOOLBAR_W, HEIGHT), 2)

        # Tool buttons
        for t, btn in tool_buttons.items():
            btn.draw(screen, font_sm, active=(tool == t))

        # Brush size label
        lbl = font_sm.render("Brush size:", True, BLACK)
        screen.blit(lbl, (bx, 382))
        for k, btn in size_buttons.items():
            btn.draw(screen, font_sm, active=(brush_level == k))

        # Color palette label
        lbl2 = font_sm.render("Colors:", True, BLACK)
        screen.blit(lbl2, (bx, 435))
        for c, btn in color_buttons:
            btn.draw(screen, font_sm)
            if c == color:
                pygame.draw.rect(screen, BLACK, btn.rect, 3, border_radius=4)

        # Active color preview
        pygame.draw.rect(screen, color, (bx, 630, bw, 30), border_radius=4)
        pygame.draw.rect(screen, BLACK, (bx, 630, bw, 30), 2, border_radius=4)

        # Canvas
        screen.blit(canvas, (TOOLBAR_W, 0))

        # Text cursor preview
        if text_mode and text_pos:
            preview = font_tx.render(text_buf + "|", True, color)
            screen.blit(preview, (text_pos[0] + TOOLBAR_W, text_pos[1]))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()