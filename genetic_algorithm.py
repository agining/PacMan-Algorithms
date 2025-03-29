import random
import numpy as np
from algorithm import Algorithm

class GeneticAlgorithm(Algorithm):
    """Genetik Algoritma Sınıfı"""
    
    def __init__(self, maze, population_size=50, chromosome_length=20, 
                 mutation_rate=0.1, elite_size=5, generations=10):
        super().__init__(maze)
        self.population_size = population_size  # Popülasyondaki birey sayısı
        self.chromosome_length = chromosome_length  # Bir bireyin gen uzunluğu (hareket sayısı)
        self.mutation_rate = mutation_rate  # Mutasyon olasılığı
        self.elite_size = elite_size  # Doğrudan bir sonraki nesle aktarılacak en iyi birey sayısı
        self.generations = generations  # Toplam evrim nesil sayısı
        self.population = []  # Mevcut popülasyon
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # [AŞAĞI, SAĞ, YUKARI, SOL]
    
    def initialize_population(self):
        """Rastgele hareketlerden oluşan başlangıç popülasyonu oluşturur"""
        self.population = []
        for _ in range(self.population_size):
            # Her birey için, rastgele hareket yönleri seç
            # 0, 1, 2, 3 değerleri (AŞAĞI, SAĞ, YUKARI, SOL) yönlerini temsil eder
            chromosome = [random.randint(0, 3) for _ in range(self.chromosome_length)]
            self.population.append(chromosome)
        return self.population
    
    def evaluate_fitness_pacman(self, pacman_pos, ghost_positions, coin_positions):
        """Pac-Man için fitness değerlendirmesi yapar (puan toplama ve hayaletlerden kaçma)"""
        fitness_scores = []
        
        for chromosome in self.population:
            # Pac-Man'in simüle edilmiş hareketi
            current_pos = pacman_pos
            coins_collected = 0
            alive = True
            path = [current_pos]
            
            # Kromozomdaki her hareketi simüle et
            for gene in chromosome:
                dx, dy = self.directions[gene]
                new_x, new_y = current_pos[0] + dx, current_pos[1] + dy
                
                # Hareket geçerli mi kontrol et
                if (0 <= new_x < len(self.maze[0]) and 
                    0 <= new_y < len(self.maze) and 
                    self.maze[new_y][new_x] == 0):  # Duvar değilse
                    current_pos = (new_x, new_y)
                    path.append(current_pos)
                    
                    # Coin toplandı mı kontrol et
                    for coin in coin_positions[:]:
                        if current_pos == (coin.x, coin.y):
                            coins_collected += 1
                            break
                    
                    # Hayalet teması kontrolü
                    for ghost_pos in ghost_positions:
                        if current_pos == ghost_pos:
                            alive = False
                            break
                    
                    if not alive:
                        break
            
            # Fitness hesaplama
            fitness = 0
            
            # 1. Toplanan coinler için bonus
            fitness += coins_collected * 50
            
            # 2. Hayatta kalma bonusu
            if alive:
                fitness += 20
            
            # 3. Hayaletlerden uzaklık bonusu
            min_ghost_dist = float('inf')
            for ghost_pos in ghost_positions:
                dist = abs(current_pos[0] - ghost_pos[0]) + abs(current_pos[1] - ghost_pos[1])
                min_ghost_dist = min(min_ghost_dist, dist)
            
            fitness += min_ghost_dist * 2
            
            # 4. En yakın coine olan mesafeye göre bonus
            if coin_positions:
                min_coin_dist = float('inf')
                for coin in coin_positions:
                    dist = abs(current_pos[0] - coin.x) + abs(current_pos[1] - coin.y)
                    min_coin_dist = min(min_coin_dist, dist)
                
                fitness -= min_coin_dist  # Coine yakınlık daha iyidir
            
            fitness_scores.append((fitness, path))
        
        # Fitness skorlarına göre sırala (en yüksekten en düşüğe)
        fitness_scores.sort(reverse=True, key=lambda x: x[0])
        return fitness_scores
    
    def evaluate_fitness_ghost(self, ghost_pos, pacman_pos, other_ghost_positions):
        """Hayaletler için fitness değerlendirmesi yapar (Pac-Man'i yakalama odaklı)"""
        fitness_scores = []
        
        for chromosome in self.population:
            # Hayaletin simüle edilmiş hareketi
            current_pos = ghost_pos
            caught_pacman = False
            path = [current_pos]
            steps_taken = 0
            
            # Kromozomdaki her hareketi simüle et
            for gene in chromosome:
                dx, dy = self.directions[gene]
                new_x, new_y = current_pos[0] + dx, current_pos[1] + dy
                
                # Hareket geçerli mi kontrol et
                if (0 <= new_x < len(self.maze[0]) and 
                    0 <= new_y < len(self.maze) and 
                    self.maze[new_y][new_x] == 0):  # Duvar değilse
                    current_pos = (new_x, new_y)
                    path.append(current_pos)
                    steps_taken += 1
                    
                    # Pac-Man'i yakaladı mı kontrol et
                    if current_pos == pacman_pos:
                        caught_pacman = True
                        break
            
            # Fitness hesaplama
            fitness = 0
            
            # 1. Pac-Man'i yakalama bonusu
            if caught_pacman:
                fitness += 1000 - steps_taken * 5  # Ne kadar az adımda yakalanırsa o kadar iyi
            
            # 2. Pac-Man'e yakınlık bonusu
            dist_to_pacman = abs(current_pos[0] - pacman_pos[0]) + abs(current_pos[1] - pacman_pos[1])
            fitness += (100 - dist_to_pacman * 10)  # Ne kadar yakınsa o kadar iyi
            
            # 3. Diğer hayaletlerden uzaklık bonusu (sürü davranışını engelle)
            for other_ghost in other_ghost_positions:
                if other_ghost != ghost_pos:  # Kendisi hariç
                    dist = abs(current_pos[0] - other_ghost[0]) + abs(current_pos[1] - other_ghost[1])
                    if dist < 3:  # Çok yakınsa ceza ver
                        fitness -= (3 - dist) * 10
            
            fitness_scores.append((fitness, path))
        
        # Fitness skorlarına göre sırala (en yüksekten en düşüğe)
        fitness_scores.sort(reverse=True, key=lambda x: x[0])
        return fitness_scores
    
    def select_parents(self, fitness_scores):
        """Rulet tekerleği seçimi ile ebeveynleri seç"""
        parents = []
        fitness_scores_only = [score for score, _ in fitness_scores]
        
        # Elite selection - en iyi bireyleri doğrudan seç
        for i in range(min(self.elite_size, len(self.population))):
            parents.append(self.population[i])
        
        # Rulet tekerleği seçimi için fitness değerlerini ayarla
        # Negatif fitness değerlerini ele almak için minimum değeri sıfıra çek
        min_fitness = min(fitness_scores_only) if fitness_scores_only else 0
        if min_fitness < 0:
            fitness_scores_only = [value - min_fitness + 1 for value in fitness_scores_only]
        
        # Toplam fitness hesapla
        total_fitness = sum(fitness_scores_only)
        
        # Kalan ebeveynleri seç
        while len(parents) < self.population_size:
            if total_fitness <= 0:
                # Eğer toplam fitness 0 veya negatifse, rastgele seç
                parents.append(random.choice(self.population))
                continue
                
            pick = random.uniform(0, total_fitness)
            current = 0
            for i, fitness in enumerate(fitness_scores_only):
                current += fitness
                if current > pick:
                    parents.append(self.population[i])
                    break
            
            # Eğer hiçbir ebeveyn seçilmediyse (nadir durum), rastgele bir ebeveyn seç
            if len(parents) == len(parents) - 1:
                parents.append(random.choice(self.population))
        
        return parents
    
    def crossover(self, parents):
        """Ebeveynleri çaprazlayarak yeni nesil oluştur"""
        children = []
        
        # Elite bireyleri doğrudan aktar
        children.extend(parents[:self.elite_size])
        
        # Geri kalanlar için çaprazlama yap
        while len(children) < self.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            
            # Çaprazlama noktası seç
            crossover_point = random.randint(1, len(parent1) - 1)
            
            # Çocukları oluştur
            child = parent1[:crossover_point] + parent2[crossover_point:]
            children.append(child)
        
        return children
    
    def mutate(self, children):
        """Çocukları belirli bir olasılıkla mutasyona uğrat"""
        for i in range(self.elite_size, len(children)):  # Elite bireyleri koruyarak
            for j in range(len(children[i])):
                if random.random() < self.mutation_rate:
                    # Rastgele bir hareket yönü ile değiştir
                    children[i][j] = random.randint(0, 3)
        
        return children
    
    def evolve_pacman(self, pacman_pos, ghost_positions, coin_positions):
        """Pac-Man için genetik algoritma ile evrim gerçekleştirir"""
        # Popülasyon yoksa başlat
        if not self.population:
            self.initialize_population()
        
        # Belirtilen nesil sayısı kadar evrim döngüsü
        for _ in range(self.generations):
            # Fitness değerlendirmesi
            fitness_scores = self.evaluate_fitness_pacman(pacman_pos, ghost_positions, coin_positions)
            
            # Ebeveyn seçimi
            parents = self.select_parents(fitness_scores)
            
            # Çaprazlama
            children = self.crossover(parents)
            
            # Mutasyon
            children = self.mutate(children)
            
            # Yeni nesil
            self.population = children
        
        # En iyi bireyi ve yolunu döndür
        if not self.population:
            return [pacman_pos]  # Başlangıç pozisyonunu döndür
            
        fitness_scores = self.evaluate_fitness_pacman(pacman_pos, ghost_positions, coin_positions)
        if not fitness_scores:
            return [pacman_pos]
            
        _, best_path = fitness_scores[0]  # En iyi birey
        return best_path
    
    def evolve_ghost(self, ghost_pos, pacman_pos, other_ghost_positions):
        """Hayalet için genetik algoritma ile evrim gerçekleştirir"""
        # Popülasyon yoksa başlat
        if not self.population:
            self.initialize_population()
        
        # Belirtilen nesil sayısı kadar evrim döngüsü
        for _ in range(self.generations):
            # Fitness değerlendirmesi
            fitness_scores = self.evaluate_fitness_ghost(ghost_pos, pacman_pos, other_ghost_positions)
            
            # Ebeveyn seçimi
            parents = self.select_parents(fitness_scores)
            
            # Çaprazlama
            children = self.crossover(parents)
            
            # Mutasyon
            children = self.mutate(children)
            
            # Yeni nesil
            self.population = children
        
        # En iyi bireyi ve yolunu döndür
        if not self.population:
            return [ghost_pos]  # Başlangıç pozisyonunu döndür
            
        fitness_scores = self.evaluate_fitness_ghost(ghost_pos, pacman_pos, other_ghost_positions)
        if not fitness_scores:
            return [ghost_pos]
            
        _, best_path = fitness_scores[0]  # En iyi birey
        return best_path
    
    def find_path(self, start, goal, **kwargs):
        """
        Genetik algoritma kullanarak başlangıç noktasından hedefe bir yol bulur
        
        Parametreler:
        - start: Başlangıç pozisyonu (x, y)
        - goal: Hedef pozisyonu (x, y)
        - kwargs: Ekstra parametreler
          - pacman: Pac-Man karakteri
          - ghosts: Hayalet listesi
          - coins: Coin listesi
          - is_ghost: Bu bir hayalet için mi çağrılıyor?
          - current_ghost_index: Şu anki hayalet indeksi (hayaletler için)
        """
        # Gerekli parametreleri al
        pacman = kwargs.get('pacman', None)
        ghosts = kwargs.get('ghosts', [])
        coins = kwargs.get('coins', [])
        is_ghost = kwargs.get('is_ghost', False)
        current_ghost_index = kwargs.get('current_ghost_index', 0)
        
        if not pacman:
            return []
            
        pacman_pos = (pacman.x, pacman.y)
        ghost_positions = [(ghost.x, ghost.y) for ghost in ghosts]
        
        # Eğer bu bir hayalet için çağrıldıysa
        if is_ghost:
            # Diğer hayaletlerin pozisyonları (şu anki hayalet hariç)
            other_ghost_positions = [pos for i, pos in enumerate(ghost_positions) if i != current_ghost_index]
            
            # Hayalet için evrim
            return self.evolve_ghost(start, pacman_pos, other_ghost_positions)
        else:
            # Pac-Man için evrim
            if goal != start and coins:  # Eğer hedef belirtilmişse ve coin varsa
                target_coin = type('obj', (object,), {'x': goal[0], 'y': goal[1]})
                temp_coins = coins + [target_coin]
                return self.evolve_pacman(pacman_pos, ghost_positions, temp_coins)
            else:
                return self.evolve_pacman(pacman_pos, ghost_positions, coins)