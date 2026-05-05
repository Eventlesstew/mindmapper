import pygame

class camClass:
    def __init__(self):
        self.pos: pygame.Vector2 = pygame.Vector2(0,0)
        self.zoom: float = 1.0
        self._zoom_index: int = 0
        self.size = pygame.Vector2(1280, 720)
    
    def move_by(self, pos_mod: pygame.Vector2):
        pos_mod = pygame.Vector2(pos_mod)
        self.pos -= pygame.Vector2(
            pos_mod.x / self.zoom,
            pos_mod.y / self.zoom
        )
    
    ## TODO - Add a move to function that will move the camera's center to a specific position.
    # Use this when opening a file to center the camera towards the elements.
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.pos,
            self.size / self.zoom
        )
    
    def zoom_by(self, zoom_mod: float):
        old_mouse_pos = self.get_mouse_pos()
        self._zoom_index -= zoom_mod

        if self._zoom_index <= 0:
            self.zoom = 1-self._zoom_index
        else:
            self.zoom = 1/(1+self._zoom_index)

        self.pos += old_mouse_pos - self.get_mouse_pos()

    def get_mouse_pos(self) -> pygame.Vector2:
        pos: pygame.Vector2 = pygame.Vector2(pygame.mouse.get_pos())
        pos /= self.zoom
        pos += self.pos
        return pos
    
    def get_camera():
        global camera
        return camera

global camera; camera = camClass()