import pygame
from functions.elements import widget
from functions.elements import widget_link
from functions.ui import widgetButton
from functions.camera import camClass
from config import C

import subprocess
import sys
import json

class toolbarDropdown:
    
    def __init__(self, pos: pygame.Vector2, options: list[str]):
        self.pos: pygame.Vector2 = pos
        self.options: list[str] = options


class toolbarButton:
    TOOLBAR_HEIGHT = 20
    TOOLBAR_SPACING = 5

    def __init__(self, type):
        self.type = type
        self.size: pygame.Vector2 = pygame.Vector2(100, self.TOOLBAR_HEIGHT)
        self.index: int = 0

    def get_text(self):
        return self.type
    
    def get_rect(self) -> pygame.Rect:
        pos = pygame.Vector2((self.size.x + self.TOOLBAR_SPACING) * self.index,0) 

        return pygame.Rect(pos, self.size)

    def set_index(self, newIndex):
        self.index = newIndex
    
    def collideMouse(self):
        return self.get_rect().collidepoint(pygame.mouse.get_pos())

    def interact(self):
        G = GClass.get_G()
        if self.type == 'save':
            G.save()
        elif self.type == 'saveas':
            G.save_as()
        elif self.type == 'open':
            G.load()

    def get_popup():
        G = GClass.get_G()

    def render(self):
        config = C.get_config()
        screen = pygame.display.get_surface()
        rect = self.get_rect()
        
        font = pygame.font.Font(config.font, round(24))

        text_surface = font.render(self.get_text(), True, 'black')
        text_pos = pygame.Vector2(rect.center) - (pygame.Vector2(font.size(self.get_text()))/2)
        
        pygame.draw.rect(screen, 'gray', rect)
        screen.blit(text_surface, (text_pos, text_pos))

