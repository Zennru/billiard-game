import pygame

class EffectsManager:
    def __init__(self, game):
        self.assets = game.assets
        self.pocket_effects = []
        self.confetti_active = False
        self.win_music_played = False

    def add_pocket_effect(self, pos):
        self.pocket_effects.append({"pos": pos, "timer": 0})

    def update_and_draw(self, screen, game_over=False):
        # pocket rings
        for eff in self.pocket_effects[:]:
            eff["timer"] += 1
            r = max(0, 20 - eff["timer"] * 2)
            if r <= 0:
                self.pocket_effects.remove(eff)
            else:
                x, y = eff["pos"]
                pygame.draw.circle(screen, (255,255,255), (int(x), int(y)), r, 2)

        # confetti
        if game_over:
            if not self.assets.confetti:
                self.assets.spawn_confetti()
            self.assets.draw_confetti(screen)
