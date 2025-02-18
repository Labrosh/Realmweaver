# TODO List for Realmweaver

## 🔹 Current Priorities (Next Steps)

- [ ] Ensure seed handling works properly across all scripts
- [ ] Decide on a single entry point for the project
- [ ] Add legend/key for current terrain types in visualization
- [ ] Allow maps to be saved as images

## 🔹 Near-Term Improvements (Before MVP)

### 🌍 World Generation

- [ ] Allow customization of world generation settings:
  - World size
  - Scale
  - Terrain thresholds (WATER_LEVEL, etc.)
  - Noise parameters (octaves, persistence, lacunarity)
- [ ] Improve terrain color representation for better readability
- [ ] Consider terrain blending/transitions

### 🎨 Visualization

- [ ] Add basic grid overlay option for easier readability
- [ ] Improve color contrast for water/land differentiation

### 🛠 Code Structure & Cleanup

- [ ] Move world generation settings to a config file
- [ ] Organize imports and clean up unused code
- [ ] Improve documentation/comments for easier future edits
- [ ] Add basic unit tests for world generation consistency

## 🔮 Future Features (Post-MVP)

### 🏰 Civilizations & Settlements

- [ ] Implement city/settlement placement (based on terrain)
- [ ] Consider basic AI-driven civilization expansion
- [ ] Add resources & points of interest

### 📊 Data Persistence

- [ ] Save/load world configurations:
  - JSON or SQLite world files
  - Allow users to revisit specific seeds/worlds
- [ ] Implement terrain history tracking (how the world changes over time)

### 🖥️ Advanced UI & CLI

- [ ] Add command-line interface (CLI) for generating worlds with user-defined settings
- [ ] Consider GUI or interactive visualization mode

## 🏆 Long-Term Goals

- [ ] Add temperature & rainfall influences on terrain
- [ ] Introduce biome-dependent weather events
- [ ] Improve map realism with rivers, coastlines, and elevation
