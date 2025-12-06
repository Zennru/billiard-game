import pygame
import math


class AimSystem:
    def __init__(self, gameplay):
        self.gp = gameplay
        self.g = gameplay.g
        self.assets = self.g.assets

    def draw(self):
        screen = self.g.screen
        cue_ball = self.gp.cue_ball
        balls = self.gp.balls

        bx, by = cue_ball.body.position
        mouse = pygame.mouse.get_pos()

        # arah cue
        angle = math.radians(self.gp.cue.angle)
        dx = math.cos(angle)
        dy = -math.sin(angle)

        # ========== HIT WALL ==========
        candidates = []
        left = 50
        right = self.g.W - 50
        top = 50
        bottom = self.g.H - 50

        if abs(dx) > 1e-6:
            if dx < 0:
                t = (left - bx) / dx
                if t > 0:
                    candidates.append(("wall_x", t, left))
            else:
                t = (right - bx) / dx
                if t > 0:
                    candidates.append(("wall_x", t, right))

        if abs(dy) > 1e-6:
            if dy < 0:
                t = (top - by) / dy
                if t > 0:
                    candidates.append(("wall_y", t, top))
            else:
                t = (bottom - by) / dy
                if t > 0:
                    candidates.append(("wall_y", t, bottom))

        t_wall = 2000
        hit_wall = None
        hit_type = None
        for kind, t, val in candidates:
            if t < t_wall:
                t_wall = t
                if kind == "wall_x":
                    hit_wall = (val, by + dy * t)
                else:
                    hit_wall = (bx + dx * t, val)
                hit_type = kind

        # ========== HIT BALL (ray-sphere) ==========
        R = self.gp.cue_ball.radius * 2
        t_ball = 2000
        first_ball = None
        for b in balls:
            if b is cue_ball:
                continue
            cx, cy = b.body.position
            t_hit = self.assets.ray_sphere_intersection(
                bx, by, dx, dy, cx, cy, R
            )
            if t_hit is not None and 0 < t_hit < t_ball:
                t_ball = t_hit
                first_ball = b

        if first_ball and t_ball < t_wall:
            first_hit = (bx + dx * t_ball, by + dy * t_ball)
            hit_ball_first = True
        else:
            first_hit = hit_wall
            hit_ball_first = False

        # garis utama
        if first_hit:
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(bx), int(by)),
                (int(first_hit[0]), int(first_hit[1])),
                3,
            )

        # ========== GHOST BALL ==========
        dxm = mouse[0] - bx
        dym = mouse[1] - by
        dlen = math.hypot(dxm, dym)
        if dlen > 1e-6:
            dxm /= dlen
            dym /= dlen

        first_hit_ball = None
        closest_dist = float("inf")
        for ball in balls:
            if ball is cue_ball:
                continue
            px = ball.body.position.x - bx
            py = ball.body.position.y - by
            proj = px * dxm + py * dym
            if proj <= 0:
                continue
            closest = abs(px * dym - py * dxm)
            if closest <= self.gp.cue_ball.radius * 2:
                if proj < closest_dist:
                    closest_dist = proj
                    first_hit_ball = ball

        if first_hit_ball:
            hx = bx + dxm * closest_dist
            hy = by + dym * closest_dist
            ghost_x = hx - dxm * (self.gp.cue_ball.radius * 2)
            ghost_y = hy - dym * (self.gp.cue_ball.radius * 2)
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(ghost_x), int(ghost_y)),
                int(self.gp.cue_ball.radius * 0.6),  # dibesarin dikit
                2,
            )

        # ========== HIGHLIGHT BOLA SESUAI KELOMPOK ==========
        if first_ball:
            ball_type = self.gp.get_ball_type_from_object(first_ball)
            own = self.gp.player_group[self.gp.current_player]

            color = (255, 255, 255)
            if ball_type == "eight":
                color = (255, 255, 0)  # kuning = bola 8
            elif own is not None:
                if ball_type == own:
                    color = (0, 255, 0)  # hijau = bola sendiri
                elif ball_type in ("solid", "stripe"):
                    color = (255, 80, 80)  # merah = bola lawan

            cx, cy = first_ball.body.position
            pygame.draw.circle(
                screen,
                color,
                (int(cx), int(cy)),
                int(self.gp.assets.radius + 3),
                2,
            )

        # ========== PREDIKSI AFTER-HIT ==========
        if hit_ball_first and first_ball:
            cx, cy = first_ball.body.position
            hx, hy = first_hit

            nx = cx - hx
            ny = cy - hy
            nlen = math.hypot(nx, ny)
            if nlen < 1e-6:
                nx, ny = dx, dy
                nlen = math.hypot(nx, ny)
            nx /= nlen
            ny /= nlen

            target_end = (hx + nx * 80, hy + ny * 80)
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(hx), int(hy)),
                (int(target_end[0]), int(target_end[1])),
                3,
            )

            dot = dx * nx + dy * ny
            projx = dot * nx
            projy = dot * ny
            cue_dx = dx - projx
            cue_dy = dy - projy
            clen = math.hypot(cue_dx, cue_dy)
            if clen < 1e-6:
                cue_dx, cue_dy = -ny, nx
                clen = math.hypot(cue_dx, cue_dy)
            cue_dx /= clen
            cue_dy /= clen

            cue_end = (hx + cue_dx * 40, hy + cue_dy * 40)
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(hx), int(hy)),
                (int(cue_end[0]), int(cue_end[1])),
                3,
            )
        else:
            # pantulan ke dinding
            if hit_type == "wall_x":
                rdx, rdy = -dx, dy
            elif hit_type == "wall_y":
                rdx, rdy = dx, -dy
            else:
                rdx, rdy = dx, dy

            if first_hit:
                end2 = (first_hit[0] + rdx * 200, first_hit[1] + rdy * 200)
                pygame.draw.line(
                    screen,
                    (200, 200, 200),
                    (int(first_hit[0]), int(first_hit[1])),
                    (int(end2[0]), int(end2[1])),
                    2,
                )
