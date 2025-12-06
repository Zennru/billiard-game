import pygame
import pymunk
import math
from ball import Ball
from cue import Cue
from table import Table
from pocket import Pocket
from scoreSystem import ScoreSystem
from UIHandler import UIHandler
from .aim_system import AimSystem
from .collision import CollisionManager
from .effects import EffectsManager

class Gameplay:
    def __init__(self, game):
        self.g = game
        self.assets = game.assets
        self.screen = game.screen

        # physics
        self.space = pymunk.Space()
        self.space.gravity = (0,0)
        self.space.damping = 0.90

        # systems
        self.score = ScoreSystem()
        self.ui = UIHandler(self.assets.font, self.assets.large_font)
        self.effects = EffectsManager(self.g)
        self.collision = CollisionManager(self)

        # table & pockets
        self.table = Table(self.space, self.g.W, self.g.H)
        self.pocket_system = Pocket(self.g.W, self.g.H)

        # balls
        self.balls = []
        self.ball_images = list(self.assets.ball_images)  # clone
        self.shadow = self.assets.shadow_img
        self.highlight = self.assets.highlight_img

        # build rack
        self._build_rack()

        # cue ball
        self.cue_ball_start = (self.g.W * 0.75, self.g.H / 2)
        self.cue_ball = Ball(self.space, self.assets.radius, self.cue_ball_start)
        self.balls.append(self.cue_ball)

        # cue
        cue_image = None
        try:
            skin = self.assets.selected_cue_p1
            cue_image = pygame.image.load(f"assets/images/cue/{skin}").convert_alpha()
        except:
            cue_image = pygame.Surface((100,10), pygame.SRCALPHA)
        self.cue = Cue(cue_image, self.cue_ball)

        # player state
        self.current_player = 1
        self.player_score = {1:0, 2:0}
        self.player_lives = {1:3, 2:3}

        self.powering_up = False
        self.force = 0
        self.max_force = 10000
        self.force_direction = 1
        self.ball_in_hand = False

        self.taking_shot = True
        self.prev_taking_shot = True

        self.pocket_effects = []

        self.game_over = False
        self.winner = None

        # aim helper
        self.aim = AimSystem(self)

    def _build_rack(self):
        rows = 5
        dia = self.assets.dia
        start_x = self.g.W * 0.25
        start_y = self.g.H * 0.40
        for col in range(5):
            for r in range(rows):
                pos = (start_x + col * (dia + 1), start_y + r * (dia + 1) + col * dia / 2)
                b = Ball(self.space, self.assets.radius, pos)
                self.balls.append(b)
            rows -= 1

    def get_ball_points(self, index: int) -> int:
        num = index + 1
        if num == 8:
            return 40
        elif num <= 7:
            return 20
        else:
            return 25

    def update(self):
        # handle menu music status (assets)
        if self.g.state == 2:
            if self.assets.menu_music and self.assets.menu_music.get_num_channels() > 0:
                self.assets.menu_music.stop()

        # physics step
        self.space.step(1 / self.g.FPS)
        self.screen.blit(self.assets.table_image, (0,0))

        # game over mode
        if self.game_over:
            overlay = pygame.Surface((self.g.W, self.g.H), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))

            base_text = self.assets.large_font.render(f"PLAYER {self.winner} WINS!", True, (255,255,0))
            glow_text = self.assets.large_font.render(f"PLAYER {self.winner} WINS!", True, (255,255,255))
            self.screen.blit(glow_text, (self.g.W//2 - glow_text.get_width()//2, self.g.H//2 - 90))

            zoom = 1.0 + math.sin(pygame.time.get_ticks() * 0.004) * 0.05
            scaled = pygame.transform.smoothscale(base_text, (int(base_text.get_width() * zoom), int(base_text.get_height() * zoom)))
            self.screen.blit(scaled, (self.g.W//2 - scaled.get_width()//2, self.g.H//2 - 90))

            # confetti and restart text
            self.effects.update_and_draw(self.screen, game_over=True)
            alpha = min(255, int((pygame.time.get_ticks() * 0.25) % 255))
            restart_text = self.assets.font.render("Press R to Restart", True, (255,255,255))
            restart_surface = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
            restart_surface.blit(restart_text, (0,0))
            restart_surface.set_alpha(alpha)
            self.screen.blit(restart_surface, (self.g.W//2 - restart_text.get_width()//2, self.g.H//2 + 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.g.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if self.assets.win_music:
                        self.assets.win_music.stop()
                    # reset game (simple full reset by reinitializing object)
                    self.__init__(self.g)
            pygame.display.update()
            return

        # pocket check
        potted_info = []
        for ball in self.balls[:]:
            pos = ball.body.position
            if self.pocket_system.check(pos):
                if ball is self.cue_ball:
                    if not self.ball_in_hand:
                        self.player_lives[self.current_player] -= 1
                        self.ball_in_hand = True
                    ball.body.velocity = (0,0)
                    ball.body.position = (-200, -200)
                    continue

                idx = self.balls.index(ball)
                pts = self.get_ball_points(idx)
                img = self.ball_images[idx]
                potted_info.append({"ball": ball, "index": idx, "image": img, "pos": pos, "points": pts})
                ball.body.velocity = (0,0)
                ball.body.position = (-200, -200)

        # process potted
        for info in sorted(potted_info, key=lambda x: x["index"], reverse=True):
            b = info["ball"]; idx = info["index"]
            self.score.add_potted(info["image"], self.current_player)
            self.player_score[self.current_player] += info["points"]
            if b in self.collision.last_vel:
                del self.collision.last_vel[b]
            self.space.remove(b.body, b.shape)
            self.balls.pop(idx)
            if idx < len(self.ball_images):
                self.ball_images.pop(idx)
            self.effects.add_pocket_effect(info["pos"])

        # collision checks
        self.collision.check()

        # draw balls
        for i, ball in enumerate(self.balls):
            # safety if images fewer than balls
            img = self.ball_images[i] if i < len(self.ball_images) else None
            ball.draw(self.screen, img, self.shadow, self.highlight)

        # draw pocket effect rings & confetti if any
        self.effects.update_and_draw(self.screen)

        # shot ready check
        taking_shot = all(ball.is_stopped() for ball in self.balls)
        if taking_shot and not self.prev_taking_shot and not self.ball_in_hand:
            # change player turn
            self.current_player = 2 if self.current_player == 1 else 1
            skin = self.assets.selected_cue_p1 if self.current_player == 1 else self.assets.selected_cue_p2
            try:
                cue_img = pygame.image.load(f"assets/images/cue/{skin}").convert_alpha()
            except:
                cue_img = self.cue.original
            self.cue = Cue(cue_img, self.cue_ball)

        self.prev_taking_shot = taking_shot

        # game over check
        if self.player_lives[1] <= 0 and self.winner is None:
            self.winner = 2
            self.game_over = True
            for b in self.balls: b.body.velocity = (0,0)
            if self.assets.win_music: self.assets.win_music.play()
        elif self.player_lives[2] <= 0 and self.winner is None:
            self.winner = 1
            self.game_over = True
            for b in self.balls: b.body.velocity = (0,0)
            if self.assets.win_music: self.assets.win_music.play()

        # ball in hand handling
        if self.ball_in_hand:
            mx, my = pygame.mouse.get_pos()
            if 50 + self.assets.radius < mx < self.g.W - 50 - self.assets.radius and 50 + self.assets.radius < my < self.g.H - 50 - self.assets.radius:
                self.cue_ball.body.position = (mx, my)
                self.cue_ball.body.velocity = (0,0)
            cx, cy = self.cue_ball.body.position
            pygame.draw.circle(self.screen, (0,255,0), (int(cx), int(cy)), int(self.assets.radius + 3), 2)

        # aim & cue (only when ready and not ball in hand)
        if taking_shot and not self.ball_in_hand:
            mouse = pygame.mouse.get_pos()
            self.cue.update(mouse)

            # draw aim lines and ghost ball via AimSystem
            self.aim.draw()
            self.cue.draw(self.screen)

        # power bar logic
        if self.powering_up and taking_shot and not self.ball_in_hand:
            self.force += 120 * self.force_direction
            if self.force >= self.max_force or self.force <= 0:
                self.force_direction *= -1
            bx, by = self.cue_ball.body.position
            bar_width = int((self.force / self.max_force) * 110)
            pygame.draw.rect(self.screen, (255,0,0), (int(bx - 55), int(by + 35), bar_width, 10))

        # bottom panel draw
        pygame.draw.rect(self.screen, (40,40,40), (0, self.g.H, self.g.W, self.g.BOTTOM))
        p1_text = f"P1 Score:{self.player_score[1]} | Lives:{self.player_lives[1]}"
        self.ui.draw_text(self.screen, p1_text, self.assets.font, (255,255,255), 20, self.g.H + 5)
        self.ui.draw_potted_for_player(self.screen, self.score.potted_p1, 20, self.g.H + 28)

        p2_text = f"P2 Score:{self.player_score[2]} | Lives:{self.player_lives[2]}"
        p2_w = self.assets.font.render(p2_text, True, (0,0,0)).get_width()
        p2_x = self.g.W - p2_w - 20
        self.ui.draw_text(self.screen, p2_text, self.assets.font, (255,255,255), p2_x, self.g.H + 5)
        icons_w = len(self.score.potted_p2) * 26
        icons_start = self.g.W - icons_w - 20
        self.ui.draw_potted_for_player(self.screen, self.score.potted_p2, icons_start, self.g.H + 28)

        turn_text = self.assets.font.render(f"Turn: P{self.current_player}", True, (255,255,0))
        self.screen.blit(turn_text, (self.g.W//2 - turn_text.get_width()//2, self.g.H + 10))

        # input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.g.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.ball_in_hand:
                    pass
                elif taking_shot:
                    self.powering_up = True

            if event.type == pygame.MOUSEBUTTONUP:
                if self.ball_in_hand:
                    self.ball_in_hand = False
                else:
                    if self.powering_up and taking_shot:
                        if self.assets.hit_sound: self.assets.hit_sound.play()
                        self.cue.shoot(self.force)
                    self.powering_up = False
                    self.force = 0
                    self.force_direction = 1

        pygame.display.update()
