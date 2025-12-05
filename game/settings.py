import pygame

class Settings:
    def __init__(self, game):
        self.g = game
        self.assets = game.assets

    def update(self):
        screen = self.g.screen
        screen.blit(self.assets.menu_bg, (0,0))
        dark = pygame.Surface((self.g.W, self.g.H), pygame.SRCALPHA)
        dark.fill((0,0,0,160))
        screen.blit(dark, (0,0))

        title = self.assets.large_font.render("SETTINGS", True, (255,255,255))
        screen.blit(title, (self.g.W//2 - title.get_width()//2, 40))

        screen.blit(self.assets.button_font.render("Player 1 Cue", True, (255,255,255)), (100,170))
        screen.blit(self.assets.button_font.render("Player 2 Cue", True, (255,255,255)), (100,280))
        screen.blit(self.assets.button_font.render("Table Skin", True, (255,255,255)), (100,390))

        screen.blit(self.assets.cue_previews[self.assets.selected_cue_p1], (100,210))
        screen.blit(self.assets.cue_previews[self.assets.selected_cue_p2], (100,320))
        screen.blit(self.assets.table_previews[self.assets.selected_table], (400,360))

        back_rect = pygame.Rect(40, 530, 180, 55)
        mx, my = pygame.mouse.get_pos()
        self.assets.draw_button(screen, back_rect, "< BACK", back_rect.collidepoint(mx, my))
        self.assets.draw_sound_icon(screen, self.assets.sound_rect, self.assets.music_on)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.g.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if 170 <= my <= 260:
                    idx = self.assets.cue_skins.index(self.assets.selected_cue_p1)
                    self.assets.selected_cue_p1 = self.assets.cue_skins[(idx + 1) % len(self.assets.cue_skins)]
                elif 280 <= my <= 360:
                    idx = self.assets.cue_skins.index(self.assets.selected_cue_p2)
                    self.assets.selected_cue_p2 = self.assets.cue_skins[(idx + 1) % len(self.assets.cue_skins)]
                elif 390 <= my <= 500:
                    idx = self.assets.table_skins.index(self.assets.selected_table)
                    self.assets.selected_table = self.assets.table_skins[(idx + 1) % len(self.assets.table_skins)]
                elif back_rect.collidepoint(mx, my):
                    self.g.state = 0

        pygame.display.update()
