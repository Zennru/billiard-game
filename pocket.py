import math

class Pocket:
    def __init__(self, screen_w, screen_h, diameter=90):
        # diameter dibesarkan supaya bola lebih gampang "masuk"
        self.radius = diameter / 2

        edge_x = 50
        edge_y = 50
        
        self.pockets = [
            # Pocket Atas (Y = 50)
            (edge_x, edge_y),                             # Kiri Atas
            (screen_w / 2, edge_y),                       # Tengah Atas
            (screen_w - edge_x, edge_y),                  # Kanan Atas
            
            # Pocket Bawah (Y = screen_h - 50)
            (edge_x, screen_h - edge_y),                  # Kiri Bawah
            (screen_w / 2, screen_h - edge_y),            # Tengah Bawah
            (screen_w - edge_x, screen_h - edge_y),       # Kanan Bawah
        ]

    def check(self, ball_pos):
        return any(
            math.dist(ball_pos, pocket) <= self.radius
            for pocket in self.pockets
        )
