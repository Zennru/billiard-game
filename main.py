import pygame
import pymunk
import math
import pymunk.pygame_util

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
static_body = space.static_body

# fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# load images
cue_image = pygame.image.load("assets/images/cue/japan_cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table/japan_table.png").convert_alpha()
table_image = pygame.transform.scale(table_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

ball_images = [pygame.image.load(f"assets/images/ball/ball_{i}.png").convert_alpha()
               for i in range(1, 17)]

# systems
score = ScoreSystem(lives=3)
ui = UIHandler(font, large_font)

# create table
table = Table(space, SCREEN_WIDTH, SCREEN_HEIGHT)

# pockets
pocket_system = Pocket(SCREEN_WIDTH, SCREEN_HEIGHT)

# create balls
dia = 36
balls = []

rows = 5
start_x = SCREEN_WIDTH * 0.25
start_y = SCREEN_HEIGHT * 0.40

for col in range(5):
    for row in range(rows):
        pos = (start_x + col * (dia + 1),
               start_y + row * (dia + 1) + col * dia / 2)
        ball = Ball(space, dia/2, pos)
        balls.append(ball)
    rows -= 1

cue_ball_start = (SCREEN_WIDTH * 0.75, SCREEN_HEIGHT / 2)
cue_ball = Ball(space, dia/2, cue_ball_start)
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

while run:
    clock.tick(FPS)
    space.step(1/FPS)

    screen.blit(table_image, (0, 0))

    # check pocket events
    for i, ball in enumerate(balls[:]):
        if pocket_system.check(ball.body.position):
            if ball is cue_ball:
                score.lose_life()
                ball.body.position = (-100, -100)
            else:
                score.add_potted(ball_images[i])
                space.remove(ball.body, ball.shape)
                balls.remove(ball)
                ball_images.pop(i)

    # draw balls
    for i, ball in enumerate(balls):
        ball.draw(screen, ball_images[i])

    # check if all balls stopped
    taking_shot = all(ball.is_stopped() for ball in balls)

    # cue update
    if taking_shot and game_running:
        if score.lives <= 0:
            game_running = False

        mouse = pygame.mouse.get_pos()
        cue.update(mouse)
        cue.draw(screen)

    # power bar charge
    if powering_up and taking_shot:
        force += 100 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1

        for b in range(math.ceil(force / 2000)):
            pygame.draw.rect(screen, (255, 0, 0), (
                cue_ball.body.position[0] - 30 + b * 15,
                cue_ball.body.position[1] + 30,
                10, 20
            ))

    # shoot
    elif not powering_up and taking_shot:
        cue.shoot(force, cue.angle)
        force = 0
        force_direction = 1

    # bottom panel
    pygame.draw.rect(screen, (50, 50, 50),
                     (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))

    ui.draw_text(screen, f"LIVES: {score.lives}",
                 font, (255, 255, 255), SCREEN_WIDTH - 200, SCREEN_HEIGHT + 10)

    ui.draw_potted(screen, score.potted_balls)

    # events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot:
            powering_up = True

        if event.type == pygame.MOUSEBUTTONUP:
            powering_up = False

        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
