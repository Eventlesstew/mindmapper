import wx
from functions.vectors import *
from main import get_canvas

class Popple(wx.Panel):
    # The minimum size that the Popple can be at.
    MINIMUM_SIZE: Vector2 = Vector2(150, 100)

    # The font size used for the text.
    FONT_SIZE = 14

    def __init__(self, pos: Vector2, size: Vector2 = MINIMUM_SIZE, text: str = ""):
        canvas = get_canvas()
        super().__init__(canvas, wx.ID_ANY, style=wx.BORDER_NONE)

        textCtrl_style = (
            wx.TE_READONLY
            | wx.TE_NO_VSCROLL
            | wx.TE_CENTER
            | wx.TE_MULTILINE
            | wx.BORDER_NONE
        )

        self.textCtrl: wx.TextCtrl = wx.TextCtrl(
            self, wx.ID_ANY, text, style=textCtrl_style
        )

        ## TODO - Make sure this works on MacOS
        self.textCtrl.SetFont(
            wx.Font(
                pointSize=self.FONT_SIZE,
                family=wx.FONTFAMILY_DEFAULT,
                style=wx.FONTSTYLE_NORMAL,
                weight=wx.FONTWEIGHT_NORMAL,
                faceName="Calibri",
            )
        )

        self.SetBackgroundColour(canvas.config_popple_background_colour)

        # TODO - Find a way to make this transparent.
        self.textCtrl.SetBackgroundColour(canvas.config_popple_background_colour)
        self.textCtrl.SetForegroundColour(canvas.config_popple_text_colour)

        self.pos: Vector2 = pos
        self.size: Vector2 = size

        # A seperate function is used because both the popple and the text element can recieve inputs.
        # I cannot just disable all binds for the textctrl because it needs to be able to get text when it can.
        def Bind(event: wx.PyEventBinder, handler):
            self.textCtrl.Bind(event, handler)
            self.Bind(event, handler)

        Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_press)
        Bind(wx.EVT_LEFT_DCLICK, self._on_mouse_left_press)
        Bind(wx.EVT_MOTION, self._on_unneeded_input)
        Bind(wx.EVT_LEFT_UP, self._on_mouse_left_release)
        Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)

        self.Bind(wx.EVT_SET_FOCUS, self._on_focused)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_unfocused)
        self.textCtrl.Bind(wx.EVT_SET_FOCUS, self._on_textCtrl_focused)
        self.textCtrl.Bind(wx.EVT_KILL_FOCUS, self._on_textCtrl_unfocused)
        self.textCtrl.Bind(wx.EVT_KEY_DOWN, self._on_textCtrl_text_input)
        self.textCtrl.Bind(wx.EVT_TEXT, self._on_textCtrl_text_post)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_WINDOW_CREATE, self._on_ready)

        self.update_display()
        # self.textCtrl.Bind(wx.EVT_MOTION, self._on_unneeded_input)

    # A separate _on_ready function is necessary for drawing operations performed on initial creation of the window.
    def _on_ready(self, event: wx.Event):
        self.update_display()
        event.Skip()

    def get_display_position(self):
        """Gets the position relative to the window."""
        pos = self.pos

        canvas = get_canvas()
        if canvas:
            pos -= canvas.get_camera_position()
            pos *= canvas.get_camera_zoom()

        return pos.get_as_Vector2i()

    def set_size(self, new_size: Vector2):
        """Gets the internal size."""
        self.size = Vector2(
            max(self.MINIMUM_SIZE.x, new_size.x),
            max(self.MINIMUM_SIZE.y, new_size.y),
        )

    def get_display_size(self):
        """Gets the size relative to the window."""
        size = self.size

        canvas = get_canvas()
        if canvas:
            size *= canvas.get_camera_zoom()

        return size.get_as_Vector2i()

    def get_display_rect(self) -> wx.Rect:
        """Gets the rect of the Popple relative to the window. (Contains Position and Size)"""
        pos = self.get_display_position()
        size = self.get_display_size()
        return wx.Rect(pos.x, pos.y, size.x, size.y)

    def _on_textCtrl_text_input(self, event: wx.KeyEvent):
        """Called when inputting text to the TextInput before the text is parsed."""
        # Doesn't do anything right now.

        event.Skip()
    
    def _on_textCtrl_text_post(self, event: wx.CommandEvent):
        """Called when inputting text to the TextInput after the text is parsed."""
        canvas = get_canvas()
        if canvas:
            canvas.on_modified()
        
        self.update_display()
        event.Skip()

    def update_display(self):
        """Updates the element's appearance on the window itself."""

        new_pos = self.get_display_position()
        self.Move(new_pos.x, new_pos.y)

        new_size = self.get_display_size()
        self.SetSize(new_size.x, new_size.y)

        canvas = get_canvas()

        # Adjusts the size of the text according to Zoom.
        text_font = self.textCtrl.GetFont()
        text_font.SetPointSize(round(self.FONT_SIZE * canvas.get_camera_zoom()))
        self.textCtrl.SetFont(text_font)

        textCtrl_newSize: Vector2 = new_size
        textCtrl_newSize -= (
            canvas.get_border_width() * 4
        )  # Borderwidth*2 makes the text right on the Border Width.
        # textCtrl_newSize.y = self.textCtrl.GetBestHeight(textCtrl_newSize.x)
        self.textCtrl.SetSize(textCtrl_newSize.x, textCtrl_newSize.y)

        # TODO - Center the text
        # print("TEST")
        # text_string = self.textCtrl.GetValue()
        # print(self.textCtrl.GetTextExtent(text_string))

        # text_string = self.textCtrl.GetValue()

        # print(text_string)
        # print(self.textCtrl.GetTextExtent())

        # Centers the textCtrl
        textCtrl_newPos: Vector2 = round((new_size - textCtrl_newSize) * 0.5)
        self.textCtrl.Move(textCtrl_newPos.x, textCtrl_newPos.y)

        self.Refresh()
        self.Update()

    # Used by the file saving system to get the necessary data from this Popple.
    def get_file_data(self):
        data = {
            "x": self.pos.x,
            "y": self.pos.y,
            "width": self.size.x,
            "height": self.size.y,
            # "id":self.GetId(),
            "text": self.textCtrl.GetValue(),
        }
        return data

    def _on_unneeded_input(self, event: wx.Event):
        """Overrides default behaviour and propagates it to the Canvas."""
        canvas = get_canvas()
        if canvas:
            canvas.GetEventHandler().ProcessEvent(event)

    def _on_mouse_left_press(self, event: wx.MouseEvent):
        # Activates Text Input
        if event.LeftDClick():
            self.textCtrl.SetFocus()

        # Dragging the Popple.
        else:
            self.SetFocusIgnoringChildren()

            canvas = get_canvas()
            canvas.start_drag(self)
        # event.Skip()

    # Propagates this up to the Canvas
    def _on_mouse_left_release(self, event: wx.Event):
        self._on_unneeded_input(event)

    # Propagates this up to the Canvas
    def on_mouseMotion(self, event: wx.MouseEvent):
        self._on_unneeded_input()
        # event.Skip()

    # Propagates this up to the Canvas
    def _on_mouse_wheel(self, event: wx.MouseEvent):
        self._on_unneeded_input(event)

    # Use this instead of HasFocus so the textCtrl is taken into account.
    def hasFocus(self) -> bool:
        return self.textCtrl.HasFocus() or self.HasFocus()

    # Occurs if the TextCtrl is focused. (Text edit mode)
    def _on_textCtrl_focused(self, event: wx.Event):
        self.setEditable(True)
        event.Skip()

    # Occurs if the TextCtrl loses focus. (Text edit disabled)
    def _on_textCtrl_unfocused(self, event: wx.Event):
        self.setEditable(False)
        event.Skip()

    # Occurs when the Popple itself is focused.
    def _on_focused(self, event: wx.Event):
        self.Raise()
        event.Skip()

    # Occurs when the Popple itself loses focus.
    def _on_unfocused(self, event: wx.Event):
        event.Skip()

    # Sets editability of the textCtrl.
    def setEditable(self, value: bool):
        self.textCtrl.SetEditable(value)

    # Renders Borders.
    def _on_paint(self, event: wx.PaintEvent = None):
        dc = wx.PaintDC(self)  # event.GetEventObject()
        gc = wx.GraphicsContext.Create(dc)
        parent = get_canvas()
        if not gc:
            return

        border_width = parent.get_border_width()
        pen = wx.Pen(
            parent.config_popple_border_colour, border_width, wx.PENSTYLE_SOLID
        )
        gc.SetPen(pen)

        pos = Vector2(math.floor(border_width * 0.5))
        size = self.get_display_size() - border_width

        gc.DrawRectangle(
            pos.x,
            pos.y,
            size.x,
            size.y,
        )
        gc.Flush()


