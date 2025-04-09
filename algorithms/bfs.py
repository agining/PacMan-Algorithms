from collections import deque
from .algorithm import Algorithm

class BFSAlgorithm(Algorithm):
    """Breadth-First Search (Genişlik Öncelikli Arama) Algoritması Sınıfı"""
    
    def __init__(self, maze):
        super().__init__(maze)
    
    def find_path(self, start, goal, **kwargs):
        """BFS algoritması kullanarak başlangıç noktasından hedef noktasına bir yol bulur"""
        # Kuyruk tabanlı arama: (konum, o konuma ulaşmak için izlenen yol)
        frontier = deque([(start, [start])])
        visited = {start}
        
        while frontier:
            current, path = frontier.popleft()
            
            if current == goal:
                return path
                
            for next_pos in self.get_neighbors(current):
                if next_pos not in visited:
                    visited.add(next_pos)
                    new_path = path + [next_pos]
                    frontier.append((next_pos, new_path))
        
        return []  # Yol bulunamadıysa boş liste döndür