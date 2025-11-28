import pygame

class UIHandler:
    def __init__(self, font, large_font):
        self.font = font
        self.large_font = large_font

    def draw_text(self, screen, text, font, color, x, y):
        img = font.render(text, True, color)
        screen.blit(img, (x, y))

    def draw_potted(self, screen, images):
        base_x = 10
        base_y = screen.get_height() - 42
        for i, img in enumerate(images):
            x = base_x + i * 32
            screen.blit(img, (x, base_y))
