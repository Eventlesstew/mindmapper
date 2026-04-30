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
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.pos,
            self.size / self.zoom
        )
    
    def zoom_by(self, zoom_mod: float):
        oldRect = self.get_rect()

        self._zoom_index -= zoom_mod

        if self._zoom_index <= 0:
            self.zoom = 1-self._zoom_index
        else:
            self.zoom = 1/(1+self._zoom_index)

        newRect = self.get_rect()
        self.pos = pygame.Vector2(oldRect.center) - (pygame.Vector2(newRect.size) / 2)

        ## BUG - There are dissimilarities when zooming in
        if self.get_rect().center != oldRect.center:
            print("DISSIMILARITY AT", self.zoom, self.get_rect().center, oldRect.center)

    def get_camera():
        global camera
        return camera

global camera; camera = camClass()