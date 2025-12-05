import pygame
import random
import math

class Assets:
    def __init__(self, game):
        self.g = game
        self.W = game.W
        self.H = game.H

        # fonts
        self.font = pygame.font.SysFont("Lato", 28)
        self.large_font = pygame.font.SysFont("Lato", 70)
        self.button_font = pygame.font.SysFont("Lato", 42)

        # sizes
        self.dia = 28
        self.radius = self.dia / 2

        # skins
        self.cue_skins = ["normal_cue.png", "japan_cue.png", "winter_cue.png"]
        self.table_skins = ["normal_table.png", "japan_table.png", "winter_table.png"]
        self.selected_cue_p1 = "normal_cue.png"
        self.selected_cue_p2 = "japan_cue.png"
        self.selected_table = "normal_table.png"

        # load menu bg & table
        try:
            self.menu_bg = pygame.image.load("assets/images/ball/billiards_Bg.png").convert()
            self.menu_bg = pygame.transform.scale(self.menu_bg, (self.W, self.H))
        except:
            self.menu_bg = pygame.Surface((self.W, self.H))
            self.menu_bg.fill((20, 80, 20))

        self.load_table_image()

        # sounds
        try:
            pygame.mixer.init()

            self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
            self.hit_sound.set_volume(0.8)

            self.collision_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
            self.collision_sound.set_volume(0.35)

            self.menu_music = pygame.mixer.Sound("assets/sounds/musik.wav")
            self.menu_music.set_volume(0.5)

            self.win_music = pygame.mixer.Sound("assets/sounds/menang.wav")
            self.win_music.set_volume(0.8)

        except:
            self.hit_sound = None
            self.collision_sound = None
            self.menu_music = None
            self.win_music = None

        # control music state
        self.music_on = True
        self.menu_music_playing = False

        # load cue previews
        self.cue_previews = {}
        for name in self.cue_skins:
            try:
                img = pygame.image.load(f"assets/images/cue/{name}").convert_alpha()
                self.cue_previews[name] = pygame.transform.smoothscale(img, (240, 20))
            except:
                self.cue_previews[name] = pygame.Surface((240, 20))

        # load table previews
        self.table_previews = {}
        for name in self.table_skins:
            try:
                img = pygame.image.load(f"assets/images/table/{name}").convert_alpha()
                self.table_previews[name] = pygame.transform.smoothscale(img, (260, 140))
            except:
                self.table_previews[name] = pygame.Surface((260, 140))

        # load ball images
        self.ball_images = []
        try:
            self.ball_images = [
                pygame.transform.smoothscale(
                    pygame.image.load(f"assets/images/ball/ball_{i}.png").convert_alpha(),
                    (self.dia, self.dia)
                ) for i in range(1, 17)
            ]
            self.shadow_img = pygame.transform.smoothscale(
                pygame.image.load("assets/images/ball/ball_Shadow.png").convert_alpha(),
                (self.dia, self.dia)
            )
            self.highlight_img = pygame.transform.smoothscale(
                pygame.image.load("assets/images/ball/ball_HighLight.png").convert_alpha(),
                (self.dia, self.dia)
            )
        except:
            for i in range(16):
                surf = pygame.Surface((self.dia, self.dia), pygame.SRCALPHA)
                pygame.draw.circle(surf, (200,200,200),
                                   (int(self.radius), int(self.radius)),
                                   int(self.radius))
                self.ball_images.append(surf)

            self.shadow_img = pygame.Surface((self.dia, self.dia), pygame.SRCALPHA)
            self.highlight_img = pygame.Surface((self.dia, self.dia), pygame.SRCALPHA)

        # sound icon
        self.sound_rect = pygame.Rect(self.W - 70, self.H - 70, 45, 45)

        # confetti
        self.confetti = []

    # ----------------------------------------------------------------------------------------------------------
    # MUSIC CONTROL
    # ----------------------------------------------------------------------------------------------------------

    def play_menu_music(self):
        """Play menu music if not yet playing."""
        if self.music_on and not self.menu_music_playing and self.menu_music:
            self.menu_music.play(-1)
            self.menu_music_playing = True

    def stop_menu_music(self):
        """Stop menu music."""
        if self.menu_music_playing:
            self.menu_music.stop()
            self.menu_music_playing = False

    # ----------------------------------------------------------------------------------------------------------
    # IMAGES
    # ----------------------------------------------------------------------------------------------------------

    def load_table_image(self):
        try:
            table = pygame.image.load(f"assets/images/table/{self.selected_table}").convert_alpha()
            self.table_image = pygame.transform.scale(table, (self.W, self.H))
        except:
            self.table_image = pygame.Surface((self.W, self.H))
            self.table_image.fill((30, 120, 40))

    # ----------------------------------------------------------------------------------------------------------
    # UI Utils
    # ----------------------------------------------------------------------------------------------------------

    def draw_button(self, screen, rect, text, hover):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        top = (230, 230, 230) if hover else (200, 200, 200)
        bot = (130, 130, 130) if hover else (100, 100, 100)

        for y in range(rect.height):
            t = y / rect.height
            r = top[0] * (1 - t) + bot[0] * t
            g = top[1] * (1 - t) + bot[1] * t
            b = top[2] * (1 - t) + bot[2] * t
            pygame.draw.line(s, (int(r), int(g), int(b)), (0, y), (rect.width, y))

        screen.blit(s, rect)
        pygame.draw.rect(screen, (255,255,255), rect, 2, border_radius=18)

        txt = self.button_font.render(text, True, (0, 0, 0))
        screen.blit(txt, (rect.x + rect.width//2 - txt.get_width()//2,
                          rect.y + rect.height//2 - txt.get_height()//2))

    def draw_sound_icon(self, screen, rect, on):
        pygame.draw.rect(screen, (30,30,30), rect, border_radius=10)
        pygame.draw.rect(screen, (200,200,200), rect, 2, border_radius=10)
        sx = rect.x + 10
        sy = rect.y + rect.height // 2
        pygame.draw.polygon(screen, (230,230,230),
                            [(sx, sy - 8), (sx, sy + 8), (sx + 12, sy)])
        pygame.draw.rect(screen, (230,230,230), (sx + 12, sy - 6, 5, 12))
        if on:
            pygame.draw.arc(screen, (230,230,230),
                             (rect.x + 26, rect.y + 8, 14, 14),
                             math.radians(-60), math.radians(60), 2)
            pygame.draw.arc(screen, (230,230,230),
                             (rect.x + 30, rect.y + 4, 20, 20),
                             math.radians(-60), math.radians(60), 2)
        else:
            pygame.draw.line(screen, (255,80,80),
                             (rect.x + 8, rect.y + 8),
                             (rect.x + rect.width - 8, rect.y + rect.height - 8), 3)
            pygame.draw.line(screen, (255,80,80),
                             (rect.x + 8, rect.y + rect.height - 8),
                             (rect.x + rect.width - 8, rect.y + 8), 3)

    @staticmethod
    def ray_sphere_intersection(ox, oy, dx, dy, cx, cy, R):
        lx = cx - ox
        ly = cy - oy
        t_ca = lx * dx + ly * dy
        if t_ca < 0:
            return None
        d2 = (lx*lx + ly*ly) - t_ca*t_ca
        R2 = R * R
        if d2 > R2:
            return None
        thc = (R2 - d2) ** 0.5
        t_hit = t_ca - thc
        if t_hit < 0:
            return None
        return t_hit

    # ----------------------------------------------------------------------------------------------------------
    # CONFETTI
    # ----------------------------------------------------------------------------------------------------------

    def spawn_confetti(self):
        for _ in range(80):
            self.confetti.append({
                "x": random.randint(0, self.W),
                "y": random.randint(-300, -10),
                "speed": random.uniform(2, 5),
                "color": (
                    random.randint(150,255),
                    random.randint(150,255),
                    random.randint(150,255)
                ),
                "size": random.randint(3, 6)
            })

    def draw_confetti(self, screen):
        for c in self.confetti:
            c["y"] += c["speed"]
            pygame.draw.rect(screen, c["color"],
                             (c["x"], c["y"], c["size"], c["size"]))
        self.confetti[:] = [c for c in self.confetti if c["y"] < self.H + 20]
