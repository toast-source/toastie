# Aseprite Viewer Project Handover (v49)
**Date:** 2026-02-25
**Current Development Version:** v0.5.0.1
**Historical Version Label:** v49 (Swap System Restoration, VFX Polish & Render Optimization)

> Working-tree note (2026-07-23): The historical v49 label is retained separately. The current uncommitted development version is `v0.5.0.1`.

Development versions use `vMajorStage.FeatureStage.FeatureGroup.Fix`, so fixes
within this feature group advance from `v0.5.0.1` to `v0.5.0.2`; a new feature
group uses `v0.5.1.0`.

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

## 5. Uncommitted Stabilization Work (2026-07-22)
- Example buttons now resolve `Testfiles/Test01.aseprite` from the application/resource root instead of developer-specific absolute paths.
- Project sources and background images are saved relative to their JSON file when possible; legacy absolute paths remain readable.
- Missing paths are checked only near the project and application folders, then the user is prompted to reselect the source.
- Aseprite subprocess execution has a 120-second timeout, return-code/output validation, and concise user errors with technical log details.
- `python ase_viewer.py --check` verifies headless pygame initialization and one-frame rendering.
- `python ase_viewer.py --check-aseprite` performs a temporary export of `Testfiles/Test01.aseprite` without modifying user data.
- Automated tests cover persistence, portable paths, error cases, and conditionally the installed Aseprite CLI.

### Still requires manual verification
- EX 1/EX 2 button behavior and replacement-file dialog in the visible GUI.
- Existing multi-source projects whose original absolute paths no longer exist.
- Combat, swap, platform editing, and background reassignment workflows.

## 6. GUI and Packaging Stabilization (uncommitted, 2026-07-23)
- Added `--check-gui`, using only temporary paths and an in-memory source to exercise movement, dash, combo, swap, NPC, prop, platforms, update, and rendering.
- EX 1 and EX 2 now prepare their source before replacing current state. Both create PLAYER and NPC_1 profiles from the safe example source; they differ in background color, platform layout, and camera vertical offset.
- Project recovery is atomic: all missing paths and Aseprite exports must succeed. Canceling any replacement cancels the whole load and preserves current memory state and JSON.
- Repeated missing source paths are selected once per load.
- PyInstaller policy remains external-test-asset mode because distribution rights for `Testfiles/Test01.aseprite` are undocumented.
- A temporary PyInstaller build passed all three checks from space/Korean paths and a different working directory; repository `build/` and `dist/` were not used.
- See `MANUAL_TEST_CHECKLIST.md` for visible GUI regression steps.

## 7. EX 1 / EX 2 Resource Restoration (uncommitted, 2026-07-23)
- Restored the last complete presets from Git commit `5598e4d` and the
  previous local runtime JSON.
- Copied two shared Aseprite sources, the EX 1 lobby background, and all six EX 2
  parallax layers into `resources/examples`; originals were not changed.
- EX 1 now uses one lobby layer. EX 2 restores the six historical layers,
  ordering, offsets, alpha, parallax factors, and Loop X flags.
- Preset preparation validates every required checksum, Aseprite export, tag
  mapping, and image load before replacing any current in-memory state.
- Historical data contains one NPC profile/instance but no automatic prop
  source, profile, or spawn, so no prop configuration was invented.

## 8. NPC/PROP Slice Export and Source Integrity (uncommitted, 2026-07-23)

- `SETUP > NPCS` now exposes SAVE for explicitly classified NPC profiles; no
  live NPC instance is required.
- NPC and PROP SAVE share `export_source_slices()`. Parts excludes
  particle-named slices, while Particles includes only particle-named slices.
- Export sanitizes Windows filenames, supplies deterministic empty-name
  fallbacks, auto-renames collisions and existing files, saves through a
  same-directory temporary PNG, continues after individual failures, and
  reports saved/skipped/failed totals.
- Project saves now include optional `source_kinds` and profile `kind` fields
  while retaining schema version 2 and legacy loading behavior. Loading alone
  does not rewrite a project.
- Removing a source removes directly linked profiles and runtime NPC/PROP
  instances, shifts later source and mapping indices, repairs selection state,
  and refuses to save out-of-range profile references.
- Runtime NPC death still uses a 3x3 crop of the death frame rather than
  Parts/Particles slices. That combat behavior was intentionally not changed.
- Runtime prop positions/stages, particles, and export destinations remain
  transient and are not project data.

## 9. Layer Identity, DEAD_LOOP, and Slice Classification (uncommitted, 2026-07-23)

- Layer visibility now uses a source-local stable key made from original stack
  index and full layer path. Duplicate names and nested duplicate names can be
  toggled independently. Legacy name-only visibility is applied only when the
  name is unique; ambiguous names remain visible and generate a warning.
- A temporary Aseprite Lua export filter applies visibility by stack index
  without saving the source `.aseprite`. Visibility survives ordinary refresh
  while the source object remains loaded.
- Profiles include `DEAD_LOOP`. Auto-mapping recognizes case-insensitive
  `Dead_(Loop)`, `Dead_Loop`, `Dead Loop`, `DeadLoop` and corresponding
  `Death` forms before generic loop-suffix normalization, without replacing a
  manual mapping.
- A valid NPC `DEAD_LOOP` leaves a non-targetable, motionless corpse that
  respects forward/reverse/ping-pong playback and stops on the last frame when
  non-looping. Corpse state is runtime-only and is cleared by project/example
  reset or source removal.
- Without `DEAD_LOOP`, NPC death uses valid `Parts` Slice images first, then the
  existing 3x3 death-frame split, then colored debris. NPC and PROP share the
  precise Slice-debris helper but retain different lifetimes.
- SAVE is enabled only for a loaded source with a `Parts` tag and at least one
  non-empty Slice image in that tag range. AUTO scans all Parts/Particles
  frames; NAME retains the older name-based particle filter.
- Export names are deterministic `<Profile>_Parts_01.png` and
  `<Profile>_Particle_01.png`, with independent counters and collision suffixes.
  The result records the original Slice, representative frame, bounds, output
  name, status, and reason. Runtime 3x3 debris is not exportable.

## 10. LAYERS Regression Recovery (uncommitted, 2026-07-23)

- The regression came from treating `--list-layer-hierarchy` sprite-sheet JSON
  as a nested source inventory. Aseprite emits that JSON as flat render metadata
  without group rows, so groups and hierarchy disappeared from the UI.
- The original inventory is now collected separately through the Aseprite Lua
  API before any visibility override. It preserves the historical bottom-to-top
  stack order and records groups, depth, original visibility, image/tilemap/
  reference type, path, stack index, and UUID.
- Keys prefer `Layer.uuid`; the ordered inventory index plus path is also sent
  as a fallback because older files can receive a new transient UUID each time
  Aseprite opens them. The ordered list is never rebuilt from a set or sorted
  by name.
- The temporary export script applies an explicit UUID-keyed visibility map
  after writing the inventory. It does not save the source file and no longer
  forces every unselected/originally-hidden layer visible.
- Windows batch exports use a temporary APPDATA so large recovery/session data
  cannot block the headless CLI; the user's Aseprite settings remain untouched.
