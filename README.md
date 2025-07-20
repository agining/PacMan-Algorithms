# Pac-Man with Multiple AI Search Algorithms

Bu proje, farklı yapay zeka algoritmalarını karşılaştırmak için geliştirilmiş gelişmiş bir Pac-Man oyunudur. Pac-Man ve hayaletler için çeşitli arama algoritmaları kullanarak, algoritmaların performansını görsel olarak analiz edebilirsiniz.

## Özellikler

### Desteklenen AI Algoritmaları
- **A\* (A-Star)** - Optimal yol bulma algoritması
- **BFS (Breadth-First Search)** - Genişlik öncelikli arama
- **DFS (Depth-First Search)** - Sınırlı derinlikli arama  
- **Genetic Algorithm** - Evrimsel optimizasyon
- **Decision Tree** - Makine öğrenmesi tabanlı karar verme
- **Kullanıcı Kontrolü** - Manuel oyun modu

### Analiz ve Görselleştirme
- Gerçek zamanlı performans karşılaştırması
- Isı haritası görselleştirmesi (algoritmaların hareket kalıpları)
- Yol takibi animasyonları
- İstatistiksel analiz raporları
- Karar ağacı görselleştirmesi
- Algoritma hız karşılaştırması

### Oyun Modu Seçenekleri
- Pac-Man ve hayaletler için bağımsız algoritma seçimi
- Kullanıcı kontrollü Pac-Man modu
- Otomatik simülasyon ve benchmark testleri
- Çoklu coin toplama hedefleri

## Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

**Gerekli Kütüphaneler:**
- `pygame >= 2.0.0` - Oyun motoru
- `numpy >= 1.20.0` - Sayısal hesaplamalar
- `scikit-learn >= 0.24.0` - Makine öğrenmesi
- `matplotlib >= 3.4.0` - Grafik çizimi
- `graphviz >= 0.16` - Karar ağacı görselleştirme

## Kullanım

### Temel Oyun
```bash
python main.py
```

1. **Algoritma Seçimi**: Menüden Pac-Man ve hayaletler için algoritma seçin
2. **Oyunu Başlatın**: "Start" butonuna tıklayın
3. **Kullanıcı Kontrolü**: "Kullanıcı" seçeneği ile manuel oynayın (ok tuşları)

### Performans Testi
```bash
# Hızlı test
python demo/run_benchmark.py

# Özelleştirilmiş test
python -c "from demo.demo import run_demo; run_demo(num_trials=5, num_coins=20, max_steps=300)"
```

### Karar Ağacı Görselleştirme
```bash
python demo/visualize_tree.py
```

## Proje Yapısı

```
YAP-441/
├── main.py                    # Ana oyun giriş noktası
├── requirements.txt           # Gerekli kütüphaneler
├── README.md                 # Bu dosya
│
├── game/                     # Oyun motoru
│   ├── __init__.py
│   ├── game.py              # Ana oyun mantığı ve döngüsü
│   └── character.py         # Karakter, coin ve buton sınıfları
│
├── algorithms/              # AI Algoritmaları
│   ├── __init__.py
│   ├── algorithm.py         # Temel algoritma sınıfı
│   ├── astar.py            # A* algoritması
│   ├── bfs.py              # BFS algoritması
│   ├── dfs.py              # DFS algoritması
│   ├── genetic_algorithm.py # Genetik algoritma
│   └── decision_tree.py    # Karar ağacı algoritması
│
├── demo/                   # Analiz ve test araçları
│   ├── __init__.py
│   ├── demo.py            # Simülasyon ve benchmark
│   ├── run_benchmark.py   # Hızlı benchmark testi
│   └── visualize_tree.py  # Karar ağacı görselleştirme
│
├── dt-model/              # Karar ağacı modeli (otomatik oluşur)
│   ├── pacman_decision_tree.pkl
│   ├── pacman_decision_tree.dot
│   └── pacman_training_data.csv
│
└── results/               # Analiz sonuçları (otomatik oluşur)
    ├── sim_results_*.png  # Performans grafikleri
    ├── decision_tree.png  # Karar ağacı görseli
    └── *.png              # Diğer görselleştirmeler
```

## Algoritma Detayları

### A* (A-Star)
- **Kullanım**: Optimal yol bulma
- **Avantaj**: Garantili en kısa yol
- **Dezavantaj**: Hesaplama yoğun

### BFS (Breadth-First Search)
- **Kullanım**: Tüm seçenekleri eşit araştırma
- **Avantaj**: Optimal çözüm garanti
- **Dezavantaj**: Bellek yoğun

### DFS (Depth-First Search)
- **Kullanım**: Hızlı karar verme
- **Avantaj**: Düşük bellek kullanımı
- **Dezavantaj**: Optimal olmayabilir

### Genetik Algoritma
- **Kullanım**: Karmaşık optimizasyon
- **Avantaj**: Global optimuma yaklaşır
- **Dezavantaj**: Stokastik sonuçlar

### Karar Ağacı
- **Kullanım**: Öğrenme tabanlı kararlar
- **Avantaj**: Açıklanabilir AI
- **Dezavantaj**: Eğitim verisi gerekli

## Analiz Özellikleri

### Performans Metrikleri
- **Coin Toplama Oranı**: Her algoritmanın ortalama coin toplama sayısı
- **Hayatta Kalma Süresi**: Hayaletlerden ne kadar kaçabildiği
- **Kazanma Oranı**: Tüm coinleri toplama yüzdesi
- **Hesaplama Hızı**: Adım başına ortalama işlem süresi

### Görselleştirmeler
1. **Çubuk Grafikler**: Algoritma performans karşılaştırması
2. **Radar Grafikleri**: Çok boyutlu performans analizi
3. **Isı Haritaları**: Hareket kalıpları analizi
4. **Yol Takibi**: Algoritmaların seçtiği rotalar
5. **Karar Ağacı**: ML modelinin görsel temsili

## ⚙️ Yapılandırma

### Oyun Parametreleri
```python
# main.py içinde
SCREEN_WIDTH = 1200    # Ekran genişliği
SCREEN_HEIGHT = 900    # Ekran yüksekliği
CELL_SIZE = 40         # Hücre boyutu
FPS = 15              # Oyun hızı
```

### Benchmark Parametreleri
```python
# demo/run_benchmark.py içinde
num_trials = 1        # Test sayısı
num_coins = 25        # Coin sayısı
max_steps = 150       # Maksimum adım
```

### Algoritma Parametreleri
```python
# algorithms/genetic_algorithm.py
population_size = 50      # Popülasyon boyutu
chromosome_length = 20    # Kromozom uzunluğu
mutation_rate = 0.1       # Mutasyon oranı
generations = 10          # Evrim nesil sayısı

# algorithms/dfs.py
max_depth = 10           # Maksimum derinlik

# algorithms/decision_tree.py
max_depth = 5            # Ağaç derinliği
```

## 🎯 Kullanım Senaryoları

### 1. Eğitim Amaçlı
- AI algoritmaları öğretmek için
- Algoritma karşılaştırması yapmak için
- Görsel öğrenme materyali olarak

### 2. Araştırma Amaçlı
- Yeni algoritma geliştirmek için
- Performance benchmarking için
- AI davranış analizi için

### 3. Eğlence Amaçlı
- İnteraktif oyun oynamak için
- Farklı AI stratejilerini test etmek için



## 📈 Sonuçlar ve Analiz

Benchmark testleri şu klasörlerde saklanır:
- **Grafikler**: `results/sim_results_*.png`
- **Modeller**: `dt-model/`
- **CSV Verileri**: `dt-model/pacman_training_data.csv`



---

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**