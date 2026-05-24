import wx

class Window(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent = parent, title = "Mindmapper")
        self.panel = wx.Panel(self)

        menuBar = wx.MenuBar()
        #--------------
        fileMenu = wx.Menu()
        newFileItem  = fileMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File")
        self.Bind(wx.EVT_MENU, self.NewFile, newFileItem)

        openFileItem = fileMenu.Append(wx.ID_OPEN, '&Open\tCTRL+O', "Open File")
        self.Bind(wx.EVT_MENU, self.OpenFile, openFileItem)

        saveFileItem = fileMenu.Append(wx.ID_SAVE, '&Save\tCTRL+S', "Save File")
        self.Bind(wx.EVT_MENU, self.SaveFile, saveFileItem)

        saveAsFileItem = fileMenu.Append(wx.ID_SAVEAS, '&Save As\tCTRL+SHIFT+S', "Save As File")
        self.Bind(wx.EVT_MENU, self.SaveAsFile, saveAsFileItem)

        menuBar.Append(fileMenu, 'File')
        #--------------
        editMenu = wx.Menu()
        newFileItem  = editMenu.Append(wx.ID_NEW,  '&New\tCTRL+N',  "Create New File")
        self.Bind(wx.EVT_MENU, self.NewFile, newFileItem)

        openFileItem = editMenu.Append(wx.ID_OPEN, '&Open\tCTRL+O', "Open File")
        self.Bind(wx.EVT_MENU, self.OpenFile, openFileItem)

        saveFileItem = editMenu.Append(wx.ID_SAVE, '&Save\tCTRL+S', "Save File")
        self.Bind(wx.EVT_MENU, self.SaveFile, saveFileItem)

        menuBar.Append(editMenu, 'Edit')
        #----------------
 
        self.SetMenuBar(menuBar)

    def OnButton(self, e):
        self.result.SetLabel(self.editname.GetValue())
 
    def NewFile(self, e):
        print("New File")
 
    def OpenFile(self, e):
        print("Open File")
    
    def SaveAsFile(self, e):
        print("Save As File")

    def SaveFile(self, e):
        print("Save File")
         

         
app = wx.App()
frame = Window(None)
frame.Show()


editname = wx.TextCtrl(frame.panel, size=(140, -1))
app.MainLoop()