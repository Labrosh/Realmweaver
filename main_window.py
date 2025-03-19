# UI Implementation using PySide6 (Qt for Python)
# This is where we create our application window and all its components

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QApplication,
    QFileDialog, QComboBox, QCheckBox, QSpinBox,
    QGroupBox, QTabWidget, QSlider, QSplitter,
    QSizePolicy, QScrollArea, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSettings, QSize

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
        
        # Enable resizing with the window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
        # Pre-create the subplot with fixed spacing
        self.ax = self.fig.add_subplot(111)
        
        # Set margins
        self.fig.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
        
        # Initialize visualization options
        self.mode = TERRAIN_MODE
        self.show_rivers = True
        self.show_contours = False
        self.show_grid = False
        
    def resizeEvent(self, event):
        """Handle resize events to update the figure size"""
        super().resizeEvent(event)
        # Update figure size when widget is resized
        self.fig.tight_layout(pad=1.08, rect=[0.1, 0.1, 0.85, 0.9])
        
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
        
        # Apply stylesheet for a more modern look
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                background-color: white;
                color: black;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cccccc;
                background-color: white;
                color: black;
            }
            QComboBox::item {
                background-color: white;
                color: black;
            }
            QComboBox::item:selected {
                background-color: #4a86e8;
                color: white;
            }
            QComboBox::item:hover {
                background-color: #e0e0e0;
                color: black;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 2px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom-color: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #f8f8f8;
                border-bottom-color: #f8f8f8;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #cccccc;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
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
        left_panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        left_panel.setMinimumWidth(300)  # Set a minimum width for the left panel
        left_layout = QVBoxLayout(left_panel)
        
        # Create a scroll area for the controls to handle small screens
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create a widget to hold the tabs
        tabs_container = QWidget()
        tabs_container_layout = QVBoxLayout(tabs_container)
        tabs_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tabs for different control groups
        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tabs_container_layout.addWidget(tabs)
        
        # Set the tabs container as the scroll area widget
        scroll_area.setWidget(tabs_container)
        left_layout.addWidget(scroll_area)
        
        # World Generation Tab
        generation_tab = QWidget()
        generation_layout = QVBoxLayout(generation_tab)
        
        # Seed input
        seed_group = QGroupBox("World Seed")
        seed_layout = QVBoxLayout(seed_group)
        
        seed_input_layout = QHBoxLayout()
        
        seed_label = QLabel("Seed:")
        seed_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.seed_input = QLineEdit()
        self.seed_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.seed_input.setMinimumHeight(30)
        self.seed_input.setPlaceholderText("Enter seed (optional)")
        
        seed_input_layout.addWidget(seed_label)
        seed_input_layout.addWidget(self.seed_input)
        seed_layout.addLayout(seed_input_layout)
        
        generation_layout.addWidget(seed_group)
        
        # World Size
        size_group = QGroupBox("World Size")
        size_layout = QVBoxLayout(size_group)
        
        size_input_layout = QHBoxLayout()
        
        size_label = QLabel("Size:")
        size_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.size_input = QSpinBox()
        self.size_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.size_input.setMinimumHeight(30)
        self.size_input.setRange(20, 200)
        self.size_input.setValue(100)
        self.size_input.setSingleStep(10)
        
        size_input_layout.addWidget(size_label)
        size_input_layout.addWidget(self.size_input)
        size_layout.addLayout(size_input_layout)
        
        generation_layout.addWidget(size_group)
        
        # Generate button
        self.generate_btn = QPushButton("Generate New World")
        self.generate_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.generate_btn.setMinimumHeight(40)  # Make buttons taller
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
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.mode_combo.setMinimumHeight(30)
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
        self.rivers_check.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.rivers_check.setMinimumHeight(30)
        self.rivers_check.setChecked(True)
        self.rivers_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.rivers_check)
        
        self.contours_check = QCheckBox("Show Contour Lines")
        self.contours_check.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.contours_check.setMinimumHeight(30)
        self.contours_check.setChecked(False)
        self.contours_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.contours_check)
        
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.grid_check.setMinimumHeight(30)
        self.grid_check.setChecked(False)
        self.grid_check.stateChanged.connect(self.update_visualization)
        options_layout.addWidget(self.grid_check)
        
        visualization_layout.addWidget(options_group)
        
        # Multi-view button
        self.multi_view_btn = QPushButton("Show Multi-View")
        self.multi_view_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.multi_view_btn.setMinimumHeight(40)
        self.multi_view_btn.clicked.connect(self.show_multi_view)
        visualization_layout.addWidget(self.multi_view_btn)
        
        # Add stretch to push controls to the top
        visualization_layout.addStretch()
        
        # Export Tab
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        
        # Save map button
        self.save_btn = QPushButton("Save Map as Image")
        self.save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.save_btn.setMinimumHeight(40)
        self.save_btn.clicked.connect(self.save_map)
        export_layout.addWidget(self.save_btn)
        
        # Add stretch to push controls to the top
        export_layout.addStretch()
        
        # Biome Selection Tab
        biome_tab = QWidget()
        biome_layout = QVBoxLayout(biome_tab)
        
        # Biome presets group
        biome_presets_group = QGroupBox("Biome Presets")
        biome_presets_layout = QVBoxLayout(biome_presets_group)
        
        # Biome preset selection
        self.biome_preset_combo = QComboBox()
        self.biome_preset_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.biome_preset_combo.setMinimumHeight(30)
        self.biome_preset_combo.addItem("Default", "default")
        self.biome_preset_combo.addItem("Arid (More Deserts)", "arid")
        self.biome_preset_combo.addItem("Lush (More Forests)", "lush")
        self.biome_preset_combo.addItem("Mountainous", "mountainous")
        self.biome_preset_combo.addItem("Archipelago (More Islands)", "archipelago")
        self.biome_preset_combo.addItem("Polar (Cold Climate)", "polar")
        self.biome_preset_combo.addItem("Tropical (Warm Climate)", "tropical")
        self.biome_preset_combo.currentIndexChanged.connect(self.update_biome_preset)
        
        preset_label = QLabel("Select Biome Preset:")
        preset_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        biome_presets_layout.addWidget(preset_label)
        biome_presets_layout.addWidget(self.biome_preset_combo)
        
        biome_layout.addWidget(biome_presets_group)
        
        # Custom biome weights group
        biome_weights_group = QGroupBox("Custom Biome Weights")
        biome_weights_layout = QVBoxLayout(biome_weights_group)
        
        # Create a list widget for biome weights
        self.biome_list = QListWidget()
        self.biome_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.biome_list.setMinimumHeight(200)  # Ensure the list is tall enough
        self.biome_list.setSelectionMode(QListWidget.SingleSelection)
        
        # Add biomes to the list
        biome_categories = [
            ("Water Biomes", ["DEEP_OCEAN", "OCEAN", "SHALLOW_WATER", "RIVER"]),
            ("Shore Biomes", ["BEACH", "ROCKY_SHORE"]),
            ("Lowland Biomes", ["DESERT", "SAVANNA", "GRASSLAND", "MARSH", "SWAMP", "FOREST", "RAINFOREST", "JUNGLE"]),
            ("Highland Biomes", ["SHRUBLAND", "HILLS", "HIGHLAND_FOREST"]),
            ("Mountain Biomes", ["MOUNTAIN", "MOUNTAIN_FOREST", "ALPINE"]),
            ("Peak Biomes", ["SNOW_CAP", "VOLCANO"])
        ]
        
        # Add biomes to the list with categories
        for category, biomes in biome_categories:
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.ItemIsEnabled)
            self.biome_list.addItem(category_item)
            
            for biome in biomes:
                biome_name = biome
                biome_item = QListWidgetItem(f"  {biome_name}")
                biome_item.setData(Qt.UserRole, biome_name)
                self.biome_list.addItem(biome_item)
        
        biome_weights_layout.addWidget(QLabel("Select biomes to customize:"))
        biome_weights_layout.addWidget(self.biome_list)
        
        # Biome weight slider
        self.biome_weight_slider = QSlider(Qt.Horizontal)
        self.biome_weight_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.biome_weight_slider.setMinimumHeight(40)
        self.biome_weight_slider.setRange(0, 200)
        self.biome_weight_slider.setValue(100)
        self.biome_weight_slider.setTickPosition(QSlider.TicksBelow)
        self.biome_weight_slider.setTickInterval(25)
        self.biome_weight_slider.setEnabled(False)  # Disabled until a biome is selected
        
        self.biome_weight_label = QLabel("Weight: 100%")
        self.biome_weight_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.biome_weight_label.setMinimumHeight(30)
        self.biome_weight_label.setAlignment(Qt.AlignCenter)  # Center the text
        
        # Connect slider to update label
        self.biome_weight_slider.valueChanged.connect(self.update_biome_weight_label)
        
        # Connect list selection to enable/disable slider
        self.biome_list.itemSelectionChanged.connect(self.biome_selection_changed)
        
        biome_weights_layout.addWidget(self.biome_weight_label)
        biome_weights_layout.addWidget(self.biome_weight_slider)
        
        biome_layout.addWidget(biome_weights_group)
        
        # Apply biome settings button
        self.apply_biome_btn = QPushButton("Apply Biome Settings")
        self.apply_biome_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.apply_biome_btn.setMinimumHeight(40)
        self.apply_biome_btn.clicked.connect(self.apply_biome_settings)
        biome_layout.addWidget(self.apply_biome_btn)
        
        # Add stretch to push controls to the top
        biome_layout.addStretch()
        
        # Add tabs to the tab widget
        tabs.addTab(generation_tab, "Generation")
        tabs.addTab(biome_tab, "Biomes")
        tabs.addTab(visualization_tab, "Visualization")
        tabs.addTab(export_tab, "Export")
        
        # Right panel for map display
        right_panel = QWidget()
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        
        # Add map canvas
        self.map_canvas = WorldMapCanvas(self, width=10, height=8)
        self.map_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        
        # Initialize biome weights
        self.biome_weights = {}
        
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
        
        # Get biome weights if they exist
        biome_weights = getattr(self, 'biome_weights', {})
        
        # Create a new World object
        self.current_world = World(size=size, seed=seed)
        
        # Pass biome weights to the world generator if they exist
        if biome_weights:
            self.current_world.set_biome_weights(biome_weights)
            
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
    
    def update_biome_preset(self):
        """Updates the biome weights based on the selected preset"""
        preset = self.biome_preset_combo.currentData()
        
        # Reset all biome weights
        for i in range(self.biome_list.count()):
            item = self.biome_list.item(i)
            if item.flags() & Qt.ItemIsSelectable:  # Skip category headers
                biome_name = item.data(Qt.UserRole)
                item.setData(Qt.UserRole + 1, 100)  # Reset to 100%
                item.setText(f"  {biome_name}")  # Reset text
        
        # Apply preset-specific weights
        if preset == "arid":
            self._set_biome_weight("DESERT", 200)
            self._set_biome_weight("SAVANNA", 150)
            self._set_biome_weight("GRASSLAND", 120)
            self._set_biome_weight("FOREST", 50)
            self._set_biome_weight("RAINFOREST", 30)
            self._set_biome_weight("JUNGLE", 20)
            self._set_biome_weight("MARSH", 40)
            self._set_biome_weight("SWAMP", 30)
        elif preset == "lush":
            self._set_biome_weight("FOREST", 200)
            self._set_biome_weight("RAINFOREST", 180)
            self._set_biome_weight("JUNGLE", 150)
            self._set_biome_weight("GRASSLAND", 120)
            self._set_biome_weight("DESERT", 30)
            self._set_biome_weight("SAVANNA", 50)
            self._set_biome_weight("MARSH", 120)
            self._set_biome_weight("SWAMP", 100)
        elif preset == "mountainous":
            self._set_biome_weight("MOUNTAIN", 200)
            self._set_biome_weight("MOUNTAIN_FOREST", 180)
            self._set_biome_weight("ALPINE", 150)
            self._set_biome_weight("SNOW_CAP", 130)
            self._set_biome_weight("HILLS", 120)
            self._set_biome_weight("HIGHLAND_FOREST", 100)
            self._set_biome_weight("GRASSLAND", 50)
        elif preset == "archipelago":
            self._set_biome_weight("OCEAN", 200)
            self._set_biome_weight("DEEP_OCEAN", 180)
            self._set_biome_weight("SHALLOW_WATER", 150)
            self._set_biome_weight("BEACH", 120)
            self._set_biome_weight("ROCKY_SHORE", 100)
        elif preset == "polar":
            self._set_biome_weight("SNOW_CAP", 200)
            self._set_biome_weight("ALPINE", 180)
            self._set_biome_weight("MOUNTAIN", 150)
            self._set_biome_weight("FOREST", 50)
            self._set_biome_weight("JUNGLE", 10)
            self._set_biome_weight("DESERT", 20)
        elif preset == "tropical":
            self._set_biome_weight("JUNGLE", 200)
            self._set_biome_weight("RAINFOREST", 180)
            self._set_biome_weight("SWAMP", 150)
            self._set_biome_weight("MARSH", 130)
            self._set_biome_weight("SAVANNA", 120)
            self._set_biome_weight("DESERT", 100)
            self._set_biome_weight("SNOW_CAP", 10)
            self._set_biome_weight("ALPINE", 20)
        
        # Update the UI if a biome is selected
        self.biome_selection_changed()
    
    def _set_biome_weight(self, biome_name, weight):
        """Helper method to set the weight for a specific biome"""
        for i in range(self.biome_list.count()):
            item = self.biome_list.item(i)
            if item.flags() & Qt.ItemIsSelectable:  # Skip category headers
                if item.data(Qt.UserRole) == biome_name:
                    item.setData(Qt.UserRole + 1, weight)
                    # Update the item text to show the weight
                    item.setText(f"  {biome_name} ({weight}%)")
                    break
    
    def biome_selection_changed(self):
        """Handle biome selection changes in the list"""
        selected_items = self.biome_list.selectedItems()
        
        if selected_items and selected_items[0].flags() & Qt.ItemIsSelectable:
            # Enable the slider and set its value
            self.biome_weight_slider.setEnabled(True)
            
            # Get the current weight or default to 100
            current_weight = selected_items[0].data(Qt.UserRole + 1)
            if current_weight is None:
                current_weight = 100
                
            self.biome_weight_slider.setValue(current_weight)
            self.biome_weight_label.setText(f"Weight: {current_weight}%")
        else:
            # Disable the slider if no biome is selected
            self.biome_weight_slider.setEnabled(False)
            self.biome_weight_label.setText("Weight: N/A")
    
    def update_biome_weight_label(self):
        """Update the label when the slider value changes"""
        value = self.biome_weight_slider.value()
        self.biome_weight_label.setText(f"Weight: {value}%")
        
        # Update the selected biome's weight
        selected_items = self.biome_list.selectedItems()
        if selected_items and selected_items[0].flags() & Qt.ItemIsSelectable:
            biome_name = selected_items[0].data(Qt.UserRole)
            selected_items[0].setData(Qt.UserRole + 1, value)
            selected_items[0].setText(f"  {biome_name} ({value}%)")
    
    def apply_biome_settings(self):
        """Apply the biome settings and regenerate the world"""
        # Collect all biome weights
        biome_weights = {}
        for i in range(self.biome_list.count()):
            item = self.biome_list.item(i)
            if item.flags() & Qt.ItemIsSelectable:  # Skip category headers
                biome_name = item.data(Qt.UserRole)
                weight = item.data(Qt.UserRole + 1)
                if weight is not None:
                    biome_weights[biome_name] = weight / 100.0  # Convert to 0.0-2.0 range
        
        # Store the biome weights
        self.biome_weights = biome_weights
        
        # Regenerate the world with the new biome settings
        self.generate_new_world()
    
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
