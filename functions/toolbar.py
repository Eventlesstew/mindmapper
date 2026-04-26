import pygame

class toolbarButton:
    def __init__(self, parent, type):
        self.parent = parent
        self.type = type
        self.size: pygame.Vector2 = pygame.Vector2(100, parent.height)
        self.index: int = 0

    def get_text(self):
        return self.type
    
    def get_rect(self) -> pygame.Rect:
        pos = pygame.Vector2((self.size.x + self.parent.spacing) * self.index,0) 
        pos += pygame.Vector2(self.parent.spacing, self.parent.spacing)

        return pygame.Rect(pos, self.size)

    def set_index(self, newIndex):
        self.index = newIndex
    
    def collideMouse(self):
        return self.get_rect().collidepoint(pygame.mouse.get_pos())

    def render(self):
        screen = pygame.display.get_surface()
        rect = self.get_rect()
        font = pygame.font.Font(None, round(24))

        text_surface = font.render(self.get_text(), True, 'black')
        text_pos = pygame.Vector2(rect.center) - (pygame.Vector2(font.size(self.get_text()))/2)
        
        pygame.draw.rect(screen, 'gray', rect)
        screen.blit(text_surface, (text_pos, text_pos))

class toolbarClass:
    def __init__(self):
        self.height = 30
        self.spacing = 5

        self.buttons = [
            toolbarButton(self, 'mindmapper'),
            toolbarButton(self, 'file'),
            toolbarButton(self, 'edit'),
        ]

        for i,v in enumerate(self.buttons):
            v.set_index(i)
        
    def render(self):
        for _, b in enumerate(self.buttons):
            b.render()