class PoppleConnection:
    """The lines connecting between Popples."""

    # They're not based on wx.Panel because I didn't find that necessary.

    def __init__(self, widget1: Popple, widget2: Popple):
        self.widget1 = widget1
        self.widget2 = widget2

    def get_widget1_display_position(self) -> Vector2:
        return self.get_widget_display_position(self.widget1)

    def get_widget2_display_position(self) -> Vector2:
        if self.widget2:
            return self.get_widget_display_position(self.widget2)
        else:
            canvas = get_canvas()
            return canvas.get_display_mouse_position()

    def get_widget_display_position(self, popple: Popple) -> Vector2:
        pos = popple.get_display_position()
        pos += popple.get_display_size() * 0.5
        return pos

    def get_widget1_position(self) -> Vector2:
        return self.get_widget_position(self.widget1)

    def get_widget2_position(self) -> Vector2:
        if self.widget2:
            return self.get_widget_position(self.widget2)
        else:
            canvas = get_canvas()
            return canvas.get_mouse_position()

    def get_widget_position(self, popple: Popple) -> Vector2:
        pos = popple.pos
        pos += popple.size * 0.5
        return pos

    # TODO - Test this.
    def is_mouse_touching(self):
        if self.is_new():
            return True
        # line = self.get_line(False)
        canvas = get_canvas()
        pos1 = self.get_widget1_display_position()
        pos2 = self.get_widget2_display_position()
        posm = Vector2(canvas.get_display_mouse_position())

        linecheck: float = (
            ((pos2.x - pos1.x) * (posm.x - pos1.x))
            + ((pos2.y - pos1.y) * (posm.y - pos1.y))
        ) / (((pos2.x - pos1.x) ** 2) + ((pos2.y - pos1.y) ** 2))

        if 0.0 <= linecheck and linecheck <= 1.0:
            distance: float = abs(
                ((pos2.y - pos1.y) * (posm.x - pos1.x))
                - ((pos2.x - pos1.x) * (posm.y - pos1.y))
            ) / ((((pos2.x - pos1.x) ** 2) + ((pos2.y - pos1.y) ** 2)) ** 0.5)

            distance /= canvas.get_border_width() * 2

            if distance < 1.0:
                return True

        return False

    def is_new(self) -> bool:
        if self.widget2:
            return False
        return True

    def _on_focused(self):
        pass

    def _on_unfocused(self):
        pass
