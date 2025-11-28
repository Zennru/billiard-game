import pymunk

class Ball:
    def __init__(self, space, radius, pos, mass=5, elasticity=0.7):
        self.radius = radius

        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos

        # bola lebih cepat berhenti (anti licin)
        self.body.linear_damping = 0.45
        self.body.angular_damping = 0.9

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = elasticity
        self.shape.friction = 1.3    # cukup keras, tidak licin
        self.shape.collision_type = 1

        space.add(self.body, self.shape)

    def draw(self, screen, image):
        x = int(self.body.position.x - self.radius)
        y = int(self.body.position.y - self.radius)
        screen.blit(image, (x, y))

    def is_stopped(self):
        vx, vy = self.body.velocity
        if vx*vx + vy*vy < 40:  # threshold lebih agresif
            self.body.velocity = (0, 0)
            return True
        return False
