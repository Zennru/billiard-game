import pymunk

class Table:
    def __init__(self, space, w, h):
        self.space = space

        wall_thickness = 10
        pocket_radius = 45  # besar lubang 90px di pocket.py

        # MAIN WALLS (tanpa melewati pocket)
        self.create_edge(80, 50, w - 80, 50)        # top
        self.create_edge(80, h - 50, w - 80, h - 50)  # bottom
        self.create_edge(50, 80, 50, h - 80)        # left
        self.create_edge(w - 50, 80, w - 50, h - 80)  # right

        # ======== CORNER BLOCKERS ========
        # agar bola TIDAK bisa keluar map lewat pojok pocket

        # top left
        self.create_edge(80, 50, 50, 80)
        # top right
        self.create_edge(w - 80, 50, w - 50, 80)
        # bottom left
        self.create_edge(80, h - 50, 50, h - 80)
        # bottom right
        self.create_edge(w - 80, h - 50, w - 50, h - 80)

    def create_edge(self, x1, y1, x2, y2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
        shape.elasticity = 0.8
        shape.friction = 1.0
        self.space.add(body, shape)
