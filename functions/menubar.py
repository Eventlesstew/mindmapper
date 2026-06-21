import wx


class Window_Menubar(wx.MenuBar):
    def __init__(self):
        from main import get_canvas
        from main import get_window

        super().__init__()
        parent = get_window()
        # File Menu
        fileMenu = wx.Menu()

        newFileItem = fileMenu.Append(wx.ID_NEW, "&New\tCTRL+N", "Create New File")
        parent.Bind(wx.EVT_MENU, parent.new, newFileItem)

        fileMenu.Append(wx.ID_ANY, kind=wx.ITEM_SEPARATOR)

        openFileItem = fileMenu.Append(wx.ID_OPEN, "&Open\tCTRL+O", "Open File")
        parent.Bind(wx.EVT_MENU, parent.open, openFileItem)

        # TODO - Make this actually work.
        self._open_recent_menu = self._update_open_recent_menu()
        openRecentFileItem = fileMenu.Append(
            wx.ID_ANY, "&Open Recent", self._open_recent_menu
        )
        # parent.Bind(wx.EVT_MENU, parent.openRecent, openRecentFileItem)

        fileMenu.Append(wx.ID_ANY, kind=wx.ITEM_SEPARATOR)

        saveFileItem = fileMenu.Append(wx.ID_SAVE, "&Save\tCTRL+S", "Save File")
        parent.Bind(wx.EVT_MENU, parent.save, saveFileItem)

        saveAsFileItem = fileMenu.Append(
            wx.ID_SAVEAS, "&Save As\tCTRL+SHIFT+S", "Save As File"
        )
        parent.Bind(wx.EVT_MENU, parent.save_as, saveAsFileItem)

        self.Append(fileMenu, "File")

        # Edit Menu
        editMenu = wx.Menu()

        newPoppleItem = editMenu.Append(
            wx.ID_ADD, "&New Popple\tDouble Click", "Create new Popple"
        )
        parent.Bind(wx.EVT_MENU, get_canvas().on_add_popple, newPoppleItem)

        self.Append(editMenu, "Edit")

        # Selection Menu
        selectionMenu = wx.Menu()
        self.Append(selectionMenu, "Selection")

    def _update_open_recent_menu(self, _e: wx.Event = None):
        from main import get_window

        parent = get_window()

        result = wx.Menu()
        for file_dir in parent.file_history:
            item = result.Append(wx.ID_ANY, file_dir)
            parent.Bind(wx.EVT_MENU, parent.openRecent, item, item.GetId())

        return result
