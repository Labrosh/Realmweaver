# Core logic for generating the world
# our first step will be making a basic 50x50 grid - this was suggested because it is nice and big, and simple like me! 😊

from opensimplex import OpenSimplex
import numpy as np
import random  # Claude added this - needed for seed generation

# Lets see - this should 'make the world' - it looks like the code is just mashing together a bunch of random terrain types to make a grid.
# this looks gross, so try to revisit - maybe we can move some logic to put stuff that makes sense in correct places?

# Terrain thresholds here - adjusted for normalized OpenSimplex values (0 to 1 range)
WATER_LEVEL = 0.3    # Lower 30% is water
FOREST_LEVEL = 0.5   # Next 20% is forest
DESERT_LEVEL = 0.7   # Next 20% is desert
# Everything above 0.7 becomes mountain (30%)

# Terrain types stored here for the test
TERRAIN_TYPES = {
    "W": "Water",
    "F": "Forest",
    "D": "Desert",
    "M": "Mountain"
}

# Claude added this - converts text seeds into numbers
def string_to_seed(s):
    """Convert any string to a numeric seed"""
    return hash(s) & 0xFFFFFFFF

def generate_world(size=50, scale=10.0, seed=None):
    """Generates a world using OpenSimplex noise for natural terrain generation"""
    if isinstance(seed, str):
        seed = string_to_seed(seed)
    elif seed is None:
        seed = np.random.randint(0, 2**32 - 1)
    
    # Set the seed for both numpy and noise
    np.random.seed(seed)
    
    noise_gen = OpenSimplex(seed=seed)
    world = np.zeros((size,size), dtype=str)

    for i in range(size):
        for j in range(size):
            noise_value = (noise_gen.noise2(i / scale, j / scale) + 1) / 2  # Convert from [-1,1] to [0,1]

            if noise_value < WATER_LEVEL:
                world[i][j] = "W" # Water
            elif noise_value < FOREST_LEVEL:
                world[i][j] = "F" # Forest
            elif noise_value < DESERT_LEVEL:
                world[i][j] = "D" # Desert
            else:
                world[i][j] = "M" # Mountain
    return world, seed  # Claude modified - now returns both world and seed

def print_world(world):
    """Prints the world to the console"""
    for row in world:
        print("".join(row))

if __name__ == "__main__":
    # Claude added this - handle user input for seeds
    user_input = input("Enter a seed (leave blank for random): ").strip()
    seed = None if not user_input else user_input
    world, used_seed = generate_world(size=50, seed=seed)
    print(f"Using Seed: {used_seed}")
    print_world(world)
