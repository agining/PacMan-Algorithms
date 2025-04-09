import pygame
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import os
import sys


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from game import Game, GameState  
from collections import defaultdict

class GameSimulation:
    """Pac-Man oyunu simülasyonu için arka planda çalışan sınıf"""
    
    def __init__(self, max_steps=300, num_trials=1, num_coins=30):
        """
        Parametreler:
        - max_steps: Maksimum adım sayısı (sonsuz döngülerden kaçınmak için)
        - num_trials: Her algoritma kombinasyonu için deneme sayısı
        - num_coins: Oyun başına konulacak coin sayısı
        """
        # Pygame'i başlat (ekransız)
        pygame.init()
        pygame.font.init()
        
        # Simülasyon ayarları
        self.max_steps = max_steps
        self.num_trials = num_trials
        self.num_coins = num_coins
        
        # Ekran boyutları (arka planda çalışacak)
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.CELL_SIZE = 40
        self.grid_width = self.SCREEN_WIDTH // self.CELL_SIZE
        self.grid_height = self.SCREEN_HEIGHT // self.CELL_SIZE
        
        # Sahte bir ekran oluştur
        self.screen = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        # Mevcut algoritma listesi
        self.pacman_algorithms = ["A*", "BFS", "DFS", "GA", "DT"]
        self.ghost_algorithms = ["A*", "BFS", "DFS", "GA"]
        
        # Sonuçları saklamak için veri yapıları
        self.results = {
            "coins_collected": defaultdict(list),  # (pacman_algo, ghost_algo) -> [coins1, coins2, ...]
            "survival_steps": defaultdict(list),   # (pacman_algo, ghost_algo) -> [steps1, steps2, ...]
            "win_rate": defaultdict(int),          # (pacman_algo, ghost_algo) -> kazanma sayısı
            "total_trials": defaultdict(int)       # (pacman_algo, ghost_algo) -> toplam deneme sayısı
        }
        
        # YENİ: Isı haritası için konum takibi
        self.position_heatmap = {}  # algorithm -> 2D array of visit counts
        
        # YENİ: Algoritma zamanlama takibi
        self.step_times = {}  # algorithm -> [time1, time2, ...]
        
        # YENİ: Yol takibi (animasyon için)
        self.path_tracking = {}  # (algorithm, trial) -> [(x1,y1), (x2,y2), ...]
        
        # Oyun oluşturma için referans maze
        game = Game(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.CELL_SIZE)
        self.maze = game.maze
    
    def run_single_simulation(self, pacman_algo, ghost_algo):
        """Belirli bir algoritma kombinasyonu için tek bir simülasyon çalıştırır"""
        # Yeni bir oyun oluştur
        game = Game(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.CELL_SIZE)
        
        # Coin sayısını ayarla
        game.init_game()  # Önce oyunu başlat
        game.coins = game.generate_valid_coins(self.num_coins)  # Ardından istenen sayıda coin oluştur
        
        # Algoritmaları ayarla
        game.pacman_algorithm = pacman_algo
        game.ghost_algorithm = ghost_algo
        game.user_control = False  # Kullanıcı kontrolünü kapat
        
        # Oyun durumunu ayarla
        game.state = GameState.PLAYING
        
        # Simülasyon sonuçları
        coins_collected = 0
        steps_taken = 0
        game_won = False
        
        # YENİ: Yol takibi için başlangıç pozisyonunu kaydet
        path = [(game.pacman.x, game.pacman.y)]
        
        # YENİ: Adım süresini ölçmek için
        step_times = []
        
        # Oyunu çalıştır
        while steps_taken < self.max_steps:
            # Olayları işle (çıkış kontrolü için)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
            
            # Adım sayısını artır
            steps_taken += 1
            
            # YENİ: Adım zamanını ölçmeye başla
            step_start_time = time.time()
            
            # Oyun mantığını güncelle
            game.update_pacman()
            
            # YENİ: Adım zamanını ölç ve kaydet
            step_time = time.time() - step_start_time
            step_times.append(step_time)
            
            # YENİ: Pac-Man'in pozisyonunu takip et
            pacman_pos = (game.pacman.x, game.pacman.y)
            path.append(pacman_pos)
            
            # YENİ: Isı haritası için pozisyonu güncelle
            if pacman_algo not in self.position_heatmap:
                self.position_heatmap[pacman_algo] = np.zeros((self.grid_height, self.grid_width))
            self.position_heatmap[pacman_algo][pacman_pos[1], pacman_pos[0]] += 1
            
            # Hayaletleri güncelle
            game.update_ghosts()
            
            # Coin sayısını takip et
            coins_collected = game.score
            
            # Oyun durumunu kontrol et
            if game.state == GameState.GAME_OVER:
                break  # Hayalet yakaladı
            elif game.state == GameState.GAME_WON:
                game_won = True
                break  # Tüm coinler toplandı
        
        # YENİ: Ortalama adım süresini hesapla ve kaydet
        if len(step_times) > 0:
            avg_step_time = sum(step_times) / len(step_times)
            if pacman_algo not in self.step_times:
                self.step_times[pacman_algo] = []
            self.step_times[pacman_algo].append(avg_step_time)
        
        # YENİ: Yolu kaydet
        key = (pacman_algo, ghost_algo)
        trial_num = self.results["total_trials"].get(key, 0)  

        self.path_tracking[(pacman_algo, trial_num)] = path
        
        # Sonuçları döndür
        return {
            "coins_collected": coins_collected,
            "survival_steps": steps_taken,
            "game_won": game_won
        }
    
    def run_all_simulations(self):
        """Tüm algoritma kombinasyonları için simülasyonları çalıştırır"""
        total_combinations = len(self.pacman_algorithms) * len(self.ghost_algorithms)
        current_combination = 0
        
        print(f"Toplam {total_combinations} algoritma kombinasyonu için simülasyon başlatılıyor...")
        print(f"Her kombinasyon için {self.num_trials} deneme yapılacak.")
        print(f"Her oyunda {self.num_coins} coin olacak.")
        print("-" * 50)
        
        start_time = time.time()
        
        # Tüm kombinasyonları dene
        for pacman_algo in self.pacman_algorithms:
            for ghost_algo in self.ghost_algorithms:
                current_combination += 1
                key = (pacman_algo, ghost_algo)
                
                print(f"[{current_combination}/{total_combinations}] Pacman: {pacman_algo}, Ghost: {ghost_algo} simülasyonu başlatılıyor...")
                
                # Belirtilen sayıda deneme yap
                for trial in range(self.num_trials):
                    print(f"  Deneme {trial+1}/{self.num_trials}...", end="", flush=True)
                    
                    # Simülasyonu çalıştır
                    results = self.run_single_simulation(pacman_algo, ghost_algo)
                    
                    # Sonuçları kaydet
                    if results:
                        self.results["coins_collected"][key].append(results["coins_collected"])
                        self.results["survival_steps"][key].append(results["survival_steps"])
                        if results["game_won"]:
                            self.results["win_rate"][key] += 1
                        self.results["total_trials"][key] += 1
                        
                        print(f" Tamamlandı: {results['coins_collected']} coin, {results['survival_steps']} adım, {'Kazandı' if results['game_won'] else 'Kaybetti'}")
                    else:
                        print(" Hata!")
                
                # Kombinasyon sonuçlarını yazdır
                avg_coins = np.mean(self.results["coins_collected"][key])
                avg_steps = np.mean(self.results["survival_steps"][key])
                win_rate = self.results["win_rate"][key] / self.results["total_trials"][key] * 100
                
                print(f"  Ortalama sonuçlar: {avg_coins:.1f} coin, {avg_steps:.1f} adım, %{win_rate:.1f} kazanma oranı")
                print("-" * 50)
        
        # Toplam süreyi yazdır
        total_time = time.time() - start_time
        print(f"Tüm simülasyonlar {total_time:.1f} saniyede tamamlandı.")
        
        return self.results
    
    def print_summary(self):
        """Simülasyon sonuçlarının özetini yazdırır"""
        if not self.results["total_trials"]:
            print("Henüz simülasyon sonucu bulunmuyor.")
            return
        
        print("\n" + "=" * 80)
        print("SIMÜLASYON SONUÇLARI ÖZETİ".center(80))
        print("=" * 80)
        
        # Tablo başlığı
        print(f"{'Pacman Algo':<12} | {'Ghost Algo':<12} | {'Coins Avg':<10} | {'Steps Avg':<10} | {'Win Rate %':<10}")
        print("-" * 80)
        
        # Her kombinasyon için sonuçları yazdır
        for key in sorted(self.results["total_trials"].keys()):
            pacman_algo, ghost_algo = key
            
            avg_coins = np.mean(self.results["coins_collected"][key])
            avg_steps = np.mean(self.results["survival_steps"][key])
            win_rate = self.results["win_rate"][key] / self.results["total_trials"][key] * 100
            
            print(f"{pacman_algo:<12} | {ghost_algo:<12} | {avg_coins:<10.1f} | {avg_steps:<10.1f} | {win_rate:<10.1f}")
        
        print("=" * 80)
        
        # En iyi kombinasyonları bul
        best_coins = {}
        best_survival = {}
        best_win_rate = {}
        
        for key in self.results["total_trials"].keys():
            pacman_algo, ghost_algo = key
            
            # En yüksek ortalama coin
            avg_coins = np.mean(self.results["coins_collected"][key])
            if pacman_algo not in best_coins or avg_coins > best_coins[pacman_algo][1]:
                best_coins[pacman_algo] = (ghost_algo, avg_coins)
            
            # En yüksek ortalama hayatta kalma süresi
            avg_steps = np.mean(self.results["survival_steps"][key])
            if pacman_algo not in best_survival or avg_steps > best_survival[pacman_algo][1]:
                best_survival[pacman_algo] = (ghost_algo, avg_steps)
            
            # En yüksek kazanma oranı
            win_rate = self.results["win_rate"][key] / self.results["total_trials"][key] * 100
            if pacman_algo not in best_win_rate or win_rate > best_win_rate[pacman_algo][1]:
                best_win_rate[pacman_algo] = (ghost_algo, win_rate)
        
        # En iyi sonuçları yazdır
        print("\nPac-Man Algoritması Bazında En İyi Sonuçlar:")
        print("-" * 50)
        
        for pacman_algo in self.pacman_algorithms:
            print(f"\nPacman Algoritması: {pacman_algo}")
            if pacman_algo in best_coins:
                print(f"  En Yüksek Coin Toplama: {best_coins[pacman_algo][1]:.1f} coin (Ghost: {best_coins[pacman_algo][0]})")
            if pacman_algo in best_survival:
                print(f"  En Uzun Hayatta Kalma: {best_survival[pacman_algo][1]:.1f} adım (Ghost: {best_survival[pacman_algo][0]})")
            if pacman_algo in best_win_rate:
                print(f"  En Yüksek Kazanma Oranı: %{best_win_rate[pacman_algo][1]:.1f} (Ghost: {best_win_rate[pacman_algo][0]})")
    
    def generate_visualizations(self, output_prefix=None):
        """Sonuçları görselleştirir ve kaydeder"""
        if not self.results["total_trials"]:
            print("Henüz simülasyon sonucu bulunmuyor.")
            return
        
        # results klasörünü oluştur ve yolu belirle
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Eğer output_prefix verilmemişse, results dizinindeki varsayılan yolu kullan
        if output_prefix is None:
            output_prefix = os.path.join(results_dir, 'sim_results')
        
        print(f"\nGrafikler şu klasöre kaydedilecek: {os.path.dirname(output_prefix)}")
        
        # 1. Toplanan Coin Grafiği
        self._create_bar_chart(
            "coins_collected", 
            "Average Number of Coins Collected by Algorithms",
            "Number of Coins Collected",
            f"{output_prefix}_coins.png"
        )
        
        # 2. Hayatta Kalma Süresi Grafiği
        self._create_bar_chart(
            "survival_steps", 
            "Average Survival Time by Algorithms",
            "Number of Steps",
            f"{output_prefix}_survival.png"
        )
        
        # 3. Kazanma Oranı Grafiği
        self._create_win_rate_chart(f"{output_prefix}_win_rate.png")
        
        # 4. Radar/Örümcek Grafiği - Algoritmaların Genel Performansı
        self._create_radar_chart(f"{output_prefix}_radar.png")
        
        # YENİ: 5. Isı Haritası Grafiği
        self._create_heatmap_visualization(f"{output_prefix}_heatmap.png")
        
        # YENİ: 6. Adım Zamanı Karşılaştırma Grafiği
        self._create_time_comparison_chart(f"{output_prefix}_step_time.png")
        
        # YENİ: 7. Yol Takibi Görselleştirmesi
        self._create_path_visualization(f"{output_prefix}_path.png")
        
        print(f"\nGrafikler kaydedildi: {output_prefix}_*.png")
    
    def _create_bar_chart(self, metric, title, ylabel, filename):
        """Çubuk grafik oluşturur"""
        plt.figure(figsize=(14, 8))
        
        # Pac-Man algoritmalarını ayarla
        x = np.arange(len(self.pacman_algorithms))
        width = 0.2  # Çubuk genişliği
        
        # Hayalet algoritmaları için renkler
        colors = ['#ff6666', '#66b3ff', '#99ff99', '#ffcc99']
        
        # Her hayalet algoritması için çubuk ekle
        for i, ghost_algo in enumerate(self.ghost_algorithms):
            values = []
            
            for pacman_algo in self.pacman_algorithms:
                key = (pacman_algo, ghost_algo)
                if key in self.results[metric] and self.results[metric][key]:
                    values.append(np.mean(self.results[metric][key]))
                else:
                    values.append(0)
            
            offset = width * (i - len(self.ghost_algorithms)/2 + 0.5)
            plt.bar(x + offset, values, width, label=f'Ghost: {ghost_algo}', color=colors[i % len(colors)])
        
        # Grafik ayarları
        plt.xlabel('Pac-Man Algorithm')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(x, self.pacman_algorithms)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Y-ekseni sınırı
        if metric == "coins_collected":
            plt.ylim(0, self.num_coins * 1.1)
        
        # Kaydet
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def _create_win_rate_chart(self, filename):
        """Kazanma oranı grafiği oluşturur"""
        plt.figure(figsize=(14, 8))
        
        # Pac-Man algoritmalarını ayarla
        x = np.arange(len(self.pacman_algorithms))
        width = 0.2  # Çubuk genişliği
        
        # Hayalet algoritmaları için renkler
        colors = ['#ff6666', '#66b3ff', '#99ff99', '#ffcc99']
        
        # Her hayalet algoritması için çubuk ekle
        for i, ghost_algo in enumerate(self.ghost_algorithms):
            values = []
            
            for pacman_algo in self.pacman_algorithms:
                key = (pacman_algo, ghost_algo)
                if key in self.results["win_rate"] and key in self.results["total_trials"] and self.results["total_trials"][key] > 0:
                    win_rate = self.results["win_rate"][key] / self.results["total_trials"][key] * 100
                    values.append(win_rate)
                else:
                    values.append(0)
            
            offset = width * (i - len(self.ghost_algorithms)/2 + 0.5)
            plt.bar(x + offset, values, width, label=f'Ghost: {ghost_algo}', color=colors[i % len(colors)])
        
        # Grafik ayarları
        plt.xlabel('Pac-Man Algorithm')
        plt.ylabel('Winning Rate (%)')
        plt.title('Win Rate Comparison of Algorithms')
        plt.xticks(x, self.pacman_algorithms)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.ylim(0, 100)
        
        # Kaydet
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    def _create_radar_chart(self, filename):
        """Radar/Örümcek grafiği oluşturur"""
        # Her Pac-Man algoritması için ayrı bir radar grafiği oluştur
        for pacman_algo in self.pacman_algorithms:
            plt.figure(figsize=(10, 8))
            
            # Metrikler
            metrics = ['Coin Collection', 'Survival', 'Win Rate']
            num_metrics = len(metrics)
            
            # Açıları ayarla
            angles = np.linspace(0, 2*np.pi, num_metrics, endpoint=False).tolist()
            angles += angles[:1]  # Grafiği kapatmak için ilk açıyı tekrarla
            
            # Alt görsel oluştur
            ax = plt.subplot(111, polar=True)
            
            # Her hayalet algoritması için değerleri hesapla
            for ghost_algo in self.ghost_algorithms:
                key = (pacman_algo, ghost_algo)
                values = []
                
                # Coin toplama değeri (normalize edilmiş)
                if key in self.results["coins_collected"] and self.results["coins_collected"][key]:
                    avg_coins = np.mean(self.results["coins_collected"][key])
                    values.append(avg_coins / self.num_coins * 100)  # Yüzdelik değer
                else:
                    values.append(0)
                
                # Hayatta kalma değeri (normalize edilmiş)
                if key in self.results["survival_steps"] and self.results["survival_steps"][key]:
                    avg_steps = np.mean(self.results["survival_steps"][key])
                    values.append(min(100, avg_steps / self.max_steps * 100))  # Yüzdelik değer, maks. 100
                else:
                    values.append(0)
                
                # Kazanma oranı
                if key in self.results["win_rate"] and key in self.results["total_trials"] and self.results["total_trials"][key] > 0:
                    win_rate = self.results["win_rate"][key] / self.results["total_trials"][key] * 100
                    values.append(win_rate)
                else:
                    values.append(0)
                
                # Grafiği kapatmak için ilk değeri tekrarla
                values += values[:1]
                
                # Grafiği çiz
                ax.plot(angles, values, linewidth=2, label=f'Ghost: {ghost_algo}')
                ax.fill(angles, values, alpha=0.1)
            
            # Grafik ayarları
            ax.set_theta_offset(np.pi / 2)  # Başlangıç açısı (üst kısım)
            ax.set_theta_direction(-1)  # Saat yönünde
            
            # Etiketleri ayarla
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            
            # Y-ekseni sınırları
            ax.set_ylim(0, 100)
            
            # Izgara ve başlık ayarları
            ax.grid(True)
            plt.title(f'Performance Comparison of Pac-Man {pacman_algo} Algorithm', size=15)
            plt.legend(loc='upper right')
            
            # Dosya adındaki özel karakterleri düzelt
            safe_algo_name = pacman_algo.replace('*', '_star').replace('?', '_q').replace(':', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('\\', '_').replace('/', '_')
            
            # Kaydet
            plt.tight_layout()
            plt.savefig(f"{filename.split('.')[0]}_{safe_algo_name}.png")
            plt.close()
    
    # YENİ: Isı haritası görselleştirmesi
    def _create_heatmap_visualization(self, filename):
        """Her algoritma için konum ziyaret sıklığını gösteren ısı haritasını oluşturur"""
        if not self.position_heatmap:
            print("Isı haritası verisi yok.")
            return
        
        # Her algoritma için ayrı bir ısı haritası oluştur
        for algo, heatmap in self.position_heatmap.items():
            plt.figure(figsize=(12, 10))
            
            # Normalize et
            max_val = np.max(heatmap) if np.max(heatmap) > 0 else 1
            normalized_heatmap = heatmap / max_val
            
            # Isı haritasını oluştur
            plt.imshow(normalized_heatmap, cmap='hot', interpolation='nearest')
            plt.colorbar(label='Visit Frequency (Normalised)')
            
            # Labirent duvarlarını göster
            for y in range(len(self.maze)):
                for x in range(len(self.maze[0])):
                    if self.maze[y][x] == 1:  # Duvar
                        plt.scatter(x, y, color='blue', s=100, marker='s')
            
            # Grafik ayarları
            plt.title(f'{algo} Algorithm Location Visit Heat Map')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid(False)
            
            # Dosya adını düzenle
            safe_algo_name = algo.replace('*', '_star').replace('?', '_q').replace(':', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('\\', '_').replace('/', '_')
            
            # Kaydet
            plt.tight_layout()
            plt.savefig(f"{filename.split('.')[0]}_{safe_algo_name}.png")
            plt.close()
    
    # YENİ: Algoritmaların adım süresi karşılaştırması
    def _create_time_comparison_chart(self, filename):
        """Farklı algoritmaların adım başına ortalama süresini karşılaştıran grafik"""
        if not self.step_times:
            print("Adım süresi verisi yok.")
            return
        
        plt.figure(figsize=(12, 8))
        
        # Her algoritma için ortalama süre hesapla
        algorithms = []
        avg_times = []
        std_times = []
        
        for algo, times in sorted(self.step_times.items()):
            if times:
                algorithms.append(algo)
                avg_times.append(np.mean(times) * 1000)  # Milisaniyeye çevir
                std_times.append(np.std(times) * 1000)   # Standart sapma
        
        # Çubuk grafiği oluştur
        bars = plt.bar(algorithms, avg_times, yerr=std_times, capsize=10, 
                      color='skyblue', edgecolor='black', alpha=0.7)
        
        # En hızlı algoritmayı vurgula
        if avg_times:
            fastest_idx = np.argmin(avg_times)
            bars[fastest_idx].set_color('green')
            bars[fastest_idx].set_alpha(1.0)
        
        # Grafik ayarları
        plt.xlabel('Algorithm')
        plt.ylabel('Average Step Duration (ms)')
        plt.title('Comparison of Average Time per Step between Algorithms')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Y-ekseni logaritmik ölçek kullan (algoritmalar arasındaki fark büyükse)
        if max(avg_times) / min(avg_times) > 10:
            plt.yscale('log')
            plt.ylabel('Average Step Duration (ms, logarithmic scale)')
        
        # Değerleri çubukların üzerine ekle
        for i, v in enumerate(avg_times):
            plt.text(i, v + std_times[i] + max(avg_times) * 0.05, 
                   f'{v:.2f}ms', ha='center', va='bottom', fontweight='bold')
        
        # Kaydet
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
    
    # YENİ: Farklı algoritmalar için yol takibi görselleştirmesi
    def _create_path_visualization(self, filename):
        """Her algoritma için yol takibi görselleştirmesi oluşturur"""
        if not self.path_tracking:
            print("Yol takibi verisi yok.")
            return
        
        # Her algoritma için en uzun yollardan birini seç
        algorithm_to_longest_path = {}
        
        for (algo, trial), path in self.path_tracking.items():
            if algo not in algorithm_to_longest_path or len(path) > len(algorithm_to_longest_path[algo][1]):
                algorithm_to_longest_path[algo] = (trial, path)
        
        # Her algoritma için ayrı bir görselleştirme oluştur
        for algo, (trial, path) in algorithm_to_longest_path.items():
            if len(path) < 2:  # Anlamlı bir yol yoksa atla
                continue
                
            plt.figure(figsize=(12, 10))
            
            # Labirent duvarlarını çiz
            for y in range(len(self.maze)):
                for x in range(len(self.maze[0])):
                    if self.maze[y][x] == 1:  # Duvar
                        rect = plt.Rectangle((x-0.5, y-0.5), 1, 1, color='blue', alpha=0.7)
                        plt.gca().add_patch(rect)
            
            # Yolu gradyan renklerle çiz
            points = np.array([[x, y] for x, y in path])
            
            # Noktaları çiz
            plt.scatter(points[:,0], points[:,1], c=range(len(points)), 
                       cmap='viridis', alpha=0.5, s=10)
            
            # Yolu çiz (gradyan renkli)
            segments = np.array([np.array([points[i], points[i+1]]) for i in range(len(points)-1)])
            norm = plt.Normalize(0, len(segments))
            lc = LineCollection(segments, cmap='viridis', norm=norm)
            lc.set_array(np.array(range(len(segments))))
            lc.set_linewidth(2)
            plt.gca().add_collection(lc)
            plt.colorbar(lc, label='Step Order')
            
            # Başlangıç ve bitiş noktalarını işaretle
            plt.scatter(path[0][0], path[0][1], color='green', s=150, marker='o', 
                       label='Start', zorder=5)
            plt.scatter(path[-1][0], path[-1][1], color='red', s=150, marker='X', 
                       label='Finish', zorder=5)
            
            # Yön oklarını ekle
            arrow_indices = np.linspace(0, len(path)-2, min(20, len(path)-1), dtype=int)
            for i in arrow_indices:
                dx = path[i+1][0] - path[i][0]
                dy = path[i+1][1] - path[i][1]
                plt.arrow(path[i][0], path[i][1], dx*0.6, dy*0.6, 
                        head_width=0.2, head_length=0.3, fc='black', ec='black', zorder=4)
            
            # Grafik ayarları
            plt.title(f'{algo} Algorithm Path Tracking (Trial {trial+1})')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid(True, linestyle='--', alpha=0.3)
            plt.legend()
            
            # Grafiği kare yapıp eksen sınırlarını ayarla
            plt.axis('equal')
            plt.xlim(-1, self.grid_width+1)
            plt.ylim(-1, self.grid_height+1)
            
            # Dosya adını düzenle
            safe_algo_name = algo.replace('*', '_star').replace('?', '_q').replace(':', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('\\', '_').replace('/', '_')
            
            # Kaydet
            plt.tight_layout()
            plt.savefig(f"{filename.split('.')[0]}_{safe_algo_name}.png")
            plt.close()

def run_demo(num_trials=10, num_coins=30, max_steps=500):
    """Demo'yu çalıştırmak için yardımcı fonksiyon"""
    simulation = GameSimulation(max_steps=max_steps, num_trials=num_trials, num_coins=num_coins)
    simulation.run_all_simulations()
    simulation.print_summary()
    simulation.generate_visualizations()

if __name__ == "__main__":
    run_demo()