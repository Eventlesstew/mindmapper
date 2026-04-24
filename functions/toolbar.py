import pygame

class toolbarButton:
    def __init__(self, text):
        self.text = text

class toolbarClass:
    def __init__(self, ):
        self.buttons = [
            toolbarButton('Mindmapper'),
            toolbarButton('File'),
            toolbarButton('Edit'),
        ]
        self.height = 30
        self.spacing = 5
        
    def render(self):
        screen = pygame.display.get_surface()
        font = pygame.font.Font(None, round(24))

        for i in range(0,len(self.buttons)):
            b = self.buttons[i]

            rect = pygame.Rect(
                ((100 + self.spacing) * i) + self.spacing,
                self.spacing,
                100,
                self.height
            )
            text_surface = font.render(b.text, True, 'black')

            text_pos = pygame.Vector2(rect.center) - (pygame.Vector2(font.size(b.text))/2)
            pygame.draw.rect(screen, 'gray', rect)
            screen.blit(text_surface, (text_pos, text_pos))