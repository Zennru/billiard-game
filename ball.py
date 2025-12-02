import math
import pygame
import pymunk


class Ball:
    def __init__(self, space, radius, pos, mass=5, elasticity=0.8):
        self.radius = radius

        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        self.body.linear_damping = 1.25
        self.body.angular_damping = 0.9

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = elasticity
        self.shape.friction = 1.0
        self.shape.collision_type = 1  # bola

        space.add(self.body, self.shape)

        # sudut untuk animasi gelinding
        self.angle = 0.0

    def update_spin(self):
        vx, vy = self.body.velocity
        speed = math.hypot(vx, vy)
        if speed > 1:
            self.angle = (self.angle + speed * 0.04) % 360

    def draw(self, screen, img, shadow, highlight):
        self.update_spin()

        cx = int(self.body.position.x)
        cy = int(self.body.position.y)

        # shadow
        screen.blit(shadow, shadow.get_rect(center=(cx + 3, cy + 3)))

        # bola di-rotate
        rotated = pygame.transform.rotate(img, self.angle)
        rect = rotated.get_rect(center=(cx, cy))
        screen.blit(rotated, rect)

        # highlight
        screen.blit(highlight, highlight.get_rect(center=(cx, cy)))

    def is_stopped(self):
        vx, vy = self.body.velocity
        if vx * vx + vy * vy < 2500:
            self.body.velocity = (0, 0)
            return True
        return False
