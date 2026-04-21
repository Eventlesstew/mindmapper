import pygame
from elements import widget
from elements import widgetButton
from elements import widget_link
from elements import widgetButtonTypes
from camera import camClass

class fClass:
    def __init__(self):
        self.widget_list: list[widget] = []
        self.line_list: list[widget_link] = []
F = fClass()

global camera; camera: camClass = camClass()

global leftClick; leftClick = False
global leftClick_timestamp; leftClick_timestamp = pygame.time.get_ticks()
global leftClick_sequence; leftClick_sequence: int = 1

global rightClick; rightClick = False

global selected_element; selected_element: widget = None
global selected_button; selected_button: widgetButton = None

class gClass:
    def __init__(self):
        self.selected_element: widget = None
        
        self.selected_state: widgetButtonTypes = widgetButtonTypes.NULL
        self.selected_button: widgetButton = None

        self.panMousePos: pygame.Vector2 = pygame.Vector2(0,0)
G = gClass()

class confClass:
    def __init__(self):
        self.double_click_time = 200
conf = confClass()


pygame.init()
screen = pygame.display.set_mode(camera.size)
#print(type(screen))

clock = pygame.time.Clock()
running = True

dt = 0

def addWidget(pos: pygame.Vector2 = None):
    global camera
    newWidget = widget(screen, camera, pos)
    F.widget_list.append(newWidget)
    return newWidget

def removeWidget(w: widget):
    for i in range(0, len(F.widget_list)):
        if F.widget_list[i] == w:
            F.widget_list.pop(i)
            break
    
    # TODO - Recode this to work better.
    loop = True
    while loop:
        loop = False
        for i in range(0, len(F.line_list)):
            if F.line_list[i].widget1 == w or F.line_list[i].widget2 == w:
                F.line_list.pop(i)
                loop = True
                break

def selectWidget():
    for i in range(0, len(F.widget_list)):
        if G.selected_state == widgetButtonTypes.NULL:
            F.widget_list[i].selected = F.widget_list[i].collideMouse()
        else:
            F.widget_list[i].selected = (F.widget_list[i] == G.selected_element)

def updateWidgets():
    for i in F.widget_list:
        i.update()

def on_mouseMotion():
    selectWidget()
    global rightClick, camera
    if rightClick:
        camera.move_by(pygame.Vector2(pygame.mouse.get_rel()))

def on_leftClick():
    global leftClick, leftClick_timestamp, leftClick_sequence
    leftClick = True

    pygame.mouse.get_rel()
    timestamp = pygame.time.get_ticks()

    if abs(timestamp - leftClick_timestamp) <= conf.double_click_time:
        leftClick_sequence += 1
    else:
        leftClick_sequence = 1
    
    double_click = leftClick_sequence == 2

    selected: bool = False
    for i in range(0, len(F.widget_list))[::-1]:
        v = F.widget_list[i]
        if v.collideMouse(False):
            G.selected_state = widgetButtonTypes.REPOSITION
            selected = True
        if v.collideMouse(True):
            for b in v.get_buttons():
                if b.collideMouse():
                    G.selected_button = b
                    G.selected_state = b.type
                    selected = True
        
        if selected:
            G.selected_element = v
            break
    
    if not selected:
        if double_click:
            G.selected_element = addWidget()
            G.selected_state = widgetButtonTypes.REPOSITION
    
    leftClick_timestamp = timestamp
    selectWidget()

def onRelease_leftClick():
    global leftClick
    leftClick = False
    if G.selected_element:
        G.selected_element.update()

        if G.selected_state == widgetButtonTypes.LINK:
            widget1 = G.selected_element
            widget2: widget = None
            for i in F.widget_list:
                if i != G.selected_element and i.collideMouse():
                    widget2 = i
                    G.selected_element = None
                    break
            
            if not widget2:
                widget2 = addWidget(None)
                G.selected_element = widget2
            
            F.line_list.append(widget_link(screen, camera, widget1, widget2))
        elif G.selected_state == widgetButtonTypes.DELETE:
            if G.selected_button and G.selected_button.collideMouse():
                removeWidget(G.selected_element)
    
    G.selected_state = widgetButtonTypes.NULL
    selectWidget()

def on_rightClick():
    global rightClick; rightClick = True
    pygame.mouse.get_rel()

def onRelease_rightClick():
    global rightClick; rightClick = False

def on_mouseWheel(amount: float):
    global camera
    camera.zoom_by(amount/10)
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
        on_mouseWheel(event.precise_y)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        _input(event)
    
    screen.fill("white")

    if G.selected_state != widgetButtonTypes.NULL and G.selected_element:
        if G.selected_state == widgetButtonTypes.REPOSITION:
            G.selected_element.move_by(pygame.Vector2(pygame.mouse.get_rel()))
        elif G.selected_state == widgetButtonTypes.RESIZE:
            G.selected_element.resize_by(pygame.Vector2(pygame.mouse.get_rel()) * 2)
        elif G.selected_state == widgetButtonTypes.LINK:
            pygame.draw.line(screen, 'red', G.selected_element.get_pos(), pygame.mouse.get_pos(), 5)

    for i in F.line_list:
        i.render()
    
    for i in F.widget_list:
        i.render()
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()