- Reload maps unchanged UUIDs, defaults new layers to their original visibility,
  drops deleted keys, and preserves the last good frames/list if export or
  inventory parsing fails.
- `--check-layers`, ordered binary Layer-chunk inspection, 35-row scroll tests,
  and inventory-to-render toggle tests were added. All repository fixtures are
  flattened single-layer files, so real duplicate/group behavior still needs a
  user-owned multi-layer file to be checked manually.

## 11. NPC Source AUTO Slice Analysis (uncommitted, 2026-07-23)

- Every successful `AseSource` export prepares one revision-bound AUTO analysis
  containing Parts/Particles tag ranges and valid non-empty Slice images.
- NPC/PROP creation, AUTO SAVE, hit Particles, and death/destruction Parts all
  consume that source cache. NAME remains a SAVE-only compatibility mode and
  cannot change runtime behavior.
- NPC hits use cached custom Particles when available and retain the existing
  colored fallback otherwise. Death priority remains DEAD_LOOP, cached Parts,
  3x3, then colored debris.
- A successful refresh swaps in frames, metadata, and the new analysis
  together. A failed export keeps the previous revision and analysis.
- NPC and PROP rows show compact Parts, Particles, and SAVE availability counts.

## 12. v0.5.1.0 Korean/English UI (uncommitted, 2026-07-23)

- Added a central Korean/English translation table with Korean as the default;
  the app-level `language` setting accepts only `ko`/`en`, remains compatible
  with older settings, and changes only when the user selects a language.
- Added a cached Windows Korean-capable system-font fallback and localized the
  main setup categories, NPC/PROP Slice status, export confirmation, export
  options, and completion summary. Technical names such as NPC, PROP, Parts,
  Particles, Slice, AUTO, NAME, and Aseprite remain visible.
- The Parts/Particles dialog now explains classification and filename modes,
  preserves an inactive target name, and previews target-based or actual Slice
  filenames as the options change.
- Next planned feature: Unity parallax-value export. It is not part of v0.5.1.0.

## 13. v0.5.1.1 Measured UI and hover help (uncommitted, 2026-07-23)

- Translated top-bar and NPC/PROP action buttons now use measured font widths,
  shared padding, bounded maximum widths, and non-overlapping row placement.
- Added shared word/character wrapping, path-aware ellipsis, and width-aware
  status ellipsis for Korean and English text.
- Added delayed translated hover tooltips for project, source, NPC/PROP export,
  Slice status, platform, physics, VFX, layer, camera, and parallax controls.
  AUTO/NAME and both export filename modes use the same tooltip policy in Tk.
- Unity parallax-value export remains the next separate task.

## 14. v0.5.1.2 Empty-project OPTIONS access (uncommitted, 2026-07-24)

- OPTIONS rendering is no longer gated by the presence of a profile; its button,
  click state, scrolling, language, physics, VFX, camera, guide, background, and
  other global settings remain available in a completely empty project.
- Source-dependent LAYERS content shows a translated disabled notice and the
  existing delayed tooltip instead of indexing a missing source or profile.
- Empty/add/remove transitions preserve the open OPTIONS state. Shared content
  height calculation keeps empty-project scrolling within a valid range.

## 15. v0.5.2.0 Unity parallax handoff (uncommitted, 2026-07-24)

- The Viewer runtime remains unchanged: layer center is screen center plus
  `(spawn - camera) * parallax * cameraZoom + offset * cameraZoom`; image size
  is `sourceSize * layerZoom * cameraZoom * 0.5`.
- Therefore Viewer parallax 0 is screen-fixed and 1 is world-fixed. The exact
  Unity Transform camera-follow ratio is `1 - viewerParallax`.
- Unity offsets use `(viewerX / PPU, -viewerY / PPU)`, and local scale uses
  `viewer layerZoom * 0.5`; camera zoom is deliberately excluded.
- BG IMAGE now opens a translated preview with PPU, detailed/compact format,
  disabled-layer inclusion, read-only text, and clipboard copy. Preferences
  are optional app settings and do not change the project schema.

## 16. v0.5.2.1 Unity sharing formats (uncommitted, 2026-07-24)

- The detailed handoff remains unchanged. The old `compact` setting is read as
  `slack` in memory without rewriting the settings file; newly saved values are
  `detailed`, `slack`, `markdown`, or `tsv`.
- Slack output uses Unicode display-width alignment, two narrow code-block
  tables, 24-column display-name truncation with a full-name map, a safe
  variable-length backtick fence, and a card fallback for oversized content.
- Jira/Notion output uses separate Parallax and Transform Markdown tables,
  escaped cells, and a separate Sources list. TSV output is metadata-free,
  tab-separated data with normalized layer-name line breaks and tabs.
- The export preview updates immediately, uses a fixed-width font, provides
  both scrollbars, wraps only detailed output, and reports included-layer and
  character counts. Copy confirmation is specific to the selected format.
- Viewer parallax, Unity follow, PPU, Y inversion, offset, scale, render order,
  project schema, and runtime background behavior are unchanged.

## 17. v0.5.2.2 Performance measurement and targeted optimization (uncommitted, 2026-07-24)

- Added a disabled-by-default 600-frame `PerformanceMonitor`. F10 toggles a
  four-Hz cached overlay with frame percentiles, update/render sections, object
  counts, tooltip regions, and text-cache usage. `--profile-performance`
  enables it at startup, prints five-second and exit summaries, and skips
  automatic project/settings saves when the profile window closes.
- `--benchmark-performance` runs 120 warm-up and 600 measured dummy-SDL frames
  with seed 240724, NPC 8, PROP 5, six backgrounds, 100 image Parts, and 100
  color particles. It uses temporary paths, creates no Tk window, disables the
  limiter, and does not save project or settings data.
- The comparable pre/post headless workload changed from 0.8413/1.1688 ms
  average/p95 to 0.7690/0.9383 ms. This is an 8.6% average and 19.7% p95
  reduction; the workload was already below 1 ms, so no visual-quality or
  behavior-changing optimization was added merely to reach a target.
- Confirmed work was concentrated in world rendering. Image Parts now reuse
  their exact same-zoom scaled Surface before rotation. Particle, Spark,
  Projectile, damage-number, afterimage, and temporary-AI survivors are
  compacted in one update pass instead of repeated list removal.
- UI text and measurement/wrap/ellipsis results use bounded 512-entry LRUs.
  Animation transformations include source revision in a bounded 256-entry
  cache. Language and window-size changes invalidate the relevant caches.
- The main frame no longer polls project existence, source mtimes, or
  background mtimes. Project availability is updated when saving, and source
  refresh remains available through the existing explicit F5 workflow.
- The next v0.5.3.0 task remains the resource/character selection UI: resource
  library, instance list, selection summary, clearer action labels, missing
  tooltip coverage, and a scrollable full Parts/Particles filename preview.

## 18. v0.5.3.0 Selection workspace and full export preview (uncommitted, 2026-07-24)

