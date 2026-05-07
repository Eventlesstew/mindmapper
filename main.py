import pygame
from functions.elements import widget
from functions.elements import widget_link
from functions.ui import widgetButton
from functions.ui import toolbarClass
from functions.ui import toolbarButton
from functions.camera import camClass
from config import C
from config import fileClass

## TODO
# Move the fileClass to a new file
# Make it so you can add images and they are included in the save.
# Allow saving of config options.

pygame.init()

camera = camClass.get_camera()
screen = pygame.display.set_mode(camera.size, pygame.RESIZABLE)
pygame.display.set_caption('Mindmapper - BS without BS')

global leftClick; leftClick = False
global leftClick_timestamp; leftClick_timestamp = pygame.time.get_ticks()
global leftClick_sequence; leftClick_sequence: int = 1

global rightClick; rightClick = False

global selected_element; selected_element: widget = None
global selected_button; selected_button: widgetButton = None

toolbar = toolbarClass()

button_list = [
    widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,0),20),
    widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0,0.5),20),
    widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(0.5,1),20),
    widgetButton(widgetButton.buttonTypes.LINK,pygame.Vector2(1,0.5),20),
    widgetButton(widgetButton.buttonTypes.RESIZE,pygame.Vector2(1,1)),
    widgetButton(widgetButton.buttonTypes.DELETE,pygame.Vector2(1,0),0,0.5),
]

clock = pygame.time.Clock()
global running; running = True

dt = 0

def addWidget(pos: pygame.Vector2 = None, select: bool = True):
    global selected_element, selected_button
    fileManager = fileClass.get_fileManager()

    if not pos:
        camera = camClass.get_camera()
        pos = camera.get_mouse_pos()
    newWidget = widget(pos)
    fileManager.widget_list.append(newWidget)

    if select:
        selected_element = newWidget
        selected_button = newWidget
        updateWidgets()
    return newWidget

def removeWidget(w: widget):
    global selected_element, selected_button
    fileManager = fileClass.get_fileManager()
    def _widget_filter(v: widget):
        return v != w
    def _line_filter(v: widget_link):
        return not(v == w or v.widget1 == w or v.widget2 == w)

    if w == selected_element:
        selected_element = None
        selected_button = None
    
    fileManager.widget_list = list(filter(_widget_filter,fileManager.widget_list))
    fileManager.line_list = list(filter(_line_filter,fileManager.line_list))

def updateWidgets():
    fileManager = fileClass.get_fileManager()
    for _, v in enumerate(fileManager.widget_list):
        if v == selected_element:
            if v.state == v.stateTypes.IDLE:
                v.state = v.stateTypes.SELECTED
        else:
            v.state = v.stateTypes.IDLE

        #v.update()

def on_mouseMotion():
    global rightClick, selected_element, selected_button
    camera = camClass.get_camera()
    if rightClick:
        camera.move_by(pygame.Vector2(pygame.mouse.get_rel()))
    elif isinstance(selected_element, widget):
        if selected_button == selected_element:
            selected_element.move_by(pygame.Vector2(pygame.mouse.get_rel()) / camera.zoom)
        elif isinstance(selected_button, widgetButton):
            if selected_button.type == widgetButton.buttonTypes.RESIZE:
                selected_element.resize_by(pygame.Vector2(pygame.mouse.get_rel()) * 2 / camera.zoom)

def interact():
    global selected_element, selected_button

    selected_button = None

    for b in toolbar.buttons:
        if b.collideMouse():
            selected_button = b
    
    if not selected_button:
        if selected_element:
            for b in button_list:
                if b.collideMouse(selected_element):
                    selected_button = b
                    break
            
            if not selected_button:
                if selected_element.collideMouse():
                    selected_button = selected_element
                else:
                    selected_element = None
                    
        fileManager = fileClass.get_fileManager()
        if not selected_element:
            for i, v in enumerate(fileManager.widget_list[::-1]):
                i = len(fileManager.widget_list)-1-i
                if v.collideMouse():
                    selected_element = v
                    selected_button = v
                    fileManager.widget_list.append(fileManager.widget_list.pop(i))
                    break
            
        if not selected_element:
            for i, v in enumerate(fileManager.line_list):
                if v.collideMouse():
                    selected_element = v
                    selected_button = v
                    break
        
        if selected_element and isinstance(selected_button, widgetButton):
            if selected_button.type == widgetButton.buttonTypes.RESIZE:
                selected_element.reset_size()
    updateWidgets()


def on_leftClick():
    global leftClick, leftClick_timestamp, leftClick_sequence, selected_element, selected_button
    config = C.get_config()
    leftClick = True

    pygame.mouse.get_rel()
    timestamp = pygame.time.get_ticks()

    if abs(timestamp - leftClick_timestamp) <= config.double_click_time:
        leftClick_sequence += 1
    else:
        leftClick_sequence = 1
    double_click = leftClick_sequence == 2

    interact()
    
    if double_click:
        if selected_element:
            selected_element.state = widget.stateTypes.TEXT
        else:
            selected_element = addWidget()
            selected_button = selected_element
    
    leftClick_timestamp = timestamp

def onRelease_leftClick():
    global leftClick, selected_element, selected_button
    leftClick = False

    if selected_button:
        if isinstance(selected_button, toolbarButton):
            selected_button.interact()
        elif selected_element and isinstance(selected_button, widgetButton):
            if selected_button.type == widgetButton.buttonTypes.RESIZE:
                selected_element.reset_size()
            elif selected_button.type == widgetButton.buttonTypes.LINK:
                fileManager = fileClass.get_fileManager()
                widget1 = selected_element
                widget2: widget = None
                for i in fileManager.widget_list:
                    if i != selected_element and i.collideMouse():
                        widget2 = i
                        break
                
                if not widget2:
                    widget2 = addWidget()
                
                fileManager.line_list.append(widget_link(widget1, widget2))
                selected_element = widget2
                updateWidgets()
            elif selected_button.type == widgetButton.buttonTypes.DELETE:
                if selected_button.collideMouse(selected_element):
                    removeWidget(selected_element)
    
    selected_button = None

def on_rightClick():
    global rightClick; rightClick = True
    pygame.mouse.get_rel()

def onRelease_rightClick():
    global rightClick; rightClick = False

def on_mouseWheel(event):
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
        fileManager = fileClass.get_fileManager()
        camera.zoom_by(event.precise_y)
        for i in fileManager.widget_list:
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
        global selected_element
        if selected_element:
            selected_element.input_text(event)

    #if event.type == pygame.FINGERMOTION:
    #    print(pygame.Vector2(event.dx,event.dy))



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        _input(event)
    
    screen.fill("white")

    if isinstance(selected_button, widgetButton) and selected_element:
        if selected_button.type == widgetButton.buttonTypes.LINK:
            pygame.draw.line(screen, 'red', selected_element.get_pos(), pygame.mouse.get_pos(), 5)

    fileManager = fileClass.get_fileManager()
    for i in fileManager.line_list:
        i.render(selected_element)
    
    for i in fileManager.widget_list:
        i.render()

    for i in button_list:
        i.render(selected_element)
    
    toolbar.render()

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()