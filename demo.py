import pygame
import time
import numpy as np
import matplotlib.pyplot as plt
from game import Game, GameState
from collections import defaultdict

class GameSimulation:
    """Pac-Man oyunu simülasyonu için arka planda çalışan sınıf"""
    
    def __init__(self, max_steps=1000, num_trials=10, num_coins=30):
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
        
        # Oyunu çalıştır
        while steps_taken < self.max_steps:
            # Olayları işle (çıkış kontrolü için)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
            
            # Adım sayısını artır
            steps_taken += 1
            
            # Oyun mantığını güncelle
            game.update_pacman()
            game.update_ghosts()
            
            # Coin sayısını takip et
            coins_collected = game.score
            
            # Oyun durumunu kontrol et
            if game.state == GameState.GAME_OVER:
                break  # Hayalet yakaladı
            elif game.state == GameState.GAME_WON:
                game_won = True
                break  # Tüm coinler toplandı
        
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
    
    def generate_visualizations(self, output_prefix="sim_results"):
        """Sonuçları görselleştirir ve kaydeder"""
        if not self.results["total_trials"]:
            print("Henüz simülasyon sonucu bulunmuyor.")
            return
        
        # 1. Toplanan Coin Grafiği
        self._create_bar_chart(
            "coins_collected", 
            "Algoritmalara Göre Ortalama Toplanan Coin Sayısı",
            "Toplanan Coin Sayısı",
            f"{output_prefix}_coins.png"
        )
        
        # 2. Hayatta Kalma Süresi Grafiği
        self._create_bar_chart(
            "survival_steps", 
            "Algoritmalara Göre Ortalama Hayatta Kalma Süresi",
            "Adım Sayısı",
            f"{output_prefix}_survival.png"
        )
        
        # 3. Kazanma Oranı Grafiği
        self._create_win_rate_chart(f"{output_prefix}_win_rate.png")
        
        # 4. Radar/Örümcek Grafiği - Algoritmaların Genel Performansı
        self._create_radar_chart(f"{output_prefix}_radar.png")
        
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
        plt.xlabel('Pac-Man Algoritması')
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
        plt.xlabel('Pac-Man Algoritması')
        plt.ylabel('Kazanma Oranı (%)')
        plt.title('Algoritmalara Göre Kazanma Oranı')
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
            metrics = ['Coin Toplama', 'Hayatta Kalma', 'Kazanma Oranı']
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
            plt.title(f'Pac-Man {pacman_algo} Algoritmasının Performans Karşılaştırması', size=15)
            plt.legend(loc='upper right')
            
            # Kaydet
            plt.tight_layout()
            plt.savefig(f"{filename.split('.')[0]}_{pacman_algo}.png")
            plt.close()

def run_demo(num_trials=10, num_coins=30, max_steps=500):
    """Demo'yu çalıştırmak için yardımcı fonksiyon"""
    simulation = GameSimulation(max_steps=max_steps, num_trials=num_trials, num_coins=num_coins)
    simulation.run_all_simulations()
    simulation.print_summary()
    simulation.generate_visualizations()

if __name__ == "__main__":
    run_demo()