import pymunk

class Table:
    def __init__(self, space, w, h):
        self.space = space

        self.create_edge(80, 50, w - 80, 50)
        self.create_edge(80, h - 50, w - 80, h - 50)
        self.create_edge(50, 80, 50, h - 80)
        self.create_edge(w - 50, 80, w - 50, h - 80)

    def create_edge(self, x1, y1, x2, y2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
        shape.elasticity = 0.8
        self.space.add(body, shape)
