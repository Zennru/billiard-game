import math


class Pocket:
    def __init__(self, w, h, diameter=80):
        r = diameter / 2
        edge = 50

        self.radius = r
        self.pockets = [
            (edge, edge),
            (w / 2, edge),
            (w - edge, edge),
            (edge, h - edge),
            (w / 2, h - edge),
            (w - edge, h - edge),
        ]

    def check(self, pos):
        return any(math.dist(pos, p) <= self.radius for p in self.pockets)
