from abc import ABC, abstractmethod

class Algorithm(ABC):
    """Tüm algoritmaların temel sınıfı"""
    
    def __init__(self, maze):
        self.maze = maze
    
    @abstractmethod
    def find_path(self, start, goal, **kwargs):
        """
        start: Başlangıç pozisyonu (x, y)
        goal: Hedef pozisyonu (x, y)
        kwargs: Ekstra parametreler (coin'ler, hayaletler gibi)
        
        Dönüş: Hareketleri içeren bir liste [(x1, y1), (x2, y2), ...]
        """
        pass
    
    def get_neighbors(self, pos):
        """Belirli bir pozisyonun geçerli komşularını döndürür"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Aşağı, Sağ, Yukarı, Sol
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if (0 <= new_x < len(self.maze[0]) and 
                0 <= new_y < len(self.maze) and 
                self.maze[new_y][new_x] == 0):  # Duvar değilse
                neighbors.append((new_x, new_y))
        return neighbors