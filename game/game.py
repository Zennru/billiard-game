import pygame
from .state import STATE_MENU, STATE_SETTINGS, STATE_GAME
from .assets_loader import Assets
from .menu import Menu
from .settings import Settings
from .gameplay import Gameplay

class Game:
    def __init__(self):
        pygame.init()

        # screen
        self.W, self.H = 1100, 600
        self.BOTTOM = 50
        self.screen = pygame.display.set_mode((self.W, self.H + self.BOTTOM))
        pygame.display.set_caption("Pool Game")

        # clock
        self.clock = pygame.time.Clock()
        self.FPS = 120

        # assets loader
        self.assets = Assets(self)

        # state
        self.state = STATE_MENU
        self.running = True

        # state controllers
        self.menu = Menu(self)
        self.settings = Settings(self)
        self.gameplay = Gameplay(self)

    def run(self):
        while self.running:
            self.clock.tick(self.FPS)

            if self.state == STATE_MENU:
                self.menu.update()
            elif self.state == STATE_SETTINGS:
                self.settings.update()
            elif self.state == STATE_GAME:
                self.gameplay.update()

        pygame.quit()
