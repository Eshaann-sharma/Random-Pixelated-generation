import pygame
from gpu_map import GPUMap

def run():
    pygame.init()

    TILE_SIZE = 16
    WIDTH, HEIGHT = 100, 60
    screen = pygame.display.set_mode((WIDTH * TILE_SIZE, HEIGHT * TILE_SIZE))
    pygame.display.set_caption("GPU Map (Numba CUDA)")

    game_map = GPUMap(WIDTH, HEIGHT, TILE_SIZE)

    camera_x, camera_y = 0, 0
    speed = 2
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: camera_y -= speed
        if keys[pygame.K_s]: camera_y += speed
        if keys[pygame.K_a]: camera_x -= speed
        if keys[pygame.K_d]: camera_x += speed

        game_map.display(screen, camera_x, camera_y)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run()
