import pygame
from enum import Enum
from functions.camera import camClass

class widget_base():
    class stateTypes(Enum):
        IDLE = 0,
        SELECTED = 1,
        TEXT = 2,
    
    def __init__(
        self, 
        pos: pygame.Vector2, 
        size: pygame.Vector2 = pygame.Vector2(50, 50), 
        min_size: pygame.Vector2 = pygame.Vector2(0,0),
    ):
        self.size: pygame.Vector2 = size.copy()
        self.min_size: pygame.Vector2 = min_size.copy()

        if pos:
            self.pos: pygame.Vector2 = pos
        else:
            self.pos = self.get_mousePos()

    def get_pos(self, camMod: bool = True) -> pygame.Vector2:
        self.pos = pygame.Vector2(self.pos)

        if camMod:
            camera = camClass.get_camera()
            return (self.pos - camera.pos) * camera.zoom
        else:
            return self.pos

    def get_mousePos(self) -> pygame.Vector2:
        camera = camClass.get_camera()
        return (pygame.Vector2(pygame.mouse.get_pos()) / camera.zoom) + camera.pos

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
            camera = camClass.get_camera()
            s *= camera.zoom
              
        ret = pygame.Rect((p - (s/2)),s)
        return ret

    def _rect_collideMouse(self, rect:pygame.Rect):
        return rect.collidepoint(pygame.mouse.get_pos())

    def collideMouse(self, padding: float = 0) -> bool:
        rect = self.get_rect(padding=padding)
        
        return self._rect_collideMouse(rect)

class widget(widget_base):
    FONT_SIZE: int = 24
    FONT_OFFSET: int = 20
    MIN_SIZE = pygame.Vector2(100, 75)
    OUTLINE_SIZE = 5

    def __init__(self, pos: pygame.Vector2, size: pygame.Vector2 = None, text: str = ''):
        if size:
            pass
        else:
            size = self.MIN_SIZE

        super().__init__(pos, size, self.MIN_SIZE)
        self.selected: bool = False
        self.state: int = 0
        self.raw_text: str = text
        self.update_text()
    
    def is_selected(self):
        return self.state != self.stateTypes.IDLE
    
    def resize_to(self, size_mod: pygame.Vector2):
        self.size = size_mod
        self.update_text()

    def resize_by(self, size_mod: pygame.Vector2):
        self.size += size_mod
        self.update_text()
    
    def move_by(self, pos_mod: pygame.Vector2):
        super().move_by(pos_mod)
    
    def get_font(self, camMod: bool = True) -> pygame.font.Font:
        size = self.FONT_SIZE
        if camMod:
            camera = camClass.get_camera()
            size *= camera.zoom
        
        return pygame.font.Font(None, round(size))

    def update_text(self):
        font = self.get_font(False)
        text_bounds = self.get_rect(False, -self.FONT_OFFSET)
        self.text = [self.raw_text]
        loop = True

        while loop:
            loop = False
            chosen_break = None

            for text_i, text in enumerate(self.text):
                for i, t in enumerate(text[::-1]):
                    i = len(text)-1-i
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

        for i, text in enumerate(self.text):
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

        pygame.draw.rect(screen, color, self.get_rect(padding=self.OUTLINE_SIZE/2))
        pygame.draw.rect(screen, 'white', self.get_rect(padding=self.OUTLINE_SIZE/-2))
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
    
    def set_text(self, new_text: str):
        self.raw_text = new_text
        self.update_text()
        
# TODO - Make this inherited from widget base.
class widget_link:
    def __init__(self, widget1: widget, widget2: widget, width: float = 5):
        self.widget1 = widget1
        self.widget2 = widget2
        self.width = width
        self._queue_deletion = False

    def queue_delete(self):
        self._queue_deletion = True

    def is_queued_for_deletion(self):
        return self._queue_deletion

    def get_line(self, inside_widgets: bool = True):
        pos1 = self.widget1.get_pos()
        pos2 = self.widget2.get_pos()

        if not inside_widgets:
            print("LINES")
            clip1 = self.widget1.get_rect(widget.OUTLINE_SIZE/-2).clipline(pos1, pos2)
            if pos1 == pygame.Vector2(clip1[0]):
                pos1 = pygame.Vector2(clip1[1])
                print(pos1)
            
            clip2 = self.widget2.get_rect(widget.OUTLINE_SIZE/-2).clipline(pos2, pos1)
            if pos2 == pygame.Vector2(clip2[0]):
                pos2 = pygame.Vector2(clip2[1])
                print(pos2)
        return [pos1, pos2]
    
    def collideMouse(self):
        line = self.get_line(False)
        pos1 = line[0]
        pos2 = line[1]
        posm = pygame.Vector2(pygame.mouse.get_pos())
        
        linecheck: float = (((pos2.x-pos1.x)*(posm.x-pos1.x))+((pos2.y-pos1.y)*(posm.y-pos1.y)))/(((pos2.x-pos1.x)**2)+((pos2.y-pos1.y)**2))

        if 0.0 <= linecheck and linecheck <= 1.0:
            distance: float = abs(
                    (
                        (pos2.y-pos1.y)*(posm.x-pos1.x)
                    )-(
                        (pos2.x-pos1.x)*(posm.y-pos1.y)
                    )
                )/(
                    ((
                        (pos2.x-pos1.x)**2
                    )+(
                        (pos2.y-pos1.y)**2
                    ))**0.5
                )

            camera = camClass.get_camera()
            distance /= (widget.OUTLINE_SIZE * 2 * camera.zoom)

            if distance < 1.0:
                return True
        
        return False
    
    def render(self, selected):
        screen = pygame.display.get_surface()
        camera = camClass.get_camera()
        color = 'black'
        if self == selected:
            color = 'red'

        line = self.get_line()
        pygame.draw.line(screen, color, line[0], line[1], round(widget.OUTLINE_SIZE*camera.zoom))