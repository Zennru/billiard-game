import pymunk

class Ball:
    def __init__(self, space, radius, pos, mass=5, elasticity=0.8):
        self.radius = radius

        # body dinamis dengan momen inersia lingkaran
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        # bikin bola tidak licin
        self.body.linear_damping = 1.25
        self.body.angular_damping = 0.9

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = elasticity

        # friksi supaya tidak selicin es
        self.shape.friction = 1.55
        self.shape.collision_type = 1

        space.add(self.body, self.shape)

    def draw(self, screen, image):
        x = int(self.body.position.x - self.radius)
        y = int(self.body.position.y - self.radius)
        screen.blit(image, (x, y))

    # bola berhenti lebih cepat
    def is_stopped(self):
        vx, vy = self.body.velocity
        speed_sq = vx*vx + vy*vy

        if speed_sq < 650:     # threshold agresif = berhenti cepat
            self.body.velocity = (0, 0)
            return True
        return False
