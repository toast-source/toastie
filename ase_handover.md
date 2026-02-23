# Aseprite Viewer Project Handover (v47)
**Date:** 2026-02-20
**Current Version:** v47 (Platform Editor, Physics Polish & UI Overhaul)

## 1. Project Overview
Pygame-based Aseprite previewer with action game physics. Now features a built-in platform editor, advanced time control, and improved UI.

## 2. Recent Updates (v47)
- **Platform Editor:**
  - **Edit Mode:** Toggle "EDIT PLAT" to drag & drop platforms.
  - **Features:** Add new platforms (`+ PLAT`), adjust transparency via Settings (`Plat Alpha`).
  - **Persistence:** Platform layout is automatically saved to/loaded from `ase_project.json`.
  - **Drop-Through:** Press `Down + Jump` to fall through platforms (excluding ground).
- **Physics & Time Control:**
  - **Global Time Scale:** `[` and `]` keys now affect all game physics (movement, gravity), not just animation speed.
  - **Stability:** Fixed jump height inconsistency at low speeds by applying delta-time to gravity.
  - **Summon:** Press `G` to teleport NPCs near the player with `Swap_Enter` animation.
- **UI & UX Overhaul:**
  - **Layout:** Top bar reorganized into 2 rows to prevent overlapping.
  - **Tab Management:** Right-click on tabs (NPC/Source) to delete them.
  - **Scroll Logic:** Separated main view zoom vs. sidebar scroll. Added scroll clamping to prevent infinite scrolling.
  - **Background:** Auto-reloads background image when the file is modified.

## 3. Key Files in this Folder
- `ase_viewer.py`: Main logic (v47).
- `ase_settings.json`: Persisted physics/VFX settings.
- `ase_project.json`: Project state (sources, mappings, platforms, NPCs).
- `ase_debug.log`: Runtime logs.

## 4. Instructions for Next Session
1. Run `python ase_viewer.py`.
2. **Platform Edit:** Click `EDIT PLAT`, drag blue boxes, or add new ones.
3. **Combat Test:** Try `Down + Jump` on platforms. Use `G` to summon dummy targets.
4. **Slow Motion:** Press `[` to test physics stability in slow motion.
5. **Shortcuts:** `Z` (Attack), `X` (Dash), `C/B/N` (Skills), `G` (Summon), `R-Click Tab` (Delete).
