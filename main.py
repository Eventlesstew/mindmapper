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
    def append_popple(self, pos: Vector2, size: Vector2 = Vector2(100,100), text:str=""):
        true_pos = pos - (size*0.5)
        return Popple(self, true_pos, size, text)

    # TODO - Rename this to get_elements
    # Gets all Popples and Links.
    def get_popples(self):
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, Popple):
                result.append(v)

        return result

    def get_popple_connections(self):
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, PoppleConnection):
                result.append(v)

        return result

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

    # Moves camera by a specified amount
    def move_camera(self, pos: Vector2):
        self.camera_pos += pos
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
        for _,v in enumerate(self.get_popple_connections()):
            if isinstance(v,PoppleConnection):
                v.update_display()
    
    def update_popple_buttons(self):
        for _,v in enumerate(self.get_popple_buttons()):
            v.update_display()
    
    def on_focus_changed(self, event):
        self.update_all_elements()

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
        self.textCtrl.SetFocus()

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
            # So you cannot drag the Popple when editing text.
            event.Skip()
        
        elif self.hasFocus() and self.original_mouse_position and self.original_mouse_position:
            # Main Drag Code.
            parent: Canvas = self.GetParent()
            mousePos = parent.get_mouse_position()
            dist = self.original_mouse_position - self.original_position
            pos = mousePos - dist
            self.pos = pos
            self.update_display()
            parent.update_popple_buttons()
    
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
        return self.textCtrl.HasFocus()

    def on_focused(self, event:wx.Event):
        self.Raise()
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

class PoppleConnection(wx.Panel):
    def __init__(self, parent, widget1: Popple, widget2: Popple):
        super().__init__(parent)

        self.widget1 = widget1
        self.widget2 = widget2
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.update_display()
        
    def update_display(self):
        self.Lower()
        widget1_pos = self.widget1.get_display_position()
        widget1_opposite_pos = widget1_pos + self.widget1.get_display_size()
        widget2_pos = self.widget2.get_display_position()
        widget2_opposite_pos = widget2_pos + self.widget2.get_display_size()

        pos = Vector2(
            min(widget1_pos.x, widget2_pos.x),
            min(widget1_pos.y, widget2_pos.y)
        )
        size = Vector2(
            max(widget1_opposite_pos.x, widget2_opposite_pos.x)-pos.x,
            max(widget1_opposite_pos.y, widget2_opposite_pos.y)-pos.y
        )

        self.Move(pos.x, pos.y)
        self.SetSize(size.x, size.y)
        #self.on_paint()
    
    def on_paint(self, event = None):
        self.update_display()
        # Create a Paint Device Context
        dc = wx.PaintDC(self)#event.GetEventObject())
        gc = wx.GraphicsContext.Create(dc)
        if not gc: return

        # make a path that contains a circle and some lines
        pen = wx.Pen(wx.Colour(255, 0, 0), 3, wx.PENSTYLE_SOLID)
        gc.SetPen(pen)

        pos = self.GetPosition()
        widget1_pos = self.widget1.get_display_position() 
        widget1_pos += self.widget1.get_display_size() * 0.5
        widget1_pos -= pos

        widget2_pos = self.widget2.get_display_position()
        widget2_pos += self.widget2.get_display_size() * 0.5
        widget2_pos -= pos

        path = gc.CreatePath()

        path.MoveToPoint(widget1_pos.x, widget1_pos.y)
        path.AddLineToPoint(widget2_pos.x, widget2_pos.y)
        path.CloseSubpath()

        gc.StrokePath(path)
        gc.Flush()
        
class PoppleButton(wx.Button):
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

        self.Bind(wx.EVT_BUTTON, self.on_clicked)
    
    def get_focused_popple(self):
        focused_element = self.FindFocus()
        if not isinstance(focused_element, wx.TextCtrl): return None

        # Since the Popple's TextCtrl has focus, we need to get the Popple through the GetParent function.
        focused_popple = focused_element.GetParent() 
        if not isinstance(focused_popple, Popple): return None
    
        return focused_popple

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
    
    def on_clicked(self, event):
        parent = self.GetParent()
        focused_popple = self.get_focused_popple()
        if (not isinstance(parent, Canvas)) or (not isinstance(focused_popple, Popple)):
            return
        
        if self.type == self.Types.LINK:
            new_popple = parent.append_popple(Vector2())
            PoppleConnection(parent, focused_popple, new_popple)

APP = wx.App(True)
frame = Window(None)
frame.Show()
APP.MainLoop()