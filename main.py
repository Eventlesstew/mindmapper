import pygame
from functions.elements import widget
from functions.elements import widgetButton
from functions.elements import widget_link
from functions.toolbar import toolbarClass
from functions.toolbar import toolbarButton
from functions.camera import camClass
from config import confClass

from tkinter import filedialog
import json

## TODO
# Move the fileClass to a new file
# Make it so you can add images and they are included in the save.
# Allow saving of config options.
class fClass:
    FILETYPES = [
        ('Mindmap File','*.mindmap'),
        ('JSON File','*.json')
    ]
    def __init__(self):
        self.widget_list: list[widget] = []
        self.line_list: list[widget_link] = []
        self.file_path: str = None
    
    def _save_file(self, path: str):
        if not path:
            path = filedialog.asksaveasfilename(filetypes=self.FILETYPES,defaultextension=self.FILETYPES)
        
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
        
        with open(path, 'w') as f:
            f.write(json.dumps(file))

    def _load_file(self, path: str):
        filetypes = [('JSON File','*.json')]

        if not path:
            path = filedialog.askopenfilename(
                initialdir=F.file_path,
                filetypes=filetypes,
                defaultextension=filetypes
            )
        
        self.widget_list = []
        self.line_list = []
        file = {}
        with open(path, 'r') as f:
            file = json.loads(f.read())

        global camera
        for _,v in enumerate(file['widgets']):
            w = widget(
                camera,
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
                l = widget_link(camera, widget1, widget2)
            else:
                print("ERROR")
            self.line_list.append(l)

            

    def save(self):
        self._save_file(self.file_path)

    def save_as(self):
        self._save_file(None)
    
    def load(self):
        self._load_file(None)

F = fClass()

pygame.init()

global camera; camera: camClass = camClass()
screen = pygame.display.set_mode(camera.size, pygame.RESIZABLE)
pygame.display.set_caption('Mindmapper - BS without BS')

global leftClick; leftClick = False
global leftClick_timestamp; leftClick_timestamp = pygame.time.get_ticks()
global leftClick_sequence; leftClick_sequence: int = 1

global rightClick; rightClick = False

global selected_widget; selected_widget: widget = None
global selected_button; selected_button: widgetButton = None

toolbar = toolbarClass()

button_list = [
    widgetButton(camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
    widgetButton(camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
    widgetButton(camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
    widgetButton(camera, widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
    widgetButton(camera, widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
    widgetButton(camera, widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0)),
]

conf = confClass()

clock = pygame.time.Clock()
global running; running = True

dt = 0

def addWidget(pos: pygame.Vector2 = None, select: bool = True):
    global camera, selected_widget, selected_button
    newWidget = widget(camera, pos)
    F.widget_list.append(newWidget)

    if select:
        selected_widget = newWidget
        selected_button = newWidget
        updateWidgets()
    return newWidget

def removeWidget(w: widget):
    global selected_widget, selected_button

    def _widget_filter(v: widget):
        return v != w
    def _line_filter(v: widget_link):
        return not(v.widget1 == w or v.widget2 == w)

    print(F.widget_list)
    if w == selected_widget:
        selected_widget = None
        selected_button = None
    
    F.widget_list = list(filter(_widget_filter,F.widget_list))
    F.line_list = list(filter(_line_filter,F.line_list))

def updateWidgets():
    for _, v in enumerate(F.widget_list):
        if v == selected_widget:
            if v.state == v.stateTypes.IDLE:
                v.state = v.stateTypes.SELECTED
        else:
            v.state = v.stateTypes.IDLE

        #v.update()

def on_mouseMotion():
    global rightClick, camera, selected_widget, selected_button
    if rightClick:
        camera.move_by(pygame.Vector2(pygame.mouse.get_rel()))
    elif selected_widget:
        if selected_button == selected_widget:
            selected_widget.move_by(pygame.Vector2(pygame.mouse.get_rel()) / camera.zoom)
        elif isinstance(selected_button, widgetButton):
            if selected_button.type == widgetButton.buttonTypes.RESIZE:
                selected_widget.resize_by(pygame.Vector2(pygame.mouse.get_rel()) * 2 / camera.zoom)

def interact():
    global selected_widget, selected_button

    selected_button = None

    for b in toolbar.buttons:
        if b.collideMouse():
            selected_button = b
    
    if not selected_button:
        if selected_widget:
            for b in button_list:
                if b.collideMouse(selected_widget):
                    selected_button = b
                    break
            
            if not selected_button:
                if selected_widget.collideMouse():
                    selected_button = selected_widget
                else:
                    selected_widget = None
        
        if not selected_widget:
            for i, v in enumerate(F.widget_list[::-1]):
                i = len(F.widget_list)-1-i
                if v.collideMouse():
                    selected_widget = v
                    selected_button = v
                    F.widget_list.append(F.widget_list.pop(i))
                    break
    updateWidgets()


def on_leftClick():
    global leftClick, leftClick_timestamp, leftClick_sequence, selected_widget, selected_button
    leftClick = True

    pygame.mouse.get_rel()
    timestamp = pygame.time.get_ticks()

    if abs(timestamp - leftClick_timestamp) <= conf.double_click_time:
        leftClick_sequence += 1
    else:
        leftClick_sequence = 1
    double_click = leftClick_sequence == 2

    interact()
    
    if double_click:
        if selected_widget:
            selected_widget.state = widget.stateTypes.TEXT
        else:
            selected_widget = addWidget()
            selected_button = selected_widget
    
    leftClick_timestamp = timestamp

def onRelease_leftClick():
    global leftClick, selected_widget, selected_button
    leftClick = False

    if selected_button:
        if isinstance(selected_button, toolbarButton):
            if selected_button.type == 'file':
                F.save()
            elif selected_button.type == 'edit':
                F.load()
        elif selected_widget:
            if isinstance(selected_button, widgetButton):
                if selected_button.type == widgetButton.buttonTypes.RESIZE:
                    selected_widget.reset_size()
                elif selected_button.type == widgetButton.buttonTypes.LINK:
                    widget1 = selected_widget
                    widget2: widget = None
                    for i in F.widget_list:
                        if i != selected_widget and i.collideMouse():
                            widget2 = i
                            break
                    
                    if not widget2:
                        widget2 = addWidget()
                    
                    F.line_list.append(widget_link(camera, widget1, widget2))
                    selected_widget = widget2
                    updateWidgets()
                elif selected_button.type == widgetButton.buttonTypes.DELETE:
                    if selected_button.collideMouse(selected_widget):
                        removeWidget(selected_widget)
    
    selected_button = None

def on_rightClick():
    global rightClick; rightClick = True
    pygame.mouse.get_rel()

def onRelease_rightClick():
    global rightClick; rightClick = False

def on_mouseWheel(event):
    global camera
    if conf.trackpad:
        movement: pygame.Vector2 = pygame.Vector2(event.precise_x, event.precise_y) * conf.trackpad_sensitivity
        if conf.invert_trackpad_x:
            movement.x *= -1
        if conf.invert_trackpad_y:
            movement.y *= -1
        camera.move_by(movement)
    else:
        camera.zoom_by(event.precise_y/10)
        for i in F.widget_list:
            i.update_text()
    updateWidgets()
    
def _input(event):
    if event.type == pygame.MOUSEMOTION:
        on_mouseMotion()
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            on_leftClick()
        if event.button == 3:
            on_rightClick()
    if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            onRelease_leftClick()
        if event.button == 3:
            onRelease_rightClick()
    if event.type == pygame.MOUSEWHEEL:
        on_mouseWheel(event)
    if event.type == pygame.KEYDOWN:
        global selected_widget
        if selected_widget:
            selected_widget.input_text(event)

    if event.type == pygame.FINGERMOTION:
        print(pygame.Vector2(event.dx,event.dy))



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        _input(event)
    
    screen.fill("white")

    if isinstance(selected_button, widgetButton) and selected_widget:
        if selected_button.type == widgetButton.buttonTypes.LINK:
            pygame.draw.line(screen, 'red', selected_widget.get_pos(), pygame.mouse.get_pos(), 5)

    for i in F.line_list:
        i.render()
    
    for i in F.widget_list:
        i.render()

    if selected_widget:
        for i in button_list:
            i.render(selected_widget)
    
    toolbar.render()

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()