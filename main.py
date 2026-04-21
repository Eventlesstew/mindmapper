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

global selected_state; selected_state: widgetButtonTypes = widgetButtonTypes.NULL
global selected_element; selected_element: widget = None
global selected_button; selected_button: widgetButton = None

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
    global selected_state, selected_element
    for i in range(0, len(F.widget_list)):
        if selected_state == widgetButtonTypes.NULL:
            F.widget_list[i].selected = F.widget_list[i].collideMouse(30)
        else:
            F.widget_list[i].selected = (F.widget_list[i] == selected_element)

def updateWidgets():
    for i in F.widget_list:
        i.update()

def on_mouseMotion():
    selectWidget()
    global rightClick, camera, selected_element, selected_state
    if rightClick:
        camera.move_by(pygame.Vector2(pygame.mouse.get_rel()))
    elif selected_element:
        if selected_state == widgetButtonTypes.REPOSITION:
            selected_element.move_by(pygame.Vector2(pygame.mouse.get_rel()) / camera.zoom)
        elif selected_state == widgetButtonTypes.RESIZE:
            selected_element.resize_by(pygame.Vector2(pygame.mouse.get_rel()) * 2 / camera.zoom)

def on_leftClick():
    global leftClick, leftClick_timestamp, leftClick_sequence, selected_element, selected_state, selected_button
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
        if v.collideMouse(20):
            if v.collideMouse():
                selected_state = widgetButtonTypes.REPOSITION
                selected = True
            for b in v.get_buttons():
                if b.collideMouse():
                    selected_button = b
                    selected_state = b.type
                    selected = True
        
        if selected:
            selected_element = v
            break
    
    if not selected:
        if double_click:
            selected_element = addWidget()
            selected_state = widgetButtonTypes.REPOSITION
    
    leftClick_timestamp = timestamp
    selectWidget()

def onRelease_leftClick():
    global leftClick, selected_element, selected_state, selected_button
    leftClick = False
    if selected_element:
        selected_element.update()

        if selected_state == widgetButtonTypes.LINK:
            widget1 = selected_element
            widget2: widget = None
            for i in F.widget_list:
                if i != selected_element and i.collideMouse():
                    widget2 = i
                    selected_element = None
                    break
            
            if not widget2:
                widget2 = addWidget(None)
                selected_element = widget2
            
            F.line_list.append(widget_link(screen, camera, widget1, widget2))
        elif selected_state == widgetButtonTypes.DELETE:
            if selected_button and selected_button.collideMouse():
                removeWidget(selected_element)
    
    selected_state = widgetButtonTypes.NULL
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

    if selected_state != widgetButtonTypes.NULL and selected_element:
        if selected_state == widgetButtonTypes.LINK:
            pygame.draw.line(screen, 'red', selected_element.get_pos(), pygame.mouse.get_pos(), 5)

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