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
        newFileItem  = fileMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File"); self.Bind(wx.EVT_MENU, self.filler, newFileItem) # New TODO
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
                    "widgets":[]
                }

                for _, v in enumerate(self.canvas.get_popples()):
                    v_data = v.get_file_data()
                    file['widgets'].append(v_data)

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
        file = {}
        try:
            with open(dir, 'r') as f:
                file = json.loads(f.read())
        except IOError: print('save failed'); return
        
        for _, v in enumerate(file['widgets']):
            self.canvas.append_popple(Vector2(v['x'],v['y']),Vector2(v['width'], v['height']),v['text'])
            
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

        APP.Bind(wx.EVT_RIGHT_DOWN, self.on_rightClick)
        APP.Bind(wx.EVT_RIGHT_UP, self.onRelease_rightClick)
        
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_focus_changed)
        APP.Bind(wx.EVT_MOTION, self.on_mouseMotion)
        APP.Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        if self.EnableTouchEvents(wx.TOUCH_ZOOM_GESTURE):
            self.Bind(wx.EVT_GESTURE_ZOOM, self.on_mouseWheel)

        self.original_zoom_factor = None
        self.original_mouse_position = None
        self.original_position = None

        self.popple_connections = []

    # Gets the mouse position with camera taken into account.
    def get_mouse_position(self) -> Vector2:
        position = Vector2(wx.GetMousePosition())
        parent = self.GetParent()
        if isinstance(parent, Window):
            position -= parent.GetPosition()
        
        position /= self.camera_zoom
        position += self.camera_pos

        return position
    
    # Adds a new Popple to the field
    def append_popple(self, pos: Vector2, size: Vector2 = Vector2(100,100), text:str=""):
        true_pos = pos - (size*0.5)
        return Popple(self, true_pos, size, text)

    def append_popple_connection(self, popple1, popple2 = None):
        if not popple2:
            popple2 = self.append_popple(self.get_mouse_position())
        new_connection = PoppleConnection(popple1, popple2)
        self.popple_connections.append(new_connection)

    def get_popples(self):
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
    
    def on_leftClick(self, event: wx.Event):
        self.SetFocusIgnoringChildren()
    
    def on_rightClick(self, event:wx.MouseEvent):
        # Makes it so the camera will be dragged.
        self.original_mouse_position = self.get_mouse_position()
        self.original_position = self.camera_pos

    def onRelease_rightClick(self, event:wx.MouseEvent):
        # Stops the camera from being dragged.
        self.original_mouse_position = None
        self.original_position = None
    
    def on_mouseMotion(self, event:wx.MouseEvent): # When the mouse is moved
        if event.leftIsDown:
            focused_popple = self.get_focused_popple()
            if not isinstance(focused_popple, Popple): return
            if isinstance(focused_popple.original_mouse_position, Vector2) and isinstance(focused_popple.original_position, Vector2):
                # Main Drag Code.
                mousePos = self.get_mouse_position()
                dist = focused_popple.original_mouse_position - focused_popple.original_position
                pos = mousePos - dist
                focused_popple.pos = pos
                focused_popple.update_display()
                self.update_popple_buttons()
                self.update_popple_connections()

        elif event.rightIsDown:
            if isinstance(self.original_mouse_position, Vector2) and isinstance(self.original_position, Vector2): # Checks if the camera is going to be dragged.
                self.camera_pos = self.original_position # Direct modification for get_mouse_position to work correctly.
                mousePos = self.get_mouse_position()
                dist = self.original_mouse_position + self.original_position
                pos = -mousePos + dist
                self.move_camera_to(pos) # Properly updates Camera position

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
        popples: list[Popple] = self.get_popples()

        if len(popples) <= 0: return

        pos = popples[0].get_display_position()
        opposite_pos = pos + popples[0].get_display_size()
        for i in popples:
            i_pos = i.get_display_position()
            i_opposite_pos = i_pos + i.get_display_size()

            pos.x = min(pos.x, i_pos.x)
            pos.y = min(pos.y, i_pos.y)
            opposite_pos.x = max(opposite_pos.x, i_opposite_pos.x)
            opposite_pos.y = max(opposite_pos.y, i_opposite_pos.y)
        
        size = opposite_pos-pos
        rect = wx.Rect(pos.x,pos.y,size.x,size.y)

        #self.RefreshRect(rect)
        self.Refresh()
    
    def update_popple_buttons(self):
        for _,v in enumerate(self.get_popple_buttons()):
            v.update_display()
    
    def on_focus_changed(self, event):
        self.update_all_elements()

    def on_paint(self, event = None):
        # Create a Paint Device Context
        dc = wx.PaintDC(self)#event.GetEventObject()
        gc = wx.GraphicsContext.Create(dc)
        if not gc: return

        # make a pen
        pen = wx.Pen(wx.Colour(255, 0, 0), 3, wx.PENSTYLE_SOLID)
        gc.SetPen(pen)

        for i in self.get_popple_connections():
            if isinstance(i,PoppleConnection):
                widget1_pos = i.widget1.get_display_position() 
                widget1_pos += i.widget1.get_display_size() * 0.5

                widget2_pos = i.widget2.get_display_position()
                widget2_pos += i.widget2.get_display_size() * 0.5

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

