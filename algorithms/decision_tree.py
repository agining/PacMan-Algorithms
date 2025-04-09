from .algorithm import Algorithm
import numpy as np
import os
import pickle
from sklearn.tree import DecisionTreeClassifier, export_graphviz

class DecisionTreeAlgorithm(Algorithm):
    """Decision Tree Algorithm for Pac-Man"""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.classifier = None
        self.features = [
            "goal_distance_x",
            "goal_distance_y",
            "closest_ghost_distance",
            "closest_ghost_direction_x",
            "closest_ghost_direction_y",
            "can_move_up",
            "can_move_right",
            "can_move_down",
            "can_move_left"
        ]
        
        # Try to load a pre-trained model if it exists
        self.load_model()
        
    def load_model(self, filepath=None):
        """Load a trained model from disk"""
        if filepath is None:
            # Proje kök dizinini temel alan mutlak yol
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, 'dt-model', 'pacman_decision_tree.pkl')
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.classifier = pickle.load(f)
                print(f"Karar ağacı modeli yüklendi: {filepath}")
                return True
            else:
                print(f"Model dosyası bulunamadı: {filepath}")
        except Exception as e:
            print(f"Model yükleme hatası: {e}")
        return False
    
    def save_model(self, filepath=None):
        """Save the trained model to disk"""
        if filepath is None:
            # Proje kök dizinini temel alan mutlak yol
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, 'dt-model', 'pacman_decision_tree.pkl')
            
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if self.classifier:
            try:
                with open(filepath, 'wb') as f:
                    pickle.dump(self.classifier, f)
                print(f"Karar ağacı modeli kaydedildi: {filepath}")
                return True
            except Exception as e:
                print(f"Model kaydetme hatası: {e}")
        return False
    
    def train(self, training_data):
        """
        Train the decision tree classifier with generated data
        
        Parameters:
        - training_data: List of (features, action) pairs
        """
        if not training_data:
            print("Eğitim verisi yok!")
            return False
            
        # Extract features and labels
        X = np.array([item[0] for item in training_data])
        y = np.array([item[1] for item in training_data])
        
        print(f"Karar ağacı eğitiliyor... {len(X)} örnek kullanılıyor.")
        
        # Create and train the classifier
        self.classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.classifier.fit(X, y)
        
        # Save the trained model
        self.save_model()
        
        print("Karar ağacı eğitimi tamamlandı.")
        return True
    
    def generate_features(self, current_pos, goal_pos, ghosts, coins, maze=None):
        """
        Generate features for the decision tree
        
        Parameters:
        - current_pos: Pac-Man's current position (x, y)
        - goal_pos: Target position (x, y) (usually nearest coin)
        - ghosts: List of ghost positions [(x, y), ...]
        - coins: List of coin positions [(x, y), ...]
        - maze: 2D grid representation of the maze (optional)
        
        Returns:
        - features: List of numerical features
        """
        if maze is None:
            maze = self.maze
            
        # Calculate distances to goal
        goal_distance_x = goal_pos[0] - current_pos[0]
        goal_distance_y = goal_pos[1] - current_pos[1]
        
        # Find closest ghost
        closest_ghost_distance = float('inf')
        closest_ghost_direction_x = 0
        closest_ghost_direction_y = 0
        
        for ghost_pos in ghosts:
            ghost_distance = abs(ghost_pos[0] - current_pos[0]) + abs(ghost_pos[1] - current_pos[1])
            if ghost_distance < closest_ghost_distance:
                closest_ghost_distance = ghost_distance
                closest_ghost_direction_x = ghost_pos[0] - current_pos[0]
                closest_ghost_direction_y = ghost_pos[1] - current_pos[1]
        
        # If no ghosts, set default values
        if closest_ghost_distance == float('inf'):
            closest_ghost_distance = 99  # Large value
        
        # Check valid moves (walls)
        valid_moves = [0, 0, 0, 0]  # [UP, RIGHT, DOWN, LEFT]
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for i, (dx, dy) in enumerate(directions):
            new_x, new_y = current_pos[0] + dx, current_pos[1] + dy
            if (0 <= new_x < len(maze[0]) and 
                0 <= new_y < len(maze) and 
                maze[new_y][new_x] == 0):  # Not a wall
                valid_moves[i] = 1
        
        # Compile all features
        features = [
            goal_distance_x,
            goal_distance_y,
            closest_ghost_distance,
            closest_ghost_direction_x,
            closest_ghost_direction_y,
            valid_moves[0],  # Can move UP
            valid_moves[1],  # Can move RIGHT
            valid_moves[2],  # Can move DOWN
            valid_moves[3]   # Can move LEFT
        ]
        
        return features
    
    def generate_training_data(self, num_samples=1000, astar_algo=None):
        """
        Generate training data by simulating different scenarios
        and using A* algorithm as a 'teacher'
        
        Parameters:
        - num_samples: Number of samples to generate
        - astar_algo: A* algorithm instance (optional)
        
        Returns:
        - training_data: List of (features, action) pairs
        """
        if astar_algo is None:
            from .astar import AStarAlgorithm
            astar_algo = AStarAlgorithm(self.maze)
        
        training_data = []
        print(f"Eğitim verisi oluşturuluyor... {num_samples} örnek hedefleniyor.")
        
        # Grid dimensions
        height = len(self.maze)
        width = len(self.maze[0]) if height > 0 else 0
        
        for _ in range(num_samples):
            # Generate random pacman position
            while True:
                pacman_x = np.random.randint(1, width-1)
                pacman_y = np.random.randint(1, height-1)
                if self.maze[pacman_y][pacman_x] == 0:  # Not a wall
                    break
            pacman_pos = (pacman_x, pacman_y)
            
            # Generate random goal position (coin)
            while True:
                goal_x = np.random.randint(1, width-1)
                goal_y = np.random.randint(1, height-1)
                if self.maze[goal_y][goal_x] == 0 and (goal_x, goal_y) != pacman_pos:
                    break
            goal_pos = (goal_x, goal_y)
            
            # Generate random ghost positions (1-3 ghosts)
            ghost_positions = []
            for _ in range(np.random.randint(1, 4)):
                while True:
                    ghost_x = np.random.randint(1, width-1)
                    ghost_y = np.random.randint(1, height-1)
                    if (self.maze[ghost_y][ghost_x] == 0 and 
                        (ghost_x, ghost_y) != pacman_pos and 
                        (ghost_x, ghost_y) != goal_pos and
                        not any((gx, gy) == (ghost_x, ghost_y) for gx, gy in ghost_positions)):
                        break
                ghost_positions.append((ghost_x, ghost_y))
            
            # Get A* path
            astar_path = astar_algo.find_path(pacman_pos, goal_pos)
            
            # If A* found a path
            if len(astar_path) > 1:
                next_pos = astar_path[1]
                
                # Determine action based on next position
                # 0: UP, 1: RIGHT, 2: DOWN, 3: LEFT
                dx = next_pos[0] - pacman_pos[0]
                dy = next_pos[1] - pacman_pos[1]
                
                if dx == 0 and dy == -1:
                    action = 0  # UP
                elif dx == 1 and dy == 0:
                    action = 1  # RIGHT
                elif dx == 0 and dy == 1:
                    action = 2  # DOWN
                elif dx == -1 and dy == 0:
                    action = 3  # LEFT
                else:
                    continue  # Invalid move, skip this sample
                
                # Generate features for this scenario
                features = self.generate_features(
                    pacman_pos, goal_pos, ghost_positions, [], self.maze
                )
                
                # Add to training data
                training_data.append((features, action))
        
        print(f"Toplam {len(training_data)} örnek oluşturuldu.")
        return training_data
    
    def save_training_data(self, training_data, filepath=None):
        """Save the training data to a CSV file for analysis"""
        if filepath is None:
            # Proje kök dizinini temel alan mutlak yol
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, 'dt-model', 'pacman_training_data.csv')
            
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
        try:
            with open(filepath, 'w') as f:
                # Write header
                header = ','.join(self.features + ['action'])
                f.write(header + '\n')
                
                # Write data
                for features, action in training_data:
                    line = ','.join(map(str, features + [action]))
                    f.write(line + '\n')
            print(f"Eğitim verileri kaydedildi: {filepath}")
            return True
        except Exception as e:
            print(f"Eğitim verisi kaydetme hatası: {e}")
            return False
    
    def find_path(self, start, goal, **kwargs):
        """
        Use the trained decision tree to determine Pac-Man's next move
        
        Parameters:
        - start: Pac-Man's current position (x, y)
        - goal: Target position (x, y) (usually nearest coin)
        - kwargs: Additional parameters including ghosts and coins
        
        Returns:
        - path: A list containing [current_pos, next_pos]
        """
        # Extract needed information from kwargs
        ghosts = kwargs.get('ghosts', [])
        coins = kwargs.get('coins', [])
        
        # If classifier isn't trained, train it
        if self.classifier is None:
            print("Karar ağacı modelini eğitiyorum...")
            from astar import AStarAlgorithm
            astar = AStarAlgorithm(self.maze)
            training_data = self.generate_training_data(num_samples=2000, astar_algo=astar)
            self.train(training_data)
            self.save_training_data(training_data)
            self.export_tree_visualization()
        
        # Convert game objects to positions
        ghost_positions = [(ghost.x, ghost.y) for ghost in ghosts]
        
        # Ensure we have a valid goal
        if goal == start:
            # If we're at the goal already, find another one
            min_dist = float('inf')
            best_coin = None
            for coin in coins:
                coin_pos = (coin.x, coin.y)
                dist = abs(start[0] - coin_pos[0]) + abs(start[1] - coin_pos[1])
                if dist < min_dist and coin_pos != start:
                    min_dist = dist
                    best_coin = coin_pos
            
            if best_coin:
                goal = best_coin
        
        # Generate features for current state
        features = self.generate_features(start, goal, ghost_positions, [])
        
        # Debugging output for valid moves
        valid_moves = features[5:9]
        if sum(valid_moves) == 0:
            print(f"Uyarı: {start} konumunda geçerli hareket yok!")
            return [start]  # Can't move
        
        try:
            # Predict action using the classifier
            action = int(self.classifier.predict([features])[0])
            
            # Convert action to next position
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # UP, RIGHT, DOWN, LEFT
            
            # Ensure action is in valid range
            if action < 0 or action >= len(directions):
                print(f"Uyarı: Geçersiz aksiyon tahmin edildi: {action}")
                # Find a valid move instead
                for i, is_valid in enumerate(valid_moves):
                    if is_valid:
                        action = i
                        break
            
            dx, dy = directions[action]
            next_pos = (start[0] + dx, start[1] + dy)
            
            # Check if the move is valid (not a wall)
            if (0 <= next_pos[0] < len(self.maze[0]) and 
                0 <= next_pos[1] < len(self.maze) and 
                self.maze[next_pos[1]][next_pos[0]] == 0):
                print(f"Tahmin edilen hareket: {start} -> {next_pos} (Aksiyon: {action})")
                # ÖNEMLİ: Dönüş değerini [mevcut, sonraki] formatında döndür
                return [start, next_pos]
            else:
                print(f"Uyarı: Tahmin edilen {next_pos} konumu geçerli değil!")
                # Fallback to a valid move
                for i, is_valid in enumerate(valid_moves):
                    if is_valid:
                        dx, dy = directions[i]
                        next_pos = (start[0] + dx, start[1] + dy)
                        print(f"Alternatif hareket: {start} -> {next_pos} (Aksiyon: {i})")
                        return [start, next_pos]
        except Exception as e:
            print(f"Karar ağacı tahmin hatası: {e}")
        
        # Default fallback: if we get here, something went wrong
        print("Uyarı: Varsayılan harekete döndüm.")
        return [start]
    
    def export_tree_visualization(self, filepath=None):
        """Export the decision tree visualization to a DOT file"""
        if filepath is None:
            # Proje kök dizinini temel alan mutlak yol
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, 'dt-model', 'pacman_decision_tree.dot')
            
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
        if self.classifier:
            try:
                export_graphviz(
                    self.classifier,
                    out_file=filepath,
                    feature_names=self.features,
                    class_names=['UP', 'RIGHT', 'DOWN', 'LEFT'],
                    filled=True,
                    rounded=True
                )
                print(f"Karar ağacı görseli aktarıldı: {filepath}")
                return True
            except Exception as e:
                print(f"Ağaç görselleştirme hatası: {e}")
        return False