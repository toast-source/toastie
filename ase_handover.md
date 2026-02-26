# Aseprite Viewer Project Handover (v49)
**Date:** 2026-02-25
**Current Version:** v49 (Swap System Restoration, VFX Polish & Render Optimization)

## 1. Project Overview
Pygame-based Aseprite previewer with action game physics. Focuses on accurate animation testing, combat logic validation, and easy asset management.

## 2. Recent Updates (v49)
- **Swap System Refinement:**
  - **Pending Swap Logic:** Restored original logic where pressing 'T' during an attack queues the swap. The existing character will finish its entire attack sequence and `attack_buffer` before executing `Swap_Exit`.
  - **Zombie NPC Fix:** Fixed an issue where swapped out NPCs (stored in `temp_ai_list`) would freeze permanently because their update loop was skipped. Now they correctly play `Swap_Exit` and are removed from memory.
  - **Swap VFX:** Replaced the chunky scaling yellow blob with a clean, thin yellow outline (stroke) using `mask.outline()` that flashes and fades out when a new character enters.
- **Rendering & Performance Optimizations:**
  - **V-Sync & HW Acceleration:** Added `pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1` to the display initialization and `VIDEORESIZE` events to prevent screen tearing.
  - **Sub-pixel Jitter Fix:** Casted all rendering coordinates (grid, platforms, boxes, backgrounds) to `int()` in the `draw` method to prevent elements from jittering when the camera moves quickly.
- **Controls & UI Improvements:**
  - **Keybindings:** Restored the ability to dynamically rebind controls in the `CONTROLS` settings tab. Clicking a key switches it to `PRESS KEY` mode. Added conflict resolution (Swap) so mapping an existing key automatically swaps the bindings instead of overwriting/losing one.
  - **Settings Scroll Limit:** Fixed a bug where the settings menu could scroll infinitely off-screen by dynamically calculating the total height of all expanded tabs.
  - **Slider Values:** Added numerical text readouts next to all `BG IMAGE` and `BG COLOR` sliders for precise adjustment.
- **Physics Logic:**
  - **Drop-Through Animation:** When dropping through a platform (`Down + Jump`), the `Fall_Ready` animation is explicitly skipped, and the player immediately transitions into `Fall_(Loop)` to feel more responsive.
  - **Solid Box Collision:** Reverted Y-axis solid box collision to strictly use the `player_rect` top/bottom bounds rather than a small foot sensor, fixing bugs where the character would sink into boxes.

## 3. Key Files in this Folder
- `ase_viewer.py`: Main logic.
- `ase_settings.json`: Persisted physics/VFX settings and custom controls.
- `ase_project.json`: Project state (sources, mappings, platforms, NPCs).
- `ase_debug.log`: Runtime logs.
- `ase_handover.md`: AI Context file tracking development state.

## 4. Instructions for Next Session
1. Run `python ase_viewer.py`.
2. **Verify Swap Logic:** Add multiple profiles/sources, execute attacks (`Z`), and press Swap (`T`). The original character should finish hitting, then trigger `Swap_Exit`. The new character should flash a yellow outline.
3. **Verify Settings:** Test scroll limits, check slider value displays, and test dynamic control rebinding.
4. **Test Physics:** Use Down + Jump on platforms to verify the correct fall animation bypass. Jump on Solid Boxes to verify the character lands cleanly on top.
