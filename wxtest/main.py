from wx import *

class WxButton(Frame):

    def __init__(self, *args, **kw):
        super(WxButton, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
        pnl = Panel(self)
        closeButton = Button(pnl, label='Close Me', pos=(20, 20))

        closeButton.Bind(EVT_BUTTON, self.OnClose)

        self.SetSize((350, 250))
        self.SetTitle('Close Button')
        self.Centre()

    def OnClose(self, e):
        self.Close(True)

def main():
    app = App()
    menubar = MenuBar()
    ex = WxButton(None)
    ex.Show()

    menubar = MenuBar()
    menubar.Attach(app)
    app.MainLoop()

if __name__ == "__main__":
    main()