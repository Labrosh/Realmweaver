# Code for displaying the world using matplotlib
# This file provides visualization functions for the generated world

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from world_generator import World, generate_world
from terrain_config import TERRAIN_COLORS, BIOMES, ELEVATION_THRESHOLDS, MOISTURE_THRESHOLDS

# Visualization modes
TERRAIN_MODE = "terrain"  # Show terrain/biome colors
ELEVATION_MODE = "elevation"  # Show elevation with a color gradient
MOISTURE_MODE = "moisture"  # Show moisture with a color gradient
TEMPERATURE_MODE = "temperature"  # Show temperature with a color gradient

# Create custom colormaps for different visualization modes
# Elevation colormap: deep blue -> green -> brown -> white
elevation_colors = [
    (0.0, (0, 0, 0.5)),      # Deep blue for deep ocean
    (0.2, (0, 0.4, 0.8)),    # Blue for ocean
    (0.3, (0.2, 0.6, 0.9)),  # Light blue for shallow water
    (0.33, (0.8, 0.8, 0.6)), # Tan for beaches
    (0.5, (0.2, 0.6, 0.2)),  # Green for lowlands
    (0.7, (0.6, 0.4, 0.2)),  # Brown for highlands
    (0.85, (0.5, 0.5, 0.5)), # Gray for mountains
    (1.0, (1.0, 1.0, 1.0))   # White for peaks
]

# Moisture colormap: tan -> green -> dark blue
moisture_colors = [
    (0.0, (0.8, 0.7, 0.4)),  # Tan for very dry
    (0.3, (0.6, 0.7, 0.4)),  # Light green for dry
    (0.5, (0.4, 0.7, 0.4)),  # Green for moderate
    (0.7, (0.3, 0.6, 0.5)),  # Dark green for wet
    (1.0, (0.2, 0.4, 0.6))   # Blue for very wet
]

# Temperature colormap: blue -> green -> yellow -> red
temperature_colors = [
    (0.0, (0.0, 0.0, 0.7)),  # Dark blue for very cold
    (0.2, (0.0, 0.4, 0.9)),  # Blue for cold
    (0.4, (0.0, 0.8, 0.8)),  # Cyan for cool
    (0.5, (0.0, 0.9, 0.2)),  # Green for moderate
    (0.6, (0.8, 0.9, 0.0)),  # Yellow-green for warm
    (0.8, (1.0, 0.6, 0.0)),  # Orange for hot
    (1.0, (0.9, 0.0, 0.0))   # Red for very hot
]

# Create the custom colormaps
ELEVATION_CMAP = LinearSegmentedColormap.from_list("elevation", elevation_colors)
MOISTURE_CMAP = LinearSegmentedColormap.from_list("moisture", moisture_colors)
TEMPERATURE_CMAP = LinearSegmentedColormap.from_list("temperature", temperature_colors)

def visualize_world(world, seed=None, mode=TERRAIN_MODE, save_path=None, show=True, 
                   show_rivers=True, show_contours=False, show_grid=False):
    """
    Creates a visualization of the generated world.
    
    Args:
        world: Either a World object or a legacy world grid
        seed: The seed used to generate the world
        mode: Visualization mode (terrain, elevation, moisture, temperature)
        save_path: Path to save the image
        show: Whether to display the image
        show_rivers: Whether to display rivers
        show_contours: Whether to display elevation contours
        show_grid: Whether to display a grid
    """
    # Handle both World objects and legacy world grids
    if isinstance(world, World):
        world_obj = world
        size = world.size
    else:
        # For backward compatibility
        size = len(world)
        world_obj = None
    
    # Create figure with specific size for better quality
    fig = plt.figure(figsize=(12, 10))
    
    # Create the base visualization based on the selected mode
    if mode == TERRAIN_MODE:
        # Terrain/biome visualization
        color_grid = np.zeros((size, size, 3))
        
        if world_obj:
            # Use the new World object
            for i in range(size):
                for j in range(size):
                    terrain = world_obj.get_terrain_at(j, i)
                    color_hex = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                    color_grid[i, j] = mcolors.to_rgb(color_hex)
            
            # Create legend for the new biomes
            legend_elements = []
            added_biomes = set()
            
            for i in range(size):
                for j in range(size):
                    terrain = world_obj.get_terrain_at(j, i)
                    if terrain and terrain not in added_biomes:
                        color_hex, label = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))
                        legend_elements.append(
                            patches.Rectangle((0, 0), 1, 1, facecolor=color_hex, label=label)
                        )
                        added_biomes.add(terrain)
            
            # Sort legend elements by label
            legend_elements.sort(key=lambda x: x.get_label())
            
        else:
            # Use the legacy world grid
            for i in range(size):
                for j in range(size):
                    terrain = world[i][j]
                    color = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                    color_grid[i, j] = mcolors.to_rgb(color)
            
            # Create legend for legacy terrain types
            legend_elements = [
                patches.Rectangle((0, 0), 1, 1, facecolor=color, label=label)
                for terrain, (color, label) in TERRAIN_COLORS.items()
            ]
        
        # Display the terrain map
        plt.imshow(color_grid)
        
    elif mode == ELEVATION_MODE and world_obj:
        # Elevation visualization with a color gradient
        plt.imshow(world_obj.elevation_map, cmap=ELEVATION_CMAP)
        plt.colorbar(label="Elevation")
        
        # Create legend for elevation thresholds
        legend_elements = []
        for name, value in ELEVATION_THRESHOLDS.items():
            color = ELEVATION_CMAP(value)
            legend_elements.append(
                patches.Rectangle((0, 0), 1, 1, facecolor=color, label=f"{name} ({value:.2f})")
            )
        
    elif mode == MOISTURE_MODE and world_obj:
        # Moisture visualization with a color gradient
        plt.imshow(world_obj.moisture_map, cmap=MOISTURE_CMAP)
        plt.colorbar(label="Moisture")
        
        # Create legend for moisture thresholds
        legend_elements = []
        for name, value in MOISTURE_THRESHOLDS.items():
            color = MOISTURE_CMAP(value)
            legend_elements.append(
                patches.Rectangle((0, 0), 1, 1, facecolor=color, label=f"{name} ({value:.2f})")
            )
        
    elif mode == TEMPERATURE_MODE and world_obj:
        # Temperature visualization with a color gradient
        plt.imshow(world_obj.temperature_map, cmap=TEMPERATURE_CMAP)
        plt.colorbar(label="Temperature")
        
        # No specific legend for temperature
        legend_elements = []
    
    else:
        # Default to terrain mode for legacy worlds
        color_grid = np.zeros((size, size, 3))
        
        for i in range(size):
            for j in range(size):
                terrain = world[i][j]
                color = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
                color_grid[i, j] = mcolors.to_rgb(color)
        
        plt.imshow(color_grid)
        
        # Create legend for legacy terrain types
        legend_elements = [
            patches.Rectangle((0, 0), 1, 1, facecolor=color, label=label)
            for terrain, (color, label) in TERRAIN_COLORS.items()
        ]
    
    # Add rivers if requested and available
    if show_rivers and world_obj and hasattr(world_obj, 'river_map'):
        # Create a mask for rivers
        river_y, river_x = np.where(world_obj.river_map)
        
        # Plot rivers as blue dots
        plt.scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
    
    # Add contour lines if requested and elevation data is available
    if show_contours and world_obj:
        # Generate contour lines at regular intervals
        contour_levels = np.linspace(0, 1, 11)  # 10 contour lines
        plt.contour(world_obj.elevation_map, levels=contour_levels, colors='black', alpha=0.3)
    
    # Add grid if requested
    if show_grid:
        plt.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    else:
        plt.grid(False)
    
    # Turn off axis
    plt.axis("off")
    
    # Add legend if we have legend elements
    if legend_elements:
        plt.legend(
            handles=legend_elements,
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            title=mode.capitalize()
        )
    
    # Set title
    title = f"Realmweaver - {mode.capitalize()} View"
    if seed is not None:
        title += f" (Seed: {seed})"
    plt.title(title)
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    # Show if requested
    if show:
        plt.tight_layout()
        plt.show(block=False)  # Use non-blocking mode when called from GUI
    
    return fig