- The former `PLAYER`/`NPC_n` strip selected mapping profiles, while the lower
  strip selected `AseSource` data and could offer to remap the active profile.
  It did not enumerate actual NPC instances. The new Scene Actors tab derives
  rows from the player plus `ai_list` and `prop_list`, then maps a row back to
  the existing profile/source indices without changing project data.
- Current Selection shows the active scene target and resource. Friendly names
  prefer an explicit/profile name, then the Aseprite filename stem; generated
  `PLAYER`/`NPC_n`/`PROP_n` names are not exposed as primary labels. Repeated
  NPC/PROP names receive runtime-only `#n` suffixes.
- Resource Library rows show cached roles, instance counts, and already-known
  Parts/Particles counts. Actions map to the existing player selection, NPC
  spawn, PROP placement, source refresh, source removal, and Slice export
  paths. Unsupported actions remain disabled and retain bilingual tooltips.
- Both lists use a clamped visible-row range with one overscan row. Their model
  is cached by source revision, profile linkage, instance identity/state, and
  language; hidden rows do not render or register tooltips, and list drawing
  does not poll files or trigger Slice analysis.
- Slice export now builds one ordered plan shared by the modal preview and PNG
  writer. The preview shows every Parts/Particles filename in a vertically and
  horizontally scrollable list, group totals, naming/classification status,
  empty/error state, and the output-folder collision suffix notice. Editing
  only the target name reuses cached classification results.
- Runtime workspace tab/scroll/selection keys are not added to the project
  schema. Escape closes the workspace and Tab switches its two sections.

## 19. v0.5.3.1 Sidebar mode and clipping recovery (uncommitted, 2026-07-24)

- The v0.5.3.0 scene/resource buttons were drawn at `x >= play_w` but their
  click branches were nested under `x < play_w`, making both branches
  unreachable. Header clicks now test the real OPTIONS/scene/resource Rects
  before routing remaining world-toolbar clicks.
- Replaced the independent `show_settings` and `workspace_tab` state owners
  with one exclusive `sidebar_mode`: `mapping`, `settings`, `scene`, or
  `resources`. Clicking an active mode returns to mapping; clicking another
  mode switches directly without rendering two sidebar contents.
- The fixed sidebar header is `0..TOP_UI_HEIGHT`. OPTIONS now renders one
  content-height Surface in local coordinates and blits only at
  `(play_w, TOP_UI_HEIGHT)`. Settings clicks use the same translated origin,
  and tooltips are intersected with the content viewport before registration.
- Removed the duplicate scene/resource tabs inside the workspace. The fixed
  header remains the only mode switch while Current Selection and the current
  section title stay in the clipped content.
- Added `--check-sidebar-ui`, which builds a no-save, no-Aseprite three-source,
  three-profile, one-NPC, six-background stub; renders five temporary
  screenshots; and verifies header clicks, exclusive modes, and zero hidden
  control/tooltip overlap at a `-600` settings scroll.

## 20. v0.5.3.2 Scene object naming, placement preservation, and corpse cleanup (uncommitted, 2026-07-24)

- Scene rows now carry runtime-only `[PLAYER]`, `[NPC 01]`, and `[PROP 01]`
  badges. Corpse rows use an added `· CORPSE` marker. The badge order is
  recomputed from the current scene list and never changes resource names,
  filenames, object IDs, or the project schema.
- Resource-add paths previously had no contract protecting existing runtime
  actors while source/profile creation and subsequent count reconciliation
  occurred. The NPC, PROP, and refresh paths now snapshot existing actors by
  an explicit persistent ID when available, otherwise by object/profile
  identity plus instance ordinal. Position, spawn point, velocity, facing,
  visibility, scale/offset/rotation, animation, action, and death state are
  restored for pre-existing objects. The current scene selection key is also
  retained when its object still exists.
- Corpse detection prioritizes explicit corpse/dead flags and exact
  type/state/status/decision values. A corpse/remnant name match is used only
  when no explicit state exists. The Scene mode action removes only the
  selected NPC corpse by object identity, then selects the next/previous row
  or clears selection safely. Living selections and corpse-free scenes are
  no-ops with localized status text.
- The v0.5.3.1 exclusive `sidebar_mode`, fixed header, content viewport, and
  tooltip clipping remain unchanged. Targeted tests and
  `--check-sidebar-ui` verify all three add/refresh preservation paths,
  numbering, deletion/fallback, empty states, mode switching, and zero header
  overlap.
- Tests use stubs, mocks, and temporary data. No Aseprite CLI, user project or
  settings save, GUI-wide smoke, PyInstaller build, package, commit, or tag
  was performed. Manual follow-up should check real drag placement across
  NPC/PROP adds, corpse selection/deletion, minimum-window button clipping,
  deep OPTIONS scrolling, and Korean/English switching.

## 21. v0.5.4 Scene object management polish (uncommitted, 2026-07-24)

- Added session-only All, Player, NPC, Prop, and Corpse filters. Filtering is a
  pure view over the cached full scene rows; it does not reorder or mutate
  `ai_list`, `prop_list`, profiles, IDs, names, or JSON data. NPC excludes
  corpses, while Corpse uses the existing explicit-state-first helper. Badges
  retain their full-scene numbers across filters.
- A selected object hidden by a filter retains its runtime identity and is
  restored visibly when its type is shown again. Sidebar mode switches,
  language/model refresh, and resource add/refresh do not clear a surviving
  selection. Removal uses a next/previous row in the current filter and clears
  only when no visible fallback exists.
- Added Delete All Corpses without confirmation. It removes only corpse rows
  by instance identity, preserves living NPCs, PLAYER, and PROPs, reports the
  count, and compacts display numbering. A future confirmation step remains a
  possible UX enhancement if user testing shows it is needed.
- Focus Selected is implemented as a view-only action: it copies the selected
  object's finite `x/y` into `cam_x/cam_y` and disables automatic camera
  follow. It never changes object/player transforms, simulation state, or
  persisted settings/project data.
- The top-level F5 refresh path was found to bypass the v0.5.3.2 preservation
  wrapper even though Resource Library refresh already used it. F5 now shares
  the same snapshot/restore boundary around export and profile auto-mapping.
- Targeted tests cover filters, full-scene numbering, hidden selection,
  multi-corpse cleanup, living-object protection, fallback selection, camera
  focus, add/refresh transform preservation, empty states, and the three-action
  layout. Existing sidebar clipping remains at zero overlap under
  `--check-sidebar-ui`.
- No Aseprite CLI, user JSON save, LAYERS integration, full GUI smoke,
  PyInstaller build, release package, commit, or tag was performed. Manual
  checks remain necessary for real assets, minimum-window translated labels,
  camera feel, deep scrolling, and F10 overlay interaction.

## 22. v0.5.5.1 Partner roster / pivot hotfix (uncommitted, 2026-07-24)

- Plain file drop and `+ Source` now import only an `AseSource`; they no longer
  auto-create PLAYER/NPC profiles or instances. The legacy `+ NPC` and
  `+ PROP` buttons remain explicit import-and-assign shortcuts.
- Resource Library exposes Use as Player, Add as Partner, Add as NPC, and Add
  as Prop. A source stays generic when roles are assigned, and each non-player
  role receives a separate profile. NPC/PROP roles receive scene instances;
  Partner is roster-only. The source filename,
  path, ID, and other role profiles are not renamed or converted.
