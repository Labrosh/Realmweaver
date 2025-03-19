# UI Implementation using PySide6 (Qt for Python)
# This is where we create our application window and all its components

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QApplication, 
    QFileDialog, QComboBox, QCheckBox, QSpinBox,
    QGroupBox, QTabWidget, QSlider, QSplitter
)
from PySide6.QtCore import Qt, QSettings

# These help us embed Matplotlib into our Qt window
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib
matplotlib.use('Qt5Agg')  # Set the backend before importing pyplot
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import patches

# Import our world generation and visualization modules
from world_generator import World, generate_world
from visualization import (
    visualize_world, visualize_world_multi,
    TERRAIN_MODE, ELEVATION_MODE, MOISTURE_MODE, TEMPERATURE_MODE,
    TERRAIN_COLORS
)

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
        
        # Initialize visualization options
        self.mode = TERRAIN_MODE
        self.show_rivers = True
        self.show_contours = False
        self.show_grid = False
        
    def plot_world(self, world, seed=None):
        """Updates the canvas with a new world map"""
        # Clear the figure completely to prevent shrinking
        self.fig.clear()
        
        # Create a new subplot with fixed spacing
        self.ax = self.fig.add_subplot(111)
        
        # Reset the margins
        self.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
        # Check if we have a World object or a legacy world grid
        if isinstance(world, World):
            # Use the new visualization system
            if self.mode == TERRAIN_MODE:
                # Create color grid for terrain visualization
                color_grid = np.zeros((world.size, world.size, 3))
                
                for i in range(world.size):
                    for j in range(world.size):
                        terrain = world.get_terrain_at(j, i)
                        color_hex = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                        color_grid[i, j] = mcolors.to_rgb(color_hex)
                
                self.ax.imshow(color_grid)
                
                # Create legend for terrain types
                legend_elements = []
                added_biomes = set()
                
                for i in range(world.size):
                    for j in range(world.size):
                        terrain = world.get_terrain_at(j, i)
                        if terrain and terrain not in added_biomes:
                            color_hex, label = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))
                            legend_elements.append(
                                patches.Rectangle((0, 0), 1, 1, facecolor=color_hex, label=label)
                            )
                            added_biomes.add(terrain)
                
                # Sort legend elements by label
                legend_elements.sort(key=lambda x: x.get_label())
                
                # Add legend with fixed position
                self.ax.legend(
                    handles=legend_elements,
                    loc='center left',
                    bbox_to_anchor=(1.02, 0.5),
                    title="Terrain Types"
                )
                
            elif self.mode == ELEVATION_MODE:
                # Show elevation map
                elevation_img = self.ax.imshow(world.elevation_map, cmap='terrain')
                self.fig.colorbar(elevation_img, ax=self.ax, shrink=0.8, label="Elevation")
                
            elif self.mode == MOISTURE_MODE:
                # Show moisture map
                moisture_img = self.ax.imshow(world.moisture_map, cmap='Blues')
                self.fig.colorbar(moisture_img, ax=self.ax, shrink=0.8, label="Moisture")
                
            elif self.mode == TEMPERATURE_MODE:
                # Show temperature map
                temp_img = self.ax.imshow(world.temperature_map, cmap='plasma')
                self.fig.colorbar(temp_img, ax=self.ax, shrink=0.8, label="Temperature")
            
            # Add rivers if requested
            if self.show_rivers and hasattr(world, 'river_map'):
                river_y, river_x = np.where(world.river_map)
                self.ax.scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
            
            # Add contour lines if requested
            if self.show_contours:
                contour_levels = np.linspace(0, 1, 11)  # 10 contour lines
                self.ax.contour(world.elevation_map, levels=contour_levels, colors='black', alpha=0.3)
            
        else:
            # Legacy visualization for backward compatibility
            size = len(world)
            color_grid = np.zeros((size, size, 3))
            
            for i in range(size):
                for j in range(size):
                    terrain = world[i][j]
                    color = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                    color_grid[i, j] = mcolors.to_rgb(color)
            
            self.ax.imshow(color_grid)
            
            # Add legend with fixed position
            legend_elements = [
                patches.Rectangle((0, 0), 1, 1, facecolor=color, label=label)
                for terrain, (color, label) in TERRAIN_COLORS.items()
            ]
            self.ax.legend(
                handles=legend_elements,
                loc='center left',
                bbox_to_anchor=(1.02, 0.5)
            )
        
        # Add grid if requested
        if self.show_grid:
            self.ax.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
        else:
            self.ax.grid(False)
        
        # Turn off axis
        self.ax.axis('off')
        
        # Set title
        title = f"Realmweaver - {self.mode.capitalize()} View"
        if seed is not None:
            title += f" (Seed: {seed})"
        self.ax.set_title(title)
        
        # Don't use tight_layout, use our fixed layout
        self.draw()
    
    def set_mode(self, mode):
        """Set the visualization mode"""
        self.mode = mode
    
    def set_show_rivers(self, show):
        """Set whether to show rivers"""
        self.show_rivers = show
    
    def set_show_contours(self, show):
        """Set whether to show contour lines"""
        self.show_contours = show
    
    def set_show_grid(self, show):
        """Set whether to show grid lines"""
        self.show_grid = show

