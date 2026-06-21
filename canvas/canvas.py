import wx
from functions.vectors import *
from canvas.canvas_elements import *
from canvas.canvas_ui import *
from main import refresh


class Canvas(wx.Panel):
    """A singleton that represents the actual space that Popples and Popple Connections go on."""

    # TODO - Make it so the canvas can check if it's been modified from the original file.
    # This should be done as a boolean when anything is modified.

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.config_background_colour = "#303236"
        self.config_toolbar_background_colour = "#171717"
        self.config_toolbar_text_colour = "#FFFFFF"
        self.config_popple_background_colour = "#FFFFFF"
        self.config_popple_text_colour = "#000000"
        self.config_popple_border_colour = "#A600FF"
        self.config_delete_colour = "#ff0000"

        self._original_zoom_factor = None
        self._drag_element = None
        self._drag_mouse_position: Vector2 = None
        self._drag_position: Vector2 = None

        # Since Popple Connections are only rendered in the paint events, making them separate elements in wxpython isn't necessary.
        self.popple_connections: list[PoppleConnection] = []
        self._focused_popple_connection: PoppleConnection = None

        self._camera_pos: float = Vector2()
        self._camera_zoom: float = 1.0

        # TODO - Make it so this actually works.
        self._modified = False

        # This is necessary to ensure the popples can properly overlap eachother without causing issues.
        self.SetDoubleBuffered(True)
        self.SetBackgroundColour(self.config_background_colour)

        self.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_left_press)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_add_popple)
        self.Bind(wx.EVT_LEFT_UP, self._on_mouse_left_release)

        app = wx.GetApp()
        app.Bind(wx.EVT_RIGHT_DOWN, self._on_mouse_right_press)
        app.Bind(wx.EVT_RIGHT_UP, self._on_mouse_right_release)

        self.Bind(wx.EVT_CHILD_FOCUS, self._on_focus_changed)
        app.Bind(wx.EVT_MOTION, self._on_mouse_motion)

        self.Bind(wx.EVT_PAINT, self._on_paint)

        # TODO - Add more uses for touch gestures.
        # Also add a proper check for if the mousewheel input is coming from panning.
        if self.EnableTouchEvents(wx.TOUCH_ZOOM_GESTURE):
            app.Bind(wx.EVT_GESTURE_ZOOM, self._on_gesture_zoom)
            app.Bind(wx.EVT_MOUSEWHEEL, self._on_gesture_pan)
        else:
            # This is to make it so Mousewheels zoom instead of panning up and down.
            app.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_unfocused)

    def get_display_mouse_position(self) -> Vector2:
        """Gets the mouse position relative to the window."""
        absolute_position = Vector2(wx.GetMousePosition())
        return Vector2(self.ScreenToClient(absolute_position.get_as_wxPoint()))

    def get_mouse_position(self) -> Vector2:
        """Gets the mouse position with camera taken into account."""
        position = self.get_display_mouse_position()
        position /= self._camera_zoom
        position += self._camera_pos

        return position

    def clear_all(self):
        """Removes all Popples and Popple Connections"""
        self.popple_connections = []
        for popple in self.get_popples():
            popple.Destroy()

        refresh()

    # Adds a new Popple to the field
    def append_popple(self, pos: Vector2, size: Vector2 = None, text: str = ""):
        """
        Adds a new popple to the canvas, and returns the Popple.

        If size is None, Popple.MINIMUM_SIZE will be used.
        """

        if not size:
            size = Popple.MINIMUM_SIZE

        true_pos = pos - (size * 0.5)
        return Popple(true_pos, size, text)

    # Adds a new Popple Connection
    def append_popple_connection(self, popple1, popple2=None):
        """
        Adds a new Popple Connection to the canvas

        Returns the new connection if successful, or None if failure.
        """

        # popple1 must not be None
        if not popple1:
            return None

        # popple1 and popple2 must not be the same.
        if popple1 == popple2:
            return None

        # Checks if there's already a poppleconnection that links these together.
        for i in self.popple_connections:
            if (i.widget1 == popple1 and i.widget2 == popple2) or (
                i.widget2 == popple1 and i.widget1 == popple2
            ):
                return None

        new_connection = PoppleConnection(popple1, popple2)
        self.popple_connections.append(new_connection)
        self.update_popple_connections()
        return new_connection

    def remove_popple(self, popple):
        """Removes a Popple and all connections linking to that Popple."""

        # Function used for filtering out the popple connections linking to the removed Popple.
        if isinstance(popple, Popple):

            def filter_func(v: PoppleConnection):
                if v.widget1 == popple or v.widget2 == popple:
                    return False
                return True

            self.popple_connections = list(filter(filter_func, self.popple_connections))
            popple.Destroy()
            refresh()

    def remove_popple_connection(self, popple_connection):
        """Removes a Popple Connection"""
        if isinstance(popple_connection, PoppleConnection):
            # Function used for filtering out the popple connection being removed.
            def filter_func(v: PoppleConnection):
                if v == popple_connection:
                    return False
                return True

            self.popple_connections = list(filter(filter_func, self.popple_connections))
            if self._focused_popple_connection == popple_connection:
                self._focused_popple_connection = None
            refresh()

    def get_popples(self) -> list:
        """Gets an array of all Popples."""
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, Popple):
                result.append(v)

        return result

    def get_popple_connections(self) -> list:
        """Gets an array of all Popple Connections."""
        return self.popple_connections

    def get_popple_buttons(self):
        """Gets an array of the Buttons used on the Popples."""
        result = []
        for _, v in enumerate(self.GetChildren()):
            if isinstance(v, CanvasButton):
                result.append(v)

        return result

    def on_add_popple(self, event: wx.Event):
        """Called if "Edit > Add Popple" is used."""
        pos = Vector2()
        if event.GetEventObject() == self:
            pos = self.get_mouse_position()
        else:
            from main import Window
            from main import get_window

            parent = get_window()
            if isinstance(parent, Window):
                pos += Vector2(parent.GetSize()) * 0.5
            pos += self._camera_pos
        self.append_popple(pos)

    def _on_mouse_left_press(self, event: wx.MouseEvent):
        self.SetFocusIgnoringChildren()

        for i in self.get_popple_connections():
            if isinstance(i, PoppleConnection):
                if i.is_mouse_touching() and i != self._focused_popple_connection:
                    self.set_focused_popple_connection(i)
                    return
        self.set_focused_popple_connection(None)

    def get_focused_popple_connection(self):
        return self._focused_popple_connection

    def set_focused_popple_connection(self, new_focused_popple_connection):
        if new_focused_popple_connection != self._focused_popple_connection and (
            isinstance(new_focused_popple_connection, PoppleConnection)
            or not new_focused_popple_connection
        ):
            if self._focused_popple_connection:
                self._focused_popple_connection.on_unfocused()

            if new_focused_popple_connection:
                new_focused_popple_connection.on_focused()

            self._focused_popple_connection = new_focused_popple_connection
            refresh()

    # Stops dragging on anything.
    def _on_mouse_left_release(self, event: wx.MouseEvent):
        self.stop_drag()

    # Makes it so the camera will be dragged.
    def _on_mouse_right_press(self, event: wx.MouseEvent):
        self.set_drag(self)

    # Stops the camera from being dragged when right click is released.
    def _on_mouse_right_release(self, event: wx.MouseEvent):
        if self.get_drag() == self:
            self.set_drag(None)

    def remove_new_connections(self):
        """
        Removes any new Connections.

        "new connections" refers to the Popple Connections that are currently following the mouse as they lack a second widget.
        """

        def filter_func(n: PoppleConnection):
            if n.is_new():
                return True
            return False

        self.popple_connections = list(filter(filter_func, self.popple_connections))

    def get_new_connections(self):
        """
        Gets all new connections.

        "new connections" refers to the Popple Connections that are currently following the mouse as they lack a second widget.
        """
        result = []
        for i, v in enumerate(self.popple_connections):
            if not v.widget2:
                result.append(v)
        return result

    # Actions for when the mouse is being moved.
    def _on_mouse_motion(self, event: wx.MouseEvent):
        self.move_drag()

        if self.get_new_connections():
            self.update_popple_connections()

        event.Skip()
        return

    # Actions for when the Mouse Wheel is being used.
    # Also occurs for any 2+ finger gestures on Macbook.

    # Using the Zoom Gesture (Pinching or Spreading two fingers.)
    def _on_gesture_zoom(self, event: wx.ZoomGestureEvent):

        if event.IsGestureStart():
            self._original_zoom_factor = event.GetZoomFactor()
        elif event.IsGestureEnd():
            self._original_zoom_factor = None
        elif self._original_zoom_factor:
            zoom_factor = event.GetZoomFactor()
            distance = zoom_factor - self._original_zoom_factor
            self._original_zoom_factor = zoom_factor
            self.zoom_camera(distance)

    # Using the Pan Gesture (Moving two fingers around.)
    def _on_gesture_pan(self, event: wx.MouseEvent):
        amount = Vector2()
        axis = event.GetWheelAxis()
        if axis == 0:  # Y axis
            amount.y = -event.GetWheelRotation()
        elif axis == 1:  # X axis
            amount.x = event.GetWheelRotation()

        movement = amount

        self.move_camera(movement)

    def _on_mouse_wheel(self, event: wx.MouseEvent):
        # Mouse Wheel
        amount = event.GetWheelRotation()

        self.zoom_camera(amount * 0.001)

    # Zooms camera by a specified amount
    # If from_position is None, uses mouse position instead.
    def zoom_camera(self, amount: float, from_position: Vector2 = None):
        old_mouse_pos = Vector2()
        if from_position:
            old_mouse_pos = from_position
        else:
            old_mouse_pos = self.get_mouse_position()

        self._camera_zoom += amount
        self._camera_zoom = max(self._camera_zoom, 0.1)
        self._camera_zoom = round(self._camera_zoom * 100) / 100

        self._camera_pos += old_mouse_pos - self.get_mouse_position()

        refresh()

    def get_camera_zoom(self) -> Vector2:
        return self._camera_zoom

    # Moves camera by a specified amount
    def move_camera(self, pos: Vector2, affected_by_zoom: bool = True):
        if affected_by_zoom:
            pos /= self._camera_zoom
        self._camera_pos += pos
        refresh()

    # Moves camera to a position.
    def move_camera_to(self, pos: Vector2):
        self._camera_pos = pos
        refresh()

    def get_camera_position(self) -> Vector2:
        return self._camera_pos

    def update_display(self):
        """Updates visuals of everything in the Canvas."""

        # Updates visuals of all Popples.
        for _, v in enumerate(self.get_popples()):
            if isinstance(v, Popple):
                v.update_display()

        # Updates visuals of all Popple Buttons.
        for _, v in enumerate(self.get_popple_buttons()):
            if isinstance(v, CanvasButton):
                v.update_display()

        # Causes the program to refresh drawing for all Popple Connections.
        self.update_popple_connections()

    def update_popple_connections(self):
        self.Refresh()

    # Called when focus is changed (Moving to elements regardless of whether it has gained or lost focus)
    def _on_focus_changed(self, event):
        refresh()

    def on_unfocused(self, event):
        self.set_focused_popple_connection(None)

    # This constant specifies the internal border width.
    BORDER_WIDTH = 3

    # Returns the width of the border with camera zooming taken into account.
    def get_border_width(self) -> int:
        return max(1, round(self.BORDER_WIDTH * self._camera_zoom))

    # Re-renders the rendering of Popple Connections
    def _on_paint(self, event=None):
        dc = wx.PaintDC(self)

        # Using a Graphics Context because it has functions to allow shape drawing and also uses antialiasing.
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return  # TODO - Make it so the program properly handles when Graphics Context is not usable.

        # make a pen
        pen = wx.Pen(
            self.config_popple_border_colour, self.get_border_width(), wx.PENSTYLE_SOLID
        )
        gc.SetPen(pen)

        for i in self.get_popple_connections():
            if isinstance(i, PoppleConnection):
                widget1_pos = i.get_widget1_display_position()
                widget2_pos = i.get_widget2_display_position()

                path = gc.CreatePath()

                path.MoveToPoint(widget1_pos.x, widget1_pos.y)
                path.AddLineToPoint(widget2_pos.x, widget2_pos.y)
                path.CloseSubpath()

                gc.StrokePath(path)

        gc.Flush()

    def get_focused_popple(self):
        """Gets the currently focused popple if there is one."""
        focused_element = self.FindFocus()
        if isinstance(focused_element, Popple):
            return focused_element
        elif isinstance(focused_element, wx.TextCtrl):
            # Since the Popple's TextCtrl has focus, we need to get the Popple through the GetParent function.
            focused_element_parent = focused_element.GetParent()
            if isinstance(focused_element_parent, Popple):
                return focused_element_parent

    def start_drag(self, element):
        """Starts dragging of an element."""
        self.set_drag(element)

    def stop_drag(self, element=None):
        """
        Stops dragging of an element.
        If element isn't None, only stops dragging the element itself to prevent interference with other items being dragged.
        """

        if (not element) or element == self._drag_element:
            self.set_drag(None)

    def set_drag(self, element):
        """Sets which item is being dragged."""

        old_element = self._drag_element
        self._drag_element = element
        self._drag_mouse_position = self.get_mouse_position()

        if element == self:
            self._drag_position = self._camera_pos
        elif isinstance(element, Popple):
            self._drag_position = element.pos
        elif isinstance(element, CanvasButton):
            if element.type == CanvasButton.Types.LINK:
                self.append_popple_connection(self.get_focused_popple())
            elif element.type == CanvasButton.Types.RESIZE:
                self._drag_position = self.get_focused_popple().size

        if isinstance(old_element, CanvasButton):
            if old_element.type == CanvasButton.Types.LINK:
                popple_to_link: Popple = None
                for (
                    p
                ) in (
                    self.get_popples()
                ):  # Check if the mouse is in any existing Popples.
                    if isinstance(p, Popple):
                        display_mouse_position = self.get_display_mouse_position()
                        if p.get_display_rect().Contains(
                            display_mouse_position.x, display_mouse_position.y
                        ):
                            popple_to_link = p
                            self.update_popple_connections()
                            break

                if (
                    not popple_to_link
                ):  # Create a new Popple if the connection doesn't link to an existing Popple.
                    popple_to_link = self.append_popple(self.get_mouse_position())

                for (
                    v
                ) in (
                    self.get_new_connections()
                ):  # Link any new connections to the Popple to link.
                    v.widget2 = popple_to_link

    # Gets the item being dragged.
    def get_drag(self):
        return self._drag_element

    def move_drag(self):
        """Moves the dragged item around. This behaviour varies depending on the object."""
        _drag_element = self._drag_element

        if not _drag_element:
            return

        if _drag_element == self:
            self._camera_pos = (
                self._drag_position
            )  # Direct modification for get_mouse_position to work correctly.

        mousePos = self.get_mouse_position()
        mouse_dist = mousePos - self._drag_mouse_position

        if _drag_element == self:
            mouse_dist *= -1

        pos = self._drag_position + mouse_dist

        # If dragging the canvas, move the camera around.
        if _drag_element == self:
            self.move_camera_to(pos)  # Properly updates Camera position

        # Drags the Popple's position around
        elif isinstance(_drag_element, Popple):
            _drag_element.pos = pos
            refresh()

        # Causes different behaviours depending on the Button's type.
        elif isinstance(_drag_element, CanvasButton):

            # Link Button
            if _drag_element.type == CanvasButton.Types.LINK:
                # Since the PoppleConnection following the mouse is rendered visually, just give the program an update.
                self.update_popple_connections()

            # Resize button - Resizes the Popple
            if _drag_element.type == CanvasButton.Types.RESIZE:
                focused_popple = self.get_focused_popple()
                focused_popple.set_size(pos)
                refresh()

    def is_modified(self):
        return self._modified
