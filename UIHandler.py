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
        # geser sedikit ke bawah (supaya nggak nabrak tulisan SCORE)
        # screen.get_height() = SCREEN_HEIGHT + BOTTOM_PANEL
        # kalau BOTTOM_PANEL = 50 → ini jadi: SCREEN_HEIGHT + 20
        base_y = screen.get_height() - 30

        for i, img in enumerate(images):
            x = base_x + i * 32
            screen.blit(img, (x, base_y))
