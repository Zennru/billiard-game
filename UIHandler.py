import pygame

class UIHandler:
    def __init__(self, font, large_font):
        self.font = font
        self.large_font = large_font

    def draw_text(self, screen, text, font, color, x, y):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

    def draw_potted(self, screen, images):
        for i, img in enumerate(images):
            screen.blit(img, (10 + i * 50, screen.get_height() - 40))
