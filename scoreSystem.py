import pygame

class ScoreSystem:
    def __init__(self, lives=3):
        self.lives = lives
        self.score = 0
        self.potted_balls = []

    def lose_life(self):
        self.lives -= 1

    def add_potted(self, img, points=10):
        icon = pygame.transform.smoothscale(img, (28, 28))
        self.potted_balls.append(icon)
        self.score += points

    def is_dead(self):
        return self.lives <= 0
