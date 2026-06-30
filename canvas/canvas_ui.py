import wx
from enum import Enum
from functions.vectors import *
from main import get_canvas
from main import refresh
from canvas.canvas_elements import *


class CanvasButton(wx.StaticBitmap):
    class Types(Enum):
        NONE = -1
        DELETE = 0
        LINK = 1
        RESIZE = 2

    class SubTypes(Enum):
        DEFAULT = 0
        LINK_UP = 0
        LINK_DOWN = 1
        LINK_LEFT = 2
        LINK_RIGHT = 3

    def __init__(
        self, parent: wx.Window, type: int, anchor: Vector2 = (0, 0), subType: int = 0
    ):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.type = type
        self.subtype = subType
        self.anchor: Vector2 = anchor

        self.size: Vector2 = Vector2(20, 20)

        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_press)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left_release)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focused)

        self.SetBackgroundColour(self.get_colour())
        self.bitmap = wx.Bitmap(self.get_texture_path())

    def get_colour(self):
        if self.type == CanvasButton.Types.DELETE:
            return "#FF0000"
        else:
            return "#A600FF"

    def get_texture_path(self):
        image_path = ""
        if self.type == CanvasButton.Types.DELETE:
            image_path = "assets/textures/delete.png"
        elif self.type == CanvasButton.Types.RESIZE:
            image_path = "assets/textures/resize.png"
        elif self.type == CanvasButton.Types.LINK:
            if self.subtype == CanvasButton.SubTypes.LINK_UP:
                image_path = "assets/textures/uparrow.png"
            elif self.subtype == CanvasButton.SubTypes.LINK_DOWN:
                image_path = "assets/textures/downarrow.png"
            elif self.subtype == CanvasButton.SubTypes.LINK_LEFT:
                image_path = "assets/textures/leftarrow.png"
            elif self.subtype == CanvasButton.SubTypes.LINK_RIGHT:
                image_path = "assets/textures/rightarrow.png"
        return image_path

    def get_focused_popple(self):
        parent = get_canvas()

        return parent.get_focused_popple()

    def update_display(self):

        def enable():  # This local function enables the button.
            self.Enable()
            self.Show()
            self.Raise()  # TEMPORARY

        def disable():  # This local function disables the button.
            self.Hide()
            self.Disable()

        canvas = get_canvas()
        focused_popple = self.get_focused_popple()

        pos: Vector2 = Vector2()

        # Determines the Size
        size = self.size * canvas.get_camera_zoom()
        size = size.get_as_Vector2i()

        if isinstance(focused_popple, Popple):
            enable()

            # Determines the Position
            pos = focused_popple.get_display_position() - size
            pos += (focused_popple.get_display_size() + size) * self.anchor
        elif canvas.get_focused_popple_connection():
            if self.type == CanvasButton.Types.DELETE:
                enable()
                focused_popple_connection: PoppleConnection = (
                    canvas.get_focused_popple_connection()
                )
                pos1 = focused_popple_connection.get_widget1_display_position()
                pos2 = focused_popple_connection.get_widget2_display_position()

                pos = (pos1 + pos2) * 0.5
                pos -= size * 0.5
            else:
                disable()
                return
        else:
            disable()
            return

        self.Move(pos.get_as_wxPoint())
        self.SetSize(size.get_as_wxSize())

        bitmap = self.bitmap
        image = bitmap.ConvertToImage()
        image = image.Scale(size.x, size.y)
        new_bitmap = wx.Bitmap(image)
        self.SetBitmap(new_bitmap)

    def AcceptsFocus(self):
        return False

    def AcceptsFocusFromKeyboard(self):
        return False

    def on_focused(self, event: wx.FocusEvent):
        pass
    
    def on_drag(self, pos: Vector2):
        # Link Button
        if self.type == CanvasButton.Types.LINK:
            # Since the PoppleConnection following the mouse is rendered visually, just give the program an update.
            get_canvas().update_popple_connections()

        # Resize button - Resizes the Popple
        if self.type == CanvasButton.Types.RESIZE:
            focused_popple = self.get_focused_popple()
            focused_popple.set_size(pos)
            get_canvas().on_modified()
        
    def _on_mouse_left_press(self, event):
        focused_popple = self.get_focused_popple()
        if not isinstance(focused_popple, Popple):
            return

        if self.type == CanvasButton.Types.DELETE:
            pass
        else:
            parent = get_canvas()
            parent.start_drag(self)

    def _on_mouse_left_release(self, event: wx.MouseEvent):
        parent = get_canvas()

        if self.type == self.Types.DELETE:
            if parent.get_focused_popple():
                parent.remove_popple(parent.get_focused_popple())

            # TODO - Make this work properly.
            if parent.get_focused_popple_connection():
                parent.remove_popple_connection(parent.get_focused_popple_connection())
        else:
            parent.stop_drag(self)
