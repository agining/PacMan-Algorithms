import heapq
from algorithm import Algorithm

class AStarAlgorithm(Algorithm):
    """A* Arama Algoritması Sınıfı"""
    
    def __init__(self, maze):
        super().__init__(maze)
    
    def heuristic(self, a, b):
        """Manhattan mesafesi hesaplar (x1-x2) + (y1-y2)"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def find_path(self, start, goal, **kwargs):
        """A* algoritması kullanarak başlangıç noktasından hedef noktasına bir yol bulur"""
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Yolu oluştur
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        
        # Geçerli bir yol mu kontrol et
        return path if path and path[0] == start else []