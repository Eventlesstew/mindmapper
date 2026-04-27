from tkinter import filedialog
import pygame
import json
from functions.elements import widget
from functions.elements import widget_link

class confClass:
    def __init__(self):
        self.double_click_time: float = 200.0
        self.trackpad: bool = False
        self.invert_trackpad_x: bool = True
        self.invert_trackpad_y: bool = False
        self.trackpad_sensitivity: float = 10

class fileClass:
    FILETYPES = [
        ('Mindmap File','*.mindmap'),
        ('JSON File','*.json')
    ]
    def __init__(self):
        self.widget_list: list[widget] = []
        self.line_list: list[widget_link] = []
        self.file_path: str = None
    
    def _save_file(self, path: str):
        if not path:
            path = filedialog.asksaveasfilename(filetypes=self.FILETYPES,defaultextension=self.FILETYPES)
        
        file = {
            'widgets':[],
            'links':[]
        }
        for _,v in enumerate(self.widget_list):
            widget_json = {
                'x':v.get_pos(False).x,
                'y':v.get_pos(False).y,
                'width':v.get_rect(False).w,
                'height':v.get_rect(False).h,
                'text':v.raw_text,
            }
            file['widgets'].append(widget_json)
        
        for _,v in enumerate(self.line_list):
            index1:int = -1
            index2:int = -1
            for i,w in enumerate(self.widget_list):
                if v.widget1 == w:
                    index1 = i
                if v.widget2 == w:
                    index2 = i
                if index1 > -1 and index2 > -1:
                    break
            
            line_json = {
                'widget1':index1,
                'widget2':index2
            }
            file['links'].append(line_json)
        
        with open(path, 'w') as f:
            f.write(json.dumps(file))

    def _load_file(self, path: str):
        filetypes = [('JSON File','*.json')]

        if not path:
            path = filedialog.askopenfilename(
                initialdir=self.file_path,
                filetypes=filetypes,
                defaultextension=filetypes
            )
        
        self.widget_list = []
        self.line_list = []
        file = {}
        with open(path, 'r') as f:
            file = json.loads(f.read())

        global camera
        for _,v in enumerate(file['widgets']):
            w = widget(
                camera,
                pygame.Vector2(v['x'],v['y']),
                pygame.Vector2(v['width'],v['height']),
                v['text']
            )

            self.widget_list.append(w)
        
        for _,v in enumerate(file['links']):
            widget1 = None
            widget2 = None

            for i,w in enumerate(self.widget_list):
                if i == v['widget1']:
                    widget1 = w
                if i == v['widget2']:
                    widget2 = w
                if widget1 and widget2:
                    break
            
            if widget1 and widget2:
                l = widget_link(camera, widget1, widget2)
            else:
                print("ERROR")
            self.line_list.append(l)

    def save(self):
        self._save_file(self.file_path)

    def save_as(self):
        self._save_file(None)
    
    def load(self):
        self._load_file(None)