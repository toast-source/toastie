# Aseprite Viewer Project Handover (v39)
**Date:** 2026-02-12
**Current Version:** v39 (Viewport Update)

## 1. Project Overview
A Pygame-based previewer for Aseprite files, specifically designed for pixel art action games. It supports character movement, combat combos, AI NPCs, and real-time synchronization with Aseprite.

## 2. Key Files
- `ase_viewer.py`: The main application logic.
- `ase_roadmap.log`: Historical progress and completed features.
- `ase_settings.json`: Persisted user settings (Physics, VFX, Viewport, etc.).
- `config.json`: Stores the absolute path to `Aseprite.exe`.
- `ase_debug.log`: Detailed runtime logs and error traces.

## 3. Core Features (v39)
- **Hybrid System**: Manages Player and NPC profiles independently.
- **Combat**: Max 2-stack combo buffering. Attacks move forward based on input.
- **Watch Mode**: Automatically reloads `.aseprite` files on save (manual F5 supported).
- **Hitbox/Slice**: Visualizes Aseprite slices. Persistent logic avoids flickering.
- **VFX**: Screen shake on heavy impacts, Dash after-images.
- **Viewport**: 640x360 guide with letterboxing for target resolution testing.
- **Persistence**: Almost all UI settings are auto-saved and auto-loaded.

## 4. Key Shortcuts
- `Z`: Attack (Buffered) / `X`: Dash / `C, B, N`: Skills
- `Space`: Jump / `T`: Swap Exit/Enter
- `P`: Pause / `O`: Frame Step / `[` `]`: Speed Control
- `F5`: Force Reload / `H`: Toggle Hitboxes / `F`: Reset Camera
- `R-Drag`: Manual Camera Move

## 5. Known Implementation Details for Next Dev
- **CLI Dependency**: Uses `aseprite -b --list-layers` and `--sheet` for exports.
- **Coordinate System**: Center-based rendering using `spriteSourceSize` from Aseprite JSON.
- **Indentation Style**: Strictly 4 spaces. Some UI code is compact (semicolons used sparingly).
- **Bug Fix History**: Recently fixed an `AttributeError` in AI action triggering and a scroll-sync bug in the Settings UI.

## 6. Suggested Next Steps
- Implement "Project Persistence" for loaded sources (saving which files were open).
- Add frame-by-frame hitbox editing if needed.
- Enhance AI behaviors (simple pathfinding or platform detection).
