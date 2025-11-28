import pygame

class ScoreSystem:
    def __init__(self, lives=3):
        self.lives = lives
        self.potted_balls = []
        self.score = 0

    def lose_life(self):
        self.lives -= 1

    def add_potted(self, img, points=10):
        # kecilkan gambar bola untuk bar bawah
        icon = pygame.transform.smoothscale(img, (26, 26))
        self.potted_balls.append(icon)
        self.score += points

    def is_dead(self):
        return self.lives <= 0
