import wx
import json
from enum import *
from vectors import *

FILETYPES = "JSON File (*.json)|*.json|All files (*.*)|*.json"

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
        self.canvas = Canvas(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # The '1' means it takes up available proportional space
        # The 'wx.EXPAND' means it fills the space in both directions
        sizer.Add(self.canvas, 1, wx.EXPAND) 
        self.SetSizer(sizer)

        self.current_file_directory = None
        self.recent_file_directory = None # Currently unused, meant for the Open Recent function.

        wx.Font.AddPrivateFont("assets/fonts/calibri-regular.ttf")

        PoppleButton(self.canvas, PoppleButton.Types.DELETE, Vector2(0,0))
        PoppleButton(self.canvas, PoppleButton.Types.RESIZE, Vector2(1,1))
        PoppleButton(self.canvas, PoppleButton.Types.LINK, Vector2(0.5,0))
        PoppleButton(self.canvas, PoppleButton.Types.LINK, Vector2(0.5,1))
        PoppleButton(self.canvas, PoppleButton.Types.LINK, Vector2(0,0.5))
        PoppleButton(self.canvas, PoppleButton.Types.LINK, Vector2(1,0.5))
            #self.panel.Bind(wx.EVT_GESTURE_ZOOM, self.OnZoom)
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
        newPoppleItem  = editMenu.Append(wx.ID_ADD,  '&New Popple\tDouble Click',  "Create new Popple"); self.Bind(wx.EVT_MENU, self.canvas.on_add_popple, newPoppleItem)
        menuBar.Append(editMenu, 'Edit')
        #----------------
        self.SetMenuBar(menuBar)
        
        self.config = {}
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._load_config()
    
    def get_config_path(self):
        standardPaths = wx.StandardPaths.Get()
        config_root_dir: str = standardPaths.GetUserDataDir()
        config_dir = config_root_dir.replace("appinfo", 'eventlesstew/mindmapper/conf.json')
        return config_dir

    def _save_config(self):
        dir = self.get_config_path()
        try:
            with open(dir, 'w') as f:
                position = self.GetPosition()
                windowSize = self.GetSize()
                file = {
                    "x":position.x,
                    "y":position.y,
                    "w":windowSize.x,
                    "h":windowSize.y,
                }

                f.write(json.dumps(file))
                
            self.current_file_directory = dir
        except IOError:
            print('save failed')

    def _load_config(self):
        dir = self.get_config_path()
        try:
            with open(dir, 'r') as f:
                file = json.loads(f.read())

                # Set the size and position of the window.
                self.SetSize(file['x'],file['y'],file['w'],file['h'])
                
        except IOError:
            print('load failed')

    
    def filler(self, _e = None): pass

    def new(self, _e = None):
        self._new_file()
    
    def _new_file(self):
        self.canvas.clear_all()

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

                popples: list = self.canvas.get_popples()
                for _, v in enumerate(self.canvas.get_popples()):
                    if isinstance(v, Popple):
                        v_data = v.get_file_data()
                        file['widgets'].append(v_data)

                for _,v in enumerate(self.canvas.get_popple_connections()):
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
            print('save failed')
    
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
        except IOError: print('save failed'); return
        
        self.canvas.clear_all()
        popples: list[Popple] = []
        for _, v in enumerate(file['widgets']):
            popples.append(self.canvas.append_popple(Vector2(v['x'],v['y']),Vector2(v['width'], v['height']),v['text']))
        
        for _, v in enumerate(file['links']):
            widget1 = popples[v['widget1']]
            widget2 = popples[v['widget2']]
            self.canvas.append_popple_connection(widget1,widget2)
        
        self.current_file_directory = dir
    
    ## Function for closing a file
    def on_close(self, event: wx.Event):
        self._save_config()

        event.Skip()

class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetDoubleBuffered(True)
        self.SetBackgroundColour("#ffffff")

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
        APP.Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        if self.EnableTouchEvents(wx.TOUCH_ZOOM_GESTURE):
            self.Bind(wx.EVT_GESTURE_ZOOM, self.on_mouseWheel)

        self.original_zoom_factor = None
        self.drag_element = None
        self.drag_mouse_position: Vector2 = None
        self.drag_position: Vector2 = None

        self.popple_connections: list[PoppleConnection]= []

    # Gets the mouse position relative to the window.
    def get_display_mouse_position(self) -> Vector2:
        position = Vector2(wx.GetMousePosition())
        position -= self.GetPosition()
        parent = self.GetParent()
        if isinstance(parent, Window):
            position -= parent.GetPosition()

        return position
    
    # Gets the mouse position with camera taken into account.
    def get_mouse_position(self) -> Vector2:
        position = self.get_display_mouse_position()
        position /= self.camera_zoom
        position += self.camera_pos

        return position
    
    def clear_all(self):
        self.popple_connections = []
        for i in self.get_popples():
            i.Destroy()
        
        self.Refresh()
    
    # Adds a new Popple to the field
    def append_popple(self, pos: Vector2, size: Vector2 = Vector2(100,100), text:str=""):
        true_pos = pos - (size*0.5)
        return Popple(self, true_pos, size, text)

    def append_popple_connection(self, popple1, popple2 = None):
        #if not popple2:
            #popple2 = self.append_popple(self.get_mouse_position())
        new_connection = PoppleConnection(popple1, popple2)
        self.popple_connections.append(new_connection)
        self.Refresh()

    def remove_popple(self, popple):
        if isinstance(popple, Popple):
            def filter_func(v: PoppleConnection):
                if v.widget1 == popple or v.widget2 == popple:
                    return False
                return True
            
            self.popple_connections = list(filter(filter_func, self.popple_connections))
            popple.Destroy()
    
    def get_popples(self) -> list:
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, Popple):
                result.append(v)

        return result

    def get_popple_connections(self) -> list:
        return self.popple_connections

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
    
    def on_leftClick(self, event: wx.MouseEvent):
        self.SetFocusIgnoringChildren()
    
    def onRelease_leftClick(self, event: wx.MouseEvent):
        self.stop_drag()
    
    def on_rightClick(self, event:wx.MouseEvent):
        # Makes it so the camera will be dragged.
        self.set_drag(self)

    def onRelease_rightClick(self, event:wx.MouseEvent):
        # Stops the camera from being dragged.
        if self.get_drag() == self:
            self.set_drag(None)
    
    def remove_new_connections(self):
        for i, v in enumerate(self.popple_connections):
            if not v.widget2:
                self.popple_connections.pop(i)
        
    def get_new_connections(self):
        result = []
        for i, v in enumerate(self.popple_connections):
            if not v.widget2:
                result.append(v)
        return result
    
    def on_mouseMotion(self, event:wx.MouseEvent): # When the mouse is moved
        self.move_drag()

        if self.get_new_connections():
            self.Refresh()
        
        event.Skip()
        return
    
    def on_mouseWheel(self, event: wx.Event):
        if isinstance(event, wx.ZoomGestureEvent):
            if self.original_zoom_factor and not event.IsGestureStart():
                distance = event.GetZoomFactor() - self.original_zoom_factor
                self.zoom_camera(distance)
            self.original_zoom_factor = event.GetZoomFactor()
        elif isinstance(event, wx.MouseEvent):
            axis = event.GetWheelAxis()
            amount = event.GetWheelRotation()
            
            movement = Vector2()
            if axis == 0:
                movement.y = -amount
            elif axis == 1:
                movement.x = amount

            # TODO - Add functionality for MacOS trackpads if possible.
            if event.controlDown:
                self.zoom_camera(movement.y * -0.001)
            else:
                self.move_camera(movement)
    
    # Zooms camera by a specified amount
    def zoom_camera(self, amount: float):
        old_mouse_pos = self.get_mouse_position()
        self.camera_zoom += amount
        self.camera_zoom = max(self.camera_zoom, 0.1)
        self.camera_zoom = round(self.camera_zoom*100)/100

        self.camera_pos += old_mouse_pos - self.get_mouse_position()

        self.update_all_elements()

    # Moves camera by a specified amount
    def move_camera(self, pos: Vector2):
        self.camera_pos += pos
        self.update_all_elements()
    
    def move_camera_to(self, pos: Vector2):
        self.camera_pos = pos
        self.update_all_elements()
    
    # Called when camera is moved to ensure all elements are updated.
    def update_all_elements(self):
        self.update_popple_connections()
        self.update_popples()
        self.update_popple_buttons()

    def update_popples(self):
        for _,v in enumerate(self.get_popples()):
            if isinstance(v,Popple):
                v.update_display()
    
    def update_popple_connections(self):
        self.Refresh()
        return
    
    def update_popple_buttons(self):
        for _,v in enumerate(self.get_popple_buttons()):
            v.update_display()
    
    def on_focus_changed(self, event):
        self.update_all_elements()

    BORDER_WIDTH = 3
    def get_border_width(self) -> int:
        return round(self.BORDER_WIDTH * self.camera_zoom)
    
    def on_paint(self, event = None):
        # Create a Paint Device Context
        dc = wx.PaintDC(self)#event.GetEventObject()
        gc = wx.GraphicsContext.Create(dc)
        if not gc: return

        # make a pen
        pen = wx.Pen(wx.Colour(0, 0, 0), self.get_border_width(), wx.PENSTYLE_SOLID)
        gc.SetPen(pen)

        for i in self.get_popple_connections():
            if isinstance(i,PoppleConnection):
                widget1_pos = i.widget1.get_display_position() 
                widget1_pos += i.widget1.get_display_size() * 0.5

                widget2_pos = Vector2()
                if i.widget2:
                    widget2_pos = i.widget2.get_display_position()
                    widget2_pos += i.widget2.get_display_size() * 0.5
                else:
                    widget2_pos = self.get_display_mouse_position()

                path = gc.CreatePath()
                
                
                path.MoveToPoint(widget1_pos.x, widget1_pos.y)
                path.AddLineToPoint(widget2_pos.x, widget2_pos.y)
                path.CloseSubpath()

                gc.StrokePath(path)
        
        gc.Flush()
    
    def get_focused_popple(self):
        focused_element = self.FindFocus()
        if isinstance(focused_element, Popple):
            return focused_element
        elif isinstance(focused_element, wx.TextCtrl): 
            # Since the Popple's TextCtrl has focus, we need to get the Popple through the GetParent function.
            focused_element_parent = focused_element.GetParent() 
            if isinstance(focused_element_parent, Popple):
                return focused_element_parent
    
    def start_drag(self, element):
        self.set_drag(element)
    
    def stop_drag(self, element = None):
        if (not element) or element == self.drag_element:
            self.set_drag(None)

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
                            self.Refresh()
                            break
            
                if not popple_to_link: # Create a new Popple if the connection doesn't link to an existing Popple.
                    popple_to_link = self.append_popple(self.get_mouse_position())
            
                for v in self.get_new_connections(): # Link any new connections to the Popple to link.
                    v.widget2 = popple_to_link
                
    def get_drag(self):
        return self.drag_element
    
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

        if drag_element == self:
            self.move_camera_to(pos) # Properly updates Camera position
        
        elif isinstance(drag_element, Popple):
            drag_element.pos = pos
            self.update_all_elements()
        elif isinstance(drag_element, PoppleButton):
            if drag_element.type == PoppleButton.Types.LINK:
                self.Refresh()
            
            if drag_element.type == PoppleButton.Types.RESIZE:
                focused_popple = self.get_focused_popple()
                focused_popple.set_size(pos)
                self.update_all_elements()

