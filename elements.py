import pygame
from enum import Enum
from camera import camClass

class _widget_base():
    def __init__(
        self, 
        screen,
        camera: camClass,
        pos: pygame.Vector2, 
        size: pygame.Vector2 = pygame.Vector2(50, 50), 
        min_size: pygame.Vector2 = pygame.Vector2(0,0),
    ):
        self.screen = screen
        self.camera = camera
        self.size: pygame.Vector2 = size.copy()
        self.min_size: pygame.Vector2 = min_size.copy()

        if pos:
            self.pos: pygame.Vector2 = pos
        else:
            self.pos = self.get_mousePos()
    
    def get_pos(self, camMod: bool = True) -> pygame.Vector2:
        self.pos = pygame.Vector2(self.pos)

        if camMod:
            return self.pos - self.camera.pos
        else:
            return self.pos

    def get_mousePos(self) -> pygame.Vector2:
        return (pygame.Vector2(pygame.mouse.get_pos()) / self.camera.zoom) + self.camera.pos

    def move_by(self, pos_mod: pygame.Vector2):
        self.pos += pos_mod 
    
    def update(self):
        self.size = pygame.Vector2(self.get_rect(False, False).size)
    
    def get_rect(self, camPosMod: bool = True, camZoomMod: bool = True, padding:float = 0) -> pygame.Rect:

        p: pygame.Vector2 = self.get_pos(camPosMod).copy()
        #if camZoomMod:
        #    padding *= self.camera.zoom
        
        s: pygame.Vector2 = pygame.Vector2(
            max(self.min_size.x, self.size.x)+(padding*2),
            max(self.min_size.y, self.size.y)+(padding*2)
        )
        if camPosMod:
            p *= self.camera.zoom
        if camZoomMod:
            s *= self.camera.zoom
              
        ret = pygame.Rect((p - (s/2)),s)
        return ret

    def collideMouse(self, padding: float = 0) -> bool:
        rect = self.get_rect(padding=padding)
        
        return rect.collidepoint(pygame.mouse.get_pos())

class widget(_widget_base):
    class stateTypes(Enum):
        IDLE = 0,
        SELECTED = 1,
        TEXT = 2,
    def __init__(self, screen, camera: camClass, pos: pygame.Vector2, size: pygame.Vector2 = pygame.Vector2(100, 75)):
        super().__init__(screen, camera, pos, size, size)
        self.state: int = False

        self._buttons:list[widgetButton] = [
            widgetButton(screen, camera, self, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
            widgetButton(screen, camera, self, widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
            widgetButton(screen, camera, self, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
            widgetButton(screen, camera, self, widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
            widgetButton(screen, camera, self, widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
            widgetButton(screen, camera, self, widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0)),
        ]
        self._update_buttons()

    def _update_buttons(self):
        #rect: pygame.Rect = self.get_rect(False)
        for i in self._buttons: 
            i.update()
    
    def update(self):
        super().update()
        self._update_buttons()
    
    def resize_by(self, size_mod: pygame.Vector2):
        self.size += size_mod
        self._update_buttons()
    
    def move_by(self, pos_mod: pygame.Vector2):
        super().move_by(pos_mod)
        self._update_buttons()

    def get_buttons(self):
        return self._buttons

    def render(self):
        rect = self.get_rect()
        color = 'black'

        if self.is_selected():
            color = 'red'

        pygame.draw.rect(self.screen, 'white', rect)
        pygame.draw.rect(self.screen, color, rect,5)

        for i in self.get_buttons():
            i.render()
    
    def is_selected(self):
        return self.selected

class widgetButton(_widget_base):
    def __init__(self, screen, camera:camClass, parent:widget, type: widgetButton.buttonTypes, anchor: pygame.Vector2,offset:float=0.0):
        super().__init__(screen, camera, pygame.Vector2(0,0), pygame.Vector2(20,20))
        self.parent = parent
        self.type: widgetButton.buttonTypes = type
        self.anchor: pygame.Vector2 = anchor
        self.offset: float = offset
    
    class buttonTypes(Enum):
        NULL = 0
        LINK = 1
        REPOSITION = 2
        RESIZE = 3
        TEXTINPUT = 2
        DELETE = 4
    
    def get_rect(self, camPosMod: bool = True, camZoomMod: bool = True, padding:float = 0) -> pygame.Rect:
        rect = self.parent.get_rect(camPosMod=False, camZoomMod=False, padding=self.offset)
        rect_size = pygame.Vector2(rect.size)

        self.pos = pygame.Vector2(rect.topleft)

        #if camZoomMod: 
        #    self.pos /= self.camera.zoom
        #    rect_size /= self.camera.zoom
        
        self.pos += pygame.Vector2(
            rect_size.x * self.anchor.x,
            rect_size.y * self.anchor.y,
        )

        #self.pos.x += self.offset.x
        #self.pos.y += self.offset.y
        ret = super().get_rect(camPosMod, camZoomMod, padding)
        return ret
    
    def update(self):
        return self.pos

    def render(self):
        if self.parent and self.parent.is_selected():
            pygame.draw.rect(self.screen, 'red', self.get_rect())
        
class widget_link:
    def __init__(self, screen, camera: camClass, widget1: widget, widget2: widget, width: float = 5):
        self.screen = screen
        self.camera = camera
        self.widget1 = widget1
        self.widget2 = widget2
        self.width = width
    
    def collideMouse(self):
        pass
    
    def render(self):
        pygame.draw.line(self.screen, 'black', self.widget1.get_pos(), self.widget2.get_pos(), 5)