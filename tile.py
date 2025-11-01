import pygame

class Tile:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = None  # will be loaded later

    def load_image(self):
        if self.image is None:
            self.image = pygame.image.load(self.image_path).convert_alpha()


plains = Tile("sprites/g.png")
forest = Tile("sprites/s.png")
pines = Tile("sprites/bush.png")
mountain = Tile("sprites/t.png")
water = Tile("sprites/Water.png")