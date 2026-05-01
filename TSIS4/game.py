import pygame
import random
import json
import sys
from db import save_session, get_personal_best

WIDTH = 600
HEIGHT = 600
CELL = 20
FPS_BASE = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 0, 0)
DARK_RED = (120, 0, 0)
YELLOW = (240, 220, 0)
BLUE = (0, 120, 255)
PURPLE = (160, 60, 220)
CYAN = (0, 220, 220)
GRAY = (80, 80, 80)


def load_settings():
    with open("settings.json", "r") as file:
        return json.load(file)


def save_settings(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)


class SnakeGame:
    def __init__(self, screen, username):
        self.screen = screen
        self.username = username
        self.settings = load_settings()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 18)
        self.big_font = pygame.font.SysFont("Verdana", 48)

        self.snake_color = tuple(self.settings["snake_color"])
        self.grid = self.settings["grid"]

        self.snake = [(300, 300), (280, 300), (260, 300)]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"

        self.score = 0
        self.level = 1
        self.speed = FPS_BASE
        self.personal_best = get_personal_best(username)

        self.food = None
        self.poison = None
        self.powerup = None
        self.powerup_spawn_time = 0

        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield = False

        self.obstacles = []

        self.food_lifetime = 5000
        self.food_spawn_time = 0
        self.poison_spawn_time = 0

        self.spawn_food()
        self.spawn_poison()

        self.running = True

    def random_cell(self):
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        return (x, y)

    def occupied(self, pos):
        return (
            pos in self.snake or
            pos in self.obstacles or
            self.food and pos == self.food["pos"] or
            self.poison and pos == self.poison["pos"] or
            self.powerup and pos == self.powerup["pos"]
        )

    def safe_random_cell(self):
        while True:
            pos = self.random_cell()
            if not self.occupied(pos):
                return pos

    def spawn_food(self):
        self.food = {
            "pos": self.safe_random_cell(),
            "weight": random.choice([1, 2, 3])
        }
        self.food_spawn_time = pygame.time.get_ticks()

    def spawn_poison(self):
        self.poison = {
            "pos": self.safe_random_cell()
        }
        self.poison_spawn_time = pygame.time.get_ticks()

    def spawn_powerup(self):
        if self.powerup is not None:
            return

        self.powerup = {
            "pos": self.safe_random_cell(),
            "type": random.choice(["speed", "slow", "shield"])
        }
        self.powerup_spawn_time = pygame.time.get_ticks()

    def generate_obstacles(self):
        self.obstacles = []

        if self.level < 3:
            return

        count = min(5 + self.level, 20)

        while len(self.obstacles) < count:
            pos = self.random_cell()

            head = self.snake[0]

            if pos in self.snake:
                continue
            if abs(pos[0] - head[0]) <= CELL and abs(pos[1] - head[1]) <= CELL:
                continue
            if pos in self.obstacles:
                continue

            self.obstacles.append(pos)

    def change_direction(self):
        if self.next_direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif self.next_direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"
        elif self.next_direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif self.next_direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"

    def move_snake(self):
        x, y = self.snake[0]

        if self.direction == "UP":
            y -= CELL
        elif self.direction == "DOWN":
            y += CELL
        elif self.direction == "LEFT":
            x -= CELL
        elif self.direction == "RIGHT":
            x += CELL

        self.snake.insert(0, (x, y))

    def check_collision(self):
        head = self.snake[0]

        hit_wall = (
            head[0] < 0 or head[0] >= WIDTH or
            head[1] < 0 or head[1] >= HEIGHT
        )

        hit_self = head in self.snake[1:]
        hit_obstacle = head in self.obstacles

        if hit_wall or hit_self or hit_obstacle:
            if self.shield:
                self.shield = False
                self.active_powerup = None

                if hit_wall:
                    self.snake[0] = (300, 300)

                return False

            return True

        return False

    def eat_food(self):
        head = self.snake[0]

        if self.food and head == self.food["pos"]:
            weight = self.food["weight"]
            self.score += weight

            for i in range(weight - 1):
                self.snake.append(self.snake[-1])

            old_level = self.level
            self.level = self.score // 5 + 1

            if self.level > old_level:
                self.speed += 2
                self.generate_obstacles()

            self.spawn_food()
            return True

        return False

    def eat_poison(self):
        head = self.snake[0]

        if self.poison and head == self.poison["pos"]:
            for i in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()

            self.spawn_poison()

            if len(self.snake) <= 1:
                return True

        return False

    def collect_powerup(self):
        head = self.snake[0]

        if self.powerup and head == self.powerup["pos"]:
            ptype = self.powerup["type"]
            now = pygame.time.get_ticks()

            self.active_powerup = ptype
            self.powerup = None

            if ptype == "speed":
                self.powerup_end_time = now + 5000
            elif ptype == "slow":
                self.powerup_end_time = now + 5000
            elif ptype == "shield":
                self.shield = True

    def update_powerups(self):
        now = pygame.time.get_ticks()

        if self.active_powerup == "speed":
            if now > self.powerup_end_time:
                self.active_powerup = None

        elif self.active_powerup == "slow":
            if now > self.powerup_end_time:
                self.active_powerup = None

        if self.powerup is None and random.randint(1, 250) == 1:
            self.spawn_powerup()

        if self.powerup and now - self.powerup_spawn_time > 8000:
            self.powerup = None

    def current_speed(self):
        if self.active_powerup == "speed":
            return self.speed + 5
        if self.active_powerup == "slow":
            return max(4, self.speed - 5)
        return self.speed

    def update_timers(self):
        now = pygame.time.get_ticks()

        if now - self.food_spawn_time > self.food_lifetime:
            self.spawn_food()

        if now - self.poison_spawn_time > 7000:
            self.spawn_poison()

    def draw_grid(self):
        if not self.grid:
            return

        for x in range(0, WIDTH, CELL):
            pygame.draw.line(self.screen, (30, 30, 30), (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(self.screen, (30, 30, 30), (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()

        for block in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, (block[0], block[1], CELL, CELL))

        for block in self.snake:
            pygame.draw.rect(self.screen, self.snake_color, (block[0], block[1], CELL, CELL))

        if self.food:
            if self.food["weight"] == 1:
                color = RED
            elif self.food["weight"] == 2:
                color = YELLOW
            else:
                color = BLUE

            pygame.draw.rect(self.screen, color, (self.food["pos"][0], self.food["pos"][1], CELL, CELL))

        if self.poison:
            pygame.draw.rect(self.screen, DARK_RED, (self.poison["pos"][0], self.poison["pos"][1], CELL, CELL))

        if self.powerup:
            if self.powerup["type"] == "speed":
                color = PURPLE
            elif self.powerup["type"] == "slow":
                color = CYAN
            else:
                color = WHITE

            pygame.draw.rect(self.screen, color, (self.powerup["pos"][0], self.powerup["pos"][1], CELL, CELL))

        texts = [
            "User: " + self.username,
            "Score: " + str(self.score),
            "Level: " + str(self.level),
            "Best: " + str(self.personal_best),
            "Power: " + str(self.active_powerup if self.active_powerup else "none")
        ]

        y = 5
        for text in texts:
            img = self.font.render(text, True, WHITE)
            self.screen.blit(img, (5, y))
            y += 22

        pygame.display.update()

    def finish(self):
        save_session(self.username, self.score, self.level)
        return self.score, self.level, self.personal_best

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_session(self.username, self.score, self.level)
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.next_direction = "UP"
                    elif event.key == pygame.K_DOWN:
                        self.next_direction = "DOWN"
                    elif event.key == pygame.K_LEFT:
                        self.next_direction = "LEFT"
                    elif event.key == pygame.K_RIGHT:
                        self.next_direction = "RIGHT"

            self.change_direction()
            self.move_snake()

            if self.check_collision():
                self.running = False

            ate_food = self.eat_food()

            if self.eat_poison():
                self.running = False

            self.collect_powerup()
            self.update_powerups()
            self.update_timers()

            if not ate_food:
                self.snake.pop()

            self.draw()
            self.clock.tick(self.current_speed())

        return self.finish()