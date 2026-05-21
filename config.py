class C:
    def __init__(self):
        self.double_click_time: float = 200.0
        self.trackpad: bool = False
        self.invert_trackpad_x: bool = True
        self.invert_trackpad_y: bool = False
        self.trackpad_sensitivity: float = 10
        self.text_cursor_blink_ms: float = 500
        self.font = 'assets/fonts/calibri-regular.ttf'
        self.zoom_sensitivity = 10

    class colors():
        background = "#a1bde0"
        background_grid = "#84aad8"
        widget_outline = "#0073ff"
        widget_outline_selected = "#e70606"
        widget = "#ffffff"
        text = "#000000"
        
    
    def get_config():
        global config
        return config

global config; config = C()