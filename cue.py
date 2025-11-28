import pygame
import math

class Cue:
    def __init__(self, image, ball):
        self.original_image = image
        self.image = image
        self.angle = 0
        self.ball = ball
        self.cue_pos = ball.body.position

    def update(self, mouse_pos):
        bx, by = self.ball.body.position
        mx, my = mouse_pos

        dx = mx - bx
        dy = my - by

        # angle rotasi stick
        self.angle = -math.degrees(math.atan2(dy, dx))

        # jarak mundur stick dari bola
        stick_offset = 120  
        angle_rad = math.radians(-self.angle)

        offset_x = math.cos(angle_rad) * -stick_offset
        offset_y = math.sin(angle_rad) * -stick_offset

        self.cue_pos = (bx + offset_x, by + offset_y)

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        self.image = rotated
        rect = self.image.get_rect(center=self.cue_pos)
        screen.blit(self.image, rect)

    def shoot(self, force):
        # gunakan angle cue aktual
        angle_rad = math.radians(-self.angle)

        x_impulse = force * math.cos(angle_rad)
        y_impulse = force * math.sin(angle_rad)

        self.ball.body.apply_impulse_at_world_point((x_impulse, y_impulse), self.ball.body.position)
