import pygame
import numpy as np
from numba import cuda, njit
from tile import plains, forest, pines, mountain, water

TILE_SIZE = 16

# GPU kernel: parallel noise calculation
@cuda.jit
def generate_noise_gpu(noise, offset_x, offset_y, scale):
    x, y = cuda.grid(2)
    if x < noise.shape[1] and y < noise.shape[0]:
        val = (cuda.math.sin((x + offset_x) * scale) *
               cuda.math.cos((y + offset_y) * scale))
        noise[y, x] = val


class GPUMap:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.scale = 0.05

        # Allocate CPU array
        self.noise_cpu = np.zeros((height, width), dtype=np.float32)
        # Allocate GPU array
        self.noise_gpu = cuda.device_array((height, width), dtype=np.float32)

    def generate_map_gpu(self, offset_x, offset_y):
        threadsperblock = (16, 16)
        blockspergrid_x = (self.width + threadsperblock[0] - 1) // threadsperblock[0]
        blockspergrid_y = (self.height + threadsperblock[1] - 1) // threadsperblock[1]
        blockspergrid = (blockspergrid_x, blockspergrid_y)

        generate_noise_gpu[blockspergrid, threadsperblock](
            self.noise_gpu, offset_x, offset_y, self.scale
        )

        # Copy results back to CPU
        self.noise_gpu.copy_to_host(self.noise_cpu)

    def display(self, screen, camera_x, camera_y):
        self.generate_map_gpu(camera_x, camera_y)
        for y in range(self.height):
            for x in range(self.width):
                n = self.noise_cpu[y, x]
                if n < -0.5:
                    tile = water
                elif n < 0:
                    tile = plains
                elif n < 0.3:
                    tile = forest
                elif n < 0.6:
                    tile = pines
                else:
                    tile = mountain

                if tile.image is None:
                    tile.load_image()
                screen.blit(tile.image, (x * self.tile_size, y * self.tile_size))
