from tkinter import *
from tkinter.ttk import *
from vectors import *

class widget:
    def __init__(self, root=None, rect:Rect2=Rect2(0, 10, 100, 50), text:str=""):
        self.root = root
        self.rect = Rect2(rect)

        #self.label = Label(
        #    master=root,
        #    width=self.rect.size.x,
        #    #height=self.rect.size.y,
        #    text=text
        #)
        #self.label.pack(padx = self.rect.position.x, pady = self.rect.position.y)

        self.textbox = Text(
            master=root,
            wrap='word',
            height=10,
        )
        self.textbox.insert('1.0',text)
        self.textbox.grid(
            row=int(rect.position.x),
            column=int(rect.position.y)
        )
    
    def render(self):
        frame = Frame(self.root)
        #self.canvas.create_rectangle(
        #    self.rect.position.x, 
        #    self.rect.position.y,
        #    self.rect.size.x, 
        #    self.rect.size.y,
        #    outline="black",
        #    fill="white",
        #    width=2
        #)

        #self.canvas.pack(fill=BOTH, expand=1)

if __name__ == "__main__":
    
    master = Tk()
    shape = widget(master)

    master.title("Shapes")
    
    master.geometry("330x220+300+300")

    mainloop()