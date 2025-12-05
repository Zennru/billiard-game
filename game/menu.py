import pygame
from .state import STATE_SETTINGS, STATE_GAME

class Menu:
    def __init__(self, game):
        self.g = game
        self.assets = game.assets

    def update(self):
        # Play music immediately when menu opens
        self.assets.play_menu_music()

        screen = self.g.screen
        screen.blit(self.assets.menu_bg, (0, 0))

        overlay = pygame.Surface((self.g.W, self.g.H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = self.assets.large_font.render("POOL GAME", True, (255, 255, 255))
        screen.blit(title, (self.g.W//2 - title.get_width()//2, 80))

        play_rect = pygame.Rect(self.g.W // 2 - 200, 240, 400, 70)
        set_rect  = pygame.Rect(self.g.W // 2 - 200, 330, 400, 70)
        quit_rect = pygame.Rect(self.g.W // 2 - 200, 420, 400, 70)

        mx, my = pygame.mouse.get_pos()
        self.assets.draw_button(screen, play_rect, "PLAY", play_rect.collidepoint(mx, my))
        self.assets.draw_button(screen, set_rect, "SETTINGS", set_rect.collidepoint(mx, my))
        self.assets.draw_button(screen, quit_rect, "QUIT", quit_rect.collidepoint(mx, my))

        self.assets.draw_sound_icon(screen, self.assets.sound_rect, self.assets.music_on)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.g.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                ex, ey = event.pos

                # toggle mute
                if self.assets.sound_rect.collidepoint(ex, ey):
                    self.assets.music_on = not self.assets.music_on

                    if self.assets.music_on:
                        self.assets.play_menu_music()
                    else:
                        self.assets.stop_menu_music()

                elif play_rect.collidepoint(ex, ey):
                    self.assets.stop_menu_music()
                    self.assets.load_table_image()
                    self.g.state = STATE_GAME

                elif set_rect.collidepoint(ex, ey):
                    self.g.state = STATE_SETTINGS

                elif quit_rect.collidepoint(ex, ey):
                    self.g.running = False

        pygame.display.update()
