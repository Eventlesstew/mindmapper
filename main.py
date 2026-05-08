import pygame
from functions.camera import camClass
from G import GClass
from config import C

pygame.init()

camera = camClass.get_camera()
screen = pygame.display.set_mode(camera.size, pygame.RESIZABLE)
pygame.display.set_caption('Mindmapper - BS without BS')

clock = pygame.time.Clock()
global running; running = True

dt = 0

global G; G = GClass()
    
def _input(event):
    if event.type == pygame.MOUSEMOTION:
        G.on_mouseMotion()
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            G.on_leftClick()
        if event.button == 3:
            G.on_rightClick()
    if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            G.onRelease_leftClick()
        if event.button == 3:
            G.onRelease_rightClick()
    if event.type == pygame.MOUSEWHEEL:
        G.on_mouseWheel(event)
    if event.type == pygame.KEYDOWN:
        G.on_keyDown(event)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        _input(event)
    
    screen.fill("white")
    G.render()
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()