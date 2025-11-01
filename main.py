import pygame
from map import InfiniteMap

def run():
    pygame.init()

    TILE_SIZE = 16
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Infinite Random World Generator")

    game_map = InfiniteMap(TILE_SIZE)
    clock = pygame.time.Clock()
    running = True

    camera_x, camera_y = 0, 0
    speed = 5  # movement speed in pixels

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            camera_y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            camera_y += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            camera_x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            camera_x += speed

        # Draw the visible region
        game_map.display(screen, camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run()
