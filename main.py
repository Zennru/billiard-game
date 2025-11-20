import pygame
import pymunk
import pymunk.pygame_util
import math

pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
BOTTOM_PANEL = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pool")

# Pymunk physics
space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)

clock = pygame.time.Clock()
FPS = 120

# game variables
lives = 3
dia = 36
pocket_dia = 66
force = 0
max_force = 10000
force_direction = 1
game_running = True
cue_ball_potted = False
taking_shot = True
powering_up = False
potted_balls = []

# colours
BG = (50, 50, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# fonts
font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# ============================
# IMAGE LOAD + RESPONSIVE SCALE
# ============================
cue_image = pygame.image.load("assets/images/cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table.png").convert_alpha()
table_image = pygame.transform.scale(table_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load ball images
ball_images = []
for i in range(1, 17):
    img = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
    ball_images.append(img)

# ===========================
# DRAW TEXT
# ===========================
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# ===========================
# CREATE BALL FUNCTION
# ===========================
def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8

    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000

    space.add(body, shape, pivot)
    return shape

# ===========================
# CREATE BALL TRIANGLE (LEFT)
# ===========================
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
        new_ball = create_ball(dia / 2, pos)
        balls.append(new_ball)
    rows -= 1

# ===========================
# CUE BALL (RIGHT SIDE CENTER)
# ===========================
cue_start = (SCREEN_WIDTH * 0.75, SCREEN_HEIGHT / 2)
cue_ball = create_ball(dia / 2, cue_start)
balls.append(cue_ball)

# ===========================
# POCKETS RESPONSIVE
# ===========================
pockets = [
    (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.06),
    (SCREEN_WIDTH * 0.50, SCREEN_HEIGHT * 0.05),
    (SCREEN_WIDTH * 0.95, SCREEN_HEIGHT * 0.06),
    (SCREEN_WIDTH * 0.05, SCREEN_HEIGHT * 0.94),
    (SCREEN_WIDTH * 0.50, SCREEN_HEIGHT * 0.95),
    (SCREEN_WIDTH * 0.95, SCREEN_HEIGHT * 0.94)
]

# ===========================
# CREATE RESPONSIVE CUSHIONS
# ===========================
def create_edge(x1, y1, x2, y2):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
    shape.elasticity = 0.8
    space.add(body, shape)

# top left → top right
create_edge(80, 50, SCREEN_WIDTH - 80, 50)
# bottom left → bottom right
create_edge(80, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 50)
# left top → left bottom
create_edge(50, 80, 50, SCREEN_HEIGHT - 80)
# right top → right bottom
create_edge(SCREEN_WIDTH - 50, 80, SCREEN_WIDTH - 50, SCREEN_HEIGHT - 80)

# ===========================
# CUE CLASS
# ===========================
class Cue:
    def __init__(self, pos):
        self.original_image = cue_image
        self.angle = 0
        self.image = cue_image
        self.rect = self.image.get_rect(center=pos)

    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, rect)

cue = Cue(cue_ball.body.position)

# power bar
power_bar = pygame.Surface((10, 20))
power_bar.fill(RED)

# ===========================
# GAME LOOP
# ===========================
run = True
while run:
    clock.tick(FPS)
    space.step(1 / FPS)

    screen.fill(BG)
    screen.blit(table_image, (0, 0))

    # check potted balls
    for i, ball in enumerate(balls):
        for pocket in pockets:
            dist = math.dist(ball.body.position, pocket)
            if dist <= pocket_dia / 2:

                if i == len(balls) - 1:
                    lives -= 1
                    cue_ball_potted = True
                    ball.body.position = (-100, -100)
                    ball.body.velocity = (0, 0)

                else:
                    space.remove(ball.body)
                    balls.remove(ball)
                    potted_balls.append(ball_images[i])
                    ball_images.pop(i)
                break

    # draw balls
    for i, ball in enumerate(balls):
        x = ball.body.position[0] - ball.radius
        y = ball.body.position[1] - ball.radius
        screen.blit(ball_images[i], (x, y))

    # check movement
    taking_shot = all(
        int(ball.body.velocity[0]) == 0 and int(ball.body.velocity[1]) == 0
        for ball in balls
    )

    # draw cue
    if taking_shot and game_running:
        if cue_ball_potted:
            cue_ball.body.position = cue_start
            cue_ball_potted = False

        mouse = pygame.mouse.get_pos()
        cue.rect.center = cue_ball.body.position

        dx = cue_ball.body.position[0] - mouse[0]
        dy = -(cue_ball.body.position[1] - mouse[1])
        angle = math.degrees(math.atan2(dy, dx))

        cue.update(angle)
        cue.draw(screen)

    # power shot
    if powering_up and game_running:
        force += 100 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1

        for b in range(math.ceil(force / 2000)):
            screen.blit(power_bar, (
                cue_ball.body.position[0] - 30 + b * 15,
                cue_ball.body.position[1] + 30
            ))

    elif not powering_up and taking_shot:
        x_impulse = math.cos(math.radians(angle))
        y_impulse = math.sin(math.radians(angle))
        cue_ball.body.apply_impulse_at_local_point(
            (force * -x_impulse, force * y_impulse)
        )
        force = 0
        force_direction = 1

    # bottom panel
    pygame.draw.rect(screen, BG, (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))
    draw_text(f"LIVES: {lives}", font, WHITE, SCREEN_WIDTH - 200, SCREEN_HEIGHT + 10)

    # draw potted ball images
    for i, img in enumerate(potted_balls):
        screen.blit(img, (10 + i * 50, SCREEN_HEIGHT + 10))

    # win / lose
    if lives <= 0:
        draw_text("GAME OVER", large_font, WHITE, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 - 80)
        game_running = False

    if len(balls) == 1:
        draw_text("YOU WIN!", large_font, WHITE, SCREEN_WIDTH / 2 - 130, SCREEN_HEIGHT / 2 - 80)
        game_running = False

    # events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot:
            powering_up = True
        if event.type == pygame.MOUSEBUTTONUP and taking_shot:
            powering_up = False
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
