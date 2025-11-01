import pygame
from perlin_noise import PerlinNoise

from tile import plains, forest, pines, mountain, water

class InfiniteMap:
    def __init__(self, tile_size: int):
        self.tile_size = tile_size
        self.scale = 0.05
        self.noise = PerlinNoise(octaves=4, seed=42)

    def get_tile(self, x, y):
        n = self.noise([x * self.scale, y * self.scale])
        if n < -0.2:
            return water
        elif n < 0.0:
            return plains
        elif n < 0.2:
            return forest
        elif n < 0.4:
            return pines
        else:
            return mountain

    def display(self, screen, camera_x, camera_y, screen_width, screen_height):
        """Draw only the visible tiles based on camera offset."""
        tile_size = self.tile_size

        # Calculate which tiles are visible
        start_x = int(camera_x // tile_size)
        start_y = int(camera_y // tile_size)
        end_x = start_x + (screen_width // tile_size) + 2
        end_y = start_y + (screen_height // tile_size) + 2

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.get_tile(x, y)
                if tile.image is None:
                    tile.load_image()

                # World to screen coordinates
                screen_x = (x * tile_size) - camera_x
                screen_y = (y * tile_size) - camera_y
                screen.blit(tile.image, (screen_x, screen_y))
