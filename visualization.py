# Code for displaying the world (Suggested to use matplotlib? look into!)
# This is part of the initial version - we're just trying to get something that looks nice on the screen
# My first attempt at trying to use matplotlib - seems to work okay! The colors help see what's what.

import matplotlib.pyplot as plt # this has to be the standard - I see it all the time when I looked at code...in my one other time I used it
import matplotlib.colors as mcolors # AI helped track down why this broke code
import numpy as np # same here -np must be standard for numpy
import terrain_config # so we can grab my...uh...terrain config stuff
from world_generator import generate_world # so we can grab my world generator stuff! this one I know!

# color mapping for different terrains

TERRAIN_COLORS = {
    "W": ("blue", "Water"),
    "F": ("green", "Forest"),
    "D": ("yellow", "Desert"),
    "M": ("brown", "Mountain")
}

def visualize_world(world, seed=None, save_path=None, show=True):
    """Creates a color-coded map of the generated world"""
    size = len(world)
    color_grid = np.zeros((size, size, 3)) # 3 for RGB - woah cool - I didn't know you could do that

    # Create figure with specific size for better quality
    plt.figure(figsize=(10, 8))
    
    for i in range(size):
        for j in range(size):
            terrain = world[i][j]
            color = TERRAIN_COLORS.get(terrain, ("black", "Unknown"))[0]
            color_grid[i, j] = mcolors.to_rgb(color)

    plt.imshow(color_grid)
    plt.axis("off")
    
    # Add legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, label=label)
                      for terrain, (color, label) in TERRAIN_COLORS.items()]
    plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    title = "Realmweaver - Procedural World"
    if seed is not None:
        title += f" (Seed: {seed})"
    plt.title(title)
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    # Show if requested
    if show:
        plt.show()
    
    plt.close()

if __name__ == "__main__":
    # Claude added this part - updated to handle the seed value that generate_world now returns
    world, seed = generate_world(size=50)  # Generate a world - now with seed support!
    print(f"Visualizing world with seed: {seed}")
    visualize_world(world, seed)  # then show the map.