- Player assignment reuses or inserts the active profile at index zero,
  changes its source, remaps actions, and preserves the PLAYER transform and
  all existing actors. NPC/PROP additions create only the requested new
  instance; Add as Partner stores only a profile in `partner_profiles`.
- Partner means a standby Character Swap candidate, not a follower or scene
  actor. It has no render/update/AI/physics, scene row or numbering, Scene
  filter, Focus target, snapshot transform, HP, corpse path, or NPC count.
  Resources shows roster count, next candidate, and the T-key hint.
- Character Swap now prefers explicit partner profiles. A partner swap changes
  the incoming profile to PLAYER and the outgoing profile to Partner, rotates
  the outgoing profile into `partner_profiles`, and preserves the Player
  object's exact position, unrelated NPC/PROP transforms, and NPC count. When no explicit partner exists, the former
  non-PROP/NPC candidate path remains as a legacy fallback.
- EX 1/EX 2 keep the historical `NPC_1` profile name and mappings but classify
  that swap candidate as Partner and no longer place it in `ai_list`.
- Schema version remains 2. `partner` is an optional value in the existing
  profile `kind` field. Current loading accepts it as roster data and does not
  construct an `AseAI`. A v0.5.5 in-memory legacy `partner_list` actor can be
  absorbed into the profile roster; kind-less files retain first=Player/rest=NPC inference.
  No project is automatically migrated or saved.
- NPC ground alignment no longer depends on the old fixed
  `spawn_y = player.y - 100` compensation. New actors keep a world ground
  position and profiles copy a stable source offset: explicit pivot/anchor
  Slice first, otherwise the representative trimmed-frame bottom. The same
  metadata is used by Player, Partner-roster, NPC, and PROP profiles without
  recalculating existing scene object positions.
- 109 targeted stub/mock tests passed across 22 isolated modules. One initial
  broad `test_examples` invocation unintentionally ran its configured real
  Aseprite integration case before verification was narrowed to
  `ExampleTests`; it used temporary output and did not save user JSON or alter
  source assets. Full GUI smoke, LAYERS integration, PyInstaller, release
  package, commit, and tag were not run.

## 23. v0.5.5.2 Sidebar navigation / Tag Setup entry (uncommitted, 2026-07-24)

- The fixed sidebar header now owns four equal navigation buttons: Tag Setup,
  OPTIONS, Scene, and Resources. Tag Setup routes to the existing `mapping`
  mode; it does not introduce a new mapping format or registration subsystem.
- `set_sidebar_mode()` is now idempotent. Re-clicking an active button keeps
  that mode instead of silently falling back to mapping. All four hit targets
  remain entirely inside `x >= play_w`.
- Kept `TOP_UI_HEIGHT=70`; the four short labels fit in one row and the
  selection/resource summary remains below them. Settings, Scene, Resources,
  and mapping content continue to start at the same disjoint content origin.
- Mapping now renders a localized Tag / Animation Setup title and guidance
  even with no sources or profiles. A source-only state explains that role
  assignment and tag review are separate steps. Resource import status points
  users to Tag Setup as the next optional step.
- The mapping action list was moved below its title/help block while the tag
  list retains its lower panel. Click, right-click, and scroll coordinates use
  shared constants so drawing and interaction remain aligned.
- Partner remains a profile-only T-swap roster; Resource Role Assignment,
  SporeHeart ground alignment, and Player/NPC/PROP/F5 position preservation
  were not changed.
- 83 targeted and adjacent tests passed across 17 independently executed modules.
  `py_compile`, `--check-sidebar-ui`, and `git diff --check` passed. No
  Aseprite CLI, Example integration, LAYERS integration, full GUI smoke,
  PyInstaller, packaging, commit, or tag was run. User JSON, resources,
  build, and dist were not modified by this task.

## 24. v0.5.5.3 Placement label / first-run flow polish (uncommitted, 2026-07-24)

- Changed only the Korean user-facing Scene navigation label from `장면` to
  `배치`, and its content title to `배치된 캐릭터·오브젝트`. English keeps
  the compact `Scene` header label for continuity and minimum-width safety;
  its content title is now `Placed Characters & Objects`.
- Kept `SIDEBAR_SCENE == "scene"`, `sidebar_mode="scene"`, scene function
  names, object behavior, schema, and stored data unchanged.
- Clarified the first-run path: import in Resources, review tags/animations
  in Tag Setup, assign Player/NPC/Prop roles in Resources, then inspect placed
  characters and objects. Placement guidance deliberately excludes Partner;
  Partner remains a profile-only T-key swap roster.
- Added label-policy, Korean guidance, scene-button click, active-highlight,
  and internal-mode regression coverage. Existing four-button width,
  header/content clipping, OPTIONS scrolling, role assignment, T swap,
  SporeHeart ground alignment, position preservation, and corpse tests remain
  the adjacent verification set.
- 75 targeted and adjacent tests passed across 14 independently executed
  modules. `py_compile`, `--check-sidebar-ui`, and `git diff --check` also
  passed; the UI check reported zero header/content, hidden-control, and
  hidden-tooltip overlap.
- No Aseprite CLI, Example/LAYERS integration, full GUI smoke, PyInstaller,
  release packaging, commit, or tag is part of this polish. User JSON,
  original resources, build, and dist remain protected.

## 25. v0.5.6 Grounded Dash FX / Parallax Offset Gizmo (uncommitted, 2026-07-24)

- The former dash-dust block checked only `dash_timer > 0`, so an airborne
  dash emitted the same ground dust. Dash start now records whether it began
  grounded, and dust emission runs after the current frame's collision and
  grounding pass. Both start-grounded and current-grounded conditions must
  hold. Movement, velocity, landing logic, afterimages, and non-dash effects
  are not mutated by the helper.
- Added a default-OFF Parallax Gizmo toggle to `OPTIONS > BG IMAGE`. It targets
  the existing `bg_layers[active_bg_layer]`; no new selection model or layer
  schema was introduced. Missing, hidden, invalid, unloaded, and off-viewport
  layers safely produce no handle.
- The handle origin uses the same renderer expression as the background:
  camera/spawn parallax plus `off_x/off_y * zoom`. Screen drag deltas are
  divided by zoom and written to those existing offset fields, so right/down
  drag directions match layer motion and slider changes move the handle.
- Gizmo drag input takes priority over camera, platform, box, PROP, and actor
  selection input. Mouse-up stores changed offsets through the existing
  settings writer. The toggle itself is session-only and is deliberately not
  serialized to project or settings JSON.
- The gizmo changes editor offset metadata only. It never writes an original
  image or Aseprite file. Partner remains a profile-only T-swap roster, and
  SporeHeart ground alignment, role assignment, scene selection, corpse
  actions, and Player/NPC/PROP/F5 position preservation remain protected.
- 121 targeted and adjacent tests passed across 23 isolated modules.
  `py_compile`, `--check-sidebar-ui`, and `git diff --check` passed. No
  Aseprite CLI, Example/LAYERS integration, full GUI smoke, PyInstaller,
  release build, ZIP, commit, or tag was run.
