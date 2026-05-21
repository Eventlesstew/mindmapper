import pygame
from G import GClass
from functions.camera import camClass
from config import C

G = GClass.get_G()

# Run this program to run the full application.
if __name__ == "__main__":
    camera = camClass.get_camera()
    pygame.init()
    screen = pygame.display.set_mode(
        size=camera.size, 
        flags=pygame.RESIZABLE,
        vsync=1
        )
    pygame.display.set_caption('Mindmapper - BS without BS')
    clock = pygame.time.Clock()

    dt = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            G.input(event)
        conf: C = C.get_config()
        screen.fill(conf.colors.background)
        G.render()
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pygame.quit()  