class GClass:
    def __init__(self):
        self.selected_element = None
        self.selected_button = None

        self.element_list = []
        self.button_list = [
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
            widgetButton(widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
            widgetButton(widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0),0,0.5),
        ]
        self.toolbar = [
            toolbarButton('save'),
            toolbarButton('saveas'),
            toolbarButton('open'),
        ]
        for i,v in enumerate(self.toolbar):
            v.set_index(i)

        self.leftClick = False
        self.leftClick_timestamp = pygame.time.get_ticks()
        self.leftClick_sequence = 1
        
        self.rightClick = False

        self.file_path = None
    
    def select_element(self):
        self.selected_button = None

        buttons = []
        buttons += self.toolbar

        if self.selected_element:
            buttons += self.button_list
            buttons.append(self.selected_element)
        
        buttons += self.get_widgets()[::-1]
        buttons += self.get_widget_links()[::-1]

        has_interacted = False
        for _, v in enumerate(buttons):
            interacted = False
            if isinstance(v, widgetButton):
                interacted = v.collideMouse(self.selected_element)
            else:
                interacted = v.collideMouse()
            
            if interacted:
                self.selected_button = v

                if isinstance(v, widget):
                    self.selected_element = v
                    
                    index = self.element_list.index(v)
                    self.element_list.append(self.element_list.pop(index))
                elif isinstance(v, widget_link):
                    self.selected_element = v
                elif isinstance(v, widgetButton):
                    if v.type == widgetButton.buttonTypes.RESIZE:
                        self.selected_element.reset_size()
                
                has_interacted = True
                break
        
        if not has_interacted:
            self.selected_element = None
            self.selected_button = None
        self._update_elements()
    
    def _update_elements(self):
        for _, v in enumerate(self.element_list):
            if v == self.selected_element:
                if v.state == v.stateTypes.IDLE:
                    v.state = v.stateTypes.SELECTED
            else:
                v.state = v.stateTypes.IDLE     
                 
    def addWidget(self, pos: pygame.Vector2 = None, select: bool = True):
        if not pos:
            pos = camClass.get_camera().get_mouse_pos()
        newWidget = widget(pos)
        self.element_list.append(newWidget)

        if select:
            self.selected_element = newWidget
            self.selected_button = newWidget
            self._update_elements()
        return newWidget
    
    def removeElement(self, element_to_delete: widget):
        def _filter(v):
            if v == element_to_delete:
                return False
            elif isinstance(v, widget_link):
                if v.widget1 == element_to_delete:
                    return False
                elif v.widget2 == element_to_delete:
                    return False
            
            return True
        
        if element_to_delete == self.selected_element:
            self.selected_element = None
            self.selected_button = None
        
        self.element_list = list(filter(_filter,self.element_list))

    def save(self):
        if not self.file_path:
            self.save_as()
        else:
            self._save_file()
    def save_as(self):
        sub = subprocess.run(
            args=[sys.executable, 'functions/filemanager.py'],
            input = 'save',
            capture_output=True,
            text=True
        )
        self.file_path = sub.stdout[:-1]
        self._save_file()  
    
    def _save_file(self):
        if not self.file_path:
            return

        # Is there a way to make it so this can be one indent instead of two?
        try: 
            with open(self.file_path, 'w') as f:
                # f is not used until the end
                # open is being called at the start here to check the file path validity
                # before compiling all the data into a JSON file.
                file = {
                    'widgets':[],
                    'links':[]
                }
                for _,v in enumerate(self.element_list):
                    if isinstance(v, widget):
                        widget_json = {
                            'x':v.get_pos(False).x,
                            'y':v.get_pos(False).y,
                            'width':v.get_rect(False).w,
                            'height':v.get_rect(False).h,
                            'text':v.raw_text,
                        }

                        file['widgets'].append(widget_json)
                    elif isinstance(v, widget_link):
                        index1:int = -1
                        index2:int = -1
                        for i,w in enumerate(self.element_list):
                            if v.widget1 == w:
                                index1 = i
                            if v.widget2 == w:
                                index2 = i
                            if index1 > -1 and index2 > -1:
                                break
                        
                        line_json = {
                            'widget1':index1,
                            'widget2':index2
                        }

                        file['links'].append(line_json)
                
                f.write(json.dumps(file))
        
        except FileNotFoundError:
            print("Invalid file path")
    
    def load(self):
        sub = subprocess.run(
            args=[sys.executable, 'functions/filemanager.py'],
            input = 'open',
            capture_output=True,
            text=True
        )
        self.file_path = sub.stdout[:-1]
        self._load_file()
    
    def _load_file(self):
        file = {}
        try:
            with open(self.file_path, 'r') as f:
                file = json.loads(f.read())
            print(file)
            self.element_list = []
            self.selected_element = None
            self.selected_button = None

            for _,v in enumerate(file['widgets']):
                w = widget(
                    pygame.Vector2(v['x'],v['y']),
                    pygame.Vector2(v['width'],v['height']),
                    v['text']
                )

                self.element_list.append(w)
            
            for _,v in enumerate(file['links']):
                widget1 = None
                widget2 = None

                for i,w in enumerate(self.element_list):
                    if i == v['widget1']:
                        widget1 = w
                    if i == v['widget2']:
                        widget2 = w
                    if widget1 and widget2:
                        break
                
                if widget1 and widget2:
                    l = widget_link(widget1, widget2)
                else:
                    print("ERROR")
                self.element_list.append(l)
        except FileNotFoundError:
            print("ERROR: File read failed")
    
    def render(self):
        screen = pygame.display.get_surface()

        if (
            self.selected_element and 
            isinstance(self.selected_button, widgetButton) and
            self.selected_button.type == widgetButton.buttonTypes.LINK
        ):
            # TODO - Rework this into an actual line.
            pygame.draw.line(screen, 'red', self.selected_element.get_pos(), pygame.mouse.get_pos(), 5)
        
        elements = []
        elements += self.get_widget_links()
        elements += self.get_widgets()
        elements += self.button_list
        elements += self.toolbar
    
        for _, v in enumerate(elements):
            if isinstance(v, widgetButton):
                v.render(self.selected_element)
            else:
                v.render()
        
        config = C.get_config()
        camera = camClass.get_camera()
        
        font = pygame.font.Font(config.font, round(24))

        text = str(camera.zoom * 100)
        text_surface = font.render(text, True, 'black')
        text_pos = pygame.Vector2(screen.get_size()) - (pygame.Vector2(font.size(text)))
        screen.blit(text_surface, (text_pos, text_pos))

    # =====
    # This is how Input is handled in the program.
    # =====
    def input(self, event):
        if event.type == pygame.MOUSEMOTION:
            G.on_mouseMotion()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                G.on_leftClick()
            if event.button == 3:
                G.on_rightClick()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                G.onRelease_leftClick()
            if event.button == 3:
                G.onRelease_rightClick()
        if event.type == pygame.MOUSEWHEEL:
            G.on_mouseWheel(event)
        if event.type == pygame.KEYDOWN:
            G.on_keyDown(event)
    
    def on_leftClick(self):
        config = C.get_config()
        self.leftClick = True

        pygame.mouse.get_rel()
        timestamp = pygame.time.get_ticks()

        if abs(timestamp - self.leftClick_timestamp) <= config.double_click_time:
            self.leftClick_sequence += 1
        else:
            self.leftClick_sequence = 1
        double_click = self.leftClick_sequence == 2

        self.select_element()
        
        if double_click:
            if self.selected_element:
                self.selected_element.state = widget.stateTypes.TEXT
            else:
                self.selected_element = self.addWidget()
                self.selected_button = self.selected_element
        
        self.leftClick_timestamp = timestamp
    
    def onRelease_leftClick(self):
        self.leftClick = False

        if self.selected_button:
            if isinstance(self.selected_button, toolbarButton):
                self.selected_button.interact()
            elif isinstance(self.selected_button, widgetButton) and self.selected_element:
                if self.selected_button.type == widgetButton.buttonTypes.RESIZE:
                    self.selected_element.reset_size()
                elif self.selected_button.type == widgetButton.buttonTypes.LINK:
                    widget1 = self.selected_element
                    widget2: widget = None
                    for v in self.element_list:
                        if (
                            isinstance(v, widget) and 
                            v != self.selected_element and 
                            v.collideMouse()
                        ):
                            widget2 = v
                            break
                    
                    if not widget2:
                        widget2 = self.addWidget()
                    
                    self.element_list.append(widget_link(widget1, widget2))
                    self.selected_element = widget2
                    self._update_elements()
                elif self.selected_button.type == widgetButton.buttonTypes.DELETE:
                    if self.selected_button.collideMouse(self.selected_element):
                        self.removeElement(self.selected_element)
        
        self.selected_button = None
    
    def on_rightClick(self):
        self.rightClick = True
        pygame.mouse.get_rel()

    def onRelease_rightClick(self):
        self.rightClick = False
    
    def on_keyDown(self, event):
        if self.selected_element:
            self.selected_element.input_text(event)
    
    def on_mouseWheel(self, event):
        config = C.get_config()
        camera = camClass.get_camera()
        
        if config.trackpad:
            movement: pygame.Vector2 = pygame.Vector2(event.precise_x, event.precise_y) * config.trackpad_sensitivity
            if config.invert_trackpad_x:
                movement.x *= -1
            if config.invert_trackpad_y:
                movement.y *= -1
            camera.move_by(movement)
        else:
            camera.zoom_by(event.precise_y)

    # When you move your mouse.
    def on_mouseMotion(self):
        camera = camClass.get_camera()
        if self.rightClick:
            camera.move_by(pygame.Vector2(pygame.mouse.get_rel()))
        elif isinstance(self.selected_element, widget):
            if self.selected_button == self.selected_element:
                self.selected_element.move_by(pygame.Vector2(pygame.mouse.get_rel()) / camera.zoom)
            elif isinstance(self.selected_button, widgetButton):
                if self.selected_button.type == widgetButton.buttonTypes.RESIZE:
                    self.selected_element.resize_by(pygame.Vector2(pygame.mouse.get_rel()) * 2 / camera.zoom)
    
    ## GETTERS AND SETTERS
    def get_widgets(self):
        def _filter(v):
            return isinstance(v, widget)
        return list(filter(_filter,self.element_list))

    def get_widget_links(self):
        def _filter(v):
            return isinstance(v, widget_link)
        return list(filter(_filter,self.element_list))

    def get_G():
        global G
        return G

global G; G = GClass()