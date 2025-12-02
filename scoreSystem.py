import pygame


class ScoreSystem:
    def __init__(self):
        self.potted_p1 = []
        self.potted_p2 = []

    def add_potted(self, img, player):
        icon = pygame.transform.smoothscale(img, (24, 24))
        if player == 1:
            self.potted_p1.append(icon)
        else:
            self.potted_p2.append(icon)
