import pygame
from game import Game

def main():
    # Pygame'i başlat
    pygame.init()
    pygame.font.init()
    
    # Ekran ve oyun ayarları
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    CELL_SIZE = 40
    FPS = 30  # FPS değeri için orta seviye (daha yüksek FPS için 20-30 arası değerler denenebilir)
    
    # Ekranı oluştur
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pacman with Multiple Search Algorithms")
    
    # Oyunu oluştur ve çalıştır
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE)
    game.run(screen, FPS)
    
    # Oyun çıkışında Pygame'i kapat
    pygame.quit()

if __name__ == "__main__":
    main()