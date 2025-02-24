# UI Implementation using PySide6 (Qt for Python)
# This is where we create our application window and all its components
# PySide6 is a framework for making desktop applications - it's like tkinter but more modern

# We need these Qt components:
# - QMainWindow: The main application window
# - QWidget: Base class for all UI elements
# - QVBoxLayout/QHBoxLayout: For arranging elements vertically/horizontally
# - Other widgets like buttons, labels, etc.
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLineEdit, QLabel, QApplication, 
                              QFileDialog)
from PySide6.QtCore import Qt

# These help us embed Matplotlib into our Qt window
# FigureCanvasQTAgg is the widget that displays the map
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib
matplotlib.use('Qt5Agg')  # Set the backend before importing pyplot
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import patches
from world_generator import generate_world
from visualization import TERRAIN_COLORS, visualize_world  # Add this import

# This class handles drawing our world map inside the Qt window
class WorldMapCanvas(FigureCanvasQTAgg):
    """A Qt widget that displays our world map using Matplotlib"""
    def __init__(self, parent=None, width=8, height=6):
        self.fig = Figure(figsize=(width, height))
        super().__init__(self.fig)
        self.setParent(parent)
        # Set fixed size to prevent resizing jumps
        self.fig.set_size_inches(width, height, forward=True)
        # Pre-create the subplot with fixed spacing
        self.ax = self.fig.add_subplot(111)
        # Set fixed margins
        self.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
    def plot_world(self, world, seed=None):
        """Updates the canvas with a new world map"""
        self.ax.clear()
        
        size = len(world)
        color_grid = np.zeros((size, size, 3))
        
        for i in range(size):
            for j in range(size):
                terrain = world[i][j]
                color = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                color_grid[i, j] = mcolors.to_rgb(color)
        
        self.ax.imshow(color_grid)
        self.ax.axis('off')
        
        # Add legend with fixed position
        legend_elements = [patches.Rectangle((0,0),1,1, facecolor=color, label=label)
                         for terrain, (color, label) in TERRAIN_COLORS.items()]
        self.ax.legend(handles=legend_elements, loc='center left', 
                      bbox_to_anchor=(1.02, 0.5))
        
        title = "Realmweaver - Procedural World"
        if seed is not None:
            title += f" (Seed: {seed})"
        self.ax.set_title(title)
        
        # Don't use tight_layout, use our fixed layout
        self.draw()

# This is our main application window
class MainWindow(QMainWindow):
    """The main application window containing all our UI elements"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realmweaver")
        self.setMinimumSize(800, 600)
        
        # Qt uses a layout system to organize widgets
        # First we need a central widget to hold everything
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # VBoxLayout arranges things vertically from top to bottom
        layout = QVBoxLayout(central_widget)
        
        # Create the seed input area with label
        # HBoxLayout arranges things horizontally left to right
        seed_layout = QHBoxLayout()
        self.seed_input = QLineEdit()  # Text input field
        self.seed_input.setPlaceholderText("Enter seed (optional)")
        seed_layout.addWidget(QLabel("Seed:"))
        seed_layout.addWidget(self.seed_input)
        layout.addLayout(seed_layout)
        
        # Button that triggers world generation
        self.generate_btn = QPushButton("Generate World")
        # Connect the button's click signal to our generation method
        self.generate_btn.clicked.connect(self.generate_new_world)
        layout.addWidget(self.generate_btn)
        
        # Add our custom map display widget
        self.map_canvas = WorldMapCanvas(self)
        layout.addWidget(self.map_canvas)
        
        # Button for saving the map as an image
        self.save_btn = QPushButton("Save Map")
        self.save_btn.clicked.connect(self.save_map)
        layout.addWidget(self.save_btn)
        
        # Keep track of current world state
        self.current_world = None
        self.current_seed = None
        # Generate initial world on startup
        self.generate_new_world()
    
    def generate_new_world(self):
        """Creates a new world using the seed from the input field"""
        user_seed = self.seed_input.text().strip()
        # Only update the seed input text if the user didn't provide one
        self.current_world, self.current_seed = generate_world(seed=user_seed if user_seed else None)
        if not user_seed:  # Only update the displayed seed if user didn't provide one
            self.seed_input.setText(str(self.current_seed))
        self.map_canvas.plot_world(self.current_world, self.current_seed)
    
    def save_map(self):
        """Opens a file dialog and saves the current map as an image"""
        if self.current_world is not None:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Map",
                "",
                "PNG Files (*.png);;All Files (*)"
            )
            if filename:
                self.map_canvas.figure.savefig(filename, 
                                             bbox_inches='tight', 
                                             dpi=300)

# This part only runs if we run this file directly
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