class Popple(wx.Panel):
    def __init__(self, parent, pos: Vector2, size: Vector2, text: str):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_SIMPLE)
        self.textCtrl: wx.TextCtrl = wx.TextCtrl(self, wx.ID_ANY, text, style=wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.TE_CENTER|wx.TE_MULTILINE|wx.BORDER_NONE)

        ## TODO - Make sure this works on MacOS
        self.textCtrl.SetFont(wx.Font(
            pointSize=14, 
            family=wx.FONTFAMILY_DEFAULT, 
            style=wx.FONTSTYLE_NORMAL, 
            weight=wx.FONTWEIGHT_NORMAL, 
            faceName='Calibri'
        ))

        #self.textCtrl.SetBackgroundColour(wx.Colour("#FF0000"))
        self.textCtrl.SetForegroundColour(wx.Colour("#000000"))
        self.SetBackgroundColour(wx.Colour("#FFFFFF"))
        self.textCtrl.SetBackgroundColour(wx.Colour("#FFFFFF"))
        

        self.pos: Vector2 = pos
        self.size: Vector2 = size
        self.update_display()
        
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
        #self.textCtrl.Bind(wx.EVT_MOTION, self.on_unnecessary_input)

        # These are used for dragging
        # TODO - Add the same functionality to Canvas for dragging the camera.
        self.original_mouse_position = None
        self.original_position = None
    
    # Gets the position of the element relative to the Window.
    def get_display_position(self):
        pos = self.pos

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            pos -= parent.camera_pos
            pos *= parent.camera_zoom

        return pos.get_Vector2i()

    # Gets the size of the element relative to the Window.
    def get_display_size(self):
        size = self.size

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            size *= parent.camera_zoom

        return size.get_Vector2i()
    
    # Updates the element's appearance on the window itself.
    def update_display(self):
        posi = self.get_display_position()
        sizei = self.get_display_size()
        self.Move(posi.x,posi.y)
        self.SetSize(sizei.x, sizei.y)
        self.textCtrl.SetSize(sizei.x, sizei.y)
        
        # TODO - Finish having the text scale according to zoom.
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            self.textCtrl.GetFont().SetPointSize(round(12*parent.camera_zoom))
        
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
            self.original_mouse_position = None
            self.original_position = None
        else:
            self.SetFocusIgnoringChildren()

            parent = self.GetParent()
            if isinstance(parent, Canvas):
                self.original_mouse_position = parent.get_mouse_position()
                self.original_position = self.pos
        #event.Skip()

    def onRelease_leftClick(self, event:wx.Event):
        self.original_mouse_position = None
        self.original_position = None
    
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
        self.original_mouse_position = None
        self.original_position = None
        event.Skip()
    
    def setEditable(self, value: bool):
        self.textCtrl.SetEditable(value)

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
    
    ## TODO - Use the function in parent instead.
    def get_focused_popple(self):
        focused_element = self.FindFocus()
        if isinstance(focused_element, Popple):
            return focused_element
        elif isinstance(focused_element, wx.TextCtrl): 
            # Since the Popple's TextCtrl has focus, we need to get the Popple through the GetParent function.
            focused_element_parent = focused_element.GetParent() 
            if isinstance(focused_element_parent, Popple):
                return focused_element_parent
        
        return None

    def update_display(self):
        
        def enable(): # This local function enables the button.
            self.Enable()
            self.Show()
            self.Raise() # TEMPORARY
        
        def disable(): # This local function disables the button.
            self.Hide()
            self.Disable()
        

        parent = self.GetParent()
        focused_popple = self.get_focused_popple()
        if (not isinstance(parent, Canvas)) or (not isinstance(focused_popple, Popple)):
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
    
    def on_leftClick(self, event):
        parent = self.GetParent()
        focused_popple = self.get_focused_popple()
        if (not isinstance(parent, Canvas)) or (not isinstance(focused_popple, Popple)):
            return
        
        print("hey")
        if self.type == self.Types.LINK:
            parent.append_popple_connection(focused_popple)

APP = wx.App(True)
frame = Window(None)
frame.Show()
APP.MainLoop()