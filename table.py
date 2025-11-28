import pymunk

class Table:
    def __init__(self, space, w, h):
        self.space = space   # ← ini yang kamu lupa

        gap = 60  # bukaan untuk pocket

        # ==== TOP ====
        self.create_edge(80 + gap, 50, w/2 - gap, 50)
        self.create_edge(w/2 + gap, 50, w - 80 - gap, 50)

        # ==== BOTTOM ====
        self.create_edge(80 + gap, h - 50, w/2 - gap, h - 50)
        self.create_edge(w/2 + gap, h - 50, w - 80 - gap, h - 50)

        # ==== LEFT ====
        self.create_edge(50, 80 + gap, 50, h/2 - gap)
        self.create_edge(50, h/2 + gap, 50, h - 80 - gap)

        # ==== RIGHT ====
        self.create_edge(w - 50, 80 + gap, w - 50, h/2 - gap)
        self.create_edge(w - 50, h/2 + gap, w - 50, h - 80 - gap)

    def create_edge(self, x1, y1, x2, y2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
        shape.elasticity = 0.8
        shape.friction = 1.0
        self.space.add(body, shape)
