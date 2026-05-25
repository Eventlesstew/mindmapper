import tkinter as tk
from tkinter import filedialog
filetypes = [('JSON File','*.json')]

request = input()
output: str = ''
root = tk.Tk()
root.withdraw()  # Hide the main tkinter window

## TODO - Make it so the new window for saving is automatically focused on Mac
#root.lift() # Brings the window to the front of the stack
#root.attributes('-topmost', True) # Ensures it stays on top
#root.focus_force() # Forcefully requests focus
#root.update() # CRITICAL: Forces macOS to process these changes immediately

## TODO - Find a way to make it so the process of saving and loading is more independent. (On termination, performs more stuff.)

if request == 'save':
    output = filedialog.asksaveasfilename(filetypes=filetypes,defaultextension=filetypes)
elif request == 'open':
    output = filedialog.askopenfilename(filetypes=filetypes,defaultextension=filetypes)
root.destroy()

print(output)