# Aseprite Viewer Project Handover (v46)
**Date:** 2026-02-20
**Current Version:** v46 (Combat Polish, Camera & UI Fixes)

## 1. Project Overview
Pygame-based Aseprite previewer with action game physics. Features advanced combat logic (combos, skills), NPC AI, and optimized rendering.

## 2. Recent Updates (v46)
- **Combat Logic Refinement:**
  - **Combo System:** Added visual combo stack bar. Reset timer set to 1s. Empty combo slots now reset the chain instead of skipping.
  - **PowerBomb:** Fixed bug where `FALL` state would override PowerBomb animation mid-air.
  - **Feel:** Removed screen shake from basic combo attacks for clarity.
- **Animation Sequencing:**
  - **Fall Logic:** Explicitly chains `Fall_Ready` -> `Fall_(Loop)`. Trigger timing adjusted to start near jump apex (vy > -4.0) for smoother transition.
  - **Fixes:** Resolved animation freeze bug caused by incorrect indentation logic.
- **UI & UX Improvements:**
  - **Scroll Separation:** Mouse wheel now zooms only in the main view and scrolls only in the sidebar.
  - **Scroll Clamping:** Sidebar scroll now stops at content boundaries (no infinite scrolling).
  - **Tag Selection:** Fixed click detection offset and selection logic for tag mapping.
- **Camera & NPC:**
  - **Camera Offset:** Adjusted `cam_v_offset` to `50` (positions character higher on screen for better ground visibility). increased tracking speed (0.25).
  - **NPC Spawn:** Spawn range narrowed (600-900) to ensure NPCs appear near the player.

## 3. Key Files in this Folder
- `ase_viewer.py`: Main logic (v46).
- `ase_debug.log`: Animation state logs (useful for debugging transitions).
- `ase_settings.json`: Persisted physics/VFX settings.
- `ase_project.json`: Last used source files and tag mappings.

## 4. Instructions for Next Session
1. Run `python ase_viewer.py`.
2. **Test Combat:** Check combo stack bar at bottom, verify `Fall_Ready` plays fully on jump descent.
3. **UI Check:** Verify scroll wheel behaves correctly in viewport vs sidebar.
4. **Shortcuts:** `Z` (Attack), `X` (Dash), `C/B/N` (Skills), `F5` (Reload), `R-Drag` (Camera).
