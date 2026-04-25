import pygame
import sys
import datetime  # для получения текущего времени

pygame.init()  # запуск pygame

WIDTH, HEIGHT = 600, 600  # размеры окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # создаём окно
pygame.display.set_caption("Mickey Clock")  # название окна

clock = pygame.time.Clock()  # контроль FPS

# загружаем изображение стрелки
hand = pygame.image.load("images/mickey_hand.png").convert_alpha()

center = (WIDTH // 2, HEIGHT // 2)  # центр экрана

def draw_hand(image, angle, center, flip=False):
    img = pygame.transform.flip(image, flip, False)  # отражаем (для левой руки)
    rotated = pygame.transform.rotate(img, -angle)  # поворот изображения
    rect = rotated.get_rect(center=center)  # центрируем
    screen.blit(rotated, rect)  # рисуем на экране

while True:
    for event in pygame.event.get():  # обработка событий
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))  # очистка экрана (белый фон)

    now = datetime.datetime.now()  # текущее время
    seconds = now.second  # секунды
    minutes = now.minute  # минуты

    sec_angle = seconds * 6  # угол секунд (360/60)
    min_angle = minutes * 6  # угол минут

    draw_hand(hand, sec_angle, center, flip=True)   # левая рука = секунды
    draw_hand(hand, min_angle, center, flip=False)  # правая рука = минуты

    pygame.display.flip()  # обновление экрана
    clock.tick(1)  # обновление 1 раз в секунду