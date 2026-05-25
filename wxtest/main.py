import wx
import json
from vectors import *

FILETYPES = "JSON File (*.txt)|*.json|All files (*.*)|*.*"

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
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
        print(self.GetChildren())
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
            Popple(self, Vector2(v['x'],v['y']), Vector2(v['width'], v['height']), v['text'])
            
        self.current_file_directory = dir

class Popple(wx.TextCtrl):
    def __init__(self, parent, pos: Vector2, size: Vector2, text: str):
        super().__init__(parent, wx.ID_ANY, text, style=wx.TE_CENTER|wx.TE_MULTILINE)
        
        wx.TE_CENTER
        self.pos: Vector2 = pos
        self.size: Vector2 = size
        self._update_display()
    
    def _update_display(self):
        self.Move(int(self.pos.x),int(self.pos.y))
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