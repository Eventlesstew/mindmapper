import pygame

class camClass:
    def __init__(self):
        self.pos: pygame.Vector2 = pygame.Vector2(0,0)
        self.zoom: float = 1.0
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
        r = self.get_rect()
        self.zoom += zoom_mod
        self.pos = pygame.Vector2(r.center) - (pygame.Vector2(self.get_rect().size) / 2)
        print(self.get_rect())