import pygame

class Character:
    """Pac-Man veya hayalet gibi karakterleri temsil eder"""
    
    def __init__(self, x, y, color, cell_size=40):
        self.x = x
        self.y = y
        self.color = color
        self.path = []
        self.cell_size = cell_size
    
    def draw(self, screen):
        """Karakteri ekrana çizer"""
        pygame.draw.circle(screen, self.color, 
                         (self.x * self.cell_size + self.cell_size//2, 
                          self.y * self.cell_size + self.cell_size//2), 
                          self.cell_size//2 - 5)
    
    def move(self, new_pos):
        """Karakteri yeni bir pozisyona taşır"""
        self.x, self.y = new_pos
        return (self.x, self.y)

class Coin:
    """Oyundaki coinleri temsil eder"""
    
    def __init__(self, x, y, cell_size=40):
        self.x = x
        self.y = y
        self.cell_size = cell_size
    
    def draw(self, screen, color=(255, 215, 0)):  # Default: GOLD
        """Coini ekrana çizer"""
        pygame.draw.circle(screen, color, 
                         (self.x * self.cell_size + self.cell_size//2, 
                          self.y * self.cell_size + self.cell_size//2), 
                          self.cell_size//4)

class Button:
    """Kullanıcı arayüzündeki butonları temsil eder"""
    
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_selected = False
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen, WHITE=(255, 255, 255), BLACK=(0, 0, 0)):
        """Butonu ekrana çizer"""
        # Buton arkaplanı
        if self.is_selected:
            highlight_color = (min(self.color[0] + 50, 255),
                              min(self.color[1] + 50, 255),
                              min(self.color[2] + 50, 255))
            pygame.draw.rect(screen, highlight_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Buton çerçevesi
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Yazıyı siyah renkte render et
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Yazı arkaplanı için beyaz bir dikdörtgen
        padding = 4
        background_rect = pygame.Rect(text_rect.x - padding,
                                    text_rect.y - padding,
                                    text_rect.width + 2*padding,
                                    text_rect.height + 2*padding)
        pygame.draw.rect(screen, WHITE, background_rect)
        
        # Yazıyı çiz
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        """Butonun tıklanıp tıklanmadığını kontrol eder"""
        return self.rect.collidepoint(pos)