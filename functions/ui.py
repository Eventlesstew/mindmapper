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
    
    def __init__(self, type: int, image_type: str, anchor: pygame.Vector2,offset:float=0.0, line_anchor:float=False):
        self.pos: pygame.Vector2 = pygame.Vector2(0,0)
        self.radius: float = 10
        self.type: int = type
        self.anchor: pygame.Vector2 = anchor
        self.offset: float = offset
        self.line_anchor: float = line_anchor
        self.image_type: str = image_type
        self.texture = None
        self.load_texture()
    
    def load_texture(self):
        self.texture = pygame.image.load('assets/textures/' + self.image_type + '.png')
    
    def get_pos(self, parent: element) -> pygame.Rect:
        if isinstance(parent, widget):
            rect = parent.get_rect(camMod=False, padding=self.offset)
            rect_size = pygame.Vector2(rect.size)

            self.pos = pygame.Vector2(rect.topleft)
            self.pos += pygame.Vector2(
                rect_size.x * self.anchor.x,
                rect_size.y * self.anchor.y,
            )

            camera = camClass.get_camera()
            self.pos = (self.pos - camera.pos) * camera.zoom
        elif self.line_anchor and isinstance(parent, widget_link):
            line = parent.get_line()
            
            pos1 = pygame.Vector2(line[0])
            pos2 = pygame.Vector2(line[1])

            self.pos = ((pos1-pos2)*self.line_anchor)+pos2
        else:
            self.pos = None
        
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

            if self.texture:
                screen.blit(self.texture, pos - pygame.Vector2(self.radius, self.radius))

            
