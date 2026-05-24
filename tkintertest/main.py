from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import json
from elements import *
from vectors import *

## CONSTANTS
CONFIG_DIRECTORY: str = "conf.json"
FILETYPES = [('JSON File','*.json')]

## VARIABLES
root = Tk() # The root window
canvas = Canvas(root)
current_file_directory = None

def donothing(): pass

## Function for "Save"
def save():
   if current_file_directory:
      pass
   else:
      save_as()

## Function for "Save As"
def save_as():
   dir: str = filedialog.asksaveasfilename(filetypes=FILETYPES)
   _save_file(dir)

## Function for saving a file.
def _save_file(dir: str):
   try:
      with open(dir, 'w') as f:
         pass
         
      current_file_directory = dir
   except OSError:
      print('save failed')

## Function for "Open"
def open_file():
   dir: str = filedialog.askopenfilename(filetypes=FILETYPES)
   _load_file(dir)

## Function for opening a file
def _load_file(dir: str):
   try:
      file = {}
      with open(dir, 'r') as f:
         file = json.loads(f.read())
      
      print(file)
      canvas.delete('all')
      for _, v in enumerate(file['widgets']):
         widget(canvas, Rect2(
            v['x'],
            v['y'],
            v["width"],
            v['height'],
         ))
         print(v)

   except OSError:
      pass

def _on_closing():
   file = {
      'geometry':root.geometry()
   }
   with open(CONFIG_DIRECTORY, 'w') as f:
      f.write(json.dumps(file))
   root.destroy()

def close_application():
   if messagebox.askokcancel("Quit", "Do you want to quit?"):
      print("Performing cleanup before closing...")
      # Add your custom "stuff" here
      _on_closing()

## PROTOCOLS
root.protocol("WM_DELETE_WINDOW", close_application)

## MENU BAR
menubar = Menu(root)

## FILE
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_command(label="Open Recent", command=donothing)
filemenu.add_separator()
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Save As", command=save_as)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=close_application)
menubar.add_cascade(label="File", menu=filemenu)

## HELP
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)

## ADD MENUBAR
root.config(menu=menubar)

## LOAD CONFIGURATIONS
try: 
   file = {}
   with open(CONFIG_DIRECTORY, 'r') as f:
      file = json.loads(f.read())

   root.geometry(file['geometry'])
except OSError:
   pass

root.mainloop()