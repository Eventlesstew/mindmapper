import wx
from functions.vectors import *


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
        
        from main import get_canvas
        canvas = get_canvas()

        self.SetBackgroundColour(canvas.config_toolbar_background_colour)
        for i in self.GetChildren():
            if isinstance(i, wx.StaticText):
                i.SetForegroundColour(canvas.config_toolbar_text_colour)
        self.Show()
        self.Raise()
        self.update_display()

    def update_display(self):
        from main import get_canvas
        canvas = get_canvas()

        zoom_label_value = round(canvas.get_camera_zoom() * 100)
        pos_value = round(canvas._camera_pos)

        # Camera Zoom
        zoom_label = "ZOOM: " + str(zoom_label_value) + "%"
        self._camera_zoom_counter.SetLabel(zoom_label)

        # Camera Position
        pos_label = "X: " + str(pos_value.x) + "\n" + "Y: " + str(pos_value.y)
        self._camera_pos_counter.SetLabel(pos_label)