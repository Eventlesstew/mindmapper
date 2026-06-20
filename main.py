import wx
import json
from enum import *
from vectors import *
# CONTEXT
# The textboxes in the program are called Popples internally.
# I called them that due to this program's similarities with the Popplet app/website.

# The filetypes used for saving and loading.
FILETYPES = "JSON File (*.json)|*.json|All files (*.*)|*.json"

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
        
        self._canvas = Canvas(self)
        self._toolbar = BottomToolbar(self)
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        
        canvas_sizer.Add(self._canvas, 31, wx.EXPAND) 
        canvas_sizer.Add(self._toolbar, 0, wx.EXPAND) 
        self.SetSizer(canvas_sizer)

        self.current_file_directory = None
        self.recent_file_directory = None # Currently unused, meant for the Open Recent function.

        # TODO - Have it so the window tracks position and size whenever it is unmaximised.
        # Necessary for allowing maximisation or fullscreen to be maintained.

        #wx.Font.AddPrivateFont("assets/fonts/calibri-regular.ttf")

        # Popple Buttons
        PoppleButton(self._canvas, PoppleButton.Types.DELETE, Vector2(1,0))
        PoppleButton(self._canvas, PoppleButton.Types.RESIZE, Vector2(1,1))
        PoppleButton(self._canvas, PoppleButton.Types.LINK, Vector2(0.5,0), PoppleButton.SubTypes.LINK_UP)
        PoppleButton(self._canvas, PoppleButton.Types.LINK, Vector2(0.5,1), PoppleButton.SubTypes.LINK_DOWN)
        PoppleButton(self._canvas, PoppleButton.Types.LINK, Vector2(0,0.5), PoppleButton.SubTypes.LINK_LEFT)
        PoppleButton(self._canvas, PoppleButton.Types.LINK, Vector2(1,0.5), PoppleButton.SubTypes.LINK_RIGHT)
        
        # Menu Bar
        ##-------------
        menuBar = wx.MenuBar()
        # File Menu
        #--------------
        fileMenu = wx.Menu()
        newFileItem  = fileMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File"); self.Bind(wx.EVT_MENU, self.new, newFileItem) # New TODO
        openFileItem = fileMenu.Append(wx.ID_OPEN, '&Open\tCTRL+O', "Open File"); self.Bind(wx.EVT_MENU, self.open, openFileItem) # Open
        saveFileItem = fileMenu.Append(wx.ID_SAVE, '&Save\tCTRL+S', "Save File"); self.Bind(wx.EVT_MENU, self.save, saveFileItem) # Save
        saveAsFileItem = fileMenu.Append(wx.ID_SAVEAS, '&Save As\tCTRL+SHIFT+S', "Save As File"); self.Bind(wx.EVT_MENU, self.save_as, saveAsFileItem) # Save As
        menuBar.Append(fileMenu, 'File')
        # Edit Menu
        #--------------
        editMenu = wx.Menu()
        newPoppleItem  = editMenu.Append(wx.ID_ADD,  '&New Popple\tDouble Click',  "Create new Popple"); self.Bind(wx.EVT_MENU, self._canvas.on_add_popple, newPoppleItem)
        menuBar.Append(editMenu, 'Edit')
        #----------------
        self.SetMenuBar(menuBar)
        
        self.config = {}
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.window_pos: Vector2 = Vector2()
        self.window_size: Vector2 = Vector2()
        self.window_fullscreen: bool = False

        self.Bind(wx.EVT_MOVE, self.on_windowMoved)
        self.Bind(wx.EVT_FULLSCREEN, self.on_windowFullscreen)
        self.Bind(wx.EVT_SIZE, self.on_windowResized)
        self._load_config()
    
    def on_windowMoved(self, event:wx.Event):
        print("POS")
        if self.window_fullscreen:
            print("Got Fullscreened")
        elif self.IsMaximized():
            print("Maximised")
        elif self.IsFullScreen():
            print("Fullscreen")
        else:
            self.window_pos = self.GetPosition()
            print(self.window_pos)
        event.Skip()

    def on_windowFullscreen(self, event:wx.FullScreenEvent):
        self.window_fullscreen = event.IsFullScreen()

    def on_windowResized(self, event:wx.SizeEvent):
        print("SIZE")
        if self.window_fullscreen:
            print("Got Fullscreened")
        elif self.IsFullScreen():
            print("Fullscreen")
        elif self.IsMaximized():
            print("Maximised")
        else:
            self.window_size = self.GetSize()
            print(self.window_size)
            
        event.Skip()

    def get_config_path(self):
        standardPaths = wx.StandardPaths.Get()
        config_root_dir: str = standardPaths.GetUserDataDir()
        config_dir = config_root_dir.replace("appinfo", 'eventlesstew/mindmapper/conf.json')
        return config_dir

    def _save_config(self):
        dir = self.get_config_path()
        try:
            with open(dir, 'w') as f:
                print(self.window_fullscreen)
                file = {
                    "x":self.window_pos.x,
                    "y":self.window_pos.y,
                    "w":self.window_size.x,
                    "h":self.window_size.y,
                    "fullscreen":self.window_fullscreen,
                    "maximised":self.IsMaximized()
                }

                f.write(json.dumps(file))
                
            self.current_file_directory = dir
        except IOError:
            # TODO - Add a popup to indicate that saving the config has failed.
            print("Config saving has failed.")

    def _load_config(self):
        dir = self.get_config_path()
        file: dict = {}
        try:
            with open(dir, 'r') as f:
                file = json.loads(f.read())
        except IOError:
            # TODO - Add a popup to indicate that loading the config has failed.
            print("Config loading has failed.")
        
        # Window Position
        self.window_pos = Vector2(
            file.get('x', 0), 
            file.get('y', 0)
        )
        self.SetPosition(self.window_pos.get_as_wxPoint())

        # Window Size
        self.window_size = Vector2(
            file.get('w', 100),
            file.get('h', 100),
        )
        self.SetSize(self.window_size.get_as_wxSize())
        
        # TODO - Ensure this works correctly on MacOS.
        # Fullscreen and maximised.
        #self.Maximize(file.get('maximised', False))
        #self.ShowFullScreen(file.get('fullscreen', False))
            
    
    def filler(self, _e = None): pass

    def new(self, _e = None):
        self._new_file()
    
    def _new_file(self):
        self._canvas.clear_all()

    ## Function called through File > Save or CTRL+S
    def save(self, _e = None):
        if self.current_file_directory:
            self._save_file(self.current_file_directory)
        else:
            self.save_as()

    ## Function called through File > Save As or CTRL+SHIFT+S
    def save_as(self, _e = None):
        dir: str = ""
        with wx.FileDialog(
            self, 
            "Save file", 
            wildcard=FILETYPES,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # User changed their mind

            # save the current contents in the file
            dir = fileDialog.GetPath()
        
        self._save_file(dir)

    ## Function for saving a file.
    def _save_file(self, dir: str):
        try:
            with open(dir, 'w') as f:
                file = {
                    "widgets":[],
                    "links":[]
                }

                popples: list = self._canvas.get_popples()
                for _, v in enumerate(self._canvas.get_popples()):
                    if isinstance(v, Popple):
                        v_data = v.get_file_data()
                        file['widgets'].append(v_data)

                for _,v in enumerate(self._canvas.get_popple_connections()):
                    if isinstance(v, PoppleConnection):
                        try:
                            popples.index(v.widget1)
                            v_data = {
                                'widget1':popples.index(v.widget1),
                                'widget2':popples.index(v.widget2)
                            }
                            file['links'].append(v_data)
                        except IndexError:
                            pass
                f.write(json.dumps(file))
                
            self.current_file_directory = dir
        except IOError:
            pass
            # TODO - Add a popup to indicate that saving the file has failed.
    
    ## Function called through File > Open or CTRL+O
    def open(self, _e = None):
        dir: str = ""
        with wx.FileDialog(
            self, 
            "Open file", 
            wildcard=FILETYPES,
            style=wx.FD_OPEN
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL: return # User changed their mind
            dir = fileDialog.GetPath() # Get the path to the file
        
        self._open_file(dir)
    
    ## Function for opening a file
    def _open_file(self, dir: str):
        ## TODO - Add a function for clearing out all elements beforehand.
        
        file = {}
        try:
            with open(dir, 'r') as f:
                file = json.loads(f.read())
        except IOError: 
            # TODO - Add a popup to indicate that loading the file has failed.
            return
        
        self._canvas.clear_all()
        popples: list[Popple] = []
        for _, v in enumerate(file['widgets']):
            popples.append(self._canvas.append_popple(Vector2(v['x'],v['y']),Vector2(v['width'], v['height']),v['text']))
        
        for _, v in enumerate(file['links']):
            widget1 = popples[v['widget1']]
            widget2 = popples[v['widget2']]
            self._canvas.append_popple_connection(widget1,widget2)
        
        self.current_file_directory = dir
    
    ## Function for closing a file
    def on_close(self, event: wx.Event):
        self._save_config()

        event.Skip()
    
    def get_canvas(self):
        return self._canvas

    def update_display(self):
        self._canvas.update_display()
        self._toolbar.update_display()


class Canvas(wx.Panel):
    # TODO - Make it so the canvas can check if it's been modified from the original file.
    # This should be done as a boolean when anything is modified.

    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetDoubleBuffered(True) # This is necessary to ensure the popples can properly overlap eachother without causing issues.

        self.config_background_colour = '#303236'
        self.config_toolbar_background_colour = "#171717"
        self.config_toolbar_text_colour = "#FFFFFF"
        self.config_popple_background_colour = "#FFFFFF"
        self.config_popple_text_colour = "#000000"
        self.config_popple_border_colour = "#A600FF"
        self.config_delete_colour = '#ff0000'

        self.SetBackgroundColour(self.config_background_colour)

        self.camera_pos: float = Vector2()
        self.camera_zoom: float = 1.0

        self.input_mousePosition: Vector2 = Vector2()

        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_add_popple)
        self.Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)

        APP.Bind(wx.EVT_RIGHT_DOWN, self.on_rightClick)
        APP.Bind(wx.EVT_RIGHT_UP, self.onRelease_rightClick)
        
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_focus_changed)
        APP.Bind(wx.EVT_MOTION, self.on_mouseMotion)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        # TODO - Add more uses for touch gestures.
        # Also add a proper check for if the mousewheel input is coming from panning.
        if self.EnableTouchEvents(wx.TOUCH_ZOOM_GESTURE):
            APP.Bind(wx.EVT_GESTURE_ZOOM, self.onGesture_zoom)
            APP.Bind(wx.EVT_MOUSEWHEEL, self.onGesture_pan)
        else:
            APP.Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocused)

        self.original_zoom_factor = None
        self.drag_element = None
        self.drag_mouse_position: Vector2 = None
        self.drag_position: Vector2 = None

        # Since Popple Connections are only rendered in the paint events, making them separate elements in wxpython isn't necessary.
        self.popple_connections: list[PoppleConnection]= []
        self._focused_popple_connection: PoppleConnection = None

    # Gets the mouse position relative to the window.
    def get_display_mouse_position(self) -> Vector2:
        absolute_position = Vector2(wx.GetMousePosition())

        # Convert them relative to your window/panel
        position = Vector2(self.ScreenToClient(absolute_position.get_as_wxPoint()))

        return position
    
    # Gets the mouse position with camera taken into account.
    def get_mouse_position(self) -> Vector2:
        position = self.get_display_mouse_position()
        position /= self.camera_zoom
        position += self.camera_pos

        return position
    
    # Removes all Popples and Popple Connections.
    def clear_all(self):
        self.popple_connections = []
        for i in self.get_popples():
            i.Destroy()
        
        refresh()
    
    # Adds a new Popple to the field
    def append_popple(self, pos: Vector2, size: Vector2 = None, text:str=""):
        
        # If Size is None, defaults it to the Popple's Minimum Size
        if not size: size = Popple.MINIMUM_SIZE
        
        true_pos = pos - (size*0.5)
        return Popple(true_pos, size, text)

    # Adds a new Popple Connection
    def append_popple_connection(self, popple1, popple2 = None):
        valid = True

        # popple1 must not be None
        if not popple1:
            valid = False
        
        # popple1 and popple2 must not be the same.
        elif popple1 == popple2:
            valid = False
        
        # Checks if there's already a poppleconnection that links these together.
        else:
            for i in self.popple_connections:
                if (
                    (i.widget1 == popple1 and i.widget2 == popple2) or
                    (i.widget2 == popple1 and i.widget1 == popple2)
                ):
                    valid = False
                    break
        
        if valid:
            new_connection = PoppleConnection(popple1, popple2)
            self.popple_connections.append(new_connection)
            self.update_popple_connections()

    # Removes a Popple.
    def remove_popple(self, popple):
        # Function used for filtering out the popple connections linking to the removed Popple.
        if isinstance(popple, Popple):
            def filter_func(v: PoppleConnection):
                if v.widget1 == popple or v.widget2 == popple:
                    return False
                return True
            
            self.popple_connections = list(filter(filter_func, self.popple_connections))
            popple.Destroy()
            refresh()
    
    def remove_popple_connection(self, popple_connection):
        if isinstance(popple_connection, PoppleConnection):
            # Function used for filtering out the popple connection being removed.
            def filter_func(v: PoppleConnection):
                if v == popple_connection:
                    return False
                return True
            
            self.popple_connections = list(filter(filter_func, self.popple_connections))
            if self._focused_popple_connection == popple_connection:
                self._focused_popple_connection = None
            refresh()
    
    # Gets an array of all Popples.
    def get_popples(self) -> list:
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, Popple):
                result.append(v)

        return result

    # Gets an array of all Popple Connections.
    def get_popple_connections(self) -> list:
        return self.popple_connections

    # Gets an array of the Buttons used on the Popples.
    def get_popple_buttons(self):
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, PoppleButton):
                result.append(v)

        return result
    
    # Called if "Edit > Add Popple" is used.
    def on_add_popple(self, event: wx.Event):
        pos = Vector2()
        if event.GetEventObject() == self:
            pos = self.get_mouse_position()
        else:
            parent = self.GetParent()
            if isinstance(parent, Window):
                pos += Vector2(parent.GetSize()) * 0.5
            pos += self.camera_pos
        self.append_popple(pos)
    
    # TODO - Make it so you can click on the Popple Connections to do stuff to them. (Like changing end designs or deleting them)
    # Sets focus to itself so the focus is on no popples. (Focus cannot be set to nothing.)
    def on_leftClick(self, event: wx.MouseEvent):
        self.SetFocusIgnoringChildren()

        for i in self.get_popple_connections():
            if isinstance(i, PoppleConnection):
                if i.is_mouse_touching() and i != self._focused_popple_connection:
                    self.set_focused_popple_connection(i)
                    return
        self.set_focused_popple_connection(None)
    
    def get_focused_popple_connection(self):
        return self._focused_popple_connection
    
    def set_focused_popple_connection(self, new_focused_popple_connection):
        if (
            new_focused_popple_connection != self._focused_popple_connection and
            (isinstance(new_focused_popple_connection, PoppleConnection) or not new_focused_popple_connection)
        ):
            if self._focused_popple_connection:
                self._focused_popple_connection.on_unfocused()
            
            if new_focused_popple_connection:
                new_focused_popple_connection.on_focused()
            
            self._focused_popple_connection = new_focused_popple_connection
            refresh()

    # Stops dragging on anything.
    def onRelease_leftClick(self, event: wx.MouseEvent):
        self.stop_drag()
    
    # Makes it so the camera will be dragged.
    def on_rightClick(self, event:wx.MouseEvent):
        self.set_drag(self)

    # Stops the camera from being dragged when right click is released.
    def onRelease_rightClick(self, event:wx.MouseEvent):
        if self.get_drag() == self:
            self.set_drag(None)
    
    # Removes any new Connections.
    # "new connections" refers to the Popple Connections that have
    def remove_new_connections(self):
        def filter_func(n: PoppleConnection):
            if n.is_new():
                return True
            return False
        
        self.popple_connections = list(filter(filter_func, self.popple_connections))
    
    # Gets all new connections.
    def get_new_connections(self):
        result = []
        for i, v in enumerate(self.popple_connections):
            if not v.widget2:
                result.append(v)
        return result
    
    # Actions for when the mouse is being moved.
    def on_mouseMotion(self, event:wx.MouseEvent):
        self.move_drag()

        if self.get_new_connections():
            self.update_popple_connections()
        
        event.Skip()
        return
    
    # Actions for when the Mouse Wheel is being used.
    # Also occurs for any 2+ finger gestures on Macbook.

    # Using the Zoom Gesture (Pinching or Spreading two fingers.)
    def onGesture_zoom(self, event:wx.ZoomGestureEvent):
        
        if event.IsGestureStart():
            self.original_zoom_factor = event.GetZoomFactor()
        elif event.IsGestureEnd():
            self.original_zoom_factor = None
        elif self.original_zoom_factor:
            zoom_factor = event.GetZoomFactor()
            distance = zoom_factor - self.original_zoom_factor
            self.original_zoom_factor = zoom_factor
            self.zoom_camera(distance)
    
    # Using the Pan Gesture (Moving two fingers around.)
    def onGesture_pan(self, event:wx.MouseEvent):
        amount = Vector2()
        axis = event.GetWheelAxis()
        if axis == 0: # Y axis
            amount.y = -event.GetWheelRotation()
        elif axis == 1: # X axis
            amount.x = event.GetWheelRotation()

        movement = amount
        
        self.move_camera(movement)

    def on_mouseWheel(self, event: wx.MouseEvent):
        # Mouse Wheel
        amount = event.GetWheelRotation()

        self.zoom_camera(amount * 0.001)
    
    # Zooms camera by a specified amount
    # If from_position is None, uses mouse position instead.
    def zoom_camera(self, amount: float, from_position: Vector2 = None):
        old_mouse_pos = Vector2()
        if from_position:
            old_mouse_pos = from_position
        else:
            old_mouse_pos = self.get_mouse_position()
        
        self.camera_zoom += amount
        self.camera_zoom = max(self.camera_zoom, 0.1)
        self.camera_zoom = round(self.camera_zoom*100)/100

        self.camera_pos += old_mouse_pos - self.get_mouse_position()

        refresh()

    # Moves camera by a specified amount
    def move_camera(self, pos: Vector2, affected_by_zoom: bool = True):
        if affected_by_zoom:
            pos /= self.camera_zoom
        self.camera_pos += pos
        refresh()
    
    # Moves camera to a position.
    def move_camera_to(self, pos: Vector2):
        self.camera_pos = pos
        refresh()
    
    # Updates visuals of everything in the Canvas.
    def update_display(self):
        # Updates visuals of all Popples.
        for _,v in enumerate(self.get_popples()):
            if isinstance(v,Popple):
                v.update_display()
        
        # Updates visuals of all Popple Buttons.
        for _,v in enumerate(self.get_popple_buttons()):
            if isinstance(v,PoppleButton):    
                v.update_display()

        # Causes the program to refresh drawing for all Popple Connections.
        self.update_popple_connections()
    
    def update_popple_connections(self):
        self.Refresh()
    # Called when focus is changed (Moving to elements regardless of whether it has gained or lost focus)
    def on_focus_changed(self, event):
        refresh()

    def on_unfocused(self, event):
        self.set_focused_popple_connection(None)
    # This constant specifies the internal border width.
    BORDER_WIDTH = 3

    # Returns the width of the border with camera zooming taken into account.
    def get_border_width(self) -> int:
        return max(1,round(self.BORDER_WIDTH * self.camera_zoom))
    
    # Re-renders the rendering of Popple Connections
    def on_paint(self, event = None):
        dc = wx.PaintDC(self)

        # Using a Graphics Context because it has functions to allow shape drawing and also uses antialiasing.
        gc = wx.GraphicsContext.Create(dc)
        if not gc: return # TODO - Make it so the program properly handles when Graphics Context is not usable.

        # make a pen
        pen = wx.Pen(self.config_popple_border_colour, self.get_border_width(), wx.PENSTYLE_SOLID)
        gc.SetPen(pen)

        for i in self.get_popple_connections():
            if isinstance(i,PoppleConnection):
                widget1_pos = i.get_widget1_display_position()
                widget2_pos = i.get_widget2_display_position()

                path = gc.CreatePath()
                
                
                path.MoveToPoint(widget1_pos.x, widget1_pos.y)
                path.AddLineToPoint(widget2_pos.x, widget2_pos.y)
                path.CloseSubpath()

                gc.StrokePath(path)
        
        gc.Flush()
    
    # Gets the currently focused popple if there is one.
    def get_focused_popple(self):
        focused_element = self.FindFocus()
        if isinstance(focused_element, Popple):
            return focused_element
        elif isinstance(focused_element, wx.TextCtrl): 
            # Since the Popple's TextCtrl has focus, we need to get the Popple through the GetParent function.
            focused_element_parent = focused_element.GetParent() 
            if isinstance(focused_element_parent, Popple):
                return focused_element_parent
    
    # Starts dragging of an element.
    def start_drag(self, element):
        self.set_drag(element)
    
    # Stops dragging of an element.
    def stop_drag(self, element = None):
        # If element isn't None, only stops dragging the element itself to prevent interference with other items being dragged.
        if (not element) or element == self.drag_element:
            self.set_drag(None)

    # Sets which item is being dragged.
    def set_drag(self, element):
        old_element = self.drag_element
        self.drag_element = element
        self.drag_mouse_position = self.get_mouse_position()

        if element == self:
            self.drag_position = self.camera_pos
        elif isinstance(element, Popple):
            self.drag_position = element.pos
        elif isinstance(element, PoppleButton):
            if element.type == PoppleButton.Types.LINK:
                self.append_popple_connection(self.get_focused_popple())
            elif element.type == PoppleButton.Types.RESIZE:
                self.drag_position = self.get_focused_popple().size
        
        if isinstance(old_element, PoppleButton):
            if old_element.type == PoppleButton.Types.LINK:
                popple_to_link: Popple = None
                for p in self.get_popples(): # Check if the mouse is in any existing Popples. 
                    if isinstance(p, Popple):
                        display_mouse_position = self.get_display_mouse_position()
                        if p.get_display_rect().Contains(display_mouse_position.x, display_mouse_position.y):
                            popple_to_link = p
                            self.update_popple_connections()
                            break
            
                if not popple_to_link: # Create a new Popple if the connection doesn't link to an existing Popple.
                    popple_to_link = self.append_popple(self.get_mouse_position())
            
                for v in self.get_new_connections(): # Link any new connections to the Popple to link.
                    v.widget2 = popple_to_link
    
    # Gets the item being dragged.
    def get_drag(self):
        return self.drag_element
    
    # Moves the dragged item around. This behaviour varies depending on the object.
    def move_drag(self):
        drag_element = self.drag_element

        if not drag_element: return

        if drag_element == self:
            self.camera_pos = self.drag_position # Direct modification for get_mouse_position to work correctly.

        mousePos = self.get_mouse_position()
        mouse_dist = mousePos - self.drag_mouse_position

        if drag_element == self:
            mouse_dist *= -1
        
        pos = self.drag_position + mouse_dist

        # If dragging the canvas, move the camera around.
        if drag_element == self:
            self.move_camera_to(pos) # Properly updates Camera position
        
        # Drags the Popple's position around
        elif isinstance(drag_element, Popple):
            drag_element.pos = pos
            refresh()
        
        # Causes different behaviours depending on the Button's type.
        elif isinstance(drag_element, PoppleButton):

            # Link Button
            if drag_element.type == PoppleButton.Types.LINK:
                # Since the PoppleConnection following the mouse is rendered visually, just give the program an update.
                self.update_popple_connections()
            
            # Resize button - Resizes the Popple
            if drag_element.type == PoppleButton.Types.RESIZE:
                focused_popple = self.get_focused_popple()
                focused_popple.set_size(pos)
                refresh()

