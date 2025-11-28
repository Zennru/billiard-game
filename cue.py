import pygame
import math

class Cue:
    def __init__(self, image, ball):
        self.original_image = image
        self.image = image
        self.angle = 0
        self.ball = ball
        self.rect = self.image.get_rect(center=ball.body.position)

    def update(self, mouse_pos):
        bx, by = self.ball.body.position
        dx = bx - mouse_pos[0]
        dy = -(by - mouse_pos[1])
        self.angle = math.degrees(math.atan2(dy, dx))
        self.rect.center = self.ball.body.position

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated.get_rect(center=self.rect.center)
        screen.blit(rotated, rect)

    def shoot(self, force, angle):
        # arah impulse mengikuti angle yang sama dengan garis aim
        rad = math.radians(angle)
        x_impulse = math.cos(rad)
        y_impulse = math.sin(rad)

        # sesuai kode awalmu: -x, +y
        self.ball.body.apply_impulse_at_local_point(
            (force * -x_impulse, force * y_impulse)
        )
