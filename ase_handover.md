# Aseprite Viewer Project Handover (v48)
**Date:** 2026-02-20
**Current Version:** v48 (Physics Stability, Auto-Load & NPC Management)

## 1. Project Overview
Pygame-based Aseprite previewer with action game physics. Focuses on accurate animation testing, combat logic validation, and easy asset management.

## 2. Recent Updates (v48)
- **Physics Stability:**
  - **Time Scaling:** Fixed jump height inconsistency in slow-motion by applying delta-time to gravity calculation.
- **Project Persistence:**
  - **Auto-Load:** Automatically loads platform layout and NPC setup (`ase_project.json`) on startup.
- **NPC Management:**
  - **Delete:** Right-click on profile/source tabs to remove them (Player tab is protected).
  - **Summon:** Press `G` to teleport NPCs near the player with random offsets to prevent stacking.
- **UI Refinement:**
  - **Input Handling:** Updated click detection for the new 2-row top bar layout.
  - **Layout:** Optimized button placement for better accessibility.

## 3. Key Files in this Folder
- `ase_viewer.py`: Main logic (v48).
- `ase_settings.json`: Persisted physics/VFX settings.
- `ase_project.json`: Project state (sources, mappings, platforms, NPCs).
- `ase_debug.log`: Runtime logs.

## 4. Instructions for Next Session
1. Run `python ase_viewer.py`.
2. **Verify Persistence:** Check if platforms and NPCs from previous session are loaded.
3. **Test Physics:** Use `[` to slow down time and verify jump height consistency.
4. **Manage NPCs:** Add new NPCs via `+ NPC`, summon with `G`, and remove via Right-Click on tab.
5. **Shortcuts:** `Z` (Attack), `X` (Dash), `G` (Summon), `Space/Up` (Jump), `Down+Jump` (Drop-Through).
