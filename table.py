import pymunk

class Table:
    def __init__(self, space, w, h):
        self.space = space

        wall_thickness = 10
        pocket_radius = 45  # besar lubang 90px di pocket.py

        center_x = w / 2
        gap_half = pocket_radius + 5

        corner_limit = 80

        # Kiri Atas
        self.create_edge(corner_limit, 50, center_x - gap_half, 50)
        # Kanan Atas
        self.create_edge(center_x + gap_half, 50, w - corner_limit, 50)
        
        # Kiri Bawah
        self.create_edge(corner_limit, h - 50, center_x - gap_half, h - 50)
        # Kanan Bawah
        self.create_edge(center_x + gap_half, h - 50, w - corner_limit, h - 50) 
        
        # ==== BATAS SISI KIRI/KANAN (TIDAK ADA PERUBAHAN) ====
        self.create_edge(50, corner_limit, 50, h - corner_limit) # left
        self.create_edge(w - 50, corner_limit, w - 50, h - corner_limit) # right

    def create_edge(self, x1, y1, x2, y2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 10)
        shape.elasticity = 0.8
        shape.friction = 1.0
        self.space.add(body, shape)