def get_window() -> Window:
    return wx.GetTopLevelWindows()[0]

# Helper function for below elements to get the canvas window.
def get_canvas() -> Canvas:
    result: Canvas = None
    app = get_window()
    if isinstance(app, Window):
        result = app.get_canvas()
    
    return result

def refresh():
    window = get_window()

    window.update_display()

class Popple(wx.Panel):
    # The minimum size that the Popple can be at.
    MINIMUM_SIZE: Vector2 = Vector2(150,100)

    # The font size used for the text. 
    FONT_SIZE = 14

    def __init__(self, pos: Vector2, size: Vector2 = MINIMUM_SIZE, text: str = ""):
        canvas = get_canvas()
        super().__init__(canvas, wx.ID_ANY, style=wx.BORDER_NONE)

        textCtrl_style = (
            wx.TE_READONLY|
            wx.TE_NO_VSCROLL|
            wx.TE_CENTER|
            wx.TE_MULTILINE|
            wx.BORDER_NONE
        )

        self.textCtrl: wx.TextCtrl = wx.TextCtrl(self, wx.ID_ANY, text, style=textCtrl_style)

        ## TODO - Make sure this works on MacOS
        self.textCtrl.SetFont(wx.Font(
            pointSize=self.FONT_SIZE, 
            family=wx.FONTFAMILY_DEFAULT, 
            style=wx.FONTSTYLE_NORMAL, 
            weight=wx.FONTWEIGHT_NORMAL, 
            faceName='Calibri'
        ))

        self.SetBackgroundColour(canvas.config_popple_background_colour)

        # TODO - Find a way to make this transparent.
        self.textCtrl.SetBackgroundColour(canvas.config_popple_background_colour)
        self.textCtrl.SetForegroundColour(canvas.config_popple_text_colour)
        
        self.pos: Vector2 = pos
        self.size: Vector2 = size
        
        # A seperate function is used because both the popple and the text element can recieve inputs.
        # I cannot just disable all binds for the textctrl because it needs to be able to get text when it can.
        def Bind(event: wx.PyEventBinder, handler):
            self.textCtrl.Bind(event, handler)
            self.Bind(event, handler)

        Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        Bind(wx.EVT_LEFT_DCLICK, self.on_leftClick)
        Bind(wx.EVT_MOTION, self.on_unnecessary_input)
        Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        self.Bind(wx.EVT_SET_FOCUS, self.on_focused)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocused)
        self.textCtrl.Bind(wx.EVT_SET_FOCUS, self.on_textCtrl_focused)
        self.textCtrl.Bind(wx.EVT_KILL_FOCUS, self.on_textCtrl_unfocused)
        self.textCtrl.Bind(wx.EVT_KEY_DOWN, self.on_textCtrl_textInput)
        self.textCtrl.Bind(wx.EVT_TEXT, self.on_textCtrl_text)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_WINDOW_CREATE, self.ready)

        self.update_display()
        #self.textCtrl.Bind(wx.EVT_MOTION, self.on_unnecessary_input)
    
    # A separate ready function is necessary for drawing operations performed on initial creation of the window.
    def ready(self, event:wx.Event):
        self.update_display()
        event.Skip()
    
    # Gets the position relative to the window.
    def get_display_position(self):
        pos = self.pos

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            pos -= parent.camera_pos
            pos *= parent.camera_zoom

        return pos.get_as_Vector2i()

    # Gets the internal size.
    def set_size(self, new_size: Vector2):
        self.size = Vector2(
            max(self.MINIMUM_SIZE.x, new_size.x),
            max(self.MINIMUM_SIZE.y, new_size.y),
        )
    
    # Gets the size relative to the window.
    def get_display_size(self):
        size = self.size

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            size *= parent.camera_zoom

        return size.get_as_Vector2i()
    
    # Gets the rect of the Popple relative to the window. (Contains Position and Size)
    def get_display_rect(self) -> wx.Rect:
        pos = self.get_display_position()
        size = self.get_display_size()
        return wx.Rect(pos.x,pos.y,size.x,size.y)
    
    # Called when inputting text to the TextInput before the text is parsed.
    def on_textCtrl_textInput(self, event:wx.KeyEvent):
        # Doesn't do anything right now.

        #textCtrl_size = Vector2(self.textCtrl.GetSize())
        #self.textCtrl.SetSize(textCtrl_size.x,textCtrl_size.y + self.textCtrl.GetCharHeight())

        #print(textCtrl_height)
        event.Skip()
    
    # Called when inputting text to the TextInput after the text is parsed.
    def on_textCtrl_text(self, event:wx.CommandEvent):
        # Doesn't do anything right now.

        self.update_display()

        #print(textCtrl_height)
        event.Skip()
    
    # Updates the element's appearance on the window itself.
    def update_display(self):
        # Updating the Position
        new_pos = self.get_display_position()
        self.Move(new_pos.x,new_pos.y)

        # Updating the Size
        new_size = self.get_display_size()
        self.SetSize(new_size.x, new_size.y)
        
        parent = get_canvas()

        # Adjusts the size of the text according to Zoom.
        text_font = self.textCtrl.GetFont()
        text_font.SetPointSize(round(self.FONT_SIZE*parent.camera_zoom))
        self.textCtrl.SetFont(text_font)

        textCtrl_newSize: Vector2 = new_size
        textCtrl_newSize -= parent.get_border_width()*4 # Borderwidth*2 makes the text right on the Border Width.
        #textCtrl_newSize.y = self.textCtrl.GetBestHeight(textCtrl_newSize.x)
        self.textCtrl.SetSize(textCtrl_newSize.x, textCtrl_newSize.y)

        # TODO - Center the text
        #print("TEST")
        #text_string = self.textCtrl.GetValue()
        #print(self.textCtrl.GetTextExtent(text_string))

        #text_string = self.textCtrl.GetValue()
        

        #print(text_string)
        #print(self.textCtrl.GetTextExtent())
        
        # Centers the textCtrl
        textCtrl_newPos: Vector2 = round((new_size - textCtrl_newSize) * 0.5)
        self.textCtrl.Move(textCtrl_newPos.x, textCtrl_newPos.y)

        self.Refresh()
        self.Update()
    
    # Used by the file saving system to get the necessary data from this Popple.
    def get_file_data(self):
        data = {
            "x":self.pos.x,
            "y":self.pos.y,
            "width":self.size.x,
            "height":self.size.y,
            #"id":self.GetId(),
            "text":self.textCtrl.GetValue()
        }
        return data

    # Overrides default behaviour and propagates it to the Canvas.
    def on_unnecessary_input(self, event:wx.Event):
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            parent.GetEventHandler().ProcessEvent(event)

    def on_leftClick(self, event:wx.MouseEvent):
        # Activates Text Input
        if event.LeftDClick():
            self.textCtrl.SetFocus()
            parent = get_canvas()
        
        # Dragging the Popple.
        else:
            self.SetFocusIgnoringChildren()

            parent = self.GetParent()
            if isinstance(parent, Canvas):
                parent.start_drag(self)
        #event.Skip()

    # Propagates this up to the Canvas
    def onRelease_leftClick(self, event:wx.Event):
        self.on_unnecessary_input(event)

    # Propagates this up to the Canvas
    def on_mouseMotion(self, event:wx.MouseEvent):
        self.on_unnecessary_input()
        #event.Skip()
    
    # Propagates this up to the Canvas
    def on_mouseWheel(self, event:wx.MouseEvent):
        self.on_unnecessary_input(event)
    
    # Use this instead of HasFocus so the textCtrl is taken into account.
    def hasFocus(self) -> bool:
        return self.textCtrl.HasFocus() or self.HasFocus()

    # Occurs if the TextCtrl is focused. (Text edit mode)
    def on_textCtrl_focused(self, event:wx.Event):
        self.setEditable(True)
        event.Skip()

    # Occurs if the TextCtrl loses focus. (Text edit disabled)
    def on_textCtrl_unfocused(self, event:wx.Event):
        self.setEditable(False)
        event.Skip()
    
    # Occurs when the Popple itself is focused.
    def on_focused(self, event:wx.Event):
        self.Raise()
        event.Skip()

    # Occurs when the Popple itself loses focus.
    def on_unfocused(self, event:wx.Event):
        event.Skip()

    # Sets editability of the textCtrl.
    def setEditable(self, value: bool):
        self.textCtrl.SetEditable(value)
    
    # Renders Borders.
    def on_paint(self, event:wx.PaintEvent=None):
        dc = wx.PaintDC(self)#event.GetEventObject()
        gc = wx.GraphicsContext.Create(dc)
        parent = get_canvas()
        if not gc: return
        
        border_width = parent.get_border_width()
        pen = wx.Pen(parent.config_popple_border_colour, border_width, wx.PENSTYLE_SOLID)
        gc.SetPen(pen)

        pos = Vector2(math.floor(border_width*0.5))
        size = self.get_display_size() - border_width

        gc.DrawRectangle(
            pos.x,
            pos.y,
            size.x,
            size.y,
        )
        gc.Flush()

