"""
ui.py  —  Reusable UI helpers for Racer TSIS 3
"""

import pygame

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (80,  80,  80)
LGRAY  = (180, 180, 180)
DGRAY  = (40,  40,  40)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
BLUE   = (50,  120, 220)
YELLOW = (240, 200, 40)
ORANGE = (240, 140, 30)


class Button:
    def __init__(self, rect, text, color=GRAY, hover=LGRAY, text_color=WHITE):
        self.rect       = pygame.Rect(rect)
        self.text       = text
        self.color      = color
        self.hover      = hover
        self.text_color = text_color

    def draw(self, surf, font):
        mx, my = pygame.mouse.get_pos()
        bg = self.hover if self.rect.collidepoint(mx, my) else self.color
        pygame.draw.rect(surf, bg, self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, self.text_color)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


def draw_text(surf, text, font, color, cx, cy):
    t = font.render(text, True, color)
    surf.blit(t, t.get_rect(center=(cx, cy)))


def draw_background(surf):
    surf.fill((20, 20, 30))


# ── Main Menu ─────────────────────────────────────────────────────────────

def main_menu(screen, clock, fonts, settings):
    W, H   = screen.get_size()
    title  = fonts["big"]
    btn_f  = fonts["med"]

    buttons = {
        "play":        Button((W//2-110, 220, 220, 50), "Play",        GREEN),
        "leaderboard": Button((W//2-110, 290, 220, 50), "Leaderboard", BLUE),
        "settings":    Button((W//2-110, 360, 220, 50), "Settings",    ORANGE),
        "quit":        Button((W//2-110, 430, 220, 50), "Quit",        RED),
    }

    name_buf   = ""
    name_done  = False
    name_input = True

    while True:
        draw_background(screen)
        draw_text(screen, "RACER", title, YELLOW, W//2, 100)
        draw_text(screen, "TSIS 3", fonts["sm"], LGRAY, W//2, 145)

        if name_input:
            draw_text(screen, "Enter your name:", fonts["med"], WHITE, W//2, 185)
            pygame.draw.rect(screen, DGRAY, (W//2-110, 200, 220, 36), border_radius=6)
            pygame.draw.rect(screen, LGRAY, (W//2-110, 200, 220, 36), 2, border_radius=6)
            nt = fonts["med"].render(name_buf + "|", True, WHITE)
            screen.blit(nt, nt.get_rect(center=(W//2, 218)))
        else:
            draw_text(screen, f"Hello, {name_buf}!", fonts["med"], GREEN, W//2, 185)
            for btn in buttons.values():
                btn.draw(screen, btn_f)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", name_buf

            if name_input and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name_buf.strip():
                    name_input = False
                elif event.key == pygame.K_BACKSPACE:
                    name_buf = name_buf[:-1]
                elif event.unicode and event.unicode.isprintable() and len(name_buf) < 16:
                    name_buf += event.unicode

            if not name_input:
                for key, btn in buttons.items():
                    if btn.clicked(event):
                        return key, name_buf.strip()


# ── Settings Screen ───────────────────────────────────────────────────────

def settings_screen(screen, clock, fonts, settings):
    W, H  = screen.get_size()
    btn_f = fonts["med"]

    CAR_COLORS  = ["red", "blue", "green", "yellow", "white"]
    DIFFICULTIES = ["easy", "normal", "hard"]

    back = Button((W//2-80, H-80, 160, 45), "Back", GRAY)

    while True:
        draw_background(screen)
        draw_text(screen, "Settings", fonts["big"], YELLOW, W//2, 70)

        # Sound toggle
        s_color = GREEN if settings["sound"] else RED
        s_label = "Sound: ON" if settings["sound"] else "Sound: OFF"
        sound_btn = Button((W//2-110, 160, 220, 45), s_label, s_color)
        sound_btn.draw(screen, btn_f)

        # Car color
        draw_text(screen, "Car Color:", fonts["sm"], LGRAY, W//2, 235)
        for i, c in enumerate(CAR_COLORS):
            x = W//2 - 120 + i * 52
            active = (settings["car_color"] == c)
            pygame.draw.rect(screen, _car_rgb(c), (x, 248, 42, 28), border_radius=5)
            if active:
                pygame.draw.rect(screen, WHITE, (x, 248, 42, 28), 3, border_radius=5)

        # Difficulty
        draw_text(screen, "Difficulty:", fonts["sm"], LGRAY, W//2, 305)
        for i, d in enumerate(DIFFICULTIES):
            x = W//2 - 110 + i * 76
            active = (settings["difficulty"] == d)
            col = GREEN if active else GRAY
            db  = Button((x, 318, 68, 30), d.capitalize(), col)
            db.draw(screen, fonts["sm"])

        back.draw(screen, btn_f)
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings
            if sound_btn.clicked(event):
                settings["sound"] = not settings["sound"]
            if back.clicked(event):
                from persistence import save_settings
                save_settings(settings)
                return settings

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Car color pick
                for i, c in enumerate(CAR_COLORS):
                    x = W//2 - 120 + i * 52
                    if pygame.Rect(x, 248, 42, 28).collidepoint(mx, my):
                        settings["car_color"] = c
                # Difficulty pick
                for i, d in enumerate(DIFFICULTIES):
                    x = W//2 - 110 + i * 76
                    if pygame.Rect(x, 318, 68, 30).collidepoint(mx, my):
                        settings["difficulty"] = d


def _car_rgb(name):
    return {
        "red":    (220, 50,  50),
        "blue":   (50,  100, 220),
        "green":  (50,  180, 80),
        "yellow": (230, 200, 30),
        "white":  (230, 230, 230),
    }.get(name, (200, 200, 200))


# ── Leaderboard Screen ────────────────────────────────────────────────────

def leaderboard_screen(screen, clock, fonts, lb):
    W, H = screen.get_size()
    back = Button((W//2-80, H-70, 160, 45), "Back", GRAY)

    while True:
        draw_background(screen)
        draw_text(screen, "Leaderboard", fonts["big"], YELLOW, W//2, 60)

        headers = f"{'#':<4} {'Name':<16} {'Score':>8}  {'Dist':>6}  {'Coins':>5}"
        draw_text(screen, headers, fonts["sm"], LGRAY, W//2, 110)
        pygame.draw.line(screen, LGRAY, (W//2-220, 125), (W//2+220, 125), 1)

        for i, entry in enumerate(lb[:10]):
            color = YELLOW if i == 0 else WHITE
            row = (f"{i+1:<4} {entry['name']:<16} {entry['score']:>8}"
                   f"  {int(entry['distance']):>5}m  {entry['coins']:>5}")
            draw_text(screen, row, fonts["sm"], color, W//2, 145 + i * 28)

        back.draw(screen, fonts["med"])
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if back.clicked(event):
                return


# ── Game Over Screen ──────────────────────────────────────────────────────

def game_over_screen(screen, clock, fonts, score, distance, coins):
    W, H = screen.get_size()
    retry = Button((W//2-120, 380, 220, 50), "Retry",     GREEN)
    menu  = Button((W//2-120, 445, 220, 50), "Main Menu", BLUE)

    while True:
        draw_background(screen)
        draw_text(screen, "GAME OVER",  fonts["big"], RED,   W//2, 120)
        draw_text(screen, f"Score:    {score}",       fonts["med"], WHITE,  W//2, 220)
        draw_text(screen, f"Distance: {int(distance)} m", fonts["med"], WHITE, W//2, 260)
        draw_text(screen, f"Coins:    {coins}",       fonts["med"], WHITE,  W//2, 300)

        retry.draw(screen, fonts["med"])
        menu.draw(screen,  fonts["med"])
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"
