import pygame
import sys

pygame.init()
pygame.mixer.init()  # модуль для музыки

screen = pygame.display.set_mode((500, 200))  # окно
pygame.display.set_caption("Music Player")

tracks = [
    "music/track1.wav",  # список треков
    "music/track2.wav"
]

current = 0  # текущий трек

def play_track(index):
    pygame.mixer.music.load(tracks[index])  # загрузка трека
    pygame.mixer.music.play()  # воспроизведение

font = pygame.font.Font(None, 36)  # шрифт

running = True
while running:
    screen.fill((30, 30, 30))  # фон

    # отображаем номер текущего трека
    text = font.render(f"Track: {current + 1}", True, (255, 255, 255))
    screen.blit(text, (180, 80))

    for event in pygame.event.get():  # обработка событий
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:  # нажатие клавиш
            if event.key == pygame.K_p:
                play_track(current)  # воспроизвести

            elif event.key == pygame.K_s:
                pygame.mixer.music.stop()  # остановить

            elif event.key == pygame.K_n:
                current = (current + 1) % len(tracks)  # следующий трек
                play_track(current)

            elif event.key == pygame.K_b:
                current = (current - 1) % len(tracks)  # предыдущий
                play_track(current)

            elif event.key == pygame.K_q:
                running = False  # выход

    pygame.display.flip()  # обновление

pygame.quit()
sys.exit()