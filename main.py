import wx
import json
from enum import *
from vectors import *

FILETYPES = "JSON File (*.json)|*.json|All files (*.*)|*.*"
CONFIG_DIRECTORY = "config.json"

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

        self.popple_buttons = [
            PoppleButton(self, PoppleButton.Types.DELETE, Vector2(0,0))
        ]
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

    def get_popple_buttons(self):
        return self.popple_buttons
    def _save_config(self):
        try:
            with open(CONFIG_DIRECTORY, 'w') as f:
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
        try:
            with open(CONFIG_DIRECTORY, 'r') as f:
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
                file = {}

                for _, v in enumerate(self.GetChildren()):
                    v_data = v.get_file_data()
                
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

    ## Getting all elements
    def get_popples(self):
        return self.canvas.get_popples()

class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetBackgroundColour("#ffffff")

        self.camera_pos: float = Vector2()
        self.camera_zoom: float = 1.0

        self.input_mousePosition: Vector2 = Vector2()
        self._focused_element: wx.Panel = None

        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_add_popple)
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_focus_changed)
        APP.Bind(wx.EVT_MOTION, self.on_mouseMotion)
        APP.Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        if self.EnableTouchEvents(wx.TOUCH_ZOOM_GESTURE):
            self.Bind(wx.EVT_GESTURE_ZOOM, self.on_mouseWheel)

        self.original_zoom_factor = None
        ## TODO
        # Readd zooming.
        # See if this program can detect whether a trackpad or mouse is being used
        # Make it so pinching and panning on trackpads work.

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
    def append_popple(self, pos: Vector2, size: Vector2, text:str=""):
        true_pos = pos - (size*0.5)
        Popple(self, true_pos, size, text)

    # TODO - Rename this to get_elements
    # Gets all Popples and Links.
    def get_popples(self):
        return self.GetChildren()

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
        self.append_popple(pos, Vector2(100,100))
    
    def on_leftClick(self, event: wx.Event):
        self.SetFocusIgnoringChildren()
        print(self.HasFocus())
    
    def on_mouseMotion(self, event:wx.MouseEvent):
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
                self.zoom_camera(movement.y * -0.01)
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
        print(self.camera_zoom)

    # Moves camera by a specified amount
    def move_camera(self, pos: Vector2):
        self.camera_pos += pos
        self.update_all_elements()
    
    # Called when camera is moved to ensure all elements are updated.
    def update_all_elements(self):
        for _,v in enumerate(self.get_popples()):
            if isinstance(v,Popple):
                v.update_display()
        parent = self.GetParent
        if isinstance(parent, Window):
            for _,v in enumerate(parent.get_popple_buttons()):
                v.update_display()
    
    def on_focus_changed(self, event):
        self.update_all_elements()
        print(self.FindFocus())

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
        self.SetForegroundColour(wx.Colour("#000000"))
        self.SetBackgroundColour(wx.Colour("#00FF00FF"))

        self.pos: Vector2 = pos
        self.size: Vector2 = size
        self.update_display()
        
        # A seperate function is used because both the popple and the text element can recieve inputs.
        # I cannot just disable all binds for the textctrl because it needs to be able to get text when it can.
        def Bind(event: wx.PyEventBinder, handler):
            print(handler)
            self.textCtrl.Bind(event, handler)
            self.Bind(event, handler)

        Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        Bind(wx.EVT_LEFT_DCLICK, self.on_leftClick)
        Bind(wx.EVT_MOTION, self.on_mouseMotion)
        Bind(wx.EVT_KEY_DOWN, self.on_key)
        Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        self.textCtrl.Bind(wx.EVT_SET_FOCUS, self.on_focused)
        self.textCtrl.Bind(wx.EVT_KILL_FOCUS, self.on_unfocused)
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
            print(self.textCtrl.GetFont().GetPixelSize())
    
    # Used by the file saving system to get the necessary data from this Popple.
    def get_file_data(self):
        data = {
            "x":self.pos.x,
            "y":self.pos.y,
            "width":self.size.x,
            "height":self.size.y,
            #"id":self.GetId(),
            "text":self.GetValue()
        }
        return data

    def on_unnecessary_input(self, event:wx.Event): # Overrides default behaviour and allows the canvas to manage mousewheel functions.
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            parent.GetEventHandler().ProcessEvent(event)

    def on_leftClick(self, event:wx.MouseEvent):
        self.textCtrl.SetFocus()
        print(self.textCtrl.HasFocus())

        if event.LeftDClick():
            self.setEditable(True)
            self.original_mouse_position = None
            self.original_position = None
        else:
            self.setEditable(False)

            parent = self.GetParent()
            if isinstance(parent, Canvas):
                self.original_mouse_position = parent.get_mouse_position()
                self.original_position = self.pos
        #event.Skip()

    def onRelease_leftClick(self, event:wx.Event):
        self.original_mouse_position = None
        self.original_position = None
    
    def on_mouseMotion(self, event:wx.MouseEvent):
        if self.textCtrl.IsEditable():
            event.Skip()
        elif self.hasFocus() and self.original_mouse_position and self.original_mouse_position:
            parent: Canvas = self.GetParent()
            mousePos = parent.get_mouse_position()
            dist = self.original_mouse_position - self.original_position
            pos = mousePos - dist
            self.pos = pos
            self.update_display()
    
    def on_mouseWheel(self, event:wx.MouseEvent):
        self.on_unnecessary_input(event)
    
    def on_key(self, event:wx.KeyEvent):
        keyCode = event.GetKeyCode()
        if keyCode == wx.KeyCode.WXK_BACK:
            print(self.textCtrl.IsEditable())
            #if self.textCtrl.IsEditable():
            #    pass
            #else:
            #    self.Destroy()
        
        event.Skip()
    
    def hasFocus(self) -> bool:
        return self.textCtrl.HasFocus()

    def on_focused(self, event:wx.Event):
        self.SetBackgroundColour(wx.Colour("#00FF00"))
        event.Skip()

    def on_unfocused(self, event:wx.Event):
        self.SetBackgroundColour(wx.Colour("#FF0000"))
        self.setEditable(False)
        self.original_mouse_position = None
        self.original_position = None
        event.Skip()
    
    def setEditable(self, value: bool):
        self.textCtrl.SetEditable(value)
        
class PoppleButton(wx.Button):
    class Types(Enum):
        NONE = -1
        DELETE = 0
        RESIZE = 1
    
    def __init__(self, parent: wx.Window, type: int, anchor: Vector2 = (0,0)):
        super().__init__(parent)
        self.SetSize(100,100)
        self.type = type
        self.anchor: Vector2 = anchor
    
    def update_display(self):
        focused_element = self.FindFocus()
        inactive = True
        if isinstance(focused_element, wx.TextCtrl):
            focus_parent = focused_element.GetParent()
            if isinstance(focus_parent, Popple):
                inactive = False
                self.Enable()
                pos = focus_parent.get_display_position()
                self.Move(pos)
        
        if inactive:
            self.Disable()
APP = wx.App(True)
frame = Window(None)
frame.Show()
APP.MainLoop()