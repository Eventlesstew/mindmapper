import pygame
from functions.elements import widget
from functions.elements import widget_link
from functions.ui import widgetButton
from functions.camera import camClass
from config import C

import subprocess
import sys
import json

class toolbarButton:
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type
        self.size: pygame.Vector2 = pygame.Vector2(100, parent.TOOLBAR_HEIGHT)
        self.index: int = 0

    def get_text(self):
        return self.type
    
    def get_rect(self) -> pygame.Rect:
        pos = pygame.Vector2((self.size.x + self.parent.TOOLBAR_SPACING) * self.index,0) 
        pos += pygame.Vector2(self.parent.TOOLBAR_SPACING, self.parent.TOOLBAR_SPACING)

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
    TOOLBAR_HEIGHT = 30
    TOOLBAR_SPACING = 5
    def __init__(self):
        self.selected_element = None
        self.selected_button = None

        self.line_list = []
        self.widget_list = []
        self.button_list = [
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
            widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
            widgetButton(widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
            widgetButton(widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0),0,0.5),
        ]
        self.toolbar = [
            toolbarButton(self, 'mindmapper'),
            toolbarButton(self, 'save'),
            toolbarButton(self, 'saveas'),
            toolbarButton(self, 'open'),
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

        for b in self.toolbar:
            if b.collideMouse():
                self.selected_button = b
        
        if not self.selected_button:
            if self.selected_element:
                for b in self.button_list:
                    if b.collideMouse(self.selected_element):
                        self.selected_button = b
                        break
                
                if not self.selected_button:
                    if self.selected_element.collideMouse():
                        self.selected_button = self.selected_element
                    else:
                        self.selected_element = None
                        
            if not self.selected_element:
                for i, v in enumerate(self.widget_list[::-1]):
                    i = len(self.widget_list)-1-i
                    if v.collideMouse():
                        self.selected_element = v
                        self.selected_button = v
                        self.widget_list.append(self.widget_list.pop(i))
                        break
                
            if not self.selected_element:
                for i, v in enumerate(self.line_list):
                    if v.collideMouse():
                        self.selected_element = v
                        self.selected_button = v
                        break
            
            if self.selected_element and isinstance(self.selected_button, widgetButton):
                if self.selected_button.type == widgetButton.buttonTypes.RESIZE:
                    self.selected_element.reset_size()
        self._update_elements()
    def _update_elements(self):
        for _, v in enumerate(self.widget_list):
            if v == self.selected_element:
                if v.state == v.stateTypes.IDLE:
                    v.state = v.stateTypes.SELECTED
            else:
                v.state = v.stateTypes.IDLE          
    def addWidget(self, pos: pygame.Vector2 = None, select: bool = True):
        if not pos:
            camera = camClass.get_camera()
            pos = camera.get_mouse_pos()
        newWidget = widget(pos)
        self.widget_list.append(newWidget)

        if select:
            self.selected_element = newWidget
            self.selected_button = newWidget
            self._update_elements()
        return newWidget
    def removeWidget(self, w: widget):
        def _widget_filter(v: widget):
            return v != w
        def _line_filter(v: widget_link):
            return not(v == w or v.widget1 == w or v.widget2 == w)

        if w == self.selected_element:
            self.selected_element = None
            self.selected_button = None
        
        self.widget_list = list(filter(_widget_filter,self.widget_list))
        self.line_list = list(filter(_line_filter,self.line_list))

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

        file = {
            'widgets':[],
            'links':[]
        }
        for _,v in enumerate(self.widget_list):
            widget_json = {
                'x':v.get_pos(False).x,
                'y':v.get_pos(False).y,
                'width':v.get_rect(False).w,
                'height':v.get_rect(False).h,
                'text':v.raw_text,
            }
            file['widgets'].append(widget_json)
        
        for _,v in enumerate(self.line_list):
            index1:int = -1
            index2:int = -1
            for i,w in enumerate(self.widget_list):
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
        
        try:
            with open(self.file_path, 'w') as f:
                f.write(json.dumps(file))
        except FileNotFoundError:
            pass
    
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
            ## TODO - Use Addwidget and RemoveWidget when adding and removing widgets.
            with open(self.file_path, 'r') as f:
                file = json.loads(f.read())
            print(file)
            self.widget_list = []
            self.line_list = []
            self.selected_element = None
            self.selected_button = None

            for _,v in enumerate(file['widgets']):
                w = widget(
                    pygame.Vector2(v['x'],v['y']),
                    pygame.Vector2(v['width'],v['height']),
                    v['text']
                )

                self.widget_list.append(w)
            
            for _,v in enumerate(file['links']):
                widget1 = None
                widget2 = None

                for i,w in enumerate(self.widget_list):
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
                self.line_list.append(l)
        except FileNotFoundError:
            print("ERROR: File read failed")
    
    def render(self):
        screen = pygame.display.get_surface()

        if isinstance(self.selected_button, widgetButton) and self.selected_element:
            if self.selected_button.type == widgetButton.buttonTypes.LINK:
                pygame.draw.line(screen, 'red', self.selected_element.get_pos(), pygame.mouse.get_pos(), 5)
        
        for i in self.line_list:
            i.render(self.selected_element)
        
        for i in self.widget_list:
            i.render()
        
        for i in self.button_list:
            i.render(self.selected_element)
        
        for _, v in enumerate(self.toolbar):
            v.render()
        
        config = C.get_config()
        camera = camClass.get_camera()
        
        font = pygame.font.Font(config.font, round(24))

        text = str(camera.zoom * 100)
        text_surface = font.render(text, True, 'black')
        text_pos = pygame.Vector2(screen.get_size()) - (pygame.Vector2(font.size(text)))
        screen.blit(text_surface, (text_pos, text_pos))

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
                    for i in self.widget_list:
                        if i != self.selected_element and i.collideMouse():
                            widget2 = i
                            break
                    
                    if not widget2:
                        widget2 = self.addWidget()
                    
                    self.line_list.append(widget_link(widget1, widget2))
                    self.selected_element = widget2
                    self._update_elements()
                elif self.selected_button.type == widgetButton.buttonTypes.DELETE:
                    if self.selected_button.collideMouse(self.selected_element):
                        self.removeWidget(self.selected_element)
        
        self.selected_button = None

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
    
    def on_rightClick(self):
        self.rightClick = True
        pygame.mouse.get_rel()

    def onRelease_rightClick(self):
        self.rightClick = False
    
    def on_keyDown(self, event):
        if self.selected_element:
            self.selected_element.input_text(event)
    
    def get_G():
        global G
        return G
global G; G = GClass()