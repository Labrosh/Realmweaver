# Core logic for generating the world
# our first step will be making a basic 50x50 grid - this was suggested because it is nice and big, and simple like me! 😊

import random
import terrain_config  # Import emoji mapping

USE_EMOJI = True  # This will be our horrible variable to switch between emojis and letters - I want to make a proper settings or option menu later
# UPDATE - NO EMOJIS LOOKS HORRIBLE - Emojis are on true until I fix them 

# Lets see - this should 'make the world' - it looks like the code is just mashing together a bunch of random terrain types to make a grid.
# this looks gross, so try to revisit - maybe we can move some logic to put stuff that makes sense in correct places?
def generate_world(size=50):
    """Creates a grid-based world with random terrain"""  # note - a lot of this code is from Chatgpt & Claude - I will try my best to add comments to remind myself what each part does!
    terrain_types = ["W", "F", "D", "M"]  # Water, Forest, Desert, Mountain
    world = [[random.choice(terrain_types) for _ in range(size)] for _ in range(size)]
    return world

def print_world(world):
    """Prints the world in a readable format."""
    for row in world:
        if USE_EMOJI:
            print(" ".join(terrain_config.TERRAIN_MAP[cell] for cell in row))
        else:
            print(" ".join(row))

if __name__ == "__main__":
    world = generate_world()
    print_world(world)
