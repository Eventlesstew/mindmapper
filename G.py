import pygame
from elements import widget
from enum import Enum

class dragStateTypes(Enum):
    INACTIVE = 1
    REPOSITION = 2
    RESIZE = 3

class confClass:
    def __init__(self):
        self.double_click_time = 500

class gClass:
    def __init__(self):
        self.last_click_time = pygame.time.get_ticks()
        self.click_streak = 1
        self.widget_list: list[widget] = []
        self.selected_widget: widget = None
        
        self.dragState: str = 'inactive'