# The lines connecting between Popples.
# They're not based on wx.Panel because I didn't find that necessary.
class PoppleConnection():
    ## TODO - Make things such as getting position related to the Connection.
    def __init__(self, widget1: Popple, widget2: Popple):
        self.widget1 = widget1
        self.widget2 = widget2
    
    def get_widget1_display_position(self) -> Vector2:
        return self.get_widget_display_position(self.widget1)

    def get_widget2_display_position(self) -> Vector2:
        if self.widget2:
            return self.get_widget_display_position(self.widget2)
        else:
            canvas = get_canvas()
            return canvas.get_display_mouse_position()

    def get_widget_display_position(self, popple: Popple) -> Vector2:
        pos = popple.get_display_position() 
        pos += popple.get_display_size() * 0.5
        return pos

    def get_widget1_position(self) -> Vector2:
        return self.get_widget_position(self.widget1)

    def get_widget2_position(self) -> Vector2:
        if self.widget2:
            return self.get_widget_position(self.widget2)
        else:
            canvas = get_canvas()
            return canvas.get_mouse_position()

    def get_widget_position(self, popple: Popple) -> Vector2:
        pos = popple.pos 
        pos += popple.size * 0.5
        return pos
    
    # TODO - Test this.
    def is_mouse_touching(self):
        if self.is_new(): return True
        #line = self.get_line(False)
        canvas = get_canvas()
        pos1 = self.get_widget1_display_position()
        pos2 = self.get_widget2_display_position()
        posm = Vector2(canvas.get_display_mouse_position())
        
        linecheck: float = (
            ((pos2.x-pos1.x)*(posm.x-pos1.x))+((pos2.y-pos1.y)*(posm.y-pos1.y))
        )/(
            ((pos2.x-pos1.x)**2)+((pos2.y-pos1.y)**2)
        )

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

            distance /= canvas.get_border_width() * 2

            if distance < 1.0:
                return True
        
        return False

    def is_new(self) -> bool:
        if self.widget2:
            return False
        return True
    
    def on_focused(self):
        pass

    def on_unfocused(self):
        pass
        
