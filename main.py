import wx
import json
from vectors import *

FILETYPES = "JSON File (*.json)|*.json|All files (*.*)|*.*"
CONFIG_DIRECTORY = "config.json"

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
        self.canvas = Canvas(self)
        self.current_file_directory = None
        self.recent_file_directory = None # Currently unused, meant for the Open Recent function.

        # Menu Bar
        ##-------------
        menuBar = wx.MenuBar()
        # File Menu
        #--------------
        fileMenu = wx.Menu()
        newFileItem  = fileMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File"); self.Bind(wx.EVT_MENU, self.filler, newFileItem) # New
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
    def save(self, _e = None):
        if self.current_file_directory:
            self._save_file(self.current_file_directory)
        else:
            self.save_as()

    ## Function for "Save As"
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
    
    def _open_file(self, dir: str):
        file = {}
        try:
            with open(dir, 'r') as f:
                file = json.loads(f.read())
        except IOError: print('save failed'); return
        
        for _, v in enumerate(file['widgets']):
            self.canvas.append_popple(Vector2(v['x'],v['y']),Vector2(v['width'], v['height']),v['text'])
            
        self.current_file_directory = dir
    
    def on_close(self, event: wx.Event):
        self._save_config()

        event.Skip()

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
        APP.Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        APP.Bind(wx.EVT_MOTION, self.on_mouseMotion)
        APP.Bind(wx.EVT_MOUSEWHEEL, self.on_mouseWheel)

        ## TODO
        # Readd zooming.
        # See if this program can detect whether a trackpad or mouse is being used
        # Make it so pinching and panning on trackpads work.

    def get_mouse_position(self) -> Vector2:
        position = Vector2(wx.GetMousePosition())
        parent = self.GetParent()
        if isinstance(parent, Window):
            position -= parent.GetPosition()
        
        position += self.camera_pos

        return position

    def get_focus(self):
        return self._focused_element
    
    def set_focus(self, element: wx.Panel = None):
        if self._focused_element: self._focused_element.on_unfocused()
        if element: element.on_focused()
        self._focused_element = element
    
    def append_popple(self, pos: Vector2, size: Vector2, text:str=""):
        true_pos = pos - (size*0.5)
        Popple(self, true_pos, size, text)

    def get_popples(self):
        return self.GetChildren()

    def on_add_popple(self, event: wx.Event):
        pos = Vector2()
        if event.GetEventObject() == self:
            pos = self.get_mouse_position()
        else:
            parent = self.GetParent()
            if isinstance(parent, Window):
                pos += Vector2(parent.GetSize()) * 0.5
                print(pos)
            pos += self.camera_pos
        self.append_popple(pos, Vector2(100,100))
    
    def on_leftClick(self, event: wx.Event):
        self.set_focus(None)
    
    def onRelease_leftClick(self, event: wx.Event):
        pass
    
    def on_mouseMotion(self, event:wx.MouseEvent):
        x,y = event.GetPosition()
        new_mousePosition = Vector2(x,y)
        mouse_movement = self.input_mousePosition - new_mousePosition
        self.input_mousePosition = new_mousePosition

        focus = self.get_focus()
        if event.Dragging() and isinstance(focus, Popple): 
            ## TODO - Fix this being buggy.
            focus.pos -= mouse_movement
            focus.update_display()
    
    def on_mouseWheel(self, event: wx.MouseEvent):
        axis = event.GetWheelAxis()
        amount = event.GetWheelRotation()
        
        movement = Vector2()
        if axis == 0:
            movement.y = -amount
        elif axis == 1:
            movement.x = amount
        self.move_camera(movement)
    
    def move_camera(self, pos: Vector2):
        self.camera_pos += pos
        for _,v in enumerate(self.get_popples()):
            if isinstance(v,Popple):
                v.update_display()

class Popple(wx.Panel):
    def __init__(self, parent, pos: Vector2, size: Vector2, text: str):
        super().__init__(parent, wx.ID_ANY)
        self.textCtrl: wx.TextCtrl = wx.TextCtrl(self, wx.ID_ANY, text, style=wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.TE_CENTER|wx.TE_MULTILINE)
        
        self.pos: Vector2 = pos
        self.size: Vector2 = size
        self.update_display()

        self.textCtrl.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)

        self.textCtrl.Bind(wx.EVT_LEFT_DCLICK, self.on_leftDoubleClick)

        self.textCtrl.Bind(wx.EVT_MOUSEWHEEL, self.on_unnecessary_input)
    
    def get_display_position(self):
        pos = self.pos

        parent = self.GetParent()
        if isinstance(parent,Canvas):
            pos -= parent.camera_pos

        return pos.get_Vector2i()

    def update_display(self):
        posi = self.get_display_position()
        self.Move(posi.x,posi.y)
        self.SetSize(self.size.x, self.size.y)
        self.textCtrl.SetSize(self.size.x, self.size.y)
    
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

    def on_leftClick(self, event:wx.Event):
        print("gottem")
        self.grab_focus()
        event.Skip()

    def on_leftDoubleClick(self, event):
        # When anything else is clicked on, disable editable text.
        if self.has_focus():
            self.textCtrl.SetEditable(True)
    
    def grab_focus(self):
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            parent.set_focus(self)
    
    def has_focus(self) -> bool:
        parent = self.GetParent()
        if isinstance(parent, Canvas):
            return parent.get_focus() == self
        return False

    def on_focused(self):
        pass

    def on_unfocused(self):
        self.textCtrl.SetEditable(False)
        

APP = wx.App(True)
frame = Window(None)
frame.Show()
APP.MainLoop()