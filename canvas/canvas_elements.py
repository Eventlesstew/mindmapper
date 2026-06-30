import wx
from functions.vectors import *
from main import get_canvas
from enum import Enum

class Popple(wx.Panel):
    # The minimum size that the Popple can be at.
    MINIMUM_SIZE: Vector2 = Vector2(150, 100)

    # The font size used for the text.
    FONT_SIZE = 14

    class _DRAG_STATE_TYPES(Enum):
        TOP_LEFT=0
        TOP=1
        TOP_RIGHT=2
        LEFT=3
        CENTER=4
        MOVE=4
        RIGHT=5
        BOTTOM_LEFT=6
        BOTTOM=7
        BOTTOM_RIGHT=8

        OUTSIDE=-1
        INACTIVE=-1
    
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

        self._drag_state: Popple._DRAG_STATE_TYPES = Popple._DRAG_STATE_TYPES.INACTIVE

        # A seperate function is used because both the popple and the text element can recieve inputs.
        # I cannot just disable all binds for the textctrl because it needs to be able to get text when it can.
        def Bind(event: wx.PyEventBinder, handler):
            self.textCtrl.Bind(event, handler)
            self.Bind(event, handler)

        Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_press)
        Bind(wx.EVT_LEFT_DCLICK, self._on_mouse_left_press)
        Bind(wx.EVT_MOTION, self._on_mouse_motion)
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
        # self.textCtrl.Bind(wx.EVT_MOTION, self._propagate_event)

    def _on_ready(self, event: wx.Event):
        """A separate _on_ready function is necessary for drawing operations performed on initial creation of the window."""
        self.update_display()
        event.Skip()

    def _calculate_drag_state(self) -> _DRAG_STATE_TYPES:
        """Calculates a new drag state based on the cursor position."""
        canvas = get_canvas()
        mouse_pos = canvas.get_mouse_position()

        position = self.get_display_position()
        opposite_position = position + self.get_display_size()

        # Skips all of the heavy lifting if the mouse is outside the popple.
        if (
            mouse_pos.x < position.x or 
            mouse_pos.x > opposite_position.x or
            mouse_pos.y < position.y or
            mouse_pos.y > opposite_position.y
        ):
            return self._DRAG_STATE_TYPES.OUTSIDE
        
        border = canvas.get_border_width() * 2
        drag_anchor: Vector2 = Vector2(0,0)

        if mouse_pos.x <= position.x + border:
            drag_anchor.x = -1
        elif mouse_pos.x >= opposite_position.x - border:
            drag_anchor.x = 1
        
        if mouse_pos.y <= position.y + border:
            drag_anchor.y = -1
        elif mouse_pos.y >= opposite_position.y - border:
            drag_anchor.y = 1
        
        if drag_anchor == Vector2(0,0):
            return self._DRAG_STATE_TYPES.MOVE
        elif drag_anchor == Vector2(-1,-1):
            return self._DRAG_STATE_TYPES.TOP_LEFT
        elif drag_anchor == Vector2(0,-1):
            return self._DRAG_STATE_TYPES.TOP
        elif drag_anchor == Vector2(1,-1):
            return self._DRAG_STATE_TYPES.TOP_RIGHT
        elif drag_anchor == Vector2(-1,0):
            return self._DRAG_STATE_TYPES.LEFT
        elif drag_anchor == Vector2(1,0):
            return self._DRAG_STATE_TYPES.RIGHT
        elif drag_anchor == Vector2(-1,1):
            return self._DRAG_STATE_TYPES.BOTTOM_LEFT
        elif drag_anchor == Vector2(0,1):
            return self._DRAG_STATE_TYPES.BOTTOM
        elif drag_anchor == Vector2(1,1):
            return self._DRAG_STATE_TYPES.BOTTOM_RIGHT
    
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

    def set_position(self, new_position: Vector2):
        """Sets the position of the widget and properly updates it's display. Recommended over manually setting the position."""
        self.pos = new_position
        canvas = get_canvas()
        canvas.on_modified()

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

    def _propagate_event(self, event: wx.Event):
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
            self._drag_state = self._calculate_drag_state()
            canvas = get_canvas()
            canvas.start_drag(self)
        # event.Skip()

    def _on_mouse_left_release(self, event: wx.Event):
        """Occurs when left click is released on this element"""
        self._drag_state = self._DRAG_STATE_TYPES.INACTIVE
        self._propagate_event(event)

    def set_cursor(self, cursor: wx.Cursor, textCtrl_cursor: wx.Cursor = None):
        """Sets the cursor of itself and it's textCtrl. Recommended over the wxpython function."""

        self.SetCursor(cursor)
        if textCtrl_cursor:
            self.textCtrl.SetCursor(textCtrl_cursor)
        else:
            self.textCtrl.SetCursor(cursor)

    def _on_mouse_motion(self, event: wx.MouseEvent):
        """Occurs when moving the mouse around."""

        # TODO - Make it so you can actually drag the popple's edges to resize them.
        # When finished, remove the two lines below.
        self._propagate_event(event)
        return

        new_drag_state = self._drag_state
        if self._drag_state == self._DRAG_STATE_TYPES.INACTIVE:
            new_drag_state = self._calculate_drag_state()

        if (
            new_drag_state == self._DRAG_STATE_TYPES.TOP_LEFT or
            new_drag_state == self._DRAG_STATE_TYPES.BOTTOM_RIGHT
        ):
            self.set_cursor(wx.Cursor(wx.CURSOR_SIZENWSE))

        elif (
            new_drag_state == self._DRAG_STATE_TYPES.TOP_RIGHT or
            new_drag_state == self._DRAG_STATE_TYPES.BOTTOM_LEFT
        ):
            self.set_cursor(wx.Cursor(wx.CURSOR_SIZENESW))
        
        elif (
            new_drag_state == self._DRAG_STATE_TYPES.TOP or
            new_drag_state == self._DRAG_STATE_TYPES.BOTTOM
        ):
            self.set_cursor(wx.Cursor(wx.CURSOR_SIZENS))
        
        elif (
            new_drag_state == self._DRAG_STATE_TYPES.LEFT or
            new_drag_state == self._DRAG_STATE_TYPES.RIGHT
        ):
            self.set_cursor(wx.Cursor(wx.CURSOR_SIZEWE))
        
        else:
            self.set_cursor(wx.Cursor(wx.CURSOR_HAND))

        self._propagate_event(event)
        # event.Skip()

    def _on_mouse_wheel(self, event: wx.MouseEvent):
        """Occurs during mouse wheel inputs on this element"""
        self._propagate_event(event)

    def hasFocus(self) -> bool:
        """Use this instead of HasFocus so the textCtrl is taken into account."""
        return self.textCtrl.HasFocus() or self.HasFocus()

    def _on_textCtrl_focused(self, event: wx.Event):
        """Occurs if the TextCtrl is focused. (Text edit mode)"""
        self.setEditable(True)
        event.Skip()

    def _on_textCtrl_unfocused(self, event: wx.Event):
        """Occurs if the TextCtrl loses focus. (Text edit disabled)"""
        self.setEditable(False)
        event.Skip()

    def _on_focused(self, event: wx.Event):
        """Occurs when the Popple itself is focused."""
        self.Raise()
        event.Skip()

    def _on_unfocused(self, event: wx.Event):
        """Occurs when the Popple itself loses focus."""
        event.Skip()

    def setEditable(self, value: bool):
        """Sets editability of the textCtrl."""
        self.textCtrl.SetEditable(value)

    # Public function as it is called by the Canvas.
    def on_drag(self, position:Vector2):
        """Occurs when dragged."""
        # TODO - Make it so you can actually drag this around.

        #if self._drag_state == self._DRAG_STATE_TYPES.MOVE:
        self.set_position(position)
    
    def _on_paint(self, event: wx.PaintEvent = None):
        """Renders Borders"""
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