- Manual follow-up: compare grounded versus jump/fall dash dust; drag several
  selected background layers at different zoom levels; confirm slider/handle
  synchronization, camera and selection input priority, Korean/English labels,
  minimum-window/deep-scroll layout, F10 overlay, Partner/T swap, SporeHeart
  alignment, F5 position preservation, and corpse actions.

## 26. v0.5.6.1 Parallax Gizmo axis lock / undo-redo (uncommitted, 2026-07-24)

- Chose explicit arrow handles rather than a persistent axis-mode toggle:
  center is Free, the red X handle changes only `off_x`, and the green Y
  handle changes only `off_y`. The handles share the existing play-viewport
  origin and disappear safely when unavailable or outside the viewport.
- Shift while dragging the center temporarily locks the dominant accumulated
  screen delta. Releasing Shift returns to Free movement in the same drag.
  Explicit X/Y handles remain locked regardless of Shift.
- Added a local parallax-offset history capped at 100 commands. Commands retain
  the runtime layer identity, index/path diagnostics, before/after offsets,
  and reason. A new command clears redo; deleted or replaced layer identities
  are skipped without applying an offset to another layer.
- Gizmo mouse-down captures before state, motion previews without history,
  and mouse-up records at most one command. Changing layer, disabling the
  gizmo, resizing, or losing focus cancels the preview and restores before.
- X/Y slider mouse-down-to-up is also one command; numeric offset Enter is one
  immediate command. The existing application has no offset-reset action, so
  no new reset UI was introduced.
- Global `Ctrl+Z` undoes the latest parallax command. `Ctrl+Y` and
  `Ctrl+Shift+Z` redo it. Active text entry retains priority and does not
  invoke history. Successful undo/redo uses the existing settings writer.
- History, redo, axis drag state, and gizmo visibility remain session-only and
  are absent from project/settings schemas. Only existing `off_x/off_y`
  persists; source image and Aseprite paths/files are never modified.
- Grounded dash dust, Partner roster/T swap, Resource Role Assignment,
  SporeHeart alignment, F5 position preservation, scene/corpse actions, and
  sidebar clipping remain unchanged. 138 tests across 25 isolated modules,
  `py_compile`, `--check-sidebar-ui`, and `git diff --check` passed.
- Aseprite CLI, Example/LAYERS integration, full GUI smoke, PyInstaller,
  release packaging, ZIP, commit, and tag were not run.

## 27. v0.5.7 Grounded Intro spawn / NPC behavior profiles (uncommitted, 2026-07-27)

- Added a dedicated `INTRO` profile mapping. Auto-map recognizes only explicit
  spawn aliases (`Intro`, `Spawn_Intro`, `Summon`, `Emerge`, `Appear`,
  `Entrance`, and normalized variants), avoiding action-specific names such
  as `Attack_Intro`.
- NPC and PROP `AseAI` instances no longer copy an airborne Player Y. Spawn X
  remains the existing facing-relative offset; Y resolves to the nearest
  platform below that X/current height, then falls back to `world_ground_y`.
  An available INTRO queue starts immediately from that grounded coordinate.
- Kept authored pivot and visible-bottom alignment separate from the entity
  ground coordinate. The pivot regression now verifies world-ground spawning
  and the same final sprite-bottom alignment independently.
- Added per-profile NPC behaviors: balanced legacy random, idle, follow,
  aggressive, guard/home return, patrol, and flee. Runtime instances read the
  profile each update, so changing a profile affects its existing and future
  NPCs without recreating them.
- Added a localized cycle control per NPC profile under
  `OPTIONS > AI & COMBAT > NPC Behavior`. Shared content-height calculation
  keeps click routing, scrolling, drawing, and clipping aligned.
- `ai_behavior` is an optional profile field inside schema version 2. Older
  files and unknown values normalize to `balanced`; settings, source paths,
  images, and Aseprite files are not changed.
- 181 stub/temp tests passed across 33 isolated modules, including Intro,
  grounded spawn, all behavior policies, optional-field round-trip, pivot,
  role/Partner/T-swap, position preservation, NPC/PROP death, animation,
  sidebar, localization, tooltip, parallax, persistence, path, and removal
  regressions. `py_compile`, sidebar check, and diff check passed.
- The real SporeHeart runtime module could not run because
  `SporeHeart.aseprite` is absent from the workspace. Aseprite CLI,
  Example/LAYERS integration, full GUI smoke, packaging, commit, and tag were
  not run.

## 28. v0.5.7.1 NPC combat hitbox / Intro replay / attack lock (uncommitted, 2026-07-27)

- Root cause: NPC AI directly restarted mapped ComboAttack actions but had no
  NPC-to-Player damage path, per-attack lock, active window, duplicate-hit
  guard, or post-animation cooldown. Player `check_hits()` handled only
  Player-to-NPC/PROP attacks.
- NPC attack start now selects only an available ComboAttack mapping, faces
  the Player once, locks the action/facing, and keeps essential gravity and
  ground collision active. Behavior updates return early while locked and
  NPC `trigger_action()` rejects interrupting actions. Animation completion
  enters a 650ms runtime-only recovery; malformed/stalled animation data has
  a documented 450ms duration plus 250ms grace fallback.
- Hit evaluation prefers the current authored `Hit` Slice. With no usable
  slice it uses a world-space, ground-aligned 125x80 rectangle in front of
  the locked facing. The normalized fallback window is 35% through 60%.
  A boolean instance guard applies at most one 5-point Player hit per attack.
- Existing behavior policy remains: balanced attacks only when its random
  branch selects attack; aggressive chases then attacks; guard attacks only
  nearby and returns home outside detection; idle/follow/patrol/flee do not
  attack.
- Added localized `Replay Intro` below the per-profile behavior controls.
  It targets a selected live scene NPC first, otherwise live instances of the
  current NPC profile. It never spawns or moves an actor, changes target
  counts, or touches PROP/Partner. Attack-locked NPCs are rejected/skipped so
  the hotfix cannot cancel their attack.
- `ai_behavior`, INTRO auto-map policy, and schema version 2 are unchanged.
  Attack/recovery/replay state is session-only. User project/settings JSON,
  source resources, build, and dist remain protected.
- Added isolated tests for attack lock/cooldown/fallback, front-facing
  hitboxes/authored slices/window/one-hit behavior, replay selection and
  safety, plus bilingual UI strings. Targeted adjacent Intro, pivot,
  Partner/T-swap, role, corpse, sidebar, dash, and parallax tests pass.
- Full discover remains unsuitable because pygame teardown exits the combined
  process. Known unrelated dirty-worktree tests still fail: a pre-existing
  layer-scroll expectation and empty-slice reason expectation. The real
  SporeHeart test remains unavailable because `SporeHeart.aseprite` is absent.
- No Aseprite CLI, Example/LAYERS integration, full GUI smoke, PyInstaller,
  packaging, ZIP, commit, or tag was run.
