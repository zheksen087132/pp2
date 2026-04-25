import pygame
import datetime

pygame.init()

# размер окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

# загрузка изображений
background = pygame.image.load("practice9new/mickeyclock.jpeg").convert()
right_hand = pygame.image.load("practice9new/rightarm.png").convert_alpha()
left_hand = pygame.image.load("practice9new/leftarm.png").convert_alpha()

# масштабирование
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
right_hand = pygame.transform.scale(right_hand, (250, 250))
left_hand = pygame.transform.scale(left_hand, (250, 250))

# центр часов
center = (WIDTH // 2, HEIGHT // 2)


def rotate(image, angle, center):
    rotated = pygame.transform.rotate(image, angle)
    rect = rotated.get_rect(center=center)
    return rotated, rect


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # текущее время
    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second

    # углы (360/60 = 6 градусов)
    minute_angle = -minutes * 6
    second_angle = -seconds * 6

    # фон
    screen.blit(background, (0, 0))

    # вращение
    right_rot, right_rect = rotate(right_hand, minute_angle, center)
    left_rot, left_rect = rotate(left_hand, second_angle, center)

    # рисуем
    screen.blit(right_rot, right_rect)
    screen.blit(left_rot, left_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()