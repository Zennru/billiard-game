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
        self.space.gravity = (0, 0)
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
        self.ball_images = list(self.assets.ball_images)  # clone gambar
        self.shadow = self.assets.shadow_img
        self.highlight = self.assets.highlight_img

        # mapping Ball -> tipe ("solid", "stripe", "eight", atau None)
        self.ball_type = {}

        # build rack 15 bola object
        self._build_rack()

        # cue ball
        self.cue_ball_start = (self.g.W * 0.75, self.g.H / 2)
        self.cue_ball = Ball(self.space, self.assets.radius, self.cue_ball_start)
        self.balls.append(self.cue_ball)
        self.ball_type[self.cue_ball] = None  # cue ball tidak punya tipe kelompok

        # cue
        try:
            skin = self.assets.selected_cue_p1
            cue_image = pygame.image.load(
                f"assets/images/cue/{skin}"
            ).convert_alpha()
        except:
            cue_image = pygame.Surface((100, 10), pygame.SRCALPHA)
        self.cue = Cue(cue_image, self.cue_ball)

        # player state
        self.current_player = 1
        self.player_score = {1: 0, 2: 0}
        self.player_lives = {1: 3, 2: 3}  # masih dipakai sebagai nyawa scratch

        self.powering_up = False
        self.force = 0
        self.max_force = 10000
        self.force_direction = 1
        self.ball_in_hand = False
        # saat baru mulai game, beri kesempatan Player 1 menempatkan cue ball
        # sebelum break; dibatasi agar tidak melewati garis tengah meja
        self.placing_cue_initial = True

        self.taking_shot = True
        self.prev_taking_shot = True

        self.game_over = False
        self.winner = None

        # 8-ball rules state
        self.groups_assigned = False
        self.player_group = {1: None, 2: None}  # "solid"/"stripe"
        self.remaining = {"solid": 7, "stripe": 7, "eight": 1}
        self.is_break_shot = True

        # per-shot state
        self.shot_active = False
        self.shot_potted_types = []  # list tipe bola yg masuk di shot ini
        self.first_hit_ball = None
        self.first_hit_type = None
        self.scratch_this_shot = False
        self.foul_committed = False
        self.foul_type = None

        # simple turn timer
        self.turn_time_seconds = 20
        self.turn_timer = self.g.FPS * self.turn_time_seconds

        # foul popup
        self.foul_message = ""
        self.foul_timer = 0

        # aim helper
        self.aim = AimSystem(self)

    # ===================== HELPER RULES =====================

    def _build_rack(self):
        rows = 5
        dia = self.assets.dia
        start_x = self.g.W * 0.25
        start_y = self.g.H * 0.40

        for col in range(5):
            for r in range(rows):
                pos = (
                    start_x + col * (dia + 1),
                    start_y + r * (dia + 1) + col * dia / 2,
                )
                b = Ball(self.space, self.assets.radius, pos)
                self.balls.append(b)

                # nomor bola berdasarkan urutan masuk ke list (1..15)
                num = len(self.balls)
                if num == 8:
                    t = "eight"
                elif 1 <= num <= 7:
                    t = "solid"
                elif 9 <= num <= 15:
                    t = "stripe"
                else:
                    t = None
                self.ball_type[b] = t

            rows -= 1

    def get_ball_points(self, index: int) -> int:
        num = index + 1
        if num == 8:
            return 40
        elif num <= 7:
            return 20
        else:
            return 20

    def get_ball_type(self, index: int):
        """Jika perlu dari index, ambil via object."""
        if 0 <= index < len(self.balls):
            ball = self.balls[index]
            return self.ball_type.get(ball)
        return None

    def get_ball_type_from_object(self, ball):
        """Dipakai AimSystem untuk tahu solid/stripe/eight."""
        return self.ball_type.get(ball)

    def _start_shot(self):
        """Dipanggil saat cue ditembak (mouse up)."""
        self.shot_active = True
        self.shot_potted_types = []
        self.first_hit_ball = None
        self.first_hit_type = None
        self.scratch_this_shot = False
        self.foul_committed = False
        self.foul_type = None

    def _update_first_hit(self):
        """Deteksi bola pertama yg disentuh cue ball di shot ini."""
        if not self.shot_active or self.first_hit_ball is not None:
            return

        cbx, cby = self.cue_ball.body.position
        R = self.assets.radius * 2 + 0.5
        R2 = R * R

        for b in self.balls:
            if b is self.cue_ball:
                continue
            x, y = b.body.position
            dx = x - cbx
            dy = y - cby
            if dx * dx + dy * dy <= R2:
                self.first_hit_ball = b
                self.first_hit_type = self.get_ball_type_from_object(b)
                break

    def _mark_foul(self, msg: str):
        self.foul_committed = True
        self.foul_type = msg
        self.foul_message = "Foul: " + msg
        self.foul_timer = int(self.g.FPS * 2)  # popup ~2 detik

    def _resolve_groups_if_needed(self):
        """Menentukan kelompok (solid/stripe) jika meja masih open."""
        if self.groups_assigned:
            return
        if self.is_break_shot:
            # saat break, belum menentukan kelompok walau ada bola masuk
            return
        if self.foul_committed:
            # foul -> meja tetap open
            return

        solids = [t for t in self.shot_potted_types if t == "solid"]
        stripes = [t for t in self.shot_potted_types if t == "stripe"]
        if not solids and not stripes:
            return

        # kalau dua jenis, pakai jenis terakhir yang masuk
        last_type = None
        for t in self.shot_potted_types:
            if t in ("solid", "stripe"):
                last_type = t

        if last_type is None:
            return

        if solids and not stripes:
            chosen = "solid"
        elif stripes and not solids:
            chosen = "stripe"
        else:
            chosen = last_type

        self.player_group[self.current_player] = chosen
        other = 2 if self.current_player == 1 else 1
        self.player_group[other] = "solid" if chosen == "stripe" else "stripe"
        self.groups_assigned = True

    def _resolve_eight_ball_outcome(self):
        """Cek apakah bola 8 bikin menang/kalah."""
        shooter = self.current_player
        opponent = 2 if shooter == 1 else 1
        own = self.player_group[shooter]

        potted_eight = self.shot_potted_types.count("eight")
        if potted_eight == 0:
            return

        # kalau kelompok belum ditentukan sama sekali -> kalah
        if not self.groups_assigned:
            self.winner = opponent
            self.game_over = True
            self._finish_game()
            return

        # masih ada bola kelompok sendiri -> kalah
        if own is not None and self.remaining[own] > 0:
            self.winner = opponent
            self.game_over = True
            self._finish_game()
            return

        # shot ini foul + bola 8 masuk -> kalah
        if self.foul_committed:
            self.winner = opponent
            self.game_over = True
            self._finish_game()
            return

        # selain itu -> bola 8 legal, shooter menang
        self.winner = shooter
        self.game_over = True
        self._finish_game()

    def _finish_game(self):
        for b in self.balls:
            b.body.velocity = (0, 0)
        if self.assets.win_music:
            self.assets.win_music.play()

    def _resolve_shot(self):
        """Dipanggil ketika semua bola sudah berhenti setelah sebuah shot."""
        if not self.shot_active:
            return

        shooter = self.current_player
        opponent = 2 if shooter == 1 else 1
        own_group = self.player_group[shooter]
        opp_group = self.player_group[opponent]

        # ---------- FOUL CHECK ----------
        # 1. scratch
        if self.scratch_this_shot:
            self._mark_foul("Scratch")

        # 2. no contact
        if self.first_hit_ball is None:
            self._mark_foul("No Contact")

        # 3. wrong ball first / kena 8 duluan
        if self.groups_assigned and own_group is not None:
            if self.first_hit_type == "eight":
                if self.remaining[own_group] > 0:
                    self._mark_foul("Hit 8 Ball Early")
            elif (
                self.first_hit_type is not None
                and self.first_hit_type != own_group
            ):
                self._mark_foul("Wrong Ball First")

        # ---------- EIGHT BALL OUTCOME ----------
        self._resolve_eight_ball_outcome()
        if self.game_over:
            self.shot_active = False
            return

        # ---------- GROUP ASSIGNMENT ----------
        self._resolve_groups_if_needed()

        # ---------- TURN DECISION ----------
        potted_own = (
            self.shot_potted_types.count(own_group) if own_group else 0
        )
        potted_opp = (
            self.shot_potted_types.count(opp_group) if opp_group else 0
        )
        potted_any = len(self.shot_potted_types) > 0

        continue_turn = False

        if self.foul_committed:
            # foul -> ball in hand untuk lawan
            self.ball_in_hand = True
            self.current_player = opponent
        else:
            if self.is_break_shot:
                # saat break: kalau ada bola masuk → lanjut turn
                continue_turn = potted_any
            elif not self.groups_assigned:
                # meja masih open
                continue_turn = potted_any
            else:
                # kelompok sudah fix
                if potted_own > 0:
                    continue_turn = True
                elif potted_opp > 0 and potted_own == 0:
                    continue_turn = False
                elif potted_opp > 0 and potted_own > 0:
                    continue_turn = True
                else:
                    continue_turn = False

            if not continue_turn:
                self.current_player = opponent

        # break hanya sekali di awal
        if self.is_break_shot:
            self.is_break_shot = False

        # update cue skin pemain yg akan main
        skin = (
            self.assets.selected_cue_p1
            if self.current_player == 1
            else self.assets.selected_cue_p2
        )
        try:
            cue_img = pygame.image.load(
                f"assets/images/cue/{skin}"
            ).convert_alpha()
        except:
            cue_img = self.cue.original
        self.cue = Cue(cue_img, self.cue_ball)

        # reset shot dan timer turn baru
        self.shot_active = False
        self.turn_timer = self.g.FPS * self.turn_time_seconds

    # ===================== MAIN UPDATE LOOP =====================

    def update(self):
        # pastikan musik menu berhenti ketika di game
        if self.g.state == 2:
            if (
                self.assets.menu_music
                and self.assets.menu_music.get_num_channels() > 0
            ):
                self.assets.menu_music.stop()

        # step physics
        self.space.step(1 / self.g.FPS)
        self.screen.blit(self.assets.table_image, (0, 0))

        # ========== GAME OVER MODE ==========
        if self.game_over:
            overlay = pygame.Surface((self.g.W, self.g.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            base_text = self.assets.large_font.render(
                f"PLAYER {self.winner} WINS!", True, (255, 255, 0)
            )
            glow_text = self.assets.large_font.render(
                f"PLAYER {self.winner} WINS!", True, (255, 255, 255)
            )
            self.screen.blit(
                glow_text,
                (
                    self.g.W // 2 - glow_text.get_width() // 2,
                    self.g.H // 2 - 90,
                ),
            )

            zoom = 1.0 + math.sin(pygame.time.get_ticks() * 0.004) * 0.05
            scaled = pygame.transform.smoothscale(
                base_text,
                (
                    int(base_text.get_width() * zoom),
                    int(base_text.get_height() * zoom),
                ),
            )
            self.screen.blit(
                scaled,
                (
                    self.g.W // 2 - scaled.get_width() // 2,
                    self.g.H // 2 - 90,
                ),
            )

            # confetti dan tulisan restart
            self.effects.update_and_draw(self.screen, game_over=True)
            alpha = min(255, int((pygame.time.get_ticks() * 0.25) % 255))
            restart_text = self.assets.font.render(
                "Press R to Restart", True, (255, 255, 255)
            )
            restart_surface = pygame.Surface(
                restart_text.get_size(), pygame.SRCALPHA
            )
            restart_surface.blit(restart_text, (0, 0))
            restart_surface.set_alpha(alpha)
            self.screen.blit(
                restart_surface,
                (
                    self.g.W // 2 - restart_text.get_width() // 2,
                    self.g.H // 2 + 10,
                ),
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.g.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if self.assets.win_music:
                        self.assets.win_music.stop()
                    self.__init__(self.g)

            pygame.display.update()
            return

        # ========== TURN TIMER ==========
        taking_shot_now = all(ball.is_stopped() for ball in self.balls)
        if (
            taking_shot_now
            and not self.ball_in_hand
            and not self.shot_active
        ):
            if self.turn_timer > 0:
                self.turn_timer -= 1
            else:
                # timeout → foul: berikan ball-in-hand ke lawan dan ganti giliran
                self._mark_foul("Time Out")
                opponent = 2 if self.current_player == 1 else 1
                # foul memberi ball-in-hand ke lawan
                self.ball_in_hand = True
                self.current_player = opponent

                # update skin cue pemain yang baru
                skin = (
                    self.assets.selected_cue_p1
                    if self.current_player == 1
                    else self.assets.selected_cue_p2
                )
                try:
                    cue_img = pygame.image.load(
                        f"assets/images/cue/{skin}"
                    ).convert_alpha()
                except:
                    cue_img = self.cue.original
                self.cue = Cue(cue_img, self.cue_ball)

                # reset turn timer dan flags terkait
                self.turn_timer = self.g.FPS * self.turn_time_seconds
                self.shot_active = False
                taking_shot_now = all(ball.is_stopped() for ball in self.balls)

        # update first-hit detector
        self._update_first_hit()

        # ========== POCKET CHECK ==========
        potted_info = []
        for ball in self.balls[:]:
            pos = ball.body.position
            if self.pocket_system.check(pos):
                if ball is self.cue_ball:
                    if not self.ball_in_hand:
                        self.player_lives[self.current_player] -= 1
                        self.ball_in_hand = True
                    self.scratch_this_shot = True
                    ball.body.velocity = (0, 0)
                    ball.body.position = (-200, -200)
                    continue

                idx = self.balls.index(ball)
                pts = self.get_ball_points(idx)
                img = self.ball_images[idx]
                potted_info.append(
                    {
                        "ball": ball,
                        "index": idx,
                        "image": img,
                        "pos": pos,
                        "points": pts,
                    }
                )
                ball.body.velocity = (0, 0)
                ball.body.position = (-200, -200)

        # proses bola yg masuk
        for info in sorted(potted_info, key=lambda x: x["index"], reverse=True):
            b = info["ball"]
            idx = info["index"]

            self.score.add_potted(info["image"], self.current_player)
            self.player_score[self.current_player] += info["points"]

            # tipe diambil dari object, bukan index
            btype = self.ball_type.get(b)
            if btype in self.remaining:
                self.remaining[btype] -= 1
                if self.shot_active:
                    self.shot_potted_types.append(btype)

            # hapus dari mapping & world
            if b in self.ball_type:
                del self.ball_type[b]
            if b in self.collision.last_vel:
                del self.collision.last_vel[b]

            self.space.remove(b.body, b.shape)
            self.balls.pop(idx)
            if idx < len(self.ball_images):
                self.ball_images.pop(idx)

            self.effects.add_pocket_effect(info["pos"])

        # collision sound / logic
        self.collision.check()

        # draw balls
        for i, ball in enumerate(self.balls):
            img = self.ball_images[i] if i < len(self.ball_images) else None
            ball.draw(self.screen, img, self.shadow, self.highlight)

        # efek pocket ring + confetti (kalau game_over False, hanya lingkaran)
        self.effects.update_and_draw(self.screen)

        # shot ready check & resolve turn
        taking_shot = taking_shot_now
        if taking_shot and not self.prev_taking_shot:
            self._resolve_shot()
        self.prev_taking_shot = taking_shot
        self.taking_shot = taking_shot

        # backup: game over kalau nyawa habis
        if self.player_lives[1] <= 0 and self.winner is None:
            self.winner = 2
            self.game_over = True
            self._finish_game()
        elif self.player_lives[2] <= 0 and self.winner is None:
            self.winner = 1
            self.game_over = True
            self._finish_game()

        # ball in hand handling
        # initial cue placement (Player 1 at game start)
        if self.placing_cue_initial and self.current_player == 1 and self.is_break_shot:
            mx, my = pygame.mouse.get_pos()
            min_x = int(self.g.W // 1.4 + self.assets.radius + 1)
            max_x = int(self.g.W - 50 - self.assets.radius)
            min_y = int(50 + self.assets.radius)
            max_y = int(self.g.H - 50 - self.assets.radius)
            px = max(min_x, min(mx, max_x))
            py = max(min_y, min(my, max_y))
            self.cue_ball.body.position = (px, py)
            self.cue_ball.body.velocity = (0, 0)
            cx, cy = self.cue_ball.body.position
            # outline to show placement
            pygame.draw.circle(
                self.screen,
                (0, 200, 0),
                (int(cx), int(cy)),
                int(self.assets.radius + 4),
                2,
            )
            # instruction text
            instr = self.assets.font.render(
                "Place cue ball (Player 1) - Click to confirm", True, (255, 255, 255)
            )
            self.screen.blit(instr, (20, 20))
        elif self.ball_in_hand:
            mx, my = pygame.mouse.get_pos()
            if (
                50 + self.assets.radius
                < mx
                < self.g.W - 50 - self.assets.radius
                and 50 + self.assets.radius
                < my
                < self.g.H - 50 - self.assets.radius
            ):
                self.cue_ball.body.position = (mx, my)
                self.cue_ball.body.velocity = (0, 0)
            cx, cy = self.cue_ball.body.position
            pygame.draw.circle(
                self.screen,
                (0, 255, 0),
                (int(cx), int(cy)),
                int(self.assets.radius + 3),
                2,
            )

        # aim & cue (hanya kalau siap dan tidak ball in hand dan bukan sedang menempatkan awal)
        if taking_shot and not self.ball_in_hand and not getattr(self, 'placing_cue_initial', False):
            mouse = pygame.mouse.get_pos()
            self.cue.update(mouse)
            self.aim.draw()
            self.cue.draw(self.screen)

        # power bar
        if self.powering_up and taking_shot and not self.ball_in_hand:
            self.force += 120 * self.force_direction
            if self.force >= self.max_force or self.force <= 0:
                self.force_direction *= -1
            bx, by = self.cue_ball.body.position
            bar_width = int((self.force / self.max_force) * 110)
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (int(bx - 55), int(by + 35), bar_width, 10),
            )

        # bottom panel
        pygame.draw.rect(
            self.screen,
            (40, 40, 40),
            (0, self.g.H, self.g.W, self.g.BOTTOM),
        )

        # P1
        p1_text = f"P1 Score:{self.player_score[1]} | Lives:{self.player_lives[1]}"
        self.ui.draw_text(
            self.screen,
            p1_text,
            self.assets.font,
            (255, 255, 255),
            20,
            self.g.H + 5,
        )
        self.ui.draw_potted_for_player(
            self.screen, self.score.potted_p1, 20, self.g.H + 28
        )

        # P2
        p2_text = f"P2 Score:{self.player_score[2]} | Lives:{self.player_lives[2]}"
        p2_w = self.assets.font.render(p2_text, True, (0, 0, 0)).get_width()
        p2_x = self.g.W - p2_w - 20
        self.ui.draw_text(
            self.screen,
            p2_text,
            self.assets.font,
            (255, 255, 255),
            p2_x,
            self.g.H + 5,
        )
        icons_w = len(self.score.potted_p2) * 26
        icons_start = self.g.W - icons_w - 20
        self.ui.draw_potted_for_player(
            self.screen, self.score.potted_p2, icons_start, self.g.H + 28
        )

        # turn & group display
        group_p1 = self.player_group[1] or "-"
        group_p2 = self.player_group[2] or "-"
        turn_text = self.assets.font.render(
            f"Turn: P{self.current_player}", True, (255, 255, 0)
        )
        self.screen.blit(
            turn_text,
            (
                self.g.W // 2 - turn_text.get_width() // 2,
                self.g.H + 5,
            ),
        )

        g1 = self.assets.font.render(f"P1: {group_p1}", True, (200, 200, 200))
        g2 = self.assets.font.render(f"P2: {group_p2}", True, (200, 200, 200))
        self.screen.blit(g1, (20, self.g.H - 20))
        self.screen.blit(g2, (self.g.W - g2.get_width() - 20, self.g.H - 20))

        # timer di tengah bawah
        sec_left = max(0, self.turn_timer // self.g.FPS)
        timer_txt = self.assets.font.render(
            f"Timer: {sec_left}s", True, (255, 200, 0)
        )
        self.screen.blit(
            timer_txt,
            (
                self.g.W // 2 - timer_txt.get_width() // 2,
                self.g.H + 28,
            ),
        )

        # foul popup
        if self.foul_timer > 0 and self.foul_message:
            self.foul_timer -= 1
            msg_img = self.assets.large_font.render(
                self.foul_message, True, (255, 80, 80)
            )
            bg = pygame.Surface(
                (msg_img.get_width() + 40, msg_img.get_height() + 20),
                pygame.SRCALPHA,
            )
            bg.fill((0, 0, 0, 160))
            cx = self.g.W // 2 - bg.get_width() // 2
            cy = 60
            self.screen.blit(bg, (cx, cy))
            self.screen.blit(
                msg_img,
                (
                    self.g.W // 2 - msg_img.get_width() // 2,
                    cy + 10,
                ),
            )

        # input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.g.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if getattr(self, 'placing_cue_initial', False):
                    # klik untuk mengunci posisi dan lanjut permainan
                    self.placing_cue_initial = False
                    self.turn_timer = self.g.FPS * self.turn_time_seconds
                elif self.ball_in_hand:
                    pass
                elif self.taking_shot:
                    self.powering_up = True

            if event.type == pygame.MOUSEBUTTONUP:
                if self.ball_in_hand:
                    self.ball_in_hand = False
                    self.turn_timer = self.g.FPS * self.turn_time_seconds
                else:
                    if self.powering_up and self.taking_shot:
                        if self.assets.hit_sound:
                            self.assets.hit_sound.play()
                        self._start_shot()
                        self.cue.shoot(self.force)
                    self.powering_up = False
                    self.force = 0
                    self.force_direction = 1

        pygame.display.update()
