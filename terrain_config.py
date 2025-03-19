# Terrain Configuration for Realmweaver
# This file contains all the configuration parameters for terrain generation

# Noise generation parameters
NOISE_PARAMS = {
    "elevation": {
        "octaves": 6,         # Number of noise layers to combine
        "persistence": 0.5,    # How much each octave contributes
        "lacunarity": 2.0,     # How much detail is added at each octave
        "scale": 100.0,        # Base scale of the noise
        "redistribution": 1.2  # Power to raise the noise to (for mountains/valleys) - increased to make mountains more common
    },
    "moisture": {
        "octaves": 4,
        "persistence": 0.5,
        "lacunarity": 2.0,
        "scale": 150.0,
        "redistribution": 1.0
    },
    "temperature": {
        "octaves": 3,
        "persistence": 0.5,
        "lacunarity": 2.0,
        "scale": 200.0,
        "redistribution": 1.0
    }
}

# Elevation thresholds - adjusted to make mountains more common
ELEVATION_THRESHOLDS = {
    "DEEP_WATER": 0.2,    # Deep ocean
    "SHALLOW_WATER": 0.3,  # Shallow water/coast
    "BEACH": 0.33,         # Beach/shore
    "LOWLANDS": 0.45,      # Low elevation (plains, forests) - reduced from 0.5
    "HIGHLANDS": 0.65,     # Higher elevation (hills) - reduced from 0.7
    "MOUNTAINS": 0.8,      # Mountains - reduced from 0.85
    "PEAKS": 0.9           # Mountain peaks - reduced from 0.95
}

# Moisture thresholds
MOISTURE_THRESHOLDS = {
    "ARID": 0.3,           # Very dry
    "DRY": 0.5,            # Somewhat dry
    "MODERATE": 0.7,       # Moderate moisture
    "WET": 0.9,            # Wet
    "SATURATED": 1.0       # Very wet
}

# Temperature thresholds (can be used later for more complex biomes)
TEMPERATURE_THRESHOLDS = {
    "FREEZING": 0.2,
    "COLD": 0.4,
    "MODERATE": 0.6,
    "WARM": 0.8,
    "HOT": 1.0
}

# Biome definitions based on elevation and moisture
# Format: (terrain_code, color, display_name)
BIOMES = {
    # Water biomes
    "DEEP_OCEAN": ("DO", "#0a3b5b", "Deep Ocean"),
    "OCEAN": ("OC", "#0e5c8c", "Ocean"),
    "SHALLOW_WATER": ("SW", "#1a7eb3", "Shallow Water"),
    "RIVER": ("RV", "#3a97d4", "River"),
    
    # Beach/Shore biomes
    "BEACH": ("BC", "#e0c88c", "Beach"),
    "ROCKY_SHORE": ("RS", "#8c8c8c", "Rocky Shore"),
    
    # Lowland biomes
    "DESERT": ("DS", "#e6cea8", "Desert"),
    "SAVANNA": ("SV", "#c5be6c", "Savanna"),
    "GRASSLAND": ("GL", "#a8d168", "Grassland"),
    "MARSH": ("MH", "#6ca68c", "Marsh"),
    "SWAMP": ("SP", "#4d7c64", "Swamp"),
    "FOREST": ("FR", "#4e8c4e", "Forest"),
    "RAINFOREST": ("RF", "#2d6a2d", "Rainforest"),
    "JUNGLE": ("JG", "#1e5c1e", "Jungle"),
    
    # Highland biomes
    "SHRUBLAND": ("SL", "#b3a86c", "Shrubland"),
    "HILLS": ("HL", "#8cac7c", "Hills"),
    "HIGHLAND_FOREST": ("HF", "#3d7c3d", "Highland Forest"),
    
    # Mountain biomes
    "MOUNTAIN": ("MT", "#8c8c8c", "Mountain"),
    "MOUNTAIN_FOREST": ("MF", "#4d6e4d", "Mountain Forest"),
    "ALPINE": ("AL", "#c8c8c8", "Alpine"),
    
    # Peak biomes
    "SNOW_CAP": ("SC", "#ffffff", "Snow Cap"),
    "VOLCANO": ("VC", "#3d0000", "Volcano")  # Rare special biome
}