def visualize_world_multi(world, seed=None, save_path=None, show=True):
    """
    Creates a multi-panel visualization showing different aspects of the world.
    This is useful for debugging and understanding the world generation.
    
    Args:
        world: A World object
        seed: The seed used to generate the world
        save_path: Path to save the image
        show: Whether to display the image
    """
    if not isinstance(world, World):
        print("Multi-view visualization requires a World object")
        return None
    
    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    
    # Terrain view (top left)
    color_grid = np.zeros((world.size, world.size, 3))
    for i in range(world.size):
        for j in range(world.size):
            terrain = world.get_terrain_at(j, i)
            color_hex = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
            color_grid[i, j] = mcolors.to_rgb(color_hex)
    
    axs[0, 0].imshow(color_grid)
    axs[0, 0].set_title("Terrain/Biomes")
    axs[0, 0].axis("off")
    
    # Elevation view (top right)
    elevation_img = axs[0, 1].imshow(world.elevation_map, cmap=ELEVATION_CMAP)
    axs[0, 1].set_title("Elevation")
    axs[0, 1].axis("off")
    fig.colorbar(elevation_img, ax=axs[0, 1], shrink=0.8)
    
    # Moisture view (bottom left)
    moisture_img = axs[1, 0].imshow(world.moisture_map, cmap=MOISTURE_CMAP)
    axs[1, 0].set_title("Moisture")
    axs[1, 0].axis("off")
    fig.colorbar(moisture_img, ax=axs[1, 0], shrink=0.8)
    
    # Temperature view (bottom right)
    temperature_img = axs[1, 1].imshow(world.temperature_map, cmap=TEMPERATURE_CMAP)
    axs[1, 1].set_title("Temperature")
    axs[1, 1].axis("off")
    fig.colorbar(temperature_img, ax=axs[1, 1], shrink=0.8)
    
    # Add rivers to all views
    if hasattr(world, 'river_map'):
        river_y, river_x = np.where(world.river_map)
        axs[0, 0].scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
        axs[0, 1].scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
        axs[1, 0].scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
        axs[1, 1].scatter(river_x, river_y, color='#3a97d4', s=2, alpha=0.8)
    
    # Set overall title
    fig.suptitle(f"Realmweaver - World Analysis (Seed: {world.seed})", fontsize=16)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    # Show if requested
    if show:
        plt.show(block=False)  # Use non-blocking mode when called from GUI
    
    return fig

if __name__ == "__main__":
    # Create a World object
    from world_generator import World
    
    # Get user input for seed
    user_input = input("Enter a seed (leave blank for random): ").strip()
    seed = None if not user_input else user_input
    
    # Generate the world
    world = World(size=100, seed=seed)
    world.generate()
    
    print(f"Visualizing world with seed: {world.seed}")
    
    # Show different visualization modes
    visualize_world(world, world.seed, mode=TERRAIN_MODE, show_rivers=True, show_contours=True)
    visualize_world(world, world.seed, mode=ELEVATION_MODE)
    visualize_world(world, world.seed, mode=MOISTURE_MODE)
    visualize_world(world, world.seed, mode=TEMPERATURE_MODE)
    
    # Show multi-panel visualization
    visualize_world_multi(world, world.seed)
    
    # In standalone mode, we need to block to keep the windows open
    plt.show(block=True)