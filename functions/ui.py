import pygame
from enum import Enum
from functions.elements import element
from functions.elements import widget
from functions.elements import widget_link
from functions.camera import camClass

class widgetButton():
    class buttonTypes(Enum):
        NULL = 0
        LINK = 1
        REPOSITION = 2
        RESIZE = 3
        TEXTINPUT = 4
        DELETE = 5
    
    def __init__(self, type: int, anchor: pygame.Vector2,offset:float=0.0, line_anchor:float=False):
        self.pos: pygame.Vector2 = pygame.Vector2(0,0)
        self.radius: float = 10
        self.type: int = type
        self.anchor: pygame.Vector2 = anchor
        self.offset: float = offset
        self.line_anchor: float = line_anchor
    
    def get_pos(self, parent: element, camMod: bool = True) -> pygame.Rect:
        if isinstance(parent, widget):
            rect = parent.get_rect(camMod=False, padding=self.offset)
            rect_size = pygame.Vector2(rect.size)

            self.pos = pygame.Vector2(rect.topleft)
            self.pos += pygame.Vector2(
                rect_size.x * self.anchor.x,
                rect_size.y * self.anchor.y,
            )
        elif self.line_anchor and isinstance(parent, widget_link):
            line = parent.get_line()
            
            pos1 = pygame.Vector2(line[0])
            pos2 = pygame.Vector2(line[1])

            self.pos = ((pos1-pos2)*self.line_anchor)+pos2
        else:
            self.pos = None
        
        if self.pos and camMod:
            camera = camClass.get_camera()
            return (self.pos - camera.pos) * camera.zoom
        else:
            return self.pos
    
    def collideMouse(self, parent: widget) -> bool:
        if isinstance(parent, widget):
            pos: pygame.Vector2 = self.get_pos(parent=parent)
            return pos.distance_squared_to(pygame.mouse.get_pos()) < self.radius ** 2
        else:
            return False

    def render(self, parent: widget):
        pos = self.get_pos(parent)

        if pos:
            screen = pygame.display.get_surface()
            pygame.draw.circle(screen, 'red', pos, self.radius)
