import pygame
import sys
import json

from game import SnakeGame, save_settings, load_settings
from db import get_top_scores

pygame.init()

WIDTH = 600
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
GREEN = (0, 200, 0)
RED = (220, 0, 0)
YELLOW = (240, 220, 0)
BLUE = (0, 120, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake")

font = pygame.font.SysFont("Verdana", 22)
small_font = pygame.font.SysFont("Verdana", 16)
big_font = pygame.font.SysFont("Verdana", 44)


def draw_text(text, x, y, color=WHITE, f=font):
    img = f.render(text, True, color)
    screen.blit(img, (x, y))


def draw_button(text, rect):
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    draw_text(text, rect.x + 20, rect.y + 12, WHITE, font)


def username_screen():
    username = ""

    while True:
        screen.fill(BLACK)

        draw_text("Enter username:", 140, 200, WHITE, font)
        draw_text(username + "|", 140, 245, YELLOW, font)
        draw_text("Press Enter to continue", 140, 310, WHITE, small_font)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username != "":
                    return username

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    if len(username) < 15:
                        username += event.unicode


def leaderboard_screen():
    try:
        rows = get_top_scores()
    except Exception as e:
        rows = []
        error = str(e)
    else:
        error = None

    while True:
        screen.fill(BLACK)

        draw_text("Leaderboard Top 10", 110, 40, YELLOW, font)

        if error:
            draw_text("Database error:", 50, 120, RED, small_font)
            draw_text(error[:60], 50, 150, RED, small_font)
        else:
            y = 100
            for i, row in enumerate(rows):
                username, score, level, played_at = row

                line = (
                    str(i + 1) + ". " +
                    username +
                    " | Score: " + str(score) +
                    " | Level: " + str(level)
                )

                draw_text(line, 30, y, WHITE, small_font)
                y += 30

        draw_text("ESC - Back", 230, 540, WHITE, small_font)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return


def settings_screen():
    settings = load_settings()

    colors = [
        [0, 200, 0],
        [0, 120, 255],
        [240, 220, 0],
        [220, 0, 0]
    ]

    while True:
        screen.fill(BLACK)

        draw_text("Settings", 185, 60, YELLOW, big_font)

        draw_text("1. Grid: " + str(settings["grid"]), 120, 170, WHITE, font)
        draw_text("2. Sound: " + str(settings["sound"]), 120, 220, WHITE, font)
        draw_text("3. Snake color", 120, 270, WHITE, font)

        pygame.draw.rect(screen, tuple(settings["snake_color"]), (330, 270, 35, 35))

        draw_text("Press 1/2/3 to change", 120, 350, WHITE, small_font)
        draw_text("ESC - Save and Back", 120, 380, WHITE, small_font)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return

                if event.key == pygame.K_1:
                    settings["grid"] = not settings["grid"]

                elif event.key == pygame.K_2:
                    settings["sound"] = not settings["sound"]

                elif event.key == pygame.K_3:
                    current = settings["snake_color"]

                    index = 0
                    for i in range(len(colors)):
                        if colors[i] == current:
                            index = i
                            break

                    settings["snake_color"] = colors[(index + 1) % len(colors)]


def game_over_screen(score, level, personal_best):
    retry_btn = pygame.Rect(180, 330, 240, 50)
    menu_btn = pygame.Rect(180, 400, 240, 50)

    while True:
        screen.fill(BLACK)

        draw_text("GAME OVER", 150, 100, RED, big_font)

        draw_text("Final score: " + str(score), 170, 190, WHITE, font)
        draw_text("Level reached: " + str(level), 170, 230, WHITE, font)
        draw_text("Personal best: " + str(max(score, personal_best)), 170, 270, WHITE, font)

        draw_button("Retry", retry_btn)
        draw_button("Main Menu", menu_btn)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"

                if menu_btn.collidepoint(event.pos):
                    return "menu"


def main_menu():
    username = username_screen()

    play_btn = pygame.Rect(190, 180, 220, 50)
    board_btn = pygame.Rect(190, 250, 220, 50)
    settings_btn = pygame.Rect(190, 320, 220, 50)
    quit_btn = pygame.Rect(190, 390, 220, 50)

    while True:
        screen.fill(BLACK)

        draw_text("TSIS4 SNAKE", 145, 70, YELLOW, big_font)
        draw_text("Player: " + username, 190, 130, WHITE, small_font)

        draw_button("Play", play_btn)
        draw_button("Leaderboard", board_btn)
        draw_button("Settings", settings_btn)
        draw_button("Quit", quit_btn)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    while True:
                        game = SnakeGame(screen, username)
                        score, level, personal_best = game.run()

                        choice = game_over_screen(score, level, personal_best)

                        if choice == "retry":
                            continue

                        if choice == "menu":
                            break

                elif board_btn.collidepoint(event.pos):
                    leaderboard_screen()

                elif settings_btn.collidepoint(event.pos):
                    settings_screen()

                elif quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


main_menu()