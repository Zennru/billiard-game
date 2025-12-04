import math
import random
import pygame
import pymunk

from ball import Ball
from cue import Cue
from pocket import Pocket
from table import Table
from UIHandler import UIHandler
from scoreSystem import ScoreSystem

pygame.init()

# ===== SCREEN =====
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
BOTTOM_PANEL = 50
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pool Game")

clock = pygame.time.Clock()
FPS = 120

# ===== PHYSICS =====
space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.90

# ===== FONTS =====
font = pygame.font.SysFont("Lato", 28)
large_font = pygame.font.SysFont("Lato", 70)
button_font = pygame.font.SysFont("Lato", 42)

# ===== BALL SIZE =====
dia = 28
radius = dia / 2

# ===== MENU BACKGROUND =====
menu_bg = pygame.image.load("assets/images/ball/billiards_Bg.png").convert()
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ===== SKINS =====
cue_skins = ["normal_cue.png", "japan_cue.png", "winter_cue.png"]
table_skins = ["normal_table.png", "japan_table.png", "winter_table.png"]

selected_cue_p1 = "normal_cue.png"
selected_cue_p2 = "japan_cue.png"
selected_table = "normal_table.png"

# ===== GAME BACKGROUND =====
table_image = pygame.image.load(
    f"assets/images/table/{selected_table}"
).convert_alpha()
table_image = pygame.transform.scale(table_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ===== SOUND =====
hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
hit_sound.set_volume(0.8)

collision_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
collision_sound.set_volume(0.35)

# ===== PREVIEWS =====
cue_previews = {}
for name in cue_skins:
    img = pygame.image.load(f"assets/images/cue/{name}").convert_alpha()
    cue_previews[name] = pygame.transform.smoothscale(img, (240, 20))

table_previews = {}
for name in table_skins:
    img = pygame.image.load(f"assets/images/table/{name}").convert_alpha()
    table_previews[name] = pygame.transform.smoothscale(img, (260, 140))

# ===== BALL IMAGES =====
ball_images = [
    pygame.image.load(f"assets/images/ball/ball_{i}.png").convert_alpha()
    for i in range(1, 17)
]
ball_images = [pygame.transform.smoothscale(img, (dia, dia)) for img in ball_images]

shadow_img = pygame.image.load("assets/images/ball/ball_Shadow.png").convert_alpha()
shadow_img = pygame.transform.smoothscale(shadow_img, (dia, dia))

highlight_img = pygame.image.load("assets/images/ball/ball_HighLight.png").convert_alpha()
highlight_img = pygame.transform.smoothscale(highlight_img, (dia, dia))

# ===== SYSTEMS =====
score = ScoreSystem()
ui = UIHandler(font, large_font)

table = Table(space, SCREEN_WIDTH, SCREEN_HEIGHT)
pocket_system = Pocket(SCREEN_WIDTH, SCREEN_HEIGHT)

balls = []

# ===== RACK SETUP =====
rows = 5
start_x = SCREEN_WIDTH * 0.25
start_y = SCREEN_HEIGHT * 0.40

for col in range(5):
    for r in range(rows):
        pos = (
            start_x + col * (dia + 1),
            start_y + r * (dia + 1) + col * dia / 2
        )
        balls.append(Ball(space, radius, pos))
    rows -= 1

# ===== CUE BALL =====
cue_ball_start = (SCREEN_WIDTH * 0.75, SCREEN_HEIGHT / 2)
cue_ball = Ball(space, radius, cue_ball_start)
balls.append(cue_ball)

# ===== INITIAL CUE =====
cue_image = pygame.image.load(
    f"assets/images/cue/{selected_cue_p1}"
).convert_alpha()
cue = Cue(cue_image, cue_ball)

# ===== PLAYER STATE =====
current_player = 1
player_score = {1: 0, 2: 0}
player_lives = {1: 3, 2: 3}

powering_up = False
force = 0
max_force = 10000
force_direction = 1
ball_in_hand = False

taking_shot = True
prev_taking_shot = True

pocket_effects = []

STATE_MENU = 0
STATE_SETTINGS = 1
STATE_GAME = 2
state = STATE_MENU

# deteksi tabrakan manual
last_vel = {b: (0, 0) for b in balls}

# game over + animasi
game_over = False
winner = None
confetti = []


def get_ball_points(index: int) -> int:
    num = index + 1
    if num == 8:
        return 40
    elif num <= 7:
        return 20
    else:
        return 25


def draw_modern_button(rect, text, hover):
    # shadow
    pygame.draw.rect(screen, (0, 0, 0, 150), rect.move(3, 3), border_radius=18)

    # gradient fill
    base = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    top_color = (230, 230, 230) if hover else (200, 200, 200)
    bottom_color = (130, 130, 130) if hover else (100, 100, 100)

    for y in range(rect.height):
        ratio = y / rect.height
        r = top_color[0] * (1 - ratio) + bottom_color[0] * ratio
        g = top_color[1] * (1 - ratio) + bottom_color[1] * ratio
        b = top_color[2] * (1 - ratio) + bottom_color[2] * ratio
        pygame.draw.line(base, (int(r), int(g), int(b)), (0, y), (rect.width, y))

    screen.blit(base, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=18)

    txt_img = button_font.render(text, True, (0, 0, 0))
    screen.blit(
        txt_img,
        (rect.x + rect.width // 2 - txt_img.get_width() // 2,
         rect.y + rect.height // 2 - txt_img.get_height() // 2)
    )


def spawn_confetti():
    for _ in range(80):
        confetti.append({
            "x": random.randint(0, SCREEN_WIDTH),
            "y": random.randint(-300, -10),
            "speed": random.uniform(2, 5),
            "color": (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255)
            ),
            "size": random.randint(3, 6)
        })


def draw_confetti(screen):
    for c in confetti:
        c["y"] += c["speed"]
        pygame.draw.rect(screen, c["color"], (c["x"], c["y"], c["size"], c["size"]))
    confetti[:] = [c for c in confetti if c["y"] < SCREEN_HEIGHT + 20]

def ray_sphere_intersection(ox, oy, dx, dy, cx, cy, R):
    # vektor OC
    lx = cx - ox
    ly = cy - oy

    # proyeksi OC ke arah sinar
    t_ca = lx * dx + ly * dy
    if t_ca < 0:
        return None  # sphere di belakang ray

    # jarak dari center ke garis sinar
    d2 = (lx*lx + ly*ly) - t_ca*t_ca
    R2 = R * R
    if d2 > R2:
        return None  # tidak mengenai

    # ketebalan chord
    thc = (R2 - d2) ** 0.5

    # titik intersection pertama (paling dekat)
    t_hit = t_ca - thc
    if t_hit < 0:
        return None

    return t_hit


# ============================ MAIN LOOP ==============================
run = True
while run:
    clock.tick(FPS)

    # ===================== MAIN MENU =====================
    if state == STATE_MENU:
        screen.blit(menu_bg, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = large_font.render("POOL GAME", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        play_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 240, 400, 70)
        set_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 330, 400, 70)
        quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 420, 400, 70)

        mx, my = pygame.mouse.get_pos()

        draw_modern_button(play_rect, "PLAY", play_rect.collidepoint(mx, my))
        draw_modern_button(set_rect, "SETTINGS", set_rect.collidepoint(mx, my))
        draw_modern_button(quit_rect, "QUIT", quit_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(mx, my):
                    table_image = pygame.image.load(
                        f"assets/images/table/{selected_table}"
                    ).convert_alpha()
                    table_image = pygame.transform.scale(
                        table_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
                    )

                    cue_image = pygame.image.load(
                        f"assets/images/cue/{selected_cue_p1}"
                    ).convert_alpha()
                    cue = Cue(cue_image, cue_ball)
                    current_player = 1
                    state = STATE_GAME

                elif set_rect.collidepoint(mx, my):
                    state = STATE_SETTINGS

                elif quit_rect.collidepoint(mx, my):
                    run = False

        pygame.display.update()
        continue

    # ===================== SETTINGS =====================
    if state == STATE_SETTINGS:
        screen.blit(menu_bg, (0, 0))
        dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160))
        screen.blit(dark, (0, 0))

        title = large_font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        screen.blit(button_font.render("Player 1 Cue", True, (255, 255, 255)), (100, 170))
        screen.blit(button_font.render("Player 2 Cue", True, (255, 255, 255)), (100, 280))
        screen.blit(button_font.render("Table Skin", True, (255, 255, 255)), (100, 390))

        screen.blit(cue_previews[selected_cue_p1], (100, 210))
        screen.blit(cue_previews[selected_cue_p2], (100, 320))
        screen.blit(table_previews[selected_table], (400, 360))

        back_rect = pygame.Rect(40, 530, 180, 55)
        mx, my = pygame.mouse.get_pos()
        draw_modern_button(back_rect, "< BACK", back_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if 170 <= my <= 260:
                    idx = cue_skins.index(selected_cue_p1)
                    selected_cue_p1 = cue_skins[(idx + 1) % len(cue_skins)]

                elif 280 <= my <= 360:
                    idx = cue_skins.index(selected_cue_p2)
                    selected_cue_p2 = cue_skins[(idx + 1) % len(cue_skins)]

                elif 390 <= my <= 500:
                    idx = table_skins.index(selected_table)
                    selected_table = table_skins[(idx + 1) % len(table_skins)]

                elif back_rect.collidepoint(mx, my):
                    state = STATE_MENU

        pygame.display.update()
        continue

    # ===================== GAME STATE =====================
    space.step(1 / FPS)
    screen.blit(table_image, (0, 0))

    # --------- GAME OVER MODE (ANIMASI) ----------
    if game_over:
        if not confetti:
            spawn_confetti()

        # gelapkan
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # teks utama dengan glow + zoom
        base_text = large_font.render(f"PLAYER {winner} WINS!", True, (255, 255, 0))
        glow_text = large_font.render(f"PLAYER {winner} WINS!", True, (255, 255, 255))

        screen.blit(
            glow_text,
            (SCREEN_WIDTH // 2 - glow_text.get_width() // 2,
             SCREEN_HEIGHT // 2 - 90)
        )

        zoom = 1.0 + math.sin(pygame.time.get_ticks() * 0.004) * 0.05
        scaled = pygame.transform.smoothscale(
            base_text,
            (int(base_text.get_width() * zoom), int(base_text.get_height() * zoom))
        )
        screen.blit(
            scaled,
            (SCREEN_WIDTH // 2 - scaled.get_width() // 2,
             SCREEN_HEIGHT // 2 - 90)
        )

        # confetti
        draw_confetti(screen)

        # restart info (fade)
        alpha = min(255, int((pygame.time.get_ticks() * 0.25) % 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        restart_surface = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
        restart_surface.blit(restart_text, (0, 0))
        restart_surface.set_alpha(alpha)

        screen.blit(
            restart_surface,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
             SCREEN_HEIGHT // 2 + 10)
        )

        pygame.display.update()

        # event khusus saat game over
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # RESET GAME
                current_player = 1
                player_score[1] = player_score[2] = 0
                player_lives[1] = player_lives[2] = 3

                score.potted_p1.clear()
                score.potted_p2.clear()

                for b in balls:
                    space.remove(b.body, b.shape)
                balls.clear()

                # build rack lagi
                rows = 5
                start_x = SCREEN_WIDTH * 0.25
                start_y = SCREEN_HEIGHT * 0.40
                for col in range(5):
                    for r in range(rows):
                        pos = (
                            start_x + col * (dia + 1),
                            start_y + r * (dia + 1) + col * dia / 2
                        )
                        balls.append(Ball(space, radius, pos))
                    rows -= 1

                # cue ball
                cue_ball = Ball(space, radius, cue_ball_start)
                balls.append(cue_ball)

                cue_image = pygame.image.load(
                    f"assets/images/cue/{selected_cue_p1}"
                ).convert_alpha()
                cue = Cue(cue_image, cue_ball)

                ball_in_hand = False
                game_over = False
                winner = None
                confetti.clear()
                last_vel = {b: (0, 0) for b in balls}

        continue  # skip normal game logic ketika game over

    # ================== NORMAL GAME LOGIC ==================
    potted_info = []

    # POCKET CHECK
    for ball in balls[:]:
        pos = ball.body.position
        if pocket_system.check(pos):
            if ball is cue_ball:
                if not ball_in_hand:
                    player_lives[current_player] -= 1
                    ball_in_hand = True
                ball.body.velocity = (0, 0)
                ball.body.position = (-200, -200)
                continue

            idx = balls.index(ball)
            pts = get_ball_points(idx)
            img = ball_images[idx]

            potted_info.append({
                "ball": ball,
                "index": idx,
                "image": img,
                "pos": pos,
                "points": pts
            })

            ball.body.velocity = (0, 0)
            ball.body.position = (-200, -200)

    # PROCESS POTTED BALLS
    for info in sorted(potted_info, key=lambda x: x["index"], reverse=True):
        b = info["ball"]
        idx = info["index"]

        score.add_potted(info["image"], current_player)
        player_score[current_player] += info["points"]

        if b in last_vel:
            del last_vel[b]
        space.remove(b.body, b.shape)
        balls.pop(idx)
        ball_images.pop(idx)
        pocket_effects.append({"pos": info["pos"], "timer": 0})

    # COLLISION SOUND
    seen_pairs = set()

    # ball-wall
    for b in balls:
        vx, vy = b.body.velocity
        pvx, pvy = last_vel.get(b, (0, 0))
        x, y = b.body.position
        speed = math.hypot(vx, vy)

        left = 50 + radius
        right = SCREEN_WIDTH - 50 - radius
        top = 50 + radius
        bottom = SCREEN_HEIGHT - 50 - radius

        if abs(vx) > 20 and vx * pvx < 0 and (x <= left + 1 or x >= right - 1):
            if speed > 80:
                collision_sound.play()

        if abs(vy) > 20 and vy * pvy < 0 and (y <= top + 1 or y >= bottom - 1):
            if speed > 80:
                collision_sound.play()

    # ball-ball
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1 = balls[i]
            b2 = balls[j]

            x1, y1 = b1.body.position
            x2, y2 = b2.body.position
            dx = x2 - x1
            dy = y2 - y1
            dist2 = dx * dx + dy * dy
            if dist2 <= (2 * radius + 2) ** 2:
                rvx = b1.body.velocity.x - b2.body.velocity.x
                rvy = b1.body.velocity.y - b2.body.velocity.y
                if rvx * rvx + rvy * rvy > 90 * 90:
                    key = tuple(sorted((id(b1), id(b2))))
                    if key not in seen_pairs:
                        collision_sound.play()
                        seen_pairs.add(key)

    for b in balls:
        last_vel[b] = b.body.velocity

    # DRAW BALLS
    for i, ball in enumerate(balls):
        ball.draw(screen, ball_images[i], shadow_img, highlight_img)

    # POCKET EFFECT RING
    for eff in pocket_effects[:]:
        eff["timer"] += 1
        r = max(0, 20 - eff["timer"] * 2)
        if r <= 0:
            pocket_effects.remove(eff)
        else:
            x, y = eff["pos"]
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), r, 2)

    # SHOT READY CHECK
    taking_shot = all(ball.is_stopped() for ball in balls)

    if taking_shot and not prev_taking_shot and not ball_in_hand:
        current_player = 2 if current_player == 1 else 1
        skin = selected_cue_p1 if current_player == 1 else selected_cue_p2
        cue_image = pygame.image.load(
            f"assets/images/cue/{skin}"
        ).convert_alpha()
        cue = Cue(cue_image, cue_ball)

    prev_taking_shot = taking_shot

    # GAME OVER CHECK
    if player_lives[1] <= 0 and winner is None:
        winner = 2
        game_over = True
        for b in balls:
            b.body.velocity = (0, 0)
    elif player_lives[2] <= 0 and winner is None:
        winner = 1
        game_over = True
        for b in balls:
            b.body.velocity = (0, 0)

    # BALL IN HAND
    if ball_in_hand:
        mx, my = pygame.mouse.get_pos()
        if 50 + radius < mx < SCREEN_WIDTH - 50 - radius and 50 + radius < my < SCREEN_HEIGHT - 50 - radius:
            cue_ball.body.position = (mx, my)
            cue_ball.body.velocity = (0, 0)

        cx, cy = cue_ball.body.position
        pygame.draw.circle(screen, (0, 255, 0), (int(cx), int(cy)), int(radius + 3), 2)

    # AIM & CUE
    if taking_shot and not ball_in_hand:
        mouse = pygame.mouse.get_pos()
        cue.update(mouse)

        bx, by = cue_ball.body.position
        angle = math.radians(cue.angle)
        dx = math.cos(angle)
        dy = -math.sin(angle)

        max_len = 2000

        # HIT WALL (sudah punya)
        candidates = []
        left = 50
        right = SCREEN_WIDTH - 50
        top = 50
        bottom = SCREEN_HEIGHT - 50

        # X WALL
        if abs(dx) > 1e-6:
            if dx < 0:
                t = (left - bx) / dx
                if t > 0:
                    candidates.append(("wall_x", t, left))
            else:
                t = (right - bx) / dx
                if t > 0:
                    candidates.append(("wall_x", t, right))

        # Y WALL
        if abs(dy) > 1e-6:
            if dy < 0:
                t = (top - by) / dy
                if t > 0:
                    candidates.append(("wall_y", t, top))
            else:
                t = (bottom - by) / dy
                if t > 0:
                    candidates.append(("wall_y", t, bottom))

        t_wall = max_len
        hit_wall = None
        hit_type = None

        for kind, t, val in candidates:
            if t < t_wall:
                t_wall = t
                if kind == "wall_x":
                    hit_wall = (val, by + dy * t)
                else:
                    hit_wall = (bx + dx * t, val)
                hit_type = kind

        # HIT BALL (RAY-SPHERE INTERSECTION)
        R = radius * 2
        t_ball = max_len
        first_ball = None

        for b in balls:
            if b is cue_ball:
                continue

            cx, cy = b.body.position

            t_hit = ray_sphere_intersection(bx, by, dx, dy, cx, cy, R)
            if t_hit is not None and 0 < t_hit < t_ball:
                t_ball = t_hit
                first_ball = b

        # FIRST HIT DECISION
        if first_ball and t_ball < t_wall:
            first_hit = (bx + dx * t_ball, by + dy * t_ball)
            hit_ball_first = True
        else:
            first_hit = hit_wall
            hit_ball_first = False

        # GARIS UTAMA
        pygame.draw.line(
            screen, (255, 255, 255),
            (int(bx), int(by)),
            (int(first_hit[0]), int(first_hit[1])),
            3
        )

        # GHOST BALL
        bx, by = cue_ball.body.position
        radius = cue_ball.radius

        # Arah cue → mouse
        mx, my = pygame.mouse.get_pos()
        dx = mx - bx
        dy = my - by
        dlen = math.hypot(dx, dy)

        if dlen > 1e-6:
            dx /= dlen
            dy /= dlen

        # RAYCAST: Cari bola pertama yg kena garis
        first_hit_ball = None
        closest_dist = float('inf')

        for ball in balls:
            if ball is cue_ball:
                continue
            
            px = ball.body.position.x - bx
            py = ball.body.position.y - by

            proj = px * dx + py * dy
            if proj <= 0:
                continue  # di belakang cue ball
            
            # jarak center ball ke garis
            closest = abs(px * dy - py * dx)

            if closest <= radius * 2:  # kena bola
                if proj < closest_dist:
                    closest_dist = proj
                    first_hit_ball = ball

        # Kalau ada bola yg kena garis aim
        if first_hit_ball:
            # titik tabrak
            hx = bx + dx * closest_dist
            hy = by + dy * closest_dist

            # ghost ball = geser dari titik tabrak sejauh diameter
            ghost_x = hx - dx * (radius * 2)
            ghost_y = hy - dy * (radius * 2)

            pygame.draw.circle(
                screen, (255, 255, 255),
                (int(ghost_x), int(ghost_y)),
                radius,
                2
            )

        # LANJUTAN — BOLA
        LINE_LEN = 200

        if hit_ball_first:

            cx, cy = first_ball.body.position
            hx, hy = first_hit

            LINE_GREEN = 80
            LINE_RED = 40

            # VECTOR NORMAL dari titik kontak
            nx = cx - hx
            ny = cy - hy
            nlen = math.hypot(nx, ny)
            if nlen < 1e-6:
                nx, ny = dx, dy
                nlen = math.hypot(nx, ny)
            nx /= nlen
            ny /= nlen

            # lintasan bola target (HIJAU)
            target_end = (hx + nx * LINE_GREEN, hy + ny * LINE_GREEN)

            pygame.draw.line(
                screen, (255, 255, 255),
                (int(hx), int(hy)),
                (int(target_end[0]), int(target_end[1])),
                3
            )

            # cue-ball setelah tumbukan (MERAH)
            dot = dx * nx + dy * ny
            projx = dot * nx
            projy = dot * ny
            cue_dx = dx - projx
            cue_dy = dy - projy

            clen = math.hypot(cue_dx, cue_dy)
            if clen < 1e-6:
                cue_dx, cue_dy = -ny, nx
                clen = math.hypot(cue_dx, cue_dy)

            cue_dx /= clen
            cue_dy /= clen

            cue_end = (hx + cue_dx * LINE_RED, hy + cue_dy * LINE_RED)

            pygame.draw.line(
                screen, (255, 255, 255),
                (int(hx), int(hy)),
                (int(cue_end[0]), int(cue_end[1])),
                3
            )

        # LANJUTAN — WALL
        else:
            if hit_type == "wall_x":
                rdx, rdy = -dx, dy
            elif hit_type == "wall_y":
                rdx, rdy = dx, -dy
            else:
                rdx, rdy = dx, dy

            end2 = (
                first_hit[0] + rdx * LINE_LEN,
                first_hit[1] + rdy * LINE_LEN
            )

            pygame.draw.line(
                screen, (200, 200, 200),
                (int(first_hit[0]), int(first_hit[1])),
                (int(end2[0]), int(end2[1])),
                2
            )

        cue.draw(screen)

    # POWER BAR
    if powering_up and taking_shot and not ball_in_hand:
        force += 120 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1

        bx, by = cue_ball.body.position
        bar_width = int((force / max_force) * 110)
        pygame.draw.rect(
            screen, (255, 0, 0),
            (int(bx - 55), int(by + 35), bar_width, 10)
        )

    # ===== BOTTOM PANEL (STYLE H1) =====
    pygame.draw.rect(
        screen, (40, 40, 40),
        (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL)
    )

    # P1
    p1_text = f"P1 Score:{player_score[1]} | Lives:{player_lives[1]}"
    ui.draw_text(screen, p1_text, font, (255, 255, 255), 20, SCREEN_HEIGHT + 5)
    ui.draw_potted_for_player(screen, score.potted_p1, 20, SCREEN_HEIGHT + 28)

    # P2
    p2_text = f"P2 Score:{player_score[2]} | Lives:{player_lives[2]}"
    p2_w = font.render(p2_text, True, (0, 0, 0)).get_width()
    p2_x = SCREEN_WIDTH - p2_w - 20
    ui.draw_text(screen, p2_text, font, (255, 255, 255), p2_x, SCREEN_HEIGHT + 5)

    icons_w = len(score.potted_p2) * 26
    icons_start = SCREEN_WIDTH - icons_w - 20
    ui.draw_potted_for_player(screen, score.potted_p2, icons_start, SCREEN_HEIGHT + 28)

    # TURN di tengah
    turn_text = font.render(f"Turn: P{current_player}", True, (255, 255, 0))
    screen.blit(
        turn_text,
        (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, SCREEN_HEIGHT + 10)
    )

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if ball_in_hand:
                pass
            elif taking_shot:
                powering_up = True

        if event.type == pygame.MOUSEBUTTONUP:
            if ball_in_hand:
                ball_in_hand = False
            else:
                if powering_up and taking_shot:
                    hit_sound.play()
                    cue.shoot(force)
                powering_up = False
                force = 0
                force_direction = 1

    pygame.display.update()

pygame.quit()
