import pygame
from enum import Enum
from functions.camera import camClass
from abc import ABC, abstractmethod
import copy
from config import C
import math

class element(ABC):
    class stateTypes(Enum):
        IDLE = 0,
        SELECTED = 1,
        TEXT = 2,

    @abstractmethod
    def collideMouse(self): pass 

class widget(element):
    FONT_SIZE: int = 24
    FONT_OFFSET: int = 20
    MIN_SIZE = pygame.Vector2(100, 75)
    OUTLINE_SIZE = 5
    
    def __init__(self, pos: pygame.Vector2, size: pygame.Vector2 = None, text: str = ''):
        if size:
            pass
        else:
            size = self.MIN_SIZE

        self.size: pygame.Vector2 = size
        self.min_size: pygame.Vector2 = self.MIN_SIZE.copy()
        self.pos: pygame.Vector2 = pos
        self.state: int = 0
        self.raw_text: str = text
        self.text: list[str] = [text]
        self.update_text()
        self.reset_size()
    
    def is_selected(self):
        from G import GClass
        G = GClass.get_G()
        return G.selected_element == self
    
    def get_rect(self, camMod: bool = True, padding:float = 0) -> pygame.Rect:
        min_size = self.get_min_size()
        p: pygame.Vector2 = self.get_pos(camMod).copy()
        s: pygame.Vector2 = pygame.Vector2(
            max(min_size.x, self.size.x)+(padding*2),
            max(min_size.y, self.size.y)+(padding*2)
        )
        if camMod:
            camera = camClass.get_camera()
            s *= camera.zoom
              
        ret = pygame.Rect((p - (s/2)),s)
        return ret

    def resize_to(self, size_mod: pygame.Vector2):
        self.size = size_mod
        self.update_text()

    def resize_by(self, size_mod: pygame.Vector2):
        self.size += size_mod
        self.update_text()
    
    def reset_size(self):
        self.size = pygame.Vector2(self.get_rect(False, False).size)
    
    def get_min_size(self) -> pygame.Vector2:
        result = pygame.Vector2(
            max(self.MIN_SIZE.x, self.min_size.x),
            max(self.MIN_SIZE.y, self.min_size.y)
        )
        return result

    def get_pos(self, camMod: bool = True) -> pygame.Vector2:
        self.pos = pygame.Vector2(self.pos)

        if camMod:
            camera = camClass.get_camera()
            return (self.pos - camera.pos) * camera.zoom
        else:
            return self.pos

    def move_by(self, pos_mod: pygame.Vector2):
        self.pos += pos_mod 
    
    def collideMouse(self, padding: float = 0) -> bool:
        rect = self.get_rect(padding=padding)
        
        return rect.collidepoint(pygame.mouse.get_pos())

    def get_font(self, camMod: bool = True) -> pygame.font.Font:
        size = self.FONT_SIZE
        if camMod:
            camera = camClass.get_camera()
            size *= camera.zoom
        
        return pygame.font.Font('assets/fonts/calibri-regular.ttf', round(size))
        
    def update_text(self):
        self.min_size = pygame.Vector2(0,0)
        text = copy.copy(self.raw_text)
        self.text = []
        font = self.get_font(False)

        text_words_string = text.replace("\n", " ")
        text_words = text_words_string.split(" ")
        for _, v in enumerate(text_words):
            self.min_size.x = max(self.min_size.x, font.size(v)[0]+(self.FONT_OFFSET*2))
        rect = self.get_rect(False, -self.FONT_OFFSET)

        lineSpacing = -2
        fontHeight = font.size("Tg")[1]

        lines = text.split("\n")
        for _, v in enumerate(lines):
            self.text.append("")

            words = v.split(" ")
            for _, w in enumerate(words):
                if font.size(self.text[-1]+w)[0] > rect.width:
                    self.text.append(w)
                else:
                    self.text[-1] += " " + w

        self.min_size.y = (len(self.text) * (fontHeight + lineSpacing))+(self.FONT_OFFSET*2)

    def render_text(self):
        conf: C = C.get_config()
        ## TODO - Fix a bug that causes the thing to crash if there is no text.
        screen = pygame.display.get_surface()

        font = self.get_font(True)
        font_height = font.get_height()
        
        for i, text in enumerate(self.text):
            text_surface = font.render(text, True, conf.colors.text)
            text_size = pygame.Vector2(font.size(text))
            text_pos = (self.get_pos())
            text_pos.y += font_height * (i - ((len(self.text)-1)/2))
            text_pos -= (text_size/2)
            screen.blit(text_surface, (text_pos.x, text_pos.y))

            if i == len(self.text) - 1 and self.state == self.stateTypes.TEXT:
                timestamp = pygame.time.get_ticks() % 1000
                if timestamp < 500:
                    camera = camClass.get_camera()
                    rect = pygame.Rect(
                        text_pos + pygame.Vector2(text_size.x, 0),
                        pygame.Vector2(2*camera.zoom, font_height)
                        )
                    pygame.draw.rect(screen, conf.colors.text, rect)
    
    RADIUS = 10


    def _render_rect(self, color, outline: float = 0.0):
        screen = pygame.display.get_surface()
        camera = camClass.get_camera()
        radius = self.RADIUS * camera.zoom
        outline_size = outline * camera.zoom

        rect = self.get_rect()
        rect.x += radius
        rect.y -= outline_size
        rect.w -= radius*2
        rect.h += outline_size*2
        pygame.draw.rect(screen, color, rect)

        rect = self.get_rect()
        rect.x -= outline_size
        rect.y += radius
        rect.w += outline_size*2
        rect.h -= radius*2
        pygame.draw.rect(screen, color, rect)

        rect = self.get_rect()
        circ_pos = [
            pygame.Vector2(rect.topleft) + pygame.Vector2(radius,radius),
            pygame.Vector2(rect.topright) + pygame.Vector2(-radius,radius),
            pygame.Vector2(rect.bottomleft) + pygame.Vector2(radius,-radius),
            pygame.Vector2(rect.bottomright) - pygame.Vector2(radius,radius),
        ]
        for i in circ_pos:
            pygame.draw.circle(screen, color, i, radius + outline_size)
        
    def render(self):
        conf: C = C.get_config()
        color = conf.colors.widget_outline

        if self.is_selected():#self.state == self.stateTypes.TEXT:
            color = conf.colors.widget_outline_selected

        self._render_rect(color, self.OUTLINE_SIZE)
        self._render_rect(conf.colors.widget)
    
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
        
class widget_link(element):
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
            clip1 = self.widget1.get_rect(widget.OUTLINE_SIZE/-2).clipline(pos1, pos2)
            if pos1 == pygame.Vector2(clip1[0]):
                pos1 = pygame.Vector2(clip1[1])
            
            clip2 = self.widget2.get_rect(widget.OUTLINE_SIZE/-2).clipline(pos2, pos1)
            if pos2 == pygame.Vector2(clip2[0]):
                pos2 = pygame.Vector2(clip2[1])
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
    
    def render(self):
        screen = pygame.display.get_surface()
        camera = camClass.get_camera()
        color = 'black'
        #if self == selected:
        #    color = 'red'

        line = self.get_line()
        pygame.draw.line(screen, color, line[0], line[1], round(widget.OUTLINE_SIZE*camera.zoom))