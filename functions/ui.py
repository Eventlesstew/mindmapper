import pygame
from enum import Enum
from functions.elements import widget
from functions.camera import camClass

class toolbarClass:
    def __init__(self):
        self.height = 30
        self.spacing = 5

        self.buttons = [
            toolbarButton(self, 'mindmapper'),
            toolbarButton(self, 'file'),
            toolbarButton(self, 'edit'),
        ]

        for i,v in enumerate(self.buttons):
            v.set_index(i)
        
    def render(self):
        for _, b in enumerate(self.buttons):
            b.render()

class toolbarButton:
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type
        self.size: pygame.Vector2 = pygame.Vector2(100, parent.height)
        self.index: int = 0

    def get_text(self):
        return self.type
    
    def get_rect(self) -> pygame.Rect:
        pos = pygame.Vector2((self.size.x + self.parent.spacing) * self.index,0) 
        pos += pygame.Vector2(self.parent.spacing, self.parent.spacing)

        return pygame.Rect(pos, self.size)

    def set_index(self, newIndex):
        self.index = newIndex
    
    def collideMouse(self):
        return self.get_rect().collidepoint(pygame.mouse.get_pos())

    def render(self):
        screen = pygame.display.get_surface()
        rect = self.get_rect()
        font = pygame.font.Font(None, round(24))

        text_surface = font.render(self.get_text(), True, 'black')
        text_pos = pygame.Vector2(rect.center) - (pygame.Vector2(font.size(self.get_text()))/2)
        
        pygame.draw.rect(screen, 'gray', rect)
        screen.blit(text_surface, (text_pos, text_pos))

class widgetButton():
    class buttonTypes(Enum):
        NULL = 0
        LINK = 1
        REPOSITION = 2
        RESIZE = 3
        TEXTINPUT = 4
        DELETE = 5
    
    def __init__(self, camera:camClass, type: int, anchor: pygame.Vector2,offset:float=0.0):
        self.camera = camera
        self.pos: pygame.Vector2 = pygame.Vector2(0,0)
        self.radius: float = 10
        self.type: int = type
        self.anchor: pygame.Vector2 = anchor
        self.offset: float = offset
    
    def get_pos(self, parent: widget, camMod: bool = True) -> pygame.Rect:
        if isinstance(parent, widget):
            rect = parent.get_rect(camMod=False, padding=self.offset)
            rect_size = pygame.Vector2(rect.size)

            self.pos = pygame.Vector2(rect.topleft)
            self.pos += pygame.Vector2(
                rect_size.x * self.anchor.x,
                rect_size.y * self.anchor.y,
            )

            if camMod:
                return (self.pos - self.camera.pos) * self.camera.zoom
            else:
                return self.pos
        else:
            return None
    
    def collideMouse(self, parent: widget) -> bool:
        if isinstance(parent, widget):
            pos: pygame.Vector2 = self.get_pos(parent=parent)
            return pos.distance_squared_to(pygame.mouse.get_pos()) < self.radius ** 2
        else:
            return False

    def render(self, parent: widget):
        if isinstance(parent, widget):
            screen = pygame.display.get_surface()
            pygame.draw.circle(screen, 'red', self.get_pos(parent), self.radius)