# Biome matrix - determines which biome to use based on elevation and moisture
# This is a simplified version - a real implementation would consider temperature too
BIOME_MATRIX = {
    # Elevation: DEEP_WATER
    (0, 0): BIOMES["DEEP_OCEAN"],  # Any moisture level
    (0, 1): BIOMES["DEEP_OCEAN"],
    (0, 2): BIOMES["DEEP_OCEAN"],
    (0, 3): BIOMES["DEEP_OCEAN"],
    (0, 4): BIOMES["DEEP_OCEAN"],
    
    # Elevation: SHALLOW_WATER
    (1, 0): BIOMES["OCEAN"],  # Any moisture level
    (1, 1): BIOMES["OCEAN"],
    (1, 2): BIOMES["OCEAN"],
    (1, 3): BIOMES["OCEAN"],
    (1, 4): BIOMES["OCEAN"],
    
    # Elevation: BEACH
    (2, 0): BIOMES["BEACH"],  # Dry beach
    (2, 1): BIOMES["BEACH"],
    (2, 2): BIOMES["BEACH"],
    (2, 3): BIOMES["MARSH"],  # Wet beach becomes marsh
    (2, 4): BIOMES["MARSH"],
    
    # Elevation: LOWLANDS
    (3, 0): BIOMES["DESERT"],      # Arid lowlands
    (3, 1): BIOMES["SAVANNA"],     # Dry lowlands
    (3, 2): BIOMES["GRASSLAND"],   # Moderate moisture
    (3, 3): BIOMES["FOREST"],      # Wet lowlands
    (3, 4): BIOMES["RAINFOREST"],  # Very wet lowlands
    
    # Elevation: HIGHLANDS
    (4, 0): BIOMES["SHRUBLAND"],      # Arid highlands
    (4, 1): BIOMES["HILLS"],          # Dry highlands
    (4, 2): BIOMES["HILLS"],          # Moderate moisture
    (4, 3): BIOMES["HIGHLAND_FOREST"],# Wet highlands
    (4, 4): BIOMES["HIGHLAND_FOREST"],# Very wet highlands
    
    # Elevation: MOUNTAINS
    (5, 0): BIOMES["MOUNTAIN"],       # Arid mountains
    (5, 1): BIOMES["MOUNTAIN"],       # Dry mountains
    (5, 2): BIOMES["MOUNTAIN"],       # Moderate moisture
    (5, 3): BIOMES["MOUNTAIN_FOREST"],# Wet mountains
    (5, 4): BIOMES["MOUNTAIN_FOREST"],# Very wet mountains
    
    # Elevation: PEAKS
    (6, 0): BIOMES["ALPINE"],     # Arid peaks
    (6, 1): BIOMES["ALPINE"],     # Dry peaks
    (6, 2): BIOMES["SNOW_CAP"],   # Moderate moisture
    (6, 3): BIOMES["SNOW_CAP"],   # Wet peaks
    (6, 4): BIOMES["SNOW_CAP"],   # Very wet peaks
}

# Helper function to get biome based on elevation and moisture
def get_biome(elevation, moisture):
    """
    Determine the biome based on elevation and moisture values.
    Both values should be in the range [0.0, 1.0].
    """
    # Determine elevation category
    elev_category = 0  # Default to DEEP_WATER
    if elevation >= ELEVATION_THRESHOLDS["PEAKS"]:
        elev_category = 6
    elif elevation >= ELEVATION_THRESHOLDS["MOUNTAINS"]:
        elev_category = 5
    elif elevation >= ELEVATION_THRESHOLDS["HIGHLANDS"]:
        elev_category = 4
    elif elevation >= ELEVATION_THRESHOLDS["LOWLANDS"]:
        elev_category = 3
    elif elevation >= ELEVATION_THRESHOLDS["BEACH"]:
        elev_category = 2
    elif elevation >= ELEVATION_THRESHOLDS["SHALLOW_WATER"]:
        elev_category = 1
    
    # Determine moisture category
    moist_category = 0  # Default to ARID
    if moisture >= MOISTURE_THRESHOLDS["SATURATED"]:
        moist_category = 4
    elif moisture >= MOISTURE_THRESHOLDS["WET"]:
        moist_category = 3
    elif moisture >= MOISTURE_THRESHOLDS["MODERATE"]:
        moist_category = 2
    elif moisture >= MOISTURE_THRESHOLDS["DRY"]:
        moist_category = 1
    
    # Return the biome from the matrix
    return BIOME_MATRIX.get((elev_category, moist_category), BIOMES["GRASSLAND"])

# Extract terrain codes and colors for easy access
TERRAIN_CODES = {name: info[0] for name, info in BIOMES.items()}
TERRAIN_COLORS = {info[0]: (info[1], info[2]) for name, info in BIOMES.items()}

# Legacy terrain types for backward compatibility
LEGACY_TERRAIN_TYPES = {
    "W": "Water",
    "F": "Forest",
    "D": "Desert",
    "M": "Mountain"
}

# Legacy terrain colors for backward compatibility
LEGACY_TERRAIN_COLORS = {
    "W": ("blue", "Water"),
    "F": ("green", "Forest"),
    "D": ("yellow", "Desert"),
    "M": ("brown", "Mountain")
}