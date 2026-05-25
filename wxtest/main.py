import wx
import json
from vectors import *

FILETYPES = "JSON File (*.txt)|*.json|All files (*.*)|*.*"

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
        self.canvas = Canvas(self)
        self.current_file_directory = None
        

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
        #editMenu = wx.Menu()
        #newFileItem  = editMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File"); self.Bind(wx.EVT_MENU, self.filler, newFileItem)
        #menuBar.Append(editMenu, 'Edit')
        #----------------
        self.SetMenuBar(menuBar)

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
        
        print(file)
        for _, v in enumerate(file['widgets']):
            self.add_popple(Vector2(v['x'],v['y']),Vector2(v['width'], v['height']),v['text'])
            
        self.current_file_directory = dir
        print(self.get_popples())
    
    def add_popple(self, pos: Vector2, size: Vector2, text:str=""):
        true_pos = pos - (size*0.5)
        Popple(self.canvas, true_pos, size, text)
    
    def get_popples(self):
        return self.canvas.get_popples()

class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetBackgroundColour("#ffffff")

        self.camera_pos: float = Vector2()
        self.camera_zoom: float = 1.0

        self.input_leftClick = False
        self.input_mousePosition: Vector2 = Vector2()

        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftClick)
        self.Bind(wx.EVT_LEFT_UP, self.onRelease_leftClick)
        self.Bind(wx.EVT_MOTION, self.on_mouseMotion)

        ## TODO
        # Readd zooming.
        # See if this program can detect whether a trackpad or mouse is being used
        # Make it so pinching and panning on trackpads work.

    def get_popples(self):
        return self.GetChildren()

    def on_leftClick(self, event):
        self.input_leftClick = True
    
    def onRelease_leftClick(self, event):
        self.input_leftClick = False
    
    def on_mouseMotion(self, event:wx.MouseEvent):
        x,y = event.GetPosition()
        new_mousePosition = Vector2(x,y)
        mouse_movement = self.input_mousePosition - new_mousePosition
        print(mouse_movement)
        self.input_mousePosition = new_mousePosition

        if self.input_leftClick:
            self.camera_pos += mouse_movement
            for _,v in enumerate(self.get_popples()):
                if isinstance(v,Popple):
                    v.update_display()

class Popple(wx.TextCtrl):
    def __init__(self, parent, pos: Vector2, size: Vector2, text: str):
        super().__init__(parent, wx.ID_ANY, text, style=wx.TE_CENTER|wx.TE_MULTILINE)
        
        wx.TE_CENTER
        self.pos: Vector2 = pos
        self.size: Vector2 = size
        self.update_display()
    
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

app = wx.App(True)
frame = Window(None)
frame.Show()
app.MainLoop()