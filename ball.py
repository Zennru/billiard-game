import pymunk

class Ball:
    def __init__(self, space, radius, pos, mass=5, elasticity=0.8):
        self.radius = radius
        self.body = pymunk.Body()
        self.body.position = pos

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.mass = mass
        self.shape.elasticity = elasticity

        pivot = pymunk.PivotJoint(space.static_body, self.body, (0, 0), (0, 0))
        pivot.max_bias = 0
        pivot.max_force = 1000

        space.add(self.body, self.shape, pivot)

    def draw(self, screen, image):
        x = self.body.position[0] - self.radius
        y = self.body.position[1] - self.radius
        screen.blit(image, (x, y))

    def is_stopped(self):
        return int(self.body.velocity.x) == 0 and int(self.body.velocity.y) == 0
