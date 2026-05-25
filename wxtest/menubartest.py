import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((500, 300))
        self.bt_exit = wx.Button(self, wx.ID_ANY, "exit")
        self.bt_refresh = wx.Button(self, wx.ID_ANY, "refresh")
        self.text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "some text", style=wx.TE_MULTILINE)

        self.SetTitle("My GUI")
        self.bt_exit.Bind(wx.EVT_BUTTON, self.on_exit)
        self.bt_refresh.Bind(wx.EVT_BUTTON, self.on_refresh)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.bt_exit, 1, 0, 0)
        sizer_2.Add(self.bt_refresh, 1, 0, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_1.Add(self.text_ctrl, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()

    def on_exit(self, evt):
        self.Close()

    def on_refresh(self, evt):
        self.text_ctrl.Clear()

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()