- Manual follow-up: tune the fallback hitbox and recovery against representative
  small/large NPCs; verify no animation restart, front/out-of-range/one-hit
  behavior, Intro replay/no-Intro/locked statuses, Korean/English deep-scroll
  layout, grounded Intro, Partner/T swap, SporeHeart alignment, F5 positions,
  dash dust, and parallax axis/undo/redo.
- TODO: regroup AI & COMBAT, NPC behavior, Intro replay, and future combat
  parameters into a clearer Settings panel without changing schemas.

## 29. v0.5.7.2 NPC combo / Intro lock / despawn / input guide (uncommitted, 2026-07-27)

- Combo discovery reads existing profile mappings and source tag metadata only.
  Exact numeric `ComboAttack_N` actions are sorted numerically and accepted
  only as a contiguous chain beginning at 1. Dynamic slots beyond 4 are added
  during auto-map when the source exposes a continuous numeric tag sequence.
  Plain `Attack` is a one-hit fallback; Intro/action-intro and nonnumeric
  suffixes are excluded.
- NPC attack start now stores the complete chain and locks facing for the
  entire combo. Natural action completion advances to the next segment
  internally without releasing the lock. Each segment resets elapsed time,
  duration, and its one-hit guard; only final completion starts the existing
  650ms cooldown. Invalid/zero-frame segments retain bounded fallback release.
- Added a runtime-only Intro lock for NPC and PROP. Spawn and replay Intro
  retain grounded X/Y, zero velocity, suppress AI/action interruption, and
  return to Idle/normal behavior after completion. Replaying an already-active
  Intro is a localized no-op; attack lock still has priority over replay.
- Added Scene `Despawn` for a selected living NPC. It removes only that
  runtime instance, decrements the global `target_ai_count` without going
  below zero, and reuses scene removal fallback selection. This prevents the
  automatic population loop from immediately recreating the NPC. Corpse,
  Player, PROP, Partner, source, and profile removal are deliberately excluded.
- Moved the bottom key guide to a common post-workspace HUD draw call. Mapping,
  Settings, Scene, and Resources now receive the same current-mapping,
  localized guide. It wraps at narrow play widths and keeps F10 discoverable
  while the performance overlay is active.
- There is no existing input-preset selector, so no keyboard settings were
  migrated or overwritten. Follow-up: generalized Fast Action/Action
  Platformer preset UI, controller detection and mapping, deadzone controls,
  dual keyboard/gamepad hints, and preset persistence. No commercial title is
  used in application UI.
- The protected resources folder was inspected read-only. Two example
  Aseprite files were present, but no separate safe tag metadata was available;
  Aseprite CLI was not invoked, so combo behavior is verified with stubs.
- Schema 2, `ai_behavior`, source files, user JSON, Partner roster/T swap,
  SporeHeart alignment, grounded spawn/dash dust, parallax history, and
  existing NPC hitbox policy remain unchanged.
- 126 targeted tests passed across 25 isolated modules, plus pycompile,
  sidebar UI check, and diff validation. Across every test file, 57 modules
  passed and the same three known unrelated modules remained: layer-scroll
  expectation, empty-slice reason expectation, and missing real SporeHeart
  fixture. No full GUI, CLI export, packaging, commit, or tag was run.

## 30. v0.5.7.3 App shortcut guide restore / input guide separation (uncommitted, 2026-07-27)

- Regression cause: v0.5.7.2 correctly moved the bottom guide to a common HUD
  draw stage, but replaced the old combined data with only mapped
  Attack/Dash/Jump/Swap plus F5/F10. The application event handlers remained
  intact; only their visible hints were lost.
- Split guide data into a key-map-driven Character group and a fixed,
  event-handler-backed App/Editor group. Character contains mapped
  Attack/Dash/Jump/Swap and available Skill1-3 keys. App/Editor restores the
  exact former P Pause, O Step, brackets Playback Speed, F5 Refresh,
  F10 Performance, H Hitbox, right-drag Camera, and F Camera Reset hints.
  No new shortcut or input behavior was introduced.
- The current playback speed is again included in the bracket hint. Changing
  a character mapping changes only the Character group; the App/Editor list
  remains independent even when `key_map` is empty.
- Layout begins each semantic group separately and wraps items across rows at
  narrow play widths. It remains a post-content fixed overlay in Mapping,
  Settings, Scene, and Resources, independent of deep scroll. F10 keeps both
  the guide and performance tooltip visible.
- Fast Action/Action Platformer planning is explicitly limited to character
  actions. It must never replace or suppress editor shortcuts. User mappings
  remain untouched. Controller detection, mapping, deadzone, dual hints, and
  preset persistence remain follow-up work.
- v0.5.7.2 combo, Intro lock, Despawn, target count, combat hitbox/cooldown,
  Partner/T swap, pivot alignment, dash dust, parallax history, and sidebar
  structure remain protected.
- 102 targeted tests passed across 21 isolated modules. Pycompile, sidebar
  check, and diff validation passed. Full per-file execution passed 59 modules;
  only the existing layer-scroll expectation, empty-slice reason expectation,
  and absent real SporeHeart fixture remain.

## 31. v0.5.7.4 Corpse ground snap / death state stabilization (uncommitted, 2026-07-27)

- Root cause: the early `AseAI.update()` corpse branch applied gravity only to
  airborne PROP corpses. NPC corpses instead received `vy = 0` and returned,
  while death transition retained the hit/knockback Y coordinate. An airborne
  death therefore froze permanently at that actor Y.
- Added a world-space NPC corpse grounding helper. It selects the nearest
  platform at the current X whose top is at/below the current actor Y, falling
  back to `world_ground_y`. It preserves X and spawn coordinates, snaps only
  logical Y, clears velocity, and sets grounded. Pivot/visible-bottom profile
  offsets remain renderer concerns and are not double-applied.
- Main death transition snaps before parts/corpse animation creation.
  `activate_corpse()` repeats the idempotent snap as a safe direct-entry guard.
  The corpse update branch repairs stale airborne NPC corpses but does nothing
  when already aligned, avoiding per-frame jitter.
- Death clears Intro lock, combo chain/index, attack lock/slot/timing,
  segment hit guard, cooldown, incoming-hit cooldown, pending execution, and
  velocity before the corpse state takes priority. Repeated death remains a
  no-op and does not duplicate instances.
- PROP corpse physics/destruction and live-NPC Despawn are intentionally
  separate and unchanged. Corpse filter, numbering, selection identity,
  Delete Corpse/Delete All, and F5 snapshot fields continue using the same
  object and snapped X/Y/grounded state.
- Added focused ground/platform/fallback/idempotency/malformed-state tests and
  death-during-Intro/Combo/attack-state plus snapshot stabilization tests.
  Ragdoll or animated corpse falling remains a future optional feature.
- 135 targeted tests passed across 27 isolated modules, including 14 new
  corpse tests. Pycompile, sidebar, and diff checks passed. Per-file execution
  passed 61 modules; only the existing layer-scroll expectation, empty-slice
  reason expectation, and missing real SporeHeart fixture remain.

## 32. v0.5.7.5 Swap visibility / guide clarity / safe NPC recall (uncommitted, 2026-07-27)

