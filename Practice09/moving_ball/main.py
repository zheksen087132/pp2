import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # окно
pygame.display.set_caption("Moving Ball")

x, y = WIDTH // 2, HEIGHT // 2  # начальная позиция шара
RADIUS = 25  # радиус шара
STEP = 20  # шаг движения

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():  # обработка событий
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:  # движение по кнопкам
            if event.key == pygame.K_UP:
                if y - STEP - RADIUS >= 0:  # проверка границы сверху
                    y -= STEP

            elif event.key == pygame.K_DOWN:
                if y + STEP + RADIUS <= HEIGHT:  # снизу
                    y += STEP

            elif event.key == pygame.K_LEFT:
                if x - STEP - RADIUS >= 0:  # слева
                    x -= STEP

            elif event.key == pygame.K_RIGHT:
                if x + STEP + RADIUS <= WIDTH:  # справа
                    x += STEP

    screen.fill((255, 255, 255))  # очистка экрана
    pygame.draw.circle(screen, (255, 0, 0), (x, y), RADIUS)  # рисуем шар

    pygame.display.flip()  # обновление экрана
    clock.tick(60)  # 60 FPS