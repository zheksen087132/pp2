

import pygame
import random
import time

# ── Colours ───────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (100, 100, 100)
LGRAY  = (180, 180, 180)
DGRAY  = (40,  40,  40)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
BLUE   = (50,  120, 220)
YELLOW = (240, 200, 40)
ORANGE = (240, 140, 30)
PURPLE = (160, 60,  200)
CYAN   = (40,  200, 220)
BROWN  = (140, 80,  20)

ROAD_COLOR  = (60,  60,  60)
LINE_COLOR  = (220, 220, 60)
GRASS_COLOR = (30,  120, 40)

CAR_COLORS = {
    "red":    (220, 50,  50),
    "blue":   (50,  100, 220),
    "green":  (50,  180, 80),
    "yellow": (230, 200, 30),
    "white":  (230, 230, 230),
}

DIFFICULTY = {
    "easy":   {"traffic_rate": 0.008, "obstacle_rate": 0.005, "speed": 4},
    "normal": {"traffic_rate": 0.015, "obstacle_rate": 0.010, "speed": 5},
    "hard":   {"traffic_rate": 0.025, "obstacle_rate": 0.018, "speed": 7},
}

W, H       = 800, 600
ROAD_LEFT  = 150
ROAD_RIGHT = 650
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANES      = 4
LANE_W     = ROAD_W // LANES

FINISH_DIST = 3000   # metres to finish


# ── Helpers ───────────────────────────────────────────────────────────────

def lane_x(lane):
    """Centre x of lane (0-indexed)."""
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2


def rand_lane():
    return random.randint(0, LANES - 1)


