import wx
import json
from enum import *
from functions.vectors import *
from canvas.canvas import *
from canvas.canvas_elements import *
from functions.menubar import Window_Menubar

# CONTEXT
# The textboxes in the program are called Popples internally.
# I called them that due to this program's similarities with the Popplet app/website.

# The filetypes used for saving and loading.
FILETYPES = "JSON File (*.json)|*.json|All files (*.*)|*.json"


class Window(wx.Frame):
    """The main window of the application"""

    def __init__(self):
        super().__init__(parent=None, title="Mindmapper")

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._canvas = Canvas(self)
        sizer.Add(self._canvas, 31, wx.EXPAND)

        self._toolbar = BottomToolbar(self)
        sizer.Add(self._toolbar, 0, wx.EXPAND)

        self.SetSizer(sizer)

        self.current_file: str = None
        self.file_history: list[str] = []

        # TODO - Make this work on MacOS
        wx.Font.AddPrivateFont("assets/fonts/calibri-regular.ttf")

        self._create_popple_buttons()

        self.config = {}
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._window_pos = Vector2()
        self._window_size: Vector2 = Vector2()
        self._window_fullscreen = False

        self._load_config()
        self.SetMenuBar(Window_Menubar())

        self.Bind(wx.EVT_MOVE, self._on_window_moved)
        self.Bind(wx.EVT_SIZE, self._on_window_resized)
        self.Bind(wx.EVT_FULLSCREEN, self._on_window_fullscreen)

    def _create_popple_buttons(self):
        CanvasButton(self._canvas, CanvasButton.Types.DELETE, Vector2(1, 0))

        CanvasButton(self._canvas, CanvasButton.Types.RESIZE, Vector2(1, 1))

        # Up Link
        CanvasButton(
            self._canvas,
            CanvasButton.Types.LINK,
            Vector2(0.5, 0),
            CanvasButton.SubTypes.LINK_UP,
        )

        # Down Link
        CanvasButton(
            self._canvas,
            CanvasButton.Types.LINK,
            Vector2(0.5, 1),
            CanvasButton.SubTypes.LINK_DOWN,
        )

        # Left Link
        CanvasButton(
            self._canvas,
            CanvasButton.Types.LINK,
            Vector2(0, 0.5),
            CanvasButton.SubTypes.LINK_LEFT,
        )

        # Right Link
        CanvasButton(
            self._canvas,
            CanvasButton.Types.LINK,
            Vector2(1, 0.5),
            CanvasButton.SubTypes.LINK_RIGHT,
        )

    def is_window_maximized_or_fullscreen(self) -> bool:
        """Returns whether the Window is maximised or using fullscreen."""
        return self._window_fullscreen or self.IsMaximized() or self.IsFullScreen()

    def _on_window_moved(self, event: wx.Event):
        if not self.is_window_maximized_or_fullscreen():
            self._window_pos = self.GetPosition()
        event.Skip()

    def _on_window_fullscreen(self, event: wx.FullScreenEvent):
        self._window_fullscreen = event.IsFullScreen()
        event.Skip()

    def _on_window_resized(self, event: wx.SizeEvent):
        if not self.is_window_maximized_or_fullscreen():
            self._window_size = self.GetSize()
        event.Skip()

    def get_config_path(self) -> str:
        """Returns the file path to the configuration file"""

        standardPaths = wx.StandardPaths.Get()
        config_root_dir: str = standardPaths.GetUserDataDir()
        config_dir = config_root_dir.replace(
            "appinfo", "eventlesstew/mindmapper/conf.json"
        )
        return config_dir

    def _save_config(self):
        dir = self.get_config_path()
        try:
            with open(dir, "w") as f:
                file = {
                    "x": self._window_pos.x,
                    "y": self._window_pos.y,
                    "w": self._window_size.x,
                    "h": self._window_size.y,
                    "file_history": self.file_history,
                    "fullscreen": self._window_fullscreen,
                    "maximised": self.IsMaximized(),
                }
                f.write(json.dumps(file))
        except IOError:
            pass

    def _load_config(self):
        dir = self.get_config_path()
        file: dict = {}

        try:
            with open(dir, "r") as f:
                file = json.loads(f.read())
        except IOError:
            pass

        # File History
        self.file_history = file.get("file_history", [])

        # Window Position
        self._window_pos = Vector2(file.get("x", 0), file.get("y", 0))
        self.SetPosition(self._window_pos.get_as_wxPoint())

        # Window Size
        self._window_size = Vector2(
            file.get("w", 100),
            file.get("h", 100),
        )
        self.SetSize(self._window_size.get_as_wxSize())

        # TODO - Ensure this works correctly on MacOS.
        # Fullscreen and maximised.
        self.Maximize(file.get("maximised", False))
        self.ShowFullScreen(file.get("fullscreen", False))

    def append_to_file_history(self, dir: str):
        """Adds dir to the file history. (Accessed by Open Recent.)"""

        def filter_func(n):
            if n == dir:
                return False
            else:
                return True

        self.file_history = list(filter(filter_func, self.file_history))
        self.file_history.append(dir)

    def pass_function(self, _e=None):
        """Does nothing, meant to be a placeholder for unimplemented buttons."""
        pass

    def new(self, _e=None):
        """Function calledthrough File > New or CTRL+N"""
        self._new_file()

    def _new_file(self):
        self._canvas.clear_all()

    def save(self, _e: wx.CommandEvent = None):
        """Function calledthrough File > Save or CTRL+S"""
        if self.current_file:
            self._save_file(self.current_file)
        else:
            self.save_as()

    def save_as(self, _e: wx.CommandEvent = None):
        """Called through File > Save As or CTRL+SHIFT+S"""
        dir: str = ""
        with wx.FileDialog(
            self,
            "Save file",
            wildcard=FILETYPES,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # User changed their mind

            # save the current contents in the file
            dir = fileDialog.GetPath()

        self._save_file(dir)

    def _save_file(self, dir: str):
        """Function for saving a file."""
        try:
            with open(dir, "w") as f:
                file = {"widgets": [], "links": []}

                popples: list = self._canvas.get_popples()
                for _, v in enumerate(self._canvas.get_popples()):
                    if isinstance(v, Popple):
                        v_data = v.get_file_data()
                        file["widgets"].append(v_data)

                for _, v in enumerate(self._canvas.get_popple_connections()):
                    if isinstance(v, PoppleConnection):
                        try:
                            popples.index(v.widget1)
                            v_data = {
                                "widget1": popples.index(v.widget1),
                                "widget2": popples.index(v.widget2),
                            }
                            file["links"].append(v_data)
                        except IndexError:
                            pass
                f.write(json.dumps(file))
                self.append_to_file_history(dir)

            self.current_file = dir
        except IOError:
            pass
            # TODO - Add a popup to indicate that saving the file has failed.

    ## Function called through File > Open or CTRL+O
    def open(self, _e: wx.CommandEvent = None):
        if self._canvas.is_modified():
            pass

        dir: str = ""
        with wx.FileDialog(
            self, "Open file", wildcard=FILETYPES, style=wx.FD_OPEN
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # User changed their mind
            dir = fileDialog.GetPath()  # Get the path to the file

        self._open_file(dir)

    def openRecent(self, event: wx.CommandEvent = None):
        dir = ""
        if event:
            event_object = event.GetEventObject()
            if isinstance(event_object, wx.Menu):
                dir = event_object.GetLabelText(event.GetId())
            else:
                return

        elif len(self.file_history) > 0:
            dir = self.file_history[-1]

        else:
            return

        self._open_file(dir)

    ## Function for opening a file
    def _open_file(self, dir: str):

        file = {}
        try:
            with open(dir, "r") as f:
                file = json.loads(f.read())
        except IOError:
            # TODO - Add a popup to indicate that loading the file has failed.
            return

        self._canvas.clear_all()
        popples: list[Popple] = []
        for _, v in enumerate(file["widgets"]):
            popples.append(
                self._canvas.append_popple(
                    Vector2(v["x"], v["y"]), Vector2(v["width"], v["height"]), v["text"]
                )
            )

        for _, v in enumerate(file["links"]):
            widget1 = popples[v["widget1"]]
            widget2 = popples[v["widget2"]]
            self._canvas.append_popple_connection(widget1, widget2)
        self.append_to_file_history(dir)
        self.current_file = dir

    ## Function for closing a file
    def _on_close(self, event: wx.Event):
        self._save_config()

        event.Skip()

    def get_canvas(self):
        return self._canvas

    def update_display(self):
        self._canvas.update_display()
        self._toolbar.update_display()


class BottomToolbar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(1, 40))

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._camera_zoom_counter = wx.StaticText(
            self, label="hello world", name="counter_camera_zoom"
        )
        sizer.Add(self._camera_zoom_counter, 1, wx.EXPAND)
        self._camera_pos_counter = wx.StaticText(
            self, label="hello world", name="counter_camera_position"
        )
        sizer.Add(self._camera_pos_counter, 1, wx.EXPAND)

        self.SetSizer(sizer)

        canvas = get_canvas()

        self.SetBackgroundColour(canvas.config_toolbar_background_colour)
        for i in self.GetChildren():
            if isinstance(i, wx.StaticText):
                i.SetForegroundColour(canvas.config_toolbar_text_colour)
        self.Show()
        self.Raise()
        self.update_display()

    def update_display(self):
        canvas: Canvas = get_canvas()

        zoom_label_value = round(canvas.get_camera_zoom() * 100)
        pos_value = round(canvas._camera_pos)

        # Camera Zoom
        zoom_label = "ZOOM: " + str(zoom_label_value) + "%"
        self._camera_zoom_counter.SetLabel(zoom_label)

        # Camera Position
        pos_label = "X: " + str(pos_value.x) + "\n" + "Y: " + str(pos_value.y)
        self._camera_pos_counter.SetLabel(pos_label)


def get_window() -> Window:
    """Helper function to get the base window"""
    window = wx.GetTopLevelWindows()[0]
    return window


def get_canvas():
    """Helper function to get the canvas window"""
    window = get_window()
    return window.get_canvas()


def refresh():
    """Re-renders everything"""
    window = get_window()
    window.update_display()


if __name__ == "__main__":
    APP = wx.App()

    window = Window()
    window.Show()

    import sys

    try:
        APP.MainLoop()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)
