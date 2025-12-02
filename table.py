import pymunk


class Table:
    def __init__(self, space, w, h):
        self.space = space

        pocket_radius = 40
        center = w / 2
        gap_half = pocket_radius + 5
        corner = 80

        # atas
        self.edge(space, corner, 50, center - gap_half, 50)
        self.edge(space, center + gap_half, 50, w - corner, 50)

        # bawah
        self.edge(space, corner, h - 50, center - gap_half, h - 50)
        self.edge(space, center + gap_half, h - 50, w - corner, h - 50)

        # kiri kanan
        self.edge(space, 50, corner, 50, h - corner)
        self.edge(space, w - 50, corner, w - 50, h - corner)

    def edge(self, space, x1, y1, x2, y2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
        shape.elasticity = 0.8
        shape.friction = 1
        shape.collision_type = 0  # meja
        space.add(body, shape)
