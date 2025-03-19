# Core logic for generating the world
# This file implements the terrain generation system using noise-based algorithms

from opensimplex import OpenSimplex
import numpy as np
import random
import math
from terrain_config import (
    NOISE_PARAMS, ELEVATION_THRESHOLDS, MOISTURE_THRESHOLDS,
    BIOMES, get_biome, TERRAIN_CODES, TERRAIN_COLORS,
    LEGACY_TERRAIN_TYPES, LEGACY_TERRAIN_COLORS
)

def string_to_seed(s):
    """Convert any string to a numeric seed"""
    return hash(s) & 0xFFFFFFFF

class World:
    """
    Represents a generated world with terrain, biomes, and other features.
    This class stores all the data about the world and provides methods to access it.
    """
    def __init__(self, size=50, seed=None):
        """Initialize a new world with the given size and seed"""
        # Process the seed
        if isinstance(seed, str):
            self.seed = string_to_seed(seed)
        elif seed is None:
            self.seed = np.random.randint(0, 2**32 - 1)
        else:
            self.seed = seed
            
        # Set the seed for numpy
        np.random.seed(self.seed)
        
        # Store world parameters
        self.size = size
        
        # Initialize maps
        self.elevation_map = np.zeros((size, size))
        self.moisture_map = np.zeros((size, size))
        self.temperature_map = np.zeros((size, size))
        self.biome_map = np.zeros((size, size), dtype=object)
        self.terrain_map = np.zeros((size, size), dtype=object)
        self.river_map = np.zeros((size, size), dtype=bool)
        
        # For backward compatibility
        self.legacy_map = np.zeros((size, size), dtype=str)
        
    def generate(self):
        """Generate all aspects of the world"""
        self._generate_elevation_map()
        self._generate_moisture_map()
        self._generate_temperature_map()
        self._generate_biomes()
        self._generate_rivers()
        self._generate_legacy_map()
        return self
    
    def _generate_noise_map(self, noise_params, offset=(0, 0)):
        """
        Generate a noise map using multiple octaves for more natural results.
        This creates more realistic terrain by combining noise at different scales.
        """
        # Create a new noise generator with our seed
        noise_gen = OpenSimplex(seed=self.seed)
        
        # Initialize the noise map
        noise_map = np.zeros((self.size, self.size))
        
        # Get noise parameters
        octaves = noise_params["octaves"]
        persistence = noise_params["persistence"]
        lacunarity = noise_params["lacunarity"]
        scale = noise_params["scale"]
        
        # Generate the noise map with multiple octaves
        max_value = 0
        amplitude = 1.0
        frequency = 1.0
        
        for i in range(octaves):
            for y in range(self.size):
                for x in range(self.size):
                    # Add offset to create different noise patterns for different maps
                    nx = (x / scale) * frequency + offset[0]
                    ny = (y / scale) * frequency + offset[1]
                    
                    # Add noise value to the map
                    noise_map[y][x] += noise_gen.noise2(nx, ny) * amplitude
            
            # Update parameters for next octave
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        # Normalize the noise map to [0, 1]
        noise_map = (noise_map / max_value + 1) / 2
        
        # Apply redistribution if specified (for more mountains or valleys)
        if noise_params["redistribution"] != 1.0:
            noise_map = np.power(noise_map, noise_params["redistribution"])
            
        return noise_map
    
    def _generate_elevation_map(self):
        """Generate the elevation map using noise"""
        self.elevation_map = self._generate_noise_map(NOISE_PARAMS["elevation"])
        return self.elevation_map
    
    def _generate_moisture_map(self):
        """Generate the moisture map using noise with a different offset"""
        # Use a different offset for moisture to make it independent from elevation
        self.moisture_map = self._generate_noise_map(NOISE_PARAMS["moisture"], offset=(500, 500))
        return self.moisture_map
    
    def _generate_temperature_map(self):
        """
        Generate the temperature map based on latitude (y-coordinate) and elevation.
        This creates a more realistic climate system where it's colder at the poles and on mountains.
        """
        # Start with a base temperature gradient from equator (middle) to poles (top/bottom)
        equator = self.size / 2
        max_distance = self.size / 2
        
        for y in range(self.size):
            # Calculate distance from equator (0 at equator, 1 at poles)
            distance_from_equator = abs(y - equator) / max_distance
            
            for x in range(self.size):
                # Base temperature decreases with distance from equator (quadratic falloff for more realism)
                # This creates a more pronounced equatorial band
                base_temp = 1.0 - (distance_from_equator ** 2)
                
                # Temperature decreases with elevation (higher = colder)
                # Make this effect stronger for more realistic mountain temperatures
                elevation_factor = self.elevation_map[y][x] * 0.7
                
                # Combine factors (higher elevation = colder)
                self.temperature_map[y][x] = max(0, min(1, base_temp - elevation_factor))
        
        # Add some noise for local variations (use a different offset)
        temp_noise = self._generate_noise_map(NOISE_PARAMS["temperature"], offset=(1000, 1000))
        # Use less noise influence to preserve the main temperature patterns
        self.temperature_map = self.temperature_map * 0.85 + temp_noise * 0.15
        
        return self.temperature_map
    
    def _generate_biomes(self):
        """
        Determine the biome for each cell based on elevation, moisture, and temperature.
        This creates a realistic distribution of biomes across the world.
        """
        for y in range(self.size):
            for x in range(self.size):
                elevation = self.elevation_map[y][x]
                moisture = self.moisture_map[y][x]
                
                # Get the biome based on elevation and moisture
                biome_code, biome_color, biome_name = get_biome(elevation, moisture)
                
                # Store the biome and terrain information
                self.biome_map[y][x] = biome_name
                self.terrain_map[y][x] = biome_code
        
        return self.biome_map
    
    def _generate_rivers(self):
        """
        Generate rivers flowing from high to low elevation.
        This uses a simple algorithm to create rivers that flow naturally downhill.
        """
        # Number of rivers to generate (based on world size)
        num_rivers = max(3, self.size // 10)
        
        # Start rivers at high elevation points
        for _ in range(num_rivers):
            # Find a suitable starting point (high elevation, not water)
            for _ in range(100):  # Try up to 100 times to find a good start
                x = np.random.randint(0, self.size)
                y = np.random.randint(0, self.size)
                
                # Check if this is a good starting point (high elevation, not water)
                if (self.elevation_map[y][x] > ELEVATION_THRESHOLDS["HIGHLANDS"] and
                    self.elevation_map[y][x] < ELEVATION_THRESHOLDS["PEAKS"]):
                    break
            
            # Generate the river path
            self._generate_river_path(x, y)
    
    def _generate_river_path(self, start_x, start_y):
        """Generate a single river path starting from the given coordinates"""
        x, y = start_x, start_y
        
        # Maximum river length to prevent infinite loops
        max_length = self.size * 2
        
        # Generate the river until it reaches water or the edge of the map
        for _ in range(max_length):
            # Mark this cell as a river
            self.river_map[y][x] = True
            
            # If we've reached water or the edge, stop
            if (self.elevation_map[y][x] < ELEVATION_THRESHOLDS["SHALLOW_WATER"] or
                x == 0 or x == self.size - 1 or y == 0 or y == self.size - 1):
                break
            
            # Find the lowest neighboring cell
            lowest_elevation = self.elevation_map[y][x]
            next_x, next_y = x, y
            
            # Check all 8 neighboring cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    nx, ny = x + dx, y + dy
                    
                    # Check if the neighbor is within bounds
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        # If this neighbor is lower, consider flowing there
                        if self.elevation_map[ny][nx] < lowest_elevation:
                            lowest_elevation = self.elevation_map[ny][nx]
                            next_x, next_y = nx, ny
            
            # If we couldn't find a lower neighbor, stop
            if next_x == x and next_y == y:
                break
            
            # Move to the lowest neighbor
            x, y = next_x, next_y
    
    def _generate_legacy_map(self):
        """
        Generate a legacy map for backward compatibility with the old system.
        This allows the new world generator to work with existing visualization code.
        """
        for y in range(self.size):
            for x in range(self.size):
                elevation = self.elevation_map[y][x]
                
                # Convert to legacy terrain types
                if elevation < ELEVATION_THRESHOLDS["SHALLOW_WATER"]:
                    self.legacy_map[y][x] = "W"  # Water
                elif elevation < ELEVATION_THRESHOLDS["LOWLANDS"]:
                    self.legacy_map[y][x] = "F"  # Forest
                elif elevation < ELEVATION_THRESHOLDS["HIGHLANDS"]:
                    self.legacy_map[y][x] = "D"  # Desert
                else:
                    self.legacy_map[y][x] = "M"  # Mountain
        
        return self.legacy_map
    
    def get_terrain_at(self, x, y):
        """Get the terrain code at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.terrain_map[y][x]
        return None
    
    def get_biome_at(self, x, y):
        """Get the biome name at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.biome_map[y][x]
        return None
    
    def get_elevation_at(self, x, y):
        """Get the elevation value at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.elevation_map[y][x]
        return None
    
    def get_moisture_at(self, x, y):
        """Get the moisture value at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.moisture_map[y][x]
        return None
    
    def is_river_at(self, x, y):
        """Check if there's a river at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.river_map[y][x]
        return False
    
    def get_legacy_terrain_at(self, x, y):
        """Get the legacy terrain code at the specified coordinates"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.legacy_map[y][x]
        return None

def generate_world(size=50, scale=10.0, seed=None):
    """
    Generate a world with the specified parameters.
    This function maintains backward compatibility with the old API.
    
    Args:
        size: The size of the world (size x size grid)
        scale: Scale parameter (not used in the new system)
        seed: Random seed for world generation
        
    Returns:
        A tuple containing (legacy_map, seed) for backward compatibility
    """
    # Create and generate the world
    world = World(size=size, seed=seed)
    world.generate()
    
    # Return the legacy map and seed for backward compatibility
    return world.legacy_map, world.seed

def print_world(world):
    """Prints the world to the console (for backward compatibility)"""
    if isinstance(world, World):
        for row in world.legacy_map:
            print("".join(row))
    else:
        for row in world:
            print("".join(row))

if __name__ == "__main__":
    # Handle user input for seeds
    user_input = input("Enter a seed (leave blank for random): ").strip()
    seed = None if not user_input else user_input
    
    # Generate the world
    world = World(size=50, seed=seed)
    world.generate()
    
    print(f"Using Seed: {world.seed}")
    print_world(world)
