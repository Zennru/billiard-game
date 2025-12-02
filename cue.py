import pygame
import math


class Cue:
    def __init__(self, image, ball):
        self.original = image
        self.image = image
        self.angle = 0
        self.ball = ball
        self.cue_pos = ball.body.position

    def update(self, mouse):
        bx, by = self.ball.body.position
        mx, my = mouse
        dx = mx - bx
        dy = my - by

        self.angle = -math.degrees(math.atan2(dy, dx))

        offset = 110
        rad = math.radians(-self.angle)
        ox = math.cos(rad) * -offset
        oy = math.sin(rad) * -offset
        self.cue_pos = (bx + ox, by + oy)

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.original, self.angle)
        screen.blit(rotated, rotated.get_rect(center=self.cue_pos))

    def shoot(self, force):
        rad = math.radians(-self.angle)
        ix = force * math.cos(rad)
        iy = force * math.sin(rad)
        self.ball.body.apply_impulse_at_world_point((ix, iy), self.ball.body.position)
