import os
from graphviz import Source

def visualize_decision_tree(dot_file=None, output_file=None):
    """
    Karar ağacı görselini oluşturur
    
    Parameters:
    - dot_file: .dot dosyası için yol (belirtilmezse otomatik bulunur)
    - output_file: Çıktı resmi için yol (belirtilmezse otomatik oluşturulur)
    """
    # Proje kök dizinini bul
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Varsayılan dosya yollarını ayarla
    if dot_file is None:
        dot_file = os.path.join(base_dir, 'dt-model', 'pacman_decision_tree.dot')
    
    if output_file is None:
        results_dir = os.path.join(base_dir, 'results')
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, 'decision_tree.png')
    
    # Check if the dot file exists
    if not os.path.exists(dot_file):
        print(f"Error: {dot_file} not found!")
        print("Run the game with Decision Tree algorithm first to generate the model.")
        return False
    
    try:
        # Create a graphviz Source object
        s = Source.from_file(dot_file)
        
        # Render the graph
        s.render(filename=output_file.split('.')[0], format='png', cleanup=True)
        print(f"Decision tree visualization saved as {output_file}")
        return True
    except Exception as e:
        print(f"Error visualizing decision tree: {e}")
        print("Make sure you have Graphviz installed: https://graphviz.org/download/")
        return False

if __name__ == "__main__":
    visualize_decision_tree()