import pygame
import pymunk
import math

from ball import Ball
from cue import Cue
from pocket import Pocket
from table import Table
from UIHandler import UIHandler
from scoreSystem import ScoreSystem

pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
BOTTOM_PANEL = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pool Game")

clock = pygame.time.Clock()
FPS = 120

# pymunk physics
space = pymunk.Space()
space.gravity = (0, 0)
space.damping = 0.9

# fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# ==== ukuran bola (diperkecil dari 36 ke 28) ====
dia = 28
radius = dia / 2

# load images
cue_image = pygame.image.load("assets/images/cue/japan_cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table/japan_table.png").convert_alpha()
table_image = pygame.transform.scale(table_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

ball_images = [
    pygame.image.load(f"assets/images/ball/ball_{i}.png").convert_alpha()
    for i in range(1, 17)
]
# scale gambar bola ke size baru
ball_images = [
    pygame.transform.smoothscale(img, (dia, dia)) for img in ball_images
]

# systems
score = ScoreSystem(lives=3)
ui = UIHandler(font, large_font)

# create table
table = Table(space, SCREEN_WIDTH, SCREEN_HEIGHT)

# pockets
pocket_system = Pocket(SCREEN_WIDTH, SCREEN_HEIGHT)

# create balls
balls = []

rows = 5
start_x = SCREEN_WIDTH * 0.25
start_y = SCREEN_HEIGHT * 0.40

for col in range(5):
    for row in range(rows):
        pos = (
            start_x + col * (dia + 1),
            start_y + row * (dia + 1) + col * dia / 2
        )
        ball = Ball(space, radius, pos)
        balls.append(ball)
    rows -= 1

cue_ball_start = (SCREEN_WIDTH * 0.75, SCREEN_HEIGHT / 2)
cue_ball = Ball(space, radius, cue_ball_start)
balls.append(cue_ball)

cue = Cue(cue_image, cue_ball)

# power variables
powering_up = False
force = 0
max_force = 10000
force_direction = 1
taking_shot = True

run = True
game_running = True

# helper: nilai poin tiap bola (index sama kayak ball_images)
def get_ball_points(index):
    num = index + 1   # ball_1.png → 1
    if num == 8:
        return 40
    elif 1 <= num <= 7:
        return 20
    else:
        return 25

while run:
    clock.tick(FPS)
    space.step(1 / FPS)

    # gambar meja
    screen.blit(table_image, (0, 0))

    # ==== check pocket events ====
    for i, ball in enumerate(balls[:]):
        if pocket_system.check(ball.body.position):
            if ball is cue_ball:
                score.lose_life()
                ball.body.position = (-100, -100)
                ball.body.velocity = (0, 0)
            else:
                points = get_ball_points(i)
                score.add_potted(ball_images[i], points=points)
                space.remove(ball.body, ball.shape)
                balls.remove(ball)
                ball_images.pop(i)

    # draw balls
    for i, ball in enumerate(balls):
        ball.draw(screen, ball_images[i])

    # check if all balls stopped
    taking_shot = all(ball.is_stopped() for ball in balls)

    # cue update + AIM LINE
    if taking_shot and game_running:
        if score.lives <= 0:
            game_running = False

        mouse = pygame.mouse.get_pos()
        cue.update(mouse)

        # ====== AIM LINE DENGAN PANTULAN 1X ======
        bx, by = cue_ball.body.position
        angle_rad = math.radians(cue.angle)

        # arah tembakan HARUS cocok dengan shoot(): (-cos, +sin)
        dir_x = -math.cos(angle_rad)
        dir_y = math.sin(angle_rad)

        # panjang ray awal
        max_len = 800

        # batas cushion (sama dgn table)
        left_x = 50
        right_x = SCREEN_WIDTH - 50
        top_y = 50
        bottom_y = SCREEN_HEIGHT - 50

        # cari t tabrakan dengan dinding
        t_candidates = []

        if dir_x < 0:
            t = (left_x - bx) / dir_x
            if t > 0:
                t_candidates.append(("wall_x", t, left_x))
        elif dir_x > 0:
            t = (right_x - bx) / dir_x
            if t > 0:
                t_candidates.append(("wall_x", t, right_x))

        if dir_y < 0:
            t = (top_y - by) / dir_y
            if t > 0:
                t_candidates.append(("wall_y", t, top_y))
        elif dir_y > 0:
            t = (bottom_y - by) / dir_y
            if t > 0:
                t_candidates.append(("wall_y", t, bottom_y))

        # t tabrakan dinding paling dekat
        t_wall = max_len
        hit_type = None
        hit_pos = (bx + dir_x * max_len, by + dir_y * max_len)

        for kind, t, val in t_candidates:
            if t < t_wall:
                t_wall = t
                if kind == "wall_x":
                    hit_pos = (val, by + dir_y * t)
                else:
                    hit_pos = (bx + dir_x * t, val)
                hit_type = kind

        # cek tabrakan dengan bola lain
        t_ball = max_len
        ball_hit_pos = None
        for idx, b in enumerate(balls):
            if b is cue_ball:
                continue
            cx, cy = b.body.position
            # proyeksi ke garis
            rel_x = cx - bx
            rel_y = cy - by
            t = rel_x * dir_x + rel_y * dir_y
            if t <= 0:
                continue
            # titik terdekat di garis
            px = bx + dir_x * t
            py = by + dir_y * t
            dist = math.hypot(cx - px, cy - py)
            if dist <= radius * 2 and t < t_ball:
                t_ball = t
                ball_hit_pos = (px, py)

        first_end = hit_pos
        hit_ball_first = False
        if ball_hit_pos and t_ball < t_wall:
            first_end = ball_hit_pos
            hit_ball_first = True

        # garis utama
        pygame.draw.line(
            screen, (255, 255, 255),
            (int(bx), int(by)),
            (int(first_end[0]), int(first_end[1])),
            3
        )

        # ghost ball di depan cue ball
        ghost_x = bx + dir_x * (radius * 2.5)
        ghost_y = by + dir_y * (radius * 2.5)
        pygame.draw.circle(
            screen, (255, 255, 255),
            (int(ghost_x), int(ghost_y)),
            int(radius), 1
        )

        # garis lanjutan:
        if hit_ball_first:
            # kalau kena bola: garis kecil lanjut searah
            end2 = (first_end[0] + dir_x * 150, first_end[1] + dir_y * 150)
            pygame.draw.line(
                screen, (200, 200, 200),
                (int(first_end[0]), int(first_end[1])),
                (int(end2[0]), int(end2[1])),
                2
            )
        else:
            # kalau kena dinding: pantulan
            if hit_type == "wall_x":
                ref_dir_x = -dir_x
                ref_dir_y = dir_y
            elif hit_type == "wall_y":
                ref_dir_x = dir_x
                ref_dir_y = -dir_y
            else:
                ref_dir_x, ref_dir_y = dir_x, dir_y

            end2 = (
                first_end[0] + ref_dir_x * 200,
                first_end[1] + ref_dir_y * 200
            )
            pygame.draw.line(
                screen, (200, 200, 200),
                (int(first_end[0]), int(first_end[1])),
                (int(end2[0]), int(end2[1])),
                2
            )

        cue.draw(screen)

    # power bar charge
    if powering_up and taking_shot and game_running:
        force += 100 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1

        for b in range(math.ceil(force / 2000)):
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (
                    cue_ball.body.position[0] - 30 + b * 15,
                    cue_ball.body.position[1] + 30,
                    10, 20
                ),
            )

    # shoot
    elif not powering_up and taking_shot and game_running:
        cue.shoot(force, cue.angle)
        force = 0
        force_direction = 1

    # bottom panel (gambar PALING AKHIR biar nggak ketutup apa pun)
    pygame.draw.rect(
        screen,
        (50, 50, 50),
        (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL)
    )

    # SCORE + LIVES
    ui.draw_text(
        screen,
        f"SCORE: {score.score}",
        font,
        (255, 255, 255),
        20,
        SCREEN_HEIGHT + 10
    )

    ui.draw_text(
        screen,
        f"LIVES: {score.lives}",
        font,
        (255, 255, 255),
        SCREEN_WIDTH - 200,
        SCREEN_HEIGHT + 10
    )

    # bola-bola yang sudah masuk
    ui.draw_potted(screen, score.potted_balls)

    # events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot and game_running:
            powering_up = True

        if event.type == pygame.MOUSEBUTTONUP:
            powering_up = False

        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