class Popple(wx.Panel):
    MINIMUM_SIZE: Vector2 = Vector2(100,100)

    def __init__(self, parent, pos: Vector2, size: Vector2 = MINIMUM_SIZE, text: str = ""):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE)

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
            pointSize=14, 
            family=wx.FONTFAMILY_DEFAULT, 
            style=wx.FONTSTYLE_NORMAL, 
            weight=wx.FONTWEIGHT_NORMAL, 
            faceName='Calibri'
        ))

        self.textCtrl.SetForegroundColour(wx.Colour("#000000"))
        self.SetBackgroundColour(wx.Colour("#FFFFFF"))
        self.textCtrl.SetBackgroundColour(wx.Colour("#FFFFFF"))
        

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
        Bind(wx.EVT_KEY_DOWN, self.on_key)
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
    
    def ready(self, event:wx.Event):
        self.update_display()
        event.Skip()
    # Gets the position of the element relative to the Window.
    def get_display_position(self):
        pos = self.pos

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            pos -= parent.camera_pos
            pos *= parent.camera_zoom

        return pos.get_Vector2i()

    def set_size(self, new_size: Vector2):
        self.size = Vector2(
            max(self.MINIMUM_SIZE.x, new_size.x),
            max(self.MINIMUM_SIZE.y, new_size.y),
        )
    # Gets the size of the element relative to the Window.
    def get_display_size(self):
        size = self.size

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            size *= parent.camera_zoom

        return size.get_Vector2i()
    
    def get_display_rect(self) -> wx.Rect:
        pos = self.get_display_position()
        size = self.get_display_size()
        return wx.Rect(pos.x,pos.y,size.x,size.y)
    
    def on_textCtrl_textInput(self, event:wx.KeyEvent):
        #textCtrl_size = Vector2(self.textCtrl.GetSize())
        #self.textCtrl.SetSize(textCtrl_size.x,textCtrl_size.y + self.textCtrl.GetCharHeight())

        #print(textCtrl_height)
        event.Skip()
    
    def on_textCtrl_text(self, event:wx.CommandEvent):
        #self.update_display()

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
        
        parent = self.GetParent()

        if isinstance(parent, Canvas): # Adjusts the size of the text according to Zoom.
            text_font = self.textCtrl.GetFont()
            text_font.SetPointSize(round(12*parent.camera_zoom))
            self.textCtrl.SetFont(text_font)

        textCtrl_newSize: Vector2 = new_size
        textCtrl_newSize -= parent.get_border_width()*4 # Borderwidth*2 makes the text right on the Border Width.
        #textCtrl_newSize.y = self.textCtrl.GetBestHeight(textCtrl_newSize.x)
        print(textCtrl_newSize)
        self.textCtrl.SetSize(textCtrl_newSize.x, textCtrl_newSize.y)

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

    def on_unnecessary_input(self, event:wx.Event): # Overrides default behaviour and allows the canvas to manage mousewheel functions.
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            parent.GetEventHandler().ProcessEvent(event)

    def on_leftClick(self, event:wx.MouseEvent):
        if event.LeftDClick():
            self.textCtrl.SetFocus()
            parent = self.get_canvas()
        else:
            self.SetFocusIgnoringChildren()

            parent = self.GetParent()
            if isinstance(parent, Canvas):
                parent.start_drag(self)
        #event.Skip()

    def onRelease_leftClick(self, event:wx.Event):
        self.on_unnecessary_input(event)
    
    def on_mouseMotion(self, event:wx.MouseEvent):
        self.on_unnecessary_input()
        #event.Skip()
    
    def on_mouseWheel(self, event:wx.MouseEvent):
        self.on_unnecessary_input(event)
    
    def on_key(self, event:wx.KeyEvent):
        keyCode = event.GetKeyCode()
        #if keyCode == wx.KeyCode.WXK_BACK:
        #    print(self.textCtrl.IsEditable())
            #if self.textCtrl.IsEditable():
            #    pass
            #else:
            #    self.Destroy()
        
        event.Skip()
    
    def hasFocus(self) -> bool:
        return self.textCtrl.HasFocus() or self.HasFocus()

    def on_textCtrl_focused(self, event:wx.Event):
        self.setEditable(True)
        event.Skip()

    def on_textCtrl_unfocused(self, event:wx.Event):
        self.setEditable(False)
        event.Skip()
    
    def on_focused(self, event:wx.Event):
        self.Raise()
        event.Skip()

    def on_unfocused(self, event:wx.Event):
        event.Skip()
    
    def get_canvas(self) -> Canvas:
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            return parent
        return None

    def setEditable(self, value: bool):
        self.textCtrl.SetEditable(value)
    
    def on_paint(self, event:wx.PaintEvent=None):
        dc = wx.PaintDC(self)#event.GetEventObject()
        gc = wx.GraphicsContext.Create(dc)
        parent = self.get_canvas()
        if not gc: return
        
        border_width = parent.get_border_width()
        pen = wx.Pen(wx.Colour(0, 0, 0), border_width, wx.PENSTYLE_SOLID)
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

