from .algorithm import Algorithm
from collections import deque

class LimitedDFSAlgorithm(Algorithm):
    """Derinlik Sınırlı Derinlik Öncelikli Arama Algoritması"""
    
    def __init__(self, maze, max_depth=10):
        super().__init__(maze)
        self.max_depth = max_depth
    
    def find_path(self, start, goal, **kwargs):
        """
        Sınırlı derinliğe sahip DFS algoritması kullanarak yol bulur
        
        Parametreler:
        - start: Başlangıç pozisyonu (x, y)
        - goal: Hedef pozisyonu (x, y)
        - kwargs: Ekstra parametreler
          - max_depth: Maksimum derinlik (belirtilmezse varsayılan kullanılır)
        """
        # max_depth parametresi geçildiyse kullan, aksi halde varsayılanı kullan
        max_depth = kwargs.get('max_depth', self.max_depth)
        
        # Ziyaret edilen noktaları takip etmek için set
        visited = {start}
        
        # Yığın kullanarak derinlik öncelikli arama
        # Her eleman: (konum, o konuma ulaşmak için izlenen yol, derinlik)
        stack = [(start, [start], 0)]
        
        while stack:
            current, path, depth = stack.pop()
            
            # Hedef bulundu mu?
            if current == goal:
                return path
            
            # Maksimum derinliğe ulaşıldı mı?
            if depth >= max_depth:
                continue
            
            # Komşuları tersten ekleyerek, DFS'nin sağa doğru önce gitmesini sağla
            # (sezgisel olarak daha iyi sonuçlar veriyor)
            neighbors = self.get_neighbors(current)
            neighbors.reverse()  # Yönleri tersine çevir
            
            for next_pos in neighbors:
                if next_pos not in visited:
                    visited.add(next_pos)
                    new_path = path + [next_pos]
                    stack.append((next_pos, new_path, depth + 1))
        
        # Yol bulunamadı, hedefin yönünde en azından birkaç adım at
        if start != goal:
            # Hedef yönünü belirle
            dx = 1 if goal[0] > start[0] else -1 if goal[0] < start[0] else 0
            dy = 1 if goal[1] > start[1] else -1 if goal[1] < start[1] else 0
            
            # Bir adım yönünde git (eğer geçerliyse)
            new_x, new_y = start[0] + dx, start[1] + dy
            if (0 <= new_x < len(self.maze[0]) and 
                0 <= new_y < len(self.maze) and 
                self.maze[new_y][new_x] == 0):
                return [start, (new_x, new_y)]
            
            # Diğer yönleri dene
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = start[0] + dx, start[1] + dy
                if (0 <= new_x < len(self.maze[0]) and 
                    0 <= new_y < len(self.maze) and 
                    self.maze[new_y][new_x] == 0):
                    return [start, (new_x, new_y)]
        
        # Hiçbir şey başarılı olmazsa, sadece başlangıç pozisyonunu döndür
        return [start]