class PoppleButton(wx.StaticBitmap):
    class Types(Enum):
        NONE = -1
        DELETE = 0
        LINK = 1
        RESIZE = 2
    
    class SubTypes(Enum):
        DEFAULT = 0
        LINK_UP = 0
        LINK_DOWN = 1
        LINK_LEFT = 2
        LINK_RIGHT = 3

    def __init__(self, parent: wx.Window, type: int, anchor: Vector2 = (0,0), subType: int = 0):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.type = type
        self.subtype = subType
        self.anchor: Vector2 = anchor

        self.size: Vector2 = Vector2(20,20)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focused)
        
        self.SetBackgroundColour(self.get_colour())
        self.bitmap = wx.Bitmap(self.get_texture_path())

    def get_colour(self):
        if self.type == PoppleButton.Types.DELETE:
            return "#FF0000"
        else:
            return "#A600FF"
    def get_texture_path(self):
        image_path = ""
        if self.type == PoppleButton.Types.DELETE:
            image_path = "assets/textures/delete.png"
        elif self.type == PoppleButton.Types.RESIZE:
            image_path = "assets/textures/resize.png"
        elif self.type == PoppleButton.Types.LINK:
            if self.subtype == PoppleButton.SubTypes.LINK_UP:
                image_path = "assets/textures/uparrow.png"
            elif self.subtype == PoppleButton.SubTypes.LINK_DOWN:
                image_path = "assets/textures/downarrow.png"
            elif self.subtype == PoppleButton.SubTypes.LINK_LEFT:
                image_path = "assets/textures/leftarrow.png"
            elif self.subtype == PoppleButton.SubTypes.LINK_RIGHT:
                image_path = "assets/textures/rightarrow.png"
        return image_path
    
    def get_focused_popple(self):
        parent = get_canvas()
        
        return parent.get_focused_popple()

    def update_display(self):
        
        def enable(): # This local function enables the button.
            self.Enable()
            self.Show()
            self.Raise() # TEMPORARY
        
        def disable(): # This local function disables the button.
            self.Hide()
            self.Disable()
        

        parent = get_canvas()
        focused_popple = self.get_focused_popple()

        pos: Vector2 = Vector2()

        # Determines the Size
        size = self.size * parent.camera_zoom
        size = size.get_as_Vector2i()

        if isinstance(focused_popple, Popple):
            enable()

            # Determines the Position
            pos = focused_popple.get_display_position() - size
            pos += (focused_popple.get_display_size() + size) * self.anchor
        elif parent.get_focused_popple_connection():
            if self.type == PoppleButton.Types.DELETE:
                enable()
                focused_popple_connection: PoppleConnection = parent.get_focused_popple_connection()
                pos1 = focused_popple_connection.get_widget1_display_position()
                pos2 = focused_popple_connection.get_widget2_display_position()

                pos = (pos1 + pos2)*0.5
                pos -= size * 0.5
                print(pos)
            else:
                disable()
                return
        else:
            disable()
            return

        self.Move(pos.get_as_wxPoint())
        self.SetSize(size.get_as_wxSize())

        bitmap = self.bitmap
        image = bitmap.ConvertToImage()
        image = image.Scale(size.x, size.y)
        new_bitmap = wx.Bitmap(image)
        self.SetBitmap(new_bitmap)
    
    def AcceptsFocus(self):
        return False
    
    def AcceptsFocusFromKeyboard(self):
        return False
    
    def on_focused(self, event: wx.FocusEvent):
        pass
    
    def on_leftClick(self, event):
        focused_popple = self.get_focused_popple()
        if not isinstance(focused_popple, Popple):
            return
        
        if self.type == PoppleButton.Types.DELETE:
            pass
        else:
            parent = get_canvas()
            parent.start_drag(self)
    
    def onRelease_leftClick(self, event:wx.MouseEvent):
        parent = get_canvas()
        if (not isinstance(parent, Canvas)):
            return
        if self.type == self.Types.DELETE:
            if parent.get_focused_popple():
                parent.remove_popple(parent.get_focused_popple())
            
            # TODO - Make this work properly.
            if parent.get_focused_popple_connection():
                parent.remove_popple_connection(parent.get_focused_popple_connection())
        else:
            parent.stop_drag(self)
        