def draw_car(surf, color, cx, cy, w=36, h=60):
    body = pygame.Rect(cx - w//2, cy - h//2, w, h)
    pygame.draw.rect(surf, color, body, border_radius=6)
    # windows
    pygame.draw.rect(surf, CYAN, (cx-10, cy-20, 20, 14), border_radius=3)
    # wheels
    for wx, wy in [(-w//2-4, -h//4), (w//2, -h//4),
                   (-w//2-4,  h//4), (w//2,  h//4)]:
        pygame.draw.rect(surf, BLACK, (cx+wx, cy+wy, 8, 14), border_radius=2)


def draw_obstacle(surf, kind, cx, cy):
    if kind == "oil":
        pygame.draw.ellipse(surf, (20, 20, 80), (cx-22, cy-10, 44, 20))
        pygame.draw.ellipse(surf, (40, 40, 160), (cx-18, cy-7, 36, 14))
    elif kind == "barrier":
        pygame.draw.rect(surf, ORANGE, (cx-24, cy-10, 48, 20), border_radius=4)
        pygame.draw.rect(surf, WHITE,  (cx-24, cy-10, 48, 20), 2, border_radius=4)
    elif kind == "pothole":
        pygame.draw.ellipse(surf, DGRAY, (cx-18, cy-10, 36, 20))
        pygame.draw.ellipse(surf, BLACK, (cx-14, cy-7,  28, 14))
    elif kind == "nitro_strip":
        pygame.draw.rect(surf, YELLOW, (cx-20, cy-6, 40, 12), border_radius=3)
        draw_text_small(surf, "NITRO", (cx, cy), BLACK)


def draw_powerup(surf, kind, cx, cy):
    colors = {"nitro": YELLOW, "shield": CYAN, "repair": GREEN}
    col = colors.get(kind, WHITE)
    pygame.draw.circle(surf, col, (cx, cy), 16)
    pygame.draw.circle(surf, WHITE, (cx, cy), 16, 2)
    labels = {"nitro": "N", "shield": "S", "repair": "R"}
    fnt = pygame.font.SysFont("segoeui", 14, bold=True)
    t = fnt.render(labels.get(kind, "?"), True, BLACK)
    surf.blit(t, t.get_rect(center=(cx, cy)))


def draw_coin(surf, cx, cy, value):
    col = {1: YELLOW, 3: ORANGE, 5: PURPLE}.get(value, YELLOW)
    pygame.draw.circle(surf, col, (cx, cy), 12)
    pygame.draw.circle(surf, WHITE, (cx, cy), 12, 2)
    fnt = pygame.font.SysFont("segoeui", 11, bold=True)
    t = fnt.render(str(value), True, WHITE)
    surf.blit(t, t.get_rect(center=(cx, cy)))


def draw_text_small(surf, text, pos, color=WHITE):
    fnt = pygame.font.SysFont("segoeui", 12)
    t = fnt.render(text, True, color)
    surf.blit(t, t.get_rect(center=pos))


# ── Game ──────────────────────────────────────────────────────────────────

def run_game(screen, clock, fonts, settings, player_name):
    diff   = DIFFICULTY[settings.get("difficulty", "normal")]
    car_c  = CAR_COLORS.get(settings.get("car_color", "red"), RED)

    # Player
    player_lane = 1
    player_x    = float(lane_x(player_lane))
    player_y    = H - 100
    base_speed  = diff["speed"]
    speed       = float(base_speed)

    # Road scroll
    road_offset = 0

    # Game state
    score    = 0
    coins    = 0
    distance = 0.0
    alive    = True

    # Objects  [{lane, y, ...extra}]
    traffic   = []
    obstacles = []
    powerups  = []
    coin_list = []

    # Power-up state
    active_pu    = None
    pu_end_time  = 0
    shield_on    = False

    # Nitro strip event
    nitro_strips = []

    frame = 0

    def spawn_traffic():
        lane = rand_lane()
        # don't spawn on player
        if lane == player_lane and abs(0 - player_y) < 120:
            lane = (lane + 1) % LANES
        enemy_colors = [RED, BLUE, LGRAY, ORANGE, PURPLE]
        traffic.append({"lane": lane, "y": -60,
                        "color": random.choice(enemy_colors)})

    def spawn_obstacle():
        kind = random.choice(["oil", "barrier", "pothole"])
        lane = rand_lane()
        obstacles.append({"lane": lane, "y": -40, "kind": kind})

    def spawn_powerup():
        kind = random.choice(["nitro", "shield", "repair"])
        lane = rand_lane()
        powerups.append({"lane": lane, "y": -40, "kind": kind,
                         "born": time.time()})

    def spawn_coin():
        value = random.choices([1, 3, 5], weights=[6, 3, 1])[0]
        lane  = rand_lane()
        coin_list.append({"lane": lane, "y": -30, "value": value})

    def spawn_nitro_strip():
        lane = rand_lane()
        nitro_strips.append({"lane": lane, "y": -20})

    def activate_powerup(kind):
        nonlocal active_pu, pu_end_time, shield_on, speed
        active_pu = kind
        if kind == "nitro":
            speed     = base_speed * 2.2
            pu_end_time = time.time() + 4
        elif kind == "shield":
            shield_on   = True
            pu_end_time = time.time() + 999   # until hit
        elif kind == "repair":
            active_pu = None   # instant

    def check_powerup_expiry():
        nonlocal active_pu, speed, shield_on
        if active_pu == "nitro" and time.time() > pu_end_time:
            speed     = base_speed
            active_pu = None
        # shield expires on hit (handled in collision)

    fnt_sm  = fonts["sm"]
    fnt_med = fonts["med"]
    fnt_big = fonts["big"]

    while alive:
        dt = clock.tick(60) / 1000.0
        frame += 1

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, distance, coins, "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player_lane = max(0, player_lane - 1)
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player_lane = min(LANES - 1, player_lane + 1)
                if event.key == pygame.K_ESCAPE:
                    return score, distance, coins, "menu"

        # Smooth lane follow
        target_x = float(lane_x(player_lane))
        player_x += (target_x - player_x) * 0.18

        # ── Difficulty scaling ────────────────────────────────────────────
        level = int(distance // 300)
        t_rate = min(diff["traffic_rate"]  + level * 0.003, 0.08)
        o_rate = min(diff["obstacle_rate"] + level * 0.002, 0.05)
        if active_pu != "nitro":
            speed = base_speed + level * 0.3

        # ── Spawning ──────────────────────────────────────────────────────
        if random.random() < t_rate:       spawn_traffic()
        if random.random() < o_rate:       spawn_obstacle()
        if random.random() < 0.004:        spawn_powerup()
        if random.random() < 0.018:        spawn_coin()
        if random.random() < 0.003:        spawn_nitro_strip()

        # ── Move everything ───────────────────────────────────────────────
        road_offset = (road_offset + speed) % 60
        distance   += speed * dt * 10

        for obj in traffic:       obj["y"] += speed * 1.3
        for obj in obstacles:     obj["y"] += speed
        for obj in powerups:      obj["y"] += speed * 0.8
        for obj in coin_list:     obj["y"] += speed
        for obj in nitro_strips:  obj["y"] += speed

        # Remove off-screen
        traffic      = [o for o in traffic      if o["y"] < H + 80]
        obstacles    = [o for o in obstacles    if o["y"] < H + 60]
        powerups     = [o for o in powerups     if o["y"] < H + 60
                        and time.time() - o["born"] < 8]
        coin_list    = [o for o in coin_list    if o["y"] < H + 40]
        nitro_strips = [o for o in nitro_strips if o["y"] < H + 30]

        # ── Collisions ────────────────────────────────────────────────────
        px, py = int(player_x), player_y
        pr = pygame.Rect(px-17, py-28, 34, 56)

        # Traffic
        hit_traffic = False
        for t in traffic:
            tr = pygame.Rect(lane_x(t["lane"])-17, int(t["y"])-28, 34, 56)
            if pr.colliderect(tr):
                hit_traffic = True
                break
        if hit_traffic:
            if shield_on:
                shield_on = False
                active_pu = None
                traffic   = [t for t in traffic
                             if not pygame.Rect(lane_x(t["lane"])-17,
                                                int(t["y"])-28, 34, 56).colliderect(pr)]
            else:
                alive = False

        # Obstacles
        for obs in obstacles[:]:
            if obs["kind"] == "nitro_strip":
                continue
            or_ = pygame.Rect(lane_x(obs["lane"])-22, int(obs["y"])-10, 44, 20)
            if pr.colliderect(or_):
                if obs["kind"] == "oil":
                    speed = max(2, speed * 0.5)
                    obstacles.remove(obs)
                elif obs["kind"] == "barrier":
                    if shield_on:
                        shield_on = False
                        active_pu = None
                        obstacles.remove(obs)
                    else:
                        alive = False
                elif obs["kind"] == "pothole":
                    score = max(0, score - 20)
                    obstacles.remove(obs)

        # Nitro strips
        for ns in nitro_strips[:]:
            nr = pygame.Rect(lane_x(ns["lane"])-20, int(ns["y"])-6, 40, 12)
            if pr.colliderect(nr):
                activate_powerup("nitro")
                nitro_strips.remove(ns)

        # Power-ups
        for pu in powerups[:]:
            pur = pygame.Rect(lane_x(pu["lane"])-16, int(pu["y"])-16, 32, 32)
            if pr.colliderect(pur):
                if active_pu is None or pu["kind"] == "repair":
                    activate_powerup(pu["kind"])
                powerups.remove(pu)

        # Coins
        for c in coin_list[:]:
            cr = pygame.Rect(lane_x(c["lane"])-12, int(c["y"])-12, 24, 24)
            if pr.colliderect(cr):
                coins += c["value"]
                score += c["value"] * 10
                coin_list.remove(c)

        score += int(speed * dt * 2)
        check_powerup_expiry()

        # ── Draw ──────────────────────────────────────────────────────────
        screen.fill(GRASS_COLOR)

        # Road
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_W, H))

        # Lane lines (scrolling dashes)
        for lane in range(1, LANES):
            lx = ROAD_LEFT + lane * LANE_W
            for y in range(-60 + int(road_offset) % 60, H, 60):
                pygame.draw.rect(screen, LINE_COLOR, (lx-2, y, 4, 35))

        # Road edges
        pygame.draw.rect(screen, WHITE, (ROAD_LEFT-4, 0, 4, H))
        pygame.draw.rect(screen, WHITE, (ROAD_RIGHT,  0, 4, H))

        # Nitro strips
        for ns in nitro_strips:
            draw_obstacle(screen, "nitro_strip", lane_x(ns["lane"]), int(ns["y"]))

        # Obstacles
        for obs in obstacles:
            draw_obstacle(screen, obs["kind"], lane_x(obs["lane"]), int(obs["y"]))

        # Coins
        for c in coin_list:
            draw_coin(screen, lane_x(c["lane"]), int(c["y"]), c["value"])

        # Power-ups
        for pu in powerups:
            draw_powerup(screen, pu["kind"], lane_x(pu["lane"]), int(pu["y"]))

        # Traffic
        for t in traffic:
            draw_car(screen, t["color"], lane_x(t["lane"]), int(t["y"]))

        # Player
        draw_car(screen, car_c, px, py)
        if shield_on:
            pygame.draw.circle(screen, CYAN, (px, py), 32, 3)

        # ── HUD ───────────────────────────────────────────────────────────
        pygame.draw.rect(screen, (0, 0, 0, 160), (0, 0, W, 38))
        hud = [
            f"Score: {score}",
            f"Dist: {int(distance)}m / {FINISH_DIST}m",
            f"Coins: {coins}",
        ]
        for i, txt in enumerate(hud):
            t = fnt_sm.render(txt, True, WHITE)
            screen.blit(t, (10 + i * 220, 10))

        if active_pu:
            remaining = max(0, pu_end_time - time.time())
            pu_txt = f"[{active_pu.upper()}]"
            if active_pu != "shield":
                pu_txt += f"  {remaining:.1f}s"
            pt = fnt_sm.render(pu_txt, True, YELLOW)
            screen.blit(pt, pt.get_rect(topright=(W-10, 10)))

        # Distance bar
        bar_w = int((distance / FINISH_DIST) * (W - 20))
        pygame.draw.rect(screen, DGRAY,  (10, H-14, W-20, 8), border_radius=4)
        pygame.draw.rect(screen, GREEN, (10, H-14, bar_w, 8), border_radius=4)

        # Finish check
        if distance >= FINISH_DIST:
            score += 500
            alive = False

        pygame.display.flip()

    return score, distance, coins, "gameover"
