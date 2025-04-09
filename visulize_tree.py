import os
from graphviz import Source

def visualize_decision_tree(dot_file='pacman_decision_tree.dot', output_file='decision_tree.png'):
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