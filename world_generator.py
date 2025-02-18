# Core logic for generating the world
# our first step will be making a basic 50x50 grid - this was suggested because it is nice and big, and simple like me! 😊


# import terrain_config  # now this can be called if I update terrain_config.py to be used again
import noise # perlin noise is COOL - thanks AI for the explination - see lower down where we actually use it
import numpy as np
import random  # Claude added this - needed for seed generation

# Lets see - this should 'make the world' - it looks like the code is just mashing together a bunch of random terrain types to make a grid.
# this looks gross, so try to revisit - maybe we can move some logic to put stuff that makes sense in correct places?

# Terrain threshholds here
WATER_LEVEL = -0.3
FOREST_LEVEL = 0.1
DESERT_LEVEL = 0.4
MOUNTAIN_LEVEL = 0.7


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
    """Generates a world using perlin noise for natural terrain generation"""
    # Claude added this - handle seed initialization
    if seed is None:
        seed = random.randint(0, 1000000)
    elif isinstance(seed, str):
        seed = string_to_seed(seed)
    print(f"Generated Seed: {seed}")
    
    random.seed(seed)
    np.random.seed(seed)
    
    world = np.zeros((size,size), dtype=str) # okay so here is what I got
    # np.zeros is a numpy function that creates an array of zeros, and we are making a 50x50 grid of strings and we use the dtype str because we are using Ws and Fs and stuff, not numbers
    # we could do np.full, but IDK what that is or why it would "Be easier to understand at a glance" - recheck this later
    # suggested alternative code: world = np.full((size, size), "", dtype=str)

    for i in range(size):
        for j in range(size):
            # Generates a perlins noise value with seed
            noise_value = noise.pnoise2(
                (i + seed) / scale, (j + seed) / scale,
                octaves=6, persistence=0.5, lacunarity=2.0
            ) # scale is the size of the world, octaves is the number of levels of detail you want to generate, persistence is the roughness of the terrain, and lacunarity is the frequency of the terrain
            # so big scale = big world, big octaves = more detail, big persistence = rougher terrain, big lacunarity = more frequent terrain
            # and small scale = small world, small octaves = less detail, small persistence = smoother terrain, small lacunarity = less frequent terrain

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
