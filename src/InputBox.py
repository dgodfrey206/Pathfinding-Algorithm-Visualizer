import pygame as pg
import pdb

# Initialize pygame
pg.init()

FONT = pg.font.Font(None, 32)

class InputBox:
    # InputBox will be initialized with a position, and width and height, and the placeholder text (empty by default)
    def __init__(self, x, y, w, h, text=''):
        self.COLOR_INACTIVE = pg.Color('lightskyblue3')
        self.COLOR_ACTIVE = pg.Color('dodgerblue2')
        self.rect = pg.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        # first_key_event tells us when to remove the placeholder text
        self.first_key_event = True
        self.RETURN_HIT = pg.USEREVENT + 1

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
            self.txt_surface = FONT.render(self.text, True, self.color)
            
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    # post event so the user can retrieve input
                    pg.event.post(pg.event.Event(self.RETURN_HIT))
                elif event.key == pg.K_BACKSPACE:
                    # remove placeholder text
                    if self.first_key_event:
                        self.text = ''
                        self.first_key_event = False
                    else:
                        self.text = self.text[:-1]
                else:
                    # the user is typing a character. Place character into text.
                    if self.first_key_event:
                        self.text = event.unicode
                        self.first_key_event = False
                    else:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)
