import pygame


class UIHandler:
    def __init__(self, font, large):
        self.font = font
        self.large = large

    def draw_text(self, screen, text, font, color, x, y):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

    def draw_potted_for_player(self, screen, icons, start_x, y):
        x = start_x
        for img in icons:
            screen.blit(img, (x, y))
            x += 26