- Root cause of the T-swap overlap was render order: Player was drawn before
  every `temp_ai_list` actor, so the outgoing `Swap_Exit` sprite covered the
  incoming controllable Player. Swap departures are now explicitly classified
  as below-Player transient visuals and rendered first. Other NPC, PROP, and
  legacy/assist transient ordering is preserved.
- The departing actor remains visual-only and is still cleaned up by the
  existing temporary-actor lifecycle. It is not added to Partner or scene NPC
  rosters and no project/schema field was introduced.
- Added the current `SYNERGY` mapping to the Character guide. Default E and
  remapped keys are reflected; missing mappings stay absent. The existing
  synergy input handler and combat behavior were not changed.
- G recall now filters for visible, living, ordinary NPCs. Corpses, dead/zero-HP
  NPCs, PROP, Partner, and temporary actors keep their coordinates. An empty
  result is a localized safe no-op status.
- Clarified O as `1프레임 진행 / Step 1 frame` with a localized tooltip that
  states its paused-animation purpose. The event binding remains O.
- Added focused render-layer, guide/remap, corpse-exclusion, no-target, label,
  and swap-classification regression tests. No Aseprite CLI, full GUI,
  packaging, release, commit, or tag was run.
- Character/App guide separation remains intact; no commercial game name was
  introduced in UI. Controller detection/mapping and dual keyboard/gamepad
  hints remain follow-up work.
- Protected user/project data and generated/resource roots were not touched:
  `ase_project.json`, `ase_settings.json`, `build/`, `dist/`, and real source
  assets. Validation passed 108 tests in 23 targeted isolated modules,
  pycompile, `--check`, `--check-sidebar-ui`, headless multi-frame rendering,
  and diff check. Full per-file execution passed 65 modules / 367 tests; only
  the three pre-existing unrelated layer-scroll, empty-slice reason, and
  missing SporeHeart fixture modules failed.

## 33. v0.5.8 Settings UI/UX Reorganization (uncommitted, 2026-07-27)

- Root cause of OPTIONS complexity was one scroll model containing eleven
  accumulated accordion categories. Render, left-click, right-click, tooltip,
  and height code all traversed that complete list, making AI and background
  controls difficult to find and increasing deep-scroll stale-hit risk.
- Added a fixed two-row, six-section navigator inside OPTIONS: Quick, Input,
  AI / Combat, Background, View / Debug, and Advanced. Selection is a
  session-only local runtime value; returning from another sidebar mode keeps
  it for the session, while restart defaults to Quick.
- Every legacy category remains reachable exactly once. Quick owns Language
  plus selection/workflow guidance; Input owns Controls; AI owns NPCS and
  AI & COMBAT; Background owns BG IMAGE/BG COLOR; View owns JUICE & VFX,
  LAYERS, and CAMERA; Advanced owns PROPS and PHYSICS.
- Existing category drawing and editing code remains in place. Only the
  current section's categories participate in rendering and hit-testing.
  Section changes clear scroll, pending key binding, and numeric input, so
  hidden previous-section rectangles cannot act.
- The fixed navigator and scrolling body have separate clipping. Tooltips and
  continuous slider/toggle hit tests use the body viewport, while section
  buttons remain visible. Korean/English intros wrap up to two lines.
- Quick includes current selection and first-use flow. Input documents actual
  Character/App controls, Synergy, character-only Fast Action scope, and
  controller TODO. AI explains behavior/Intro/Combo/hitbox. Background
  explains layers, parallax, gizmo, axis lock, and undo/redo. View documents
  P/O/brackets/F10/H/camera. Advanced points to project/F5 tools.
- Project schema remains 2 and settings serialization has no section field.
  User key maps and AI behavior storage are unchanged. No new input, combat,
  background, controller, or editor feature was introduced.
- Preserved v0.5.7.5 swap layer, Synergy guide, recall filtering and O label;
  Combo/Intro/Despawn/corpse grounding; Partner roster; pivot/dash/parallax;
  and existing sidebar modes and bottom guides.
- No Aseprite CLI, real SporeHeart/Example/LAYERS integration, interactive GUI,
  PyInstaller, release/ZIP, commit, or tag. Protected user JSON, build/dist,
  real resources, and source Aseprite files were not modified.
- Validation passed 133 tests in 31 targeted isolated modules, pycompile,
  `--check`, expanded `--check-sidebar-ui`, and diff check. Full per-file
  execution ran 383 tests: 71 modules passed completely, while the only three
  failing modules were the same known layer-scroll expectation, empty-slice
  reason, and missing real SporeHeart fixture.

## 34. v0.5.8.1 Settings Tab Consolidation / Header Order Polish (uncommitted, 2026-07-27)

- Changed only the visual/header API order to Tag Setup, Scene/Placement,
  Resources, Options. Internal sidebar constants and mode strings are
  unchanged. Click targeting, drawing, selection-button helpers, the legacy
  options-rect helper, sidebar check, and order-dependent tests now share the
  same order.
- Consolidated six OPTIONS sections into three one-row tabs: Controls & App,
  Scene & Combat, and View & Background. Navigator height dropped from 76 to
  42 pixels while retaining the fixed-nav/clipped-body model.
- Removed Quick and Advanced from exposed tabs. Controls & App owns LANGUAGE
  and CONTROLS. Scene & Combat owns NPCS, AI & COMBAT, PROPS, and PHYSICS.
  View & Background owns BG IMAGE, BG COLOR, CAMERA, LAYERS, and JUICE & VFX.
  Coverage tests prove all eleven legacy categories occur exactly once.
- Old session-only names migrate without persistence: quick/input to
  controls_app, ai_combat/advanced to scene_combat, and
  background/view_debug to view_background. Invalid values default to
  controls_app. Project schema stays 2 and save_settings has no section field.
- Tab transitions continue to reset scroll, pending key binding, and numeric
  input, preventing stale hidden controls. The smaller viewport offset is used
  consistently by scroll clamp, tooltip clip, and continuous hit testing.
- Language and current key editing remain together. Fast Action stays limited
  to character controls and controller support remains TODO. Camera, layers,
  VFX, parallax, F10/H and right-drag/F guidance are now together.
- Preserved Character/App guides, Synergy and O label, T-swap layering,
  G corpse filtering, Combo/Intro/Despawn/corpse grounding, Partner roster,
  pivot/dash behavior, and parallax history.
- No Aseprite CLI, real asset integration, interactive GUI, packaging,
  release/ZIP, commit, or tag. User JSON, build/dist, resources, and Aseprite
  originals were not modified.
- Validation passed 125 tests in 30 targeted isolated modules, pycompile,
  `--check`, expanded sidebar check, and diff check. Full per-file execution
  ran 391 tests: 73 modules passed completely, with only the same three known
  layer-scroll, empty-slice-reason, and missing-SporeHeart-fixture modules.

## 35. v0.5.8.2 Settings Control Reset / Tab Semantics / UI Text Polish (uncommitted, 2026-07-27)

- Added a shared verified-default table, common non-overlapping row geometry,
  and one-value reset function for physics, AI/combat, VFX, camera, background
  layer, parallax, and RGB slider/numeric controls. Reset uses the existing
  settings save path; unknown defaults and invalid layers are safe no-ops.