class PoppleConnection():
    def __init__(self, widget1: Popple, widget2: Popple):
        self.widget1 = widget1
        self.widget2 = widget2
        
class PoppleButton(wx.Panel):
    class Types(Enum):
        NONE = -1
        DELETE = 0
        LINK = 1
        RESIZE = 2
    
    def __init__(self, parent: wx.Window, type: int, anchor: Vector2 = (0,0)):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.type = type
        self.anchor: Vector2 = anchor
        self.SetBackgroundColour('#ff0000')

        self.size: Vector2 = Vector2(20,20)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focused)

    def get_canvas(self) -> Canvas:
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            return parent
        return None
    
    def get_focused_popple(self):
        parent = self.get_canvas()
        
        return parent.get_focused_popple()

    def update_display(self):
        
        def enable(): # This local function enables the button.
            self.Enable()
            self.Show()
            self.Raise() # TEMPORARY
        
        def disable(): # This local function disables the button.
            self.Hide()
            self.Disable()
        

        parent = self.get_canvas()
        focused_popple = self.get_focused_popple()
        if (not isinstance(focused_popple, Popple)):
            disable()
            return

        enable()

        # Determines the Size
        size = self.size * parent.camera_zoom

        size = size.get_Vector2i()
        self.SetSize(size.x,size.y)

        # Determines the Position
        pos = focused_popple.get_display_position() - size
        pos += (focused_popple.get_display_size() + size) * self.anchor

        pos = pos.get_Vector2i()
        self.Move(pos.x, pos.y)
    
    def AcceptsFocus(self):
        return False
    
    def AcceptsFocusFromKeyboard(self):
        return False
    
    def on_focused(self, event: wx.FocusEvent):
        print(event.GetEventObject())
    
    def on_leftClick(self, event):
        focused_popple = self.get_focused_popple()
        if not isinstance(focused_popple, Popple):
            return
        
        if self.type == PoppleButton.Types.DELETE:
            pass
        else:
            parent = self.get_canvas()
            parent.start_drag(self)
    
    def onRelease_leftClick(self, event:wx.MouseEvent):
        parent = self.get_canvas()
        if (not isinstance(parent, Canvas)):
            return
        print(event.GetEventObject())
        if self.type == self.Types.DELETE:
            parent.remove_popple(parent.get_focused_popple())
        else:
            parent.stop_drag(self)


APP = wx.App(True)
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