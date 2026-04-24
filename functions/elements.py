import pygame
from enum import Enum
from functions.camera import camClass

class _widget_base():

    def __init__(
        self, 
        camera: camClass,
        pos: pygame.Vector2, 
        size: pygame.Vector2 = pygame.Vector2(50, 50), 
        min_size: pygame.Vector2 = pygame.Vector2(0,0),
    ):
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
            return (self.pos - self.camera.pos) * self.camera.zoom
        else:
            return self.pos

    def get_mousePos(self) -> pygame.Vector2:
        return (pygame.Vector2(pygame.mouse.get_pos()) / self.camera.zoom) + self.camera.pos

    def move_by(self, pos_mod: pygame.Vector2):
        self.pos += pos_mod 
    
    def reset_size(self):
        self.size = pygame.Vector2(self.get_rect(False, False).size)
    
    def get_rect(self, camMod: bool = True, padding:float = 0) -> pygame.Rect:

        p: pygame.Vector2 = self.get_pos(camMod).copy()
        s: pygame.Vector2 = pygame.Vector2(
            max(self.min_size.x, self.size.x)+(padding*2),
            max(self.min_size.y, self.size.y)+(padding*2)
        )
        if camMod:
            s *= self.camera.zoom
              
        ret = pygame.Rect((p - (s/2)),s)
        return ret

    def _rect_collideMouse(self, rect:pygame.Rect):
        return rect.collidepoint(pygame.mouse.get_pos())

    def collideMouse(self, padding: float = 0) -> bool:
        rect = self.get_rect(padding=padding)
        
        return self._rect_collideMouse(rect)

class widget(_widget_base):
    def __init__(self, camera: camClass, pos: pygame.Vector2, size: pygame.Vector2 = pygame.Vector2(300, 200)):
        super().__init__(camera, pos, size, size)
        self.selected: bool = False
        self.state: int = 0
        self.raw_text: str = 'Hello, World!'
        self.update_text()

    FONT_SIZE: int = 32
    FONT_OFFSET: int = 20
    class stateTypes(Enum):
        IDLE = 0,
        SELECTED = 1,
        TEXT = 2,
    
    def is_selected(self):
        return self.state != self.stateTypes.IDLE
    
    def resize_by(self, size_mod: pygame.Vector2):
        self.size += size_mod
        self.update_text()
    
    def move_by(self, pos_mod: pygame.Vector2):
        super().move_by(pos_mod)
    
    def get_font(self, camMod: bool = True) -> pygame.font.Font:
        size = self.FONT_SIZE
        if camMod:
            size *= self.camera.zoom
        
        return pygame.font.Font(None, round(size))

    def update_text(self):
        font = self.get_font(False)
        text_bounds = self.get_rect(False, -self.FONT_OFFSET)
        self.text = [self.raw_text]
        loop = True

        while loop:
            loop = False
            chosen_break = None

            for text_i in range(0, len(self.text)):
                text = self.text[text_i]
                for i in range(0,len(text))[::-1]:
                    t = text[i]
                    valid = False
                    if t == '\n':
                        valid = True
                    else:
                        text_rect_size = pygame.Vector2(font.size(text))
                        wrap: bool = text_rect_size.x > pygame.Vector2(text_bounds.size).x
                        if t == ' ' and (i == 0 or wrap):
                            valid = True
                    
                    if valid:
                        chosen_break = {
                            'index':i,
                            'line':text_i,
                        }
                        break
                if chosen_break:
                    break

            if chosen_break:
                index = chosen_break['index']
                line = chosen_break['line']

                if index != 0:
                    if line+1 >= len(self.text):
                        self.text.append(self.text[line][index:])
                    else:
                        self.text[line+1] = self.text[line][index:] + self.text[line+1]
                    self.text[line] = text[0:index]
                else:
                    self.text[line] = text[1:]
                loop = True

    def render_text(self):
        screen = pygame.display.get_surface()

        font = self.get_font(True)
        font_height = font.get_height()

        for i in range(0,len(self.text)):
            text = self.text[i]

            text_surface = font.render(text, True, 'black')
            text_pos = (self.get_pos())
            text_pos.y += font_height * (i - ((len(self.text)-1)/2))
            text_pos -= (pygame.Vector2(font.size(text))/2)
            screen.blit(text_surface, (text_pos.x, text_pos.y))
    
    def render(self):
        screen = pygame.display.get_surface()
        color = 'black'

        if self.state == self.stateTypes.TEXT:
            color = 'red'

        pygame.draw.rect(screen, color, self.get_rect(padding=5))
        pygame.draw.rect(screen, 'white', self.get_rect(padding=-5))
        self.render_text()
    
    def input_text(self, event):
         if event.type == pygame.KEYDOWN and self.state == self.stateTypes.TEXT:
            if event.key == pygame.K_RETURN:
                self.raw_text += '\n'
            elif event.key == pygame.K_BACKSPACE:
                self.raw_text = self.raw_text[:-1]
            else:
                self.raw_text += event.unicode
            # Re-render the text.
            self.update_text()

class widgetButton(_widget_base):
    def __init__(self, camera:camClass, type: int, anchor: pygame.Vector2,offset:float=0.0):
        super().__init__(camera, pygame.Vector2(0,0), pygame.Vector2(20,20))
        self.type: int = type
        self.anchor: pygame.Vector2 = anchor
        self.offset: float = offset
    
    class buttonTypes(Enum):
        NULL = 0
        LINK = 1
        REPOSITION = 2
        RESIZE = 3
        TEXTINPUT = 2
        DELETE = 4
    
    def get_rect(self, parent: widget, camMod: bool = True, padding:float = 0) -> pygame.Rect:
        rect = parent.get_rect(camMod=False, padding=self.offset)
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
        ret = super().get_rect(camMod, padding)

        return ret
    
    def collideMouse(self, parent: widget, padding: float = 0) -> bool:
        rect = self.get_rect(parent=parent, padding=padding)
        return self._rect_collideMouse(rect)

    def render(self, parent: widget):
        screen = pygame.display.get_surface()
        pygame.draw.rect(screen, 'red', self.get_rect(parent))
        
class widget_link:
    def __init__(self, camera: camClass, widget1: widget, widget2: widget, width: float = 5):
        self.camera = camera
        self.widget1 = widget1
        self.widget2 = widget2
        self.width = width
    
    def collideMouse(self):
        pass
    
    def render(self):
        screen = pygame.display.get_surface()
        pygame.draw.line(screen, 'black', self.widget1.get_pos(), self.widget2.get_pos(), 5)