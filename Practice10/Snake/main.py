import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

snake = [[100,100]]
direction = "RIGHT"

food = [200, 200]

score = 0
level = 1
speed = 10

font = pygame.font.SysFont("Arial", 25)

def new_food():
    while True:
        x = random.randrange(0, WIDTH, 20)
        y = random.randrange(0, HEIGHT, 20)
        if [x,y] not in snake:
            return [x,y]

running = True

while running:
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        direction = "LEFT"
    if keys[pygame.K_RIGHT]:
        direction = "RIGHT"
    if keys[pygame.K_UP]:
        direction = "UP"
    if keys[pygame.K_DOWN]:
        direction = "DOWN"

    head = snake[0].copy()

    if direction == "LEFT":
        head[0] -= 20
    if direction == "RIGHT":
        head[0] += 20
    if direction == "UP":
        head[1] -= 20
    if direction == "DOWN":
        head[1] += 20

    snake.insert(0, head)

    if head == food:
        score += 1
        food = new_food()
    else:
        snake.pop()

    if score > 0 and score % 4 == 0:
        level = score // 4 + 1
        speed = 10 + level * 2

    for s in snake:
        pygame.draw.rect(screen, (0,255,0), (*s,20,20))

    pygame.draw.rect(screen, (255,0,0), (*food,20,20))

    text = font.render(f"Score:{score} Level:{level}", True, (255,255,255))
    screen.blit(text, (10,10))

    pygame.display.update()
    clock.tick(speed)