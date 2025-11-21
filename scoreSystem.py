class ScoreSystem:
    def __init__(self, lives=3):
        self.lives = lives
        self.potted_balls = []

    def lose_life(self):
        self.lives -= 1

    def add_potted(self, img):
        self.potted_balls.append(img)

    def is_dead(self):
        return self.lives <= 0
