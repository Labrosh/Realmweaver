# Code for displaying the world (Suggested to use matplotlib? look into!)

import matplotlib.pyplot as plt # this has to be the standard - I see it all the time when I looked at code...in my one other time I used it
import matplotlib.colors as mcolors # AI helped track down why this broke code
import numpy as np # same here -np must be standard for numpy
import terrain_config # so we can grab my...uh...terrain config stuff
from world_generator import generate_world # so we can grab my world generator stuff! this one I know!

# color mapping for different terrains

TERRAIN_COLORS = {
    "W": "blue", # Water
    "F": "green", # Forest
    "D": "yellow", # Desert
    "M": "brown" # Mountain
}

def visualize_world(world, seed=None):
    """Creates a color-coded map of the generated world"""
    size = len(world)
    color_grid = np.zeros((size, size, 3)) # 3 for RGB - woah cool - I didn't know you could do that

    for i in range(size):
        for j in range(size):
           terrain = world[i][j]
           color = TERRAIN_COLORS.get(terrain, "black") # ah if we don't have a color for the terrain, we just make it black - I guess future proofing since we only have the four terrains right now
           color_grid[i, j] = mcolors.to_rgb(color) # and then we color the grid!

    
    # plot the world map - This whole part looks like boiler plate how to use plt stuff - but might as well double check what it does when I check in.
    plt.imshow(color_grid) # Check
    plt.axis("off") # check
    
    # Claude added this part - adds seed number to plot title if one exists
    title = "Realmweaver - Procedural World"
    if seed is not None:
        title += f" (Seed: {seed})"
    plt.title(title)
    plt.show()

if __name__ == "__main__":
    # Claude added this part - updated to handle the seed value that generate_world now returns
    world, seed = generate_world(size=50)  # Generate a world - now with seed support!
    print(f"Visualizing world with seed: {seed}")
    visualize_world(world, seed)  # then show the map.