- Offset X/Y resets preserve the sibling axis and push a normal parallax
  history command, so Ctrl+Z/Ctrl+Y restores and reapplies the reset.
- Moved LAYERS and JUICE & VFX from View & Background to Scene & Combat.
  View now owns BG IMAGE, BG COLOR, and CAMERA. All eleven categories remain
  covered exactly once across the same three session-only tabs.
- Removed the duplicate main-loop dash charge bars, retaining the single
  Player HUD indicator and the Dash key in the Character guide. F10 has no
  second dash counter; dash state/recharge and grounded dust are unchanged.
- Added shared Korean/English action labels without renaming key-map keys,
  plus compact tab subtitles and explicit empty background/NPC/key-map/
  Synergy states. Reset terminology remains separate from corpse/layer delete.
- Preserved header order, fixed navigation/body clipping, stale-rect reset,
  deep scroll, Character/App guides, Synergy/O, T swap, G recall, Combo,
  Intro, Despawn/corpse, Partner, pivot, dash dust, and parallax behavior.
- Project schema remains 2. No settings-section serialization, controller
  implementation, Fast Action mutation, Aseprite CLI, real-asset write,
  package/release, commit, or tag was performed. User JSON, build/dist,
  resources, and Aseprite originals remain protected.
- Validation passed 146 tests in 35 targeted isolated modules, pycompile,
  `--check`, `--check-sidebar-ui`, and diff check. Full per-file execution ran
  412 tests across 81 modules: 78 modules passed, and the only failures remain
  the known layer-scroll expectation, empty-slice reason, and absent real
  SporeHeart fixture.

## 36. v0.5.8.3 Pre-release Cleanup / Icon Build (uncommitted, 2026-07-27)

- Cleared the three accumulated baseline failures without changing runtime
  feature code. The layer test now verifies the real content/viewport scroll
  boundary, the Slice test uses independent valid mock state and target name,
  and the optional SporeHeart integration skips with an environment-variable
  instruction when its real fixture is absent.
- All 81 test modules passed (412 tests); one real SporeHeart integration was
  skipped. Source pycompile, application/sidebar checks, and diff check passed.
- Converted the untouched 1024px RGBA `Icon.png` into a multi-size
  `Icon.ico` and added only `icon='Icon.ico'` to the existing one-file spec.
  PE inspection found RT_ICON and RT_GROUP_ICON resources.
- Preserved existing build/dist directories and produced isolated diagnostic
  builds. Packaging is blocked: the supplied Python runtime has unusable Tcl
  initialization, PyInstaller excludes top-level tkinter, and EXE `--check`
  times out even when external example resources are temporarily supplied.
- No release ZIP or ZIP hash was created. The failed diagnostic EXE is
  25,300,425 bytes with SHA-256
  `B2BAD580507CE751ACFE2C2DD7316E688D96C03E7890EBE7A999D1D4FACFA2BC`.
  Rebuild from a healthy Python 3.12 Tcl/Tk installation and require both EXE
  checks to exit zero before packaging.
- This remains an unsigned interim build. Unknown Publisher/SmartScreen
  warnings are expected; code signing remains a follow-up TODO. No signtool,
  Store/MSIX, Aseprite CLI, interactive GUI, commit, or tag was used.

## 37. v0.5.8.3.1 Tcl/Tk Runtime Build Fix (uncommitted, 2026-07-28)

- Confirmed the active Python 3.12.13 venv can import tkinter, create and
  withdraw `Tk()`, and initialize Tcl/Tk 8.6.12. Its base runtime contains
  `tcl8.6`, `tk8.6`, `_tkinter.pyd`, `tcl86t.dll`, and `tk86t.dll`.
- The prior icon build failure was caused by Tcl initialization being blocked
  in its restricted build execution context, not by a broken Python install.
  An unrestricted PyInstaller 6.21.0 clean build applied the standard
  `_tkinter` analysis and runtime hooks without spec path overrides.
- Kept the one-file/windowed spec and `Icon.ico`. No manual Tcl datas,
  binaries, hidden imports, or custom runtime hook were required.
- Frozen `--check` now treats the nine deliberately unbundled examples as
  external optional resources while source `--check` remains strict. It opens
  no dialog: a withdrawn Tk root verifies Tcl, then is immediately destroyed.
- Targeted validation passed 50 tests in nine isolated modules with one
  optional real-SporeHeart fixture skip, plus pycompile, source application
  check, sidebar check, and diff check.
- Built `dist_v0.5.8.3_tkfix2/ase_viewer.exe` in isolated paths. The analysis
  includes `_tkinter.pyd`, Tcl/Tk DLLs and data, and `pyi_rth__tkinter.py`.
  Both EXE checks exit 0; the application check reports Tcl 8.6.12 and no
  process remains.
- EXE SHA-256:
  `299EF579A110C76C85A4122A6363B81E9360A41957E2D2AD7EFE001F877D0DBF`.
  The old `dist_v0.5.8.3_icon_final` remains a non-release diagnostic.
- Release ZIP size is 17,907,557 bytes; SHA-256 is
  `FC40F85DF40287302DABAD77CDDF4241CF86F9C00E9D4A2A781B741BD4BB9A3D`.
  The authoritative value is kept outside the ZIP in its companion
  `.sha256`, avoiding a self-referential package hash.
- The package remains unsigned. No signing, Store/MSIX, Aseprite CLI,
  real-asset integration, interactive full GUI, commit, tag, or deletion of
  existing build/dist output was performed.

## 38. v0.5.8.3 Example Resources Bundled Build (uncommitted, 2026-07-28)

- The company-internal package now places only `resources/examples` beside
  the EXE. It contains EX1, EX2, and shared resources: ten files / 2,790,927
  bytes, including all nine runtime-required files and the internal README.
- Reused the smoke-passed `dist_v0.5.8.3_tkfix2/ase_viewer.exe`; no source,
  spec, or PyInstaller rebuild was necessary because `app_resource_path`
  already falls back from `_MEIPASS` to the executable directory.
- From the staging directory, frozen `--check` found 9/9 examples and Tcl
  8.6.12, while `--check-sidebar-ui` also exited zero. No dialog or lingering
  process remained.
- Passed four packaged-path tests and twelve example tests. These cover
  Korean/space/hash filenames, recorded resource hashes, actual EX1/EX2
  source preparation, six-layer EX2 parallax rendering, and unchanged
  current-project state on preparation failure.
- The old `ase_viewer_v0.5.8.3_tkfix.zip` remains an examples-absent package
  and is not the internal EX-function deployment candidate. Only the new
  `with_examples` ZIP is marked as that candidate.
- Excluded project/settings JSON, non-example resources, user data, tests,
  source, caches, `.git`, `.gemini`, and all earlier build/dist outputs.
  Remained unsigned; no Aseprite CLI, full GUI automation, commit, or tag.
- Created `ase_viewer_v0.5.8.3_with_examples.zip` (20,612,661 bytes),
  SHA-256
  `7F5D7B75014CC355D5DC7D06499429B3BE7A3342FE8514871C4CE57622DD05B8`,
  plus its companion `.sha256`.
