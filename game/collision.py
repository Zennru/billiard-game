import math

class CollisionManager:
    def __init__(self, gameplay):
        self.gp = gameplay
        self.g = gameplay.g
        self.last_vel = {b: (0,0) for b in getattr(self.gp, 'balls', [])}

    def check(self):
        # ball-wall sounds
        seen_pairs = set()
        balls = self.gp.balls
        radius = self.g.assets.radius

        for b in balls:
            vx, vy = b.body.velocity
            pvx, pvy = self.last_vel.get(b, (0,0))
            x, y = b.body.position
            speed = math.hypot(vx, vy)

            left = 50 + radius
            right = self.g.W - 50 - radius
            top = 50 + radius
            bottom = self.g.H - 50 - radius

            if abs(vx) > 20 and vx * pvx < 0 and (x <= left + 1 or x >= right - 1):
                if speed > 80 and self.g.assets.collision_sound:
                    self.g.assets.collision_sound.play()

            if abs(vy) > 20 and vy * pvy < 0 and (y <= top + 1 or y >= bottom - 1):
                if speed > 80 and self.g.assets.collision_sound:
                    self.g.assets.collision_sound.play()

        # ball-ball collision
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                b1 = balls[i]; b2 = balls[j]
                x1, y1 = b1.body.position; x2, y2 = b2.body.position
                dx = x2 - x1; dy = y2 - y1
                dist2 = dx * dx + dy * dy
                if dist2 <= (2 * radius + 2) ** 2:
                    rvx = b1.body.velocity.x - b2.body.velocity.x
                    rvy = b1.body.velocity.y - b2.body.velocity.y
                    if rvx * rvx + rvy * rvy > 90 * 90:
                        key = tuple(sorted((id(b1), id(b2))))
                        if key not in seen_pairs:
                            if self.g.assets.collision_sound:
                                self.g.assets.collision_sound.play()
                            seen_pairs.add(key)

        for b in balls:
            self.last_vel[b] = b.body.velocity
