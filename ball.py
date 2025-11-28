import pymunk

class Ball:
    def __init__(self, space, radius, pos, mass=5, elasticity=0.8):
        self.radius = radius

        # body dinamis dengan momen inersia lingkaran
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        # bikin bola agak berat supaya nggak licin
        self.body.linear_damping = 0.99   # makin besar → makin cepat melambat
        self.body.angular_damping = 0.9

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = elasticity
        self.shape.friction = 0.6      # gesekan cukup besar
        self.shape.collision_type = 1

        space.add(self.body, self.shape)

    def draw(self, screen, image):
        x = int(self.body.position.x - self.radius)
        y = int(self.body.position.y - self.radius)
        screen.blit(image, (x, y))

    def is_stopped(self):
        vx, vy = self.body.velocity
        speed_sq = vx * vx + vy * vy

        # kalau sudah pelan banget, paksa berhenti
        if speed_sq < 200:   # threshold agresif, biar cepat berhenti
            self.body.velocity = (0, 0)
            return True
        return False
