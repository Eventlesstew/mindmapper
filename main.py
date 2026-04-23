import pygame
from elements import widget
from elements import widgetButton
from elements import widget_link
from camera import camClass
from config import confClass
class fClass:
    def __init__(self):
        self.widget_list: list[widget] = []
        self.line_list: list[widget_link] = []
F = fClass()

pygame.init()

global camera; camera: camClass = camClass()
global screen; screen = pygame.display.set_mode(camera.size)
global leftClick; leftClick = False
global leftClick_timestamp; leftClick_timestamp = pygame.time.get_ticks()
global leftClick_sequence; leftClick_sequence: int = 1

global rightClick; rightClick = False

global selected_widget; selected_widget: widget = None
global selected_button; selected_button: widgetButton = None

button_list = [
    widgetButton(screen, camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
    widgetButton(screen, camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
    widgetButton(screen, camera, widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
    widgetButton(screen, camera, widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
    widgetButton(screen, camera, widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
    widgetButton(screen, camera, widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0)),
]

conf = confClass()
#print(type(screen))

clock = pygame.time.Clock()
running = True

dt = 0

def addWidget(pos: pygame.Vector2 = None):
    global camera, selected_widget, selected_button
    newWidget = widget(screen, camera, pos)
    F.widget_list.append(newWidget)

    selected_widget = newWidget
    selected_button = newWidget
    updateWidgets()
    return newWidget

def removeWidget(w: widget):
    global selected_widget, selected_button
    for i in range(0, len(F.widget_list)):
        v = F.widget_list[i]
        if v == selected_widget:
            selected_widget = None
            selected_button = None
        if v == w:
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

def updateWidgets():
    for i in range(0, len(F.widget_list)):
        v = F.widget_list[i]
        if v == selected_widget:
            if v.state == v.stateTypes.IDLE:
                v.state = v.stateTypes.SELECTED
        else:
            v.state = v.stateTypes.IDLE

        v.update()

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

    if selected_widget and selected_widget.collideMouse(30):
        selected_button = None
        
        for b in button_list + [selected_widget]:
            if isinstance(b, widgetButton):
                if b.collideMouse(selected_widget):
                    selected_button = b
                    break
            else:
                if b.collideMouse():
                    selected_button = b
                    break
    else:
        selected_widget = None
    
        for i in range(0, len(F.widget_list))[::-1]:
            v = F.widget_list[i]
            if v.collideMouse():
                selected_widget = v
                selected_button = v
                break
    
    if double_click:
        if selected_widget:
            selected_widget.state = widget.stateTypes.TEXT
            # Code here should be for text input.
        else:
            selected_widget = addWidget()
            selected_button = selected_widget
    
    leftClick_timestamp = timestamp
    updateWidgets()

def onRelease_leftClick():
    global leftClick, selected_widget, selected_button
    leftClick = False
    if selected_widget:
        selected_widget.update()

        if isinstance(selected_button, widgetButton):
            if selected_button.type == widgetButton.buttonTypes.LINK:
                widget1 = selected_widget
                widget2: widget = None
                for i in F.widget_list:
                    if i != selected_widget and i.collideMouse():
                        widget2 = i
                        break
                
                if not widget2:
                    widget2 = addWidget(None)
                
                F.line_list.append(widget_link(screen, camera, widget1, widget2))
                selected_widget = widget2
                updateWidgets()
            elif selected_button.type == widgetButton.buttonTypes.DELETE and selected_button.collideMouse():
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
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()