class BottomToolbar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(1,40))
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.camera_zoom_counter = wx.StaticText(self, label="hello world", name="counter_camera_zoom"); sizer.Add(self.camera_zoom_counter, 1, wx.EXPAND) 
        self.camera_pos_counter = wx.StaticText(self, label="hello world", name="counter_camera_position"); sizer.Add(self.camera_pos_counter, 1, wx.EXPAND) 

        self.SetSizer(sizer)

        canvas = get_canvas()
        ## TODO - Change the text colour in the Static Text.
        self.SetBackgroundColour(canvas.config_toolbar_background_colour)
        for i in self.GetChildren():
            if isinstance(i, wx.StaticText):
                i.SetForegroundColour(canvas.config_toolbar_text_colour)
        self.Show()
        self.Raise()
        self.update_display()

    def update_display(self):
        canvas: Canvas = get_canvas()

        zoom_label_value = round(canvas.camera_zoom * 100)
        pos_value = round(canvas.camera_pos)

        # Camera Zoom
        zoom_label = (
            "ZOOM: " + str(zoom_label_value) + "%"
        )
        self.camera_zoom_counter.SetLabel(zoom_label)

        # Camera Position
        pos_label = (
            "X: " + str(pos_value.x) +"\n"+
            "Y: " + str(pos_value.y)
        )
        self.camera_pos_counter.SetLabel(pos_label)

APP = wx.App()
frame = Window(None)
frame.Show()

if __name__ == '__main__':
    import signal # This is for exiting the program safely if it is killed in terminal
    import sys

    def handle_sigint(signum, frame):
        # Handles Ctrl+C by attempting to exit the wxPython main loop safely.
        wx.CallAfter(wx.GetApp().ExitMainLoop)
    
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        APP.MainLoop()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)