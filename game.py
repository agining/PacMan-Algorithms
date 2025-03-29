import pygame
import random

from character import Character, Coin, Button
from astar import AStarAlgorithm
from bfs import BFSAlgorithm
from dfs import LimitedDFSAlgorithm
from genetic_algorithm import GeneticAlgorithm

class GameState:
    """Oyun durumlarını temsil eden enum benzeri sınıf"""
    MENU = "MENU"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"
    GAME_WON = "GAME_WON"

class Game:
    """Pac-Man oyununu ve tüm oyun mantığını yönetir"""
    
    def __init__(self, screen_width=800, screen_height=600, cell_size=40):
        # Ekran ve ızgara ayarları
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.grid_width = screen_width // cell_size
        self.grid_height = screen_height // cell_size
        
        # Renkler
        self.BLACK = (0, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.WHITE = (255, 255, 255)
        self.GOLD = (255, 215, 0)
        self.GREEN = (0, 255, 0)
        
        # Oyun durumu ve algoritma seçimleri
        self.state = GameState.MENU
        self.pacman_algorithm = "A*"
        self.ghost_algorithm = "A*"
        self.score = 0
        self.num_ghosts = 2
        
        # Labirent oluştur
        self.maze = self.create_maze()
        
        # Algoritma örneklerini oluştur
        self.algorithms = {
            "A*": AStarAlgorithm(self.maze),
            "BFS": BFSAlgorithm(self.maze),
            "DFS": LimitedDFSAlgorithm(self.maze, max_depth=10),  # DFS yerine Limited DFS kullan
            "GA": GeneticAlgorithm(self.maze, population_size=50, chromosome_length=20, 
                                 mutation_rate=0.1, elite_size=5, generations=5)
        }
        
        # Oyun öğelerini başlat
        self.init_game()
        self.create_menu_buttons()
    
    def create_maze(self):
        """Labirent oluşturur"""
        maze = [[0 for x in range(self.grid_width)] for y in range(self.grid_height)]
        
        # Dış duvarlar
        for x in range(self.grid_width):
            maze[0][x] = 1
            maze[self.grid_height-1][x] = 1
        for y in range(self.grid_height):
            maze[y][0] = 1
            maze[y][self.grid_width-1] = 1
        
        # İç duvarlar
        for x in range(3, 8):
            maze[4][x] = 1
            maze[self.grid_height-5][x] = 1
        
        for x in range(self.grid_width-8, self.grid_width-3):
            maze[4][x] = 1
            maze[self.grid_height-5][x] = 1
        
        for y in range(3, 8):
            maze[y][4] = 1
            maze[y][self.grid_width-5] = 1
            
        return maze
    
    def init_game(self):
        """Oyun öğelerini başlatır"""
        # Pac-Man oluştur
        self.pacman = Character(1, 1, self.YELLOW, self.cell_size)
        
        # Hayaletleri oluştur
        self.ghosts = []
        ghost_positions = [
            (self.grid_width-2, self.grid_height-2),  # Sağ alt
            (self.grid_width-2, 1),                   # Sağ üst
            (1, self.grid_height-2)                   # Sol alt
        ]
        for x, y in ghost_positions[:self.num_ghosts]:
            self.ghosts.append(Character(x, y, self.RED, self.cell_size))
        
        # Coinleri oluştur
        self.coins = self.generate_valid_coins(15)
        self.score = 0
    
    def create_menu_buttons(self):
        """Menü butonlarını oluşturur"""
        button_width = 150
        button_height = 50
        button_spacing = 20
        start_x = (self.screen_width - (4 * button_width + 3 * button_spacing)) // 2
        
        self.buttons = {
            'pacman_astar': Button(start_x, 100, button_width, button_height, "Pacman: A*", (100, 200, 100)),
            'pacman_bfs': Button(start_x + button_width + button_spacing, 100, button_width, button_height, "Pacman: BFS", (100, 200, 100)),
            'pacman_dfs': Button(start_x + 2 * (button_width + button_spacing), 100, button_width, button_height, "Pacman: DFS", (100, 200, 100)),
            'pacman_genetic': Button(start_x + 3 * (button_width + button_spacing), 100, button_width, button_height, "Pacman: GA", (100, 200, 100)),
            
            'ghost_astar': Button(start_x, 180, button_width, button_height, "Ghost: A*", (200, 100, 100)),
            'ghost_bfs': Button(start_x + button_width + button_spacing, 180, button_width, button_height, "Ghost: BFS", (200, 100, 100)),
            'ghost_dfs': Button(start_x + 2 * (button_width + button_spacing), 180, button_width, button_height, "Ghost: DFS", (200, 100, 100)),
            'ghost_genetic': Button(start_x + 3 * (button_width + button_spacing), 180, button_width, button_height, "Ghost: GA", (200, 100, 100)),
            
            'start': Button(self.screen_width//2 - button_width//2, 260, button_width, button_height, "Start", self.GREEN)
        }
    
    def find_path(self, start, goal, algorithm_name, **kwargs):
        """Seçilen algoritmayı kullanarak yol bulur"""
        if algorithm_name in self.algorithms:
            # Ekstra parametreleri ekle
            kwargs.update({
                'pacman': self.pacman,
                'ghosts': self.ghosts,
                'coins': self.coins
            })
            # İlgili algoritmanın find_path metodunu çağır
            return self.algorithms[algorithm_name].find_path(start, goal, **kwargs)
        return []
    
    def generate_valid_coins(self, num_coins):
        """Geçerli konumlarda coin'ler oluşturur"""
        coins = []
        while len(coins) < num_coins:
            x = random.randint(1, self.grid_width-2)
            y = random.randint(1, self.grid_height-2)
            if (self.maze[y][x] == 0 and 
                not any(coin.x == x and coin.y == y for coin in coins) and
                not (x == 1 and y == 1)):
                coins.append(Coin(x, y, self.cell_size))
        return coins
    
    def find_nearest_coin(self):
        """Pac-Man'e en yakın coin'i bulur"""
        if not self.coins:
            return None
        
        nearest_coin = None
        min_distance = float('inf')
        
        for coin in self.coins:
            # Manhattan mesafesi
            distance = abs(self.pacman.x - coin.x) + abs(self.pacman.y - coin.y)
            if distance < min_distance:
                min_distance = distance
                nearest_coin = coin
                
        return nearest_coin
    
    def handle_menu_input(self, mouse_pos):
        """Menüdeki tıklamaları işler"""
        for key, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                if key == 'pacman_astar':
                    self.pacman_algorithm = "A*"
                elif key == 'pacman_bfs':
                    self.pacman_algorithm = "BFS"
                elif key == 'pacman_dfs':
                    self.pacman_algorithm = "DFS"
                elif key == 'pacman_genetic':
                    self.pacman_algorithm = "GA"
                elif key == 'ghost_astar':
                    self.ghost_algorithm = "A*"
                elif key == 'ghost_bfs':
                    self.ghost_algorithm = "BFS"
                elif key == 'ghost_dfs':
                    self.ghost_algorithm = "DFS"
                elif key == 'ghost_genetic':
                    self.ghost_algorithm = "GA"
                elif key == 'start':
                    self.state = GameState.PLAYING
                    self.init_game()
    
    def update_pacman(self):
        """Pac-Man'in hareketlerini günceller"""
        if not self.pacman.path:
            nearest_coin = self.find_nearest_coin()
            if nearest_coin:
                self.pacman.path = self.find_path(
                    (self.pacman.x, self.pacman.y),
                    (nearest_coin.x, nearest_coin.y),
                    self.pacman_algorithm
                )
            elif not self.coins:
                self.state = GameState.GAME_WON
                return
        
        if self.pacman.path and len(self.pacman.path) > 1:
            next_pos = self.pacman.path[1]
            self.pacman.move(next_pos)
            self.pacman.path = self.pacman.path[1:]
            
            # Coin toplama kontrolü
            for coin in self.coins[:]:
                if self.pacman.x == coin.x and self.pacman.y == coin.y:
                    self.coins.remove(coin)
                    self.score += 1
                    self.pacman.path = []  # Yeni yol hesapla
                    break
    
    def update_ghosts(self):
        """Hayaletlerin hareketlerini günceller"""
        # Her hayaleti tek tek güncelle
        for i, ghost in enumerate(self.ghosts):
            # Ekstra parametreler
            extra_params = {
                'is_ghost': True,
                'current_ghost_index': i
            }
            
            # Daha tutarlı hareket için hayaletleri aynı anda güncelle
            ghost_path = self.find_path(
                (ghost.x, ghost.y),
                (self.pacman.x, self.pacman.y),
                self.ghost_algorithm,
                **extra_params
            )
            
            if ghost_path and len(ghost_path) > 1:
                next_pos = ghost_path[1]
                ghost.move(next_pos)
            
            # Ghost Pac-Man'i yakaladı mı kontrolü
            if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                self.state = GameState.GAME_OVER
                break
    
    def draw_maze(self, screen):
        """Labirenti ekrana çizer"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.maze[y][x] == 1:
                    pygame.draw.rect(screen, self.BLUE, 
                                  (x * self.cell_size, y * self.cell_size, 
                                   self.cell_size, self.cell_size))
    
    def draw_menu(self, screen):
        """Menü ekranını çizer"""
        # Başlık
        title_font = pygame.font.Font(None, 48)
        title_text = "Pacman with Multiple Search Algorithms"
        title_surface = title_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.screen_width//2, 40))
        screen.blit(title_surface, title_rect)

        # Seçili algoritmaları göster
        selected_text = f"Selected: Pacman-{self.pacman_algorithm}, Ghost-{self.ghost_algorithm}"
        selected_font = pygame.font.Font(None, 36)
        selected_surface = selected_font.render(selected_text, True, self.GOLD)
        selected_rect = selected_surface.get_rect(center=(self.screen_width//2, 340))
        screen.blit(selected_surface, selected_rect)

        # Butonları çiz
        for key, button in self.buttons.items():
            if (key == f'pacman_{self.pacman_algorithm.lower()}' or 
                key == f'ghost_{self.ghost_algorithm.lower()}'):
                button.is_selected = True
            else:
                button.is_selected = False
            button.draw(screen, self.WHITE, self.BLACK)
    
    def draw_game(self, screen):
        """Oyun ekranını çizer"""
        # Labirenti çiz
        self.draw_maze(screen)
        
        # Coinleri çiz
        for coin in self.coins:
            coin.draw(screen, self.GOLD)
        
        # Pac-Man'i ve hayaletleri çiz
        self.pacman.draw(screen)
        for ghost in self.ghosts:
            ghost.draw(screen)
        
        # Skor gösterimi
        score_text = f"Score: {self.score}"
        score_surface = pygame.font.Font(None, 36).render(score_text, True, self.WHITE)
        screen.blit(score_surface, (10, 10))
        
        # Algoritma bilgisi
        algo_text = f"Pacman: {self.pacman_algorithm}, Ghost: {self.ghost_algorithm}"
        algo_surface = pygame.font.Font(None, 28).render(algo_text, True, self.WHITE)
        screen.blit(algo_surface, (10, 40))
    
    def draw_game_over(self, screen):
        """Oyun sonu ekranını çizer (kaybetme)"""
        text = f"GAME OVER! Score: {self.score}"
        text_surface = pygame.font.Font(None, 74).render(text, True, self.RED)
        text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
        screen.blit(text_surface, text_rect)
        
        # Restart butonu
        self.buttons['start'].text = "Restart"
        self.buttons['start'].draw(screen, self.WHITE, self.BLACK)
    
    def draw_game_won(self, screen):
        """Oyun sonu ekranını çizer (kazanma)"""
        text = f"YOU WIN! Score: {self.score}"
        text_surface = pygame.font.Font(None, 74).render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width//2, self.screen_height//2))
        screen.blit(text_surface, text_rect)
        
        # Restart butonu
        self.buttons['start'].text = "Restart"
        self.buttons['start'].draw(screen, self.WHITE, self.BLACK)
    
    def handle_events(self):
        """Pygame olaylarını işler"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == GameState.MENU:
                    self.handle_menu_input(mouse_pos)
                elif self.state in [GameState.GAME_OVER, GameState.GAME_WON]:
                    if self.buttons['start'].is_clicked(mouse_pos):
                        self.state = GameState.MENU
        
        return True
    
    def update(self):
        """Oyun durumunu günceller"""
        if self.state == GameState.PLAYING:
            self.update_pacman()
            self.update_ghosts()
    
    def draw(self, screen):
        """Oyun ekranını çizer"""
        screen.fill(self.BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu(screen)
        elif self.state == GameState.PLAYING:
            self.draw_game(screen)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over(screen)
        elif self.state == GameState.GAME_WON:
            self.draw_game_won(screen)
            
        pygame.display.flip()
    
    def run(self, screen, fps=15):
        """Oyunu çalıştırır"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw(screen)
            clock.tick(fps)  # FPS ayarı
        
        return False