import math

class Pocket:
    def __init__(self, screen_w, screen_h, diameter=66):
        self.radius = diameter / 2

        self.pockets = [
            (screen_w * 0.05, screen_h * 0.06),
            (screen_w * 0.50, screen_h * 0.05),
            (screen_w * 0.95, screen_h * 0.06),
            (screen_w * 0.05, screen_h * 0.94),
            (screen_w * 0.50, screen_h * 0.95),
            (screen_w * 0.95, screen_h * 0.94),
        ]

    def check(self, ball_pos):
        return any(
            math.dist(ball_pos, pocket) <= self.radius for pocket in self.pockets
        )
