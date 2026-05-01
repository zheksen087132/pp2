

import pygame
import sys

from persistence import load_settings, load_leaderboard, save_score
from ui          import main_menu, settings_screen, leaderboard_screen, game_over_screen
from racer       import run_game


def build_fonts():
    return {
        "sm":  pygame.font.SysFont("segoeui", 16),
        "med": pygame.font.SysFont("segoeui", 22, bold=True),
        "big": pygame.font.SysFont("segoeui", 48, bold=True),
    }


def main():
    pygame.init()
    screen   = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Racer — TSIS 3")
    clock    = pygame.time.Clock()
    fonts    = build_fonts()
    settings = load_settings()

    player_name = "Player"

    while True:
        action, player_name = main_menu(screen, clock, fonts, settings)

        if action == "quit":
            break

        elif action == "settings":
            settings = settings_screen(screen, clock, fonts, settings)

        elif action == "leaderboard":
            lb = load_leaderboard()
            leaderboard_screen(screen, clock, fonts, lb)

        elif action == "play":
            while True:
                score, distance, coins, result = run_game(
                    screen, clock, fonts, settings, player_name
                )

                if result == "quit":
                    pygame.quit()
                    sys.exit()

                if result in ("gameover", "menu"):
                    # Save score
                    lb = save_score(player_name, score, distance, coins)

                    if result == "gameover":
                        choice = game_over_screen(
                            screen, clock, fonts, score, distance, coins
                        )
                        if choice == "retry":
                            continue
                        elif choice == "quit":
                            pygame.quit()
                            sys.exit()
                        else:
                            break   # back to main menu
                    else:
                        break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
