from tkinter import *
from tkinter.ttk import *
from vectors import *

class widget:
    def __init__(self, canvas:Canvas=None, rect:Rect2=Rect2(0, 10, 100, 50)):
        self.canvas = canvas
        self.rect = rect
        self.render()
    
    def render(self):
        self.canvas.create_rectangle(
            self.rect.position.x, 
            self.rect.position.y,
            self.rect.size.x, 
            self.rect.size.y,
            outline="black",
            fill="white",
            width=2
        )

        self.canvas.pack(fill=BOTH, expand=1)

if __name__ == "__main__":
    
    master = Tk()
    shape = widget(master)

    master.title("Shapes")
    
    master.geometry("330x220+300+300")

    mainloop()