from demo import run_demo

if __name__ == "__main__":
    num_trials = 100    
    num_coins = 50     
    max_steps = 250    
    
    print("Pac-Man Algoritma Performans Karşılaştırması")
    print(f"Her kombinasyon için {num_trials} test, {num_coins} coin, en fazla {max_steps} adım")
    print("-" * 60)
    
    # Demo'yu çalıştır
    run_demo(num_trials=num_trials, num_coins=num_coins, max_steps=max_steps)