# This is our main application window
class MainWindow(QMainWindow):
    """The main application window containing all our UI elements"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realmweaver")
        self.setMinimumSize(1000, 700)
        
        # Qt uses a layout system to organize widgets
        # First we need a central widget to hold everything
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create a splitter to separate controls from the map
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create tabs for different control groups
        tabs = QTabWidget()
        left_layout.addWidget(tabs)
        
        # World Generation Tab
        generation_tab = QWidget()
        generation_layout = QVBoxLayout(generation_tab)
        
        # Seed input
        seed_group = QGroupBox("World Seed")
        seed_layout = QVBoxLayout(seed_group)
        
        seed_input_layout = QHBoxLayout()
        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Enter seed (optional)")
        seed_input_layout.addWidget(QLabel("Seed:"))
        seed_input_layout.addWidget(self.seed_input)
        seed_layout.addLayout(seed_input_layout)
        
        generation_layout.addWidget(seed_group)
        
        # World Size
        size_group = QGroupBox("World Size")
        size_layout = QVBoxLayout(size_group)
        
        size_input_layout = QHBoxLayout()
        self.size_input = QSpinBox()
        self.size_input.setRange(20, 200)
        self.size_input.setValue(100)
        self.size_input.setSingleStep(10)
        size_input_layout.addWidget(QLabel("Size:"))
        size_input_layout.addWidget(self.size_input)
        size_layout.addLayout(size_input_layout)
        
        generation_layout.addWidget(size_group)
        
        # Generate button
        self.generate_btn = QPushButton("Generate New World")
        self.generate_btn.clicked.connect(self.generate_new_world)
        generation_layout.addWidget(self.generate_btn)
        
        # Add stretch to push controls to the top
        generation_layout.addStretch()
        
        # Visualization Tab
        visualization_tab = QWidget()
        visualization_layout = QVBoxLayout(visualization_tab)
        
        # Visualization mode
        mode_group = QGroupBox("Visualization Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Terrain", TERRAIN_MODE)
        self.mode_combo.addItem("Elevation", ELEVATION_MODE)
        self.mode_combo.addItem("Moisture", MOISTURE_MODE)
        self.mode_combo.addItem("Temperature", TEMPERATURE_MODE)
        self.mode_combo.currentIndexChanged.connect(self.update_visualization)
        mode_layout.addWidget(self.mode_combo)
        
        visualization_layout.addWidget(mode_group)
        
        # Visualization options
        options_group = QGroupBox("Display Options")
        options_layout = QVBoxLayout(options_group)
        
        self.rivers_check = QCheckBox("Show Rivers")
        self.rivers_check.setChecked(True)
        self.rivers_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.rivers_check)
        
        self.contours_check = QCheckBox("Show Contour Lines")
        self.contours_check.setChecked(False)
        self.contours_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.contours_check)
        
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(False)
        self.grid_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.grid_check)
        
        visualization_layout.addWidget(options_group)
        
        # Multi-view button
        self.multi_view_btn = QPushButton("Show Multi-View")
        self.multi_view_btn.clicked.connect(self.show_multi_view)
        visualization_layout.addWidget(self.multi_view_btn)
        
        # Add stretch to push controls to the top
        visualization_layout.addStretch()
        
        # Export Tab
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        
        # Save map button
        self.save_btn = QPushButton("Save Map as Image")
        self.save_btn.clicked.connect(self.save_map)
        export_layout.addWidget(self.save_btn)
        
        # Add stretch to push controls to the top
        export_layout.addStretch()
        
        # Add tabs to the tab widget
        tabs.addTab(generation_tab, "Generation")
        tabs.addTab(visualization_tab, "Visualization")
        tabs.addTab(export_tab, "Export")
        
        # Right panel for map display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add map canvas
        self.map_canvas = WorldMapCanvas(self, width=10, height=8)
        right_layout.addWidget(self.map_canvas)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (30% controls, 70% map)
        splitter.setSizes([300, 700])
        
        # Keep track of current world state
        self.current_world = None
        self.current_seed = None
        
        # Store references to multi-view figures
        self.multi_view_fig = None
        
        # Generate initial world on startup
        self.generate_new_world()
    
    def generate_new_world(self):
        """Creates a new world using the current settings"""
        # Get seed from input
        user_seed = self.seed_input.text().strip()
        
        # Always clear the seed input to ensure a new random seed is generated
        # if the user doesn't provide one
        if not user_seed:
            self.seed_input.clear()
        
        seed = user_seed if user_seed else None
        
        # Get world size
        size = self.size_input.value()
        
        # Create a new World object
        self.current_world = World(size=size, seed=seed)
        self.current_world.generate()
        self.current_seed = self.current_world.seed
        
        # Update the seed input with the used seed
        self.seed_input.setText(str(self.current_seed))
        
        # Update the visualization
        self.update_visualization()
    
    def update_visualization(self):
        """Updates the visualization based on current settings"""
        if self.current_world is None:
            return
        
        # Get visualization mode
        mode = self.mode_combo.currentData()
        self.map_canvas.set_mode(mode)
        
        # Get visualization options
        show_rivers = self.rivers_check.isChecked()
        show_contours = self.contours_check.isChecked()
        show_grid = self.grid_check.isChecked()
        
        self.map_canvas.set_show_rivers(show_rivers)
        self.map_canvas.set_show_contours(show_contours)
        self.map_canvas.set_show_grid(show_grid)
        
        # Update the map
        self.map_canvas.plot_world(self.current_world, self.current_seed)
    
    def show_multi_view(self):
        """Shows a multi-panel visualization of the current world"""
        if self.current_world is None:
            return
        
        # Close previous multi-view figure if it exists
        if self.multi_view_fig is not None:
            plt.close(self.multi_view_fig)
        
        # Show the multi-view visualization
        self.multi_view_fig = visualize_world_multi(self.current_world, self.current_seed)
    
    def save_map(self):
        """Opens a file dialog and saves the current map as an image"""
        if self.current_world is None:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Map",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if filename:
            # Save the current view
            self.map_canvas.figure.savefig(
                filename,
                bbox_inches='tight',
                dpi=300
            )
    
    def closeEvent(self, event):
        """Handle window close event to clean up resources"""
        # Close any open matplotlib figures
        plt.close('all')
        super().closeEvent(event)

# This part only runs if we run this file directly
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
