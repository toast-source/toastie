import pygame
import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import random
import math
import traceback

# Comprehensive Log Function
def log_debug(msg):
    with open("ase_debug.log", "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
    print(msg)

# Crash Catcher
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log_debug("[CRITICAL ERROR]")
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_debug(err_msg)

sys.excepthook = handle_exception

# Clean old log
if os.path.exists("ase_debug.log"): os.remove("ase_debug.log")
log_debug("[SYSTEM] v27 Combo-Lock & Ref-Fix Started")

class AsePathManager:
    def __init__(self):
        self.config_path = "config.json"
        self.path = self.load_config()
        if not self.path or not os.path.exists(self.path):
            self.path = self.find_aseprite()
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f).get("aseprite_path")
            except: return None
        return None
    def save_config(self, path):
        try:
            with open(self.config_path, "w") as f:
                json.dump({"aseprite_path": path}, f)
        except Exception as e: log_debug(f"[ERROR] Config save failed: {e}")
    def find_aseprite(self):
        candidates = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe",
            r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe",
            r"C:\Program Files\Aseprite\Aseprite.exe",
            r"D:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe"
        ]
        for c in candidates:
            if os.path.exists(c): return c
        return None
    def get_path(self):
        if self.path and os.path.exists(self.path): return self.path
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        selected = filedialog.askopenfilename(title="Select Aseprite.exe", filetypes=[("Executable", "Aseprite.exe")])
        root.destroy()
        if selected: 
            self.path = selected
            self.save_config(selected)
            return selected
        else: pygame.quit(); sys.exit()

ase_manager = AsePathManager()

def select_file(ftypes):
    try:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        path = filedialog.askopenfilename(filetypes=ftypes)
        root.destroy()
        return path
    except: return None

class AseSource:
    def __init__(self, file_path, source_id):
        self.id = source_id; self.file_path = os.path.abspath(file_path); self.name = os.path.basename(file_path)
        self.frames = []; self.tags = {}; self.tag_list = []; self.slices = {}; self.orig_w = self.orig_h = 0
        self.layers = []; self.visible_layers = set()
        self.last_mtime = os.path.getmtime(self.file_path)
        self.fetch_layers()
        self.export_and_load()
    def fetch_layers(self):
        try:
            exe = ase_manager.get_path()
            startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run([exe, "-b", "--list-layers", self.file_path], check=True, capture_output=True, text=True, startupinfo=startupinfo)
            self.layers = [l.strip() for l in res.stdout.split("\n") if l.strip()]
            self.visible_layers = set(self.layers) # Default all visible
            log_debug(f"[LAYERS] Found in {self.name}: {self.layers}")
        except Exception as e: 
            log_debug(f"[ERROR] Fetch layers failed for {self.name}: {e}")
            self.layers = []
    def check_for_reload(self):
        try:
            current_mtime = os.path.getmtime(self.file_path)
            if current_mtime > self.last_mtime:
                self.last_mtime = current_mtime
                self.export_and_load()
                return True
        except: pass
        return False
    def export_and_load(self):
        png_p = f"temp_{self.id}.png"; json_p = f"temp_{self.id}.json"
        self.frames = []; self.tags = {}; self.slices = {}
        try:
            exe = ase_manager.get_path()
            startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Build command: options first, then layers, then file
            cmd = [exe, "-b"]
            # If not all layers are visible, specify which ones to include
            if len(self.visible_layers) < len(self.layers):
                for l in self.layers:
                    if l in self.visible_layers:
                        cmd.extend(["--layer", l])
            
            cmd.extend([self.file_path, "--trim", "--sheet", png_p, "--data", json_p, "--format", "json-array", "--list-tags", "--list-slices"])
            
            subprocess.run(cmd, check=True, capture_output=True, startupinfo=startupinfo)
            sheet = pygame.image.load(png_p).convert_alpha()
            with open(json_p, 'r', encoding='utf-8') as f: data = json.load(f)
            self.orig_w, self.orig_h = data['frames'][0]['sourceSize']['w'], data['frames'][0]['sourceSize']['h']
            for f in data['frames']:
                r, s = f['frame'], f['spriteSourceSize']
                surf = pygame.Surface((r['w'], r['h']), pygame.SRCALPHA); surf.blit(sheet, (0, 0), (r['x'], r['y'], r['w'], r['h']))
                self.frames.append({'img': surf, 'ox': s['x'] - self.orig_w // 2, 'oy': s['y'] - self.orig_h // 2, 'duration': f.get('duration', 100)})
            if 'meta' in data:
                if 'frameTags' in data['meta']:
                    for t in data['meta']['frameTags']: self.tags[t['name']] = (t['from'], t['to'])
                if 'slices' in data['meta']:
                    for s in data['meta']['slices']: self.slices[s['name']] = s['keys']
            self.tag_list = sorted(list(self.tags.keys()))
            log_debug(f"[LOAD] {self.name} (Layers: {len(self.layers)}) Success.")
        except Exception as e: 
            log_debug(f"[ERROR] Load failed for {self.name}: {e}")
            self.frames = [{'img': pygame.Surface((32,32), pygame.SRCALPHA), 'ox':0, 'oy':0, 'duration':100}]
        finally:
            for p in [png_p, json_p]: 
                if os.path.exists(p): os.remove(p)

class AseProfile:
    def __init__(self, name, source_idx):
        self.name = name; self.source_idx = source_idx
        self.mappings = { "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ComboAttack_1": [], "ComboAttack_2": [], "ComboAttack_3": [], "ComboAttack_4": [], "JUMPATTACK": [], "POWERBOMB": [], "DASH": [], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [], "Swap_Exit": [] }

class AseAI:
    def __init__(self, master, profile):
        self.master = master; self.profile = profile; self.spawn_x = random.randint(300, 1500); self.spawn_y = 500
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = True; self.facing_right = random.choice([True, False])
        self.frame_idx = 0; self.anim_timer = 0; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.ai_timer = random.randint(30, 90); self.decision = "IDLE"
        self.swap_timer = 0; self.visible = True; self.active_action_slot = None
    def update(self, ground_y, dt):
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0:
                self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        self.ai_timer -= 1; dist_p = self.master.x - self.x
        if self.ai_timer <= 0:
            choices = ["IDLE", "CHASE", "ATTACK", "DASH", "JUMP", "SWAP"] if abs(dist_p) < 600 else ["IDLE", "WALK_L", "WALK_R"]
            self.decision = random.choice(choices); self.ai_timer = random.randint(40, 120)
            if self.decision == "SWAP": self.trigger_action("Swap_Exit")
            elif self.decision == "ATTACK" and abs(dist_p) < 200: self.facing_right = dist_p > 0; self.trigger_action(f"ComboAttack_{random.randint(1,4)}")
            elif self.decision == "DASH": self.facing_right = dist_p > 0; self.trigger_action("DASH")
            elif self.decision == "JUMP" and self.grounded: self.vy = self.master.jump_power; self.grounded = False
        self.vx *= 0.85
        if not self.active_tag_info:
            if self.decision == "WALK_R": self.vx = 4; self.facing_right = True
            elif self.decision == "WALK_L": self.vx = -4; self.facing_right = False
            elif self.decision == "CHASE": self.vx = 5.5 if dist_p > 0 else -5.5; self.facing_right = dist_p > 0
            if abs(dist_p) < 100: self.decision = "IDLE"
        if self.active_tag_info and self.active_tag_info[1] == "DASH": self.vy = 0
        else: self.vy += self.master.gravity
        self.x += self.vx; self.y += self.vy
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True
        if self.vy >= 0:
            for plat in self.master.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - self.vy <= plat.top + 10: self.y = plat.top; self.vy = 0; self.grounded = True
        if self.grounded and self.active_tag_info:
            if "(loop)" in self.active_tag_info[1].lower(): self.active_tag_info = None; self.active_action_slot = None
        target_info = None
        if not self.active_tag_info:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            m = self.profile.mappings.get(state, []); target_info = m[0] if m else None
        else: target_info = self.active_tag_info
        if target_info:
            src = self.master.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
            if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
            if not self.master.is_paused:
                self.anim_timer += dt * self.master.playback_speed
                if self.frame_idx < len(src.frames):
                    frame_duration = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= frame_duration:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit": self.visible = False; self.swap_timer = 500; self.active_tag_info = None; self.active_action_slot = None; return
                            if "(loop)" in target_info[1].lower(): self.frame_idx = tr[0]
                            elif self.action_queue: self.active_tag_info = self.action_queue.pop(0); s = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = s.tags.get(self.active_tag_info[1], (0,0))
                            else: self.active_tag_info = None; self.active_action_slot = None
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]

    def trigger_action(self, slot):
        tags = self.profile.mappings.get(slot, [])
        if tags:
            self.active_action_slot = slot
            self.action_queue = list(tags); self.active_tag_info = self.action_queue.pop(0)
            src = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = src.tags.get(self.active_tag_info[1], (0,0)); self.anim_timer = 0
            if slot == "DASH": self.vx = 8 if self.facing_right else -8

class AsepritePlayer:
    def __init__(self, initial_path):
        self.sources = []; self.profiles = []; self.cur_profile_idx = 0; self.cur_source_idx = 0
        self.add_source(initial_path); self.add_profile("PLAYER", 0)
        self.spawn_x, self.spawn_y = 400, 500; self.x, self.y = self.spawn_x, self.spawn_y
        self.vx = self.vy = 0; self.grounded = False; self.jumps_left = 2; self.facing_right = True; self.zoom = 3.0
        self.dash_speed = 12.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 15.0; self.powerbomb_speed = 35.0; self.cam_v_offset = -120
        self.pbomb_pause_timer = 0; self.loop_counter = 0; self.cam_x, self.cam_y = 400, 300; self.cam_follow = True
        self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20), pygame.Rect(-200, 250, 300, 20), pygame.Rect(900, 300, 400, 20)]
        self.bg_img = None; self.bg_off_x = self.bg_off_y = 0; self.bg_zoom = 1.0; self.bg_alpha = 255; self.bg_parallax = 0.1; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]
        self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0; self.active_action_slot = None; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1
        self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0; self.attack_move_timer = 0; self.ai_list = []; self.swap_timer = 0; self.visible = True
        self.playback_speed = 1.0; self.is_paused = False; self.step_forward = False; self.show_hitboxes = True
        self.target_w, self.target_h = 640, 360; self.show_viewport = True
        self.shake_timer = 0; self.shake_intensity = 0; self.shake_enabled = True; self.base_shake = 1.0; self.afterimages = []; self.vfx_enabled = True; self.ghost_timer = 0
        self.load_settings()

    def save_settings(self):
        data = {
            "physics": {"dash_speed": self.dash_speed, "jump_power": self.jump_power, "powerbomb_speed": self.powerbomb_speed, "cam_v_offset": self.cam_v_offset},
            "combat": {"atk_forward_v": self.atk_forward_v},
            "vfx": {"shake_enabled": self.shake_enabled, "vfx_enabled": self.vfx_enabled, "base_shake": self.base_shake},
            "viewport": {"show_viewport": self.show_viewport, "target_w": self.target_w, "target_h": self.target_h},
            "bg": {"bg_color": self.bg_color, "bg_alpha": self.bg_alpha, "bg_zoom": self.bg_zoom, "bg_parallax": self.bg_parallax, "bg_off_x": self.bg_off_x, "bg_off_y": self.bg_off_y}
        }
        try:
            with open("ase_settings.json", "w") as f: json.dump(data, f)
        except: pass

    def load_settings(self):
        if os.path.exists("ase_settings.json"):
            try:
                with open("ase_settings.json", "r") as f: data = json.load(f)
                for cat in data.values():
                    for k, v in cat.items():
                        if hasattr(self, k): setattr(self, k, v)
            except: pass

    def add_source(self, path):
        try:
            new_source = AseSource(path, len(self.sources)); self.sources.append(new_source); self.cur_source_idx = new_source.id
            return new_source.id
        except: return 0
    def add_profile(self, name, source_idx, is_npc=False):
        new_profile = AseProfile(name, source_idx); self.profiles.append(new_profile); self.auto_map_profile(new_profile)
        if is_npc: self.ai_list.append(AseAI(self, new_profile))
    def auto_map_profile(self, profile):
        if profile.source_idx >= len(self.sources): return
        source = self.sources[profile.source_idx]; suffix = re.compile(r"(_|\s)?\(?(ready|loop|end)\)?", re.IGNORECASE)
        for slot in profile.mappings.keys():
            base_slot = slot.lower().replace("ComboAttack_", "attack").replace(" ", "").replace("_", "")
            matches = []
            for t in source.tag_list:
                clean_t = suffix.sub("", t).lower().replace(" ", "").replace("_", "")
                if clean_t == base_slot or (base_slot == "walk" and clean_t == "move"): matches.append((profile.source_idx, t))
            def sort_key(item): tl = item[1].lower(); return 0 if "ready" in tl else (2 if "end" in tl else 1)
            profile.mappings[slot] = sorted(matches, key=sort_key)
    def handle_attack(self, keys):
        if self.swap_timer > 0: return
        if not self.grounded:
            if keys[pygame.K_DOWN]: self.trigger_action("POWERBOMB", keys)
            else: self.trigger_action("JUMPATTACK", keys)
        else:
            if self.active_action_slot and "ComboAttack" in str(self.active_action_slot):
                if self.attack_buffer < 2: self.attack_buffer += 1; log_debug(f"[COMBO] Buffered: {self.attack_buffer}")
                return
            slot = f"ComboAttack_{self.combo_step+1}"
            if self.profiles[0].mappings.get(slot): 
                self.trigger_action(slot, keys)
    def trigger_action(self, slot, keys=None):
        if self.swap_timer > 0: return
        if self.active_action_slot and "ComboAttack" in str(self.active_action_slot):
            if slot == "DASH": self.attack_buffer = 0
            else: return 
        profile = self.profiles[0]; tags = profile.mappings.get(slot, [])
        if not tags and slot != "DASH": return
        if slot == "DASH" and self.dash_charges > 0:
            self.dash_charges -= 1
            for i in range(2): 
                if self.dash_cooldowns[i] <= 0: self.dash_cooldowns[i] = 90; break
            self.dash_timer = 12; self.vx = self.dash_speed if self.facing_right else -self.dash_speed; self.vy = 0; self.active_action_slot = "DASH"; self.action_queue = list(tags); self.play_next_in_queue(); return
        if tags:
            self.active_action_slot = slot; self.action_queue = list(tags); self.loop_counter = 0; self.anim_timer = 0
            if "ComboAttack" in slot:
                self.combo_step = (self.combo_step + 1) % 4; self.combo_reset_timer = 80
                curr_keys = keys if keys is not None else pygame.key.get_pressed()
                if curr_keys[pygame.K_RIGHT] or curr_keys[pygame.K_LEFT]:
                    self.attack_move_timer = 15; self.facing_right = curr_keys[pygame.K_RIGHT]
                    move_v = self.atk_forward_v * 0.4 
                    self.vx = move_v if self.facing_right else -move_v
                else: self.attack_move_timer = 0; self.vx = 0
                if self.combo_step == 0 and self.shake_enabled: self.shake_timer = 10; self.shake_intensity = 8
            elif slot == "POWERBOMB": self.pbomb_pause_timer = 15; self.vy = 0; self.vx = 0
            self.play_next_in_queue()
    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag_info = self.action_queue.pop(0); src = self.sources[self.active_tag_info[0]]
            if self.active_tag_info[1] in src.tags: self.frame_idx, self.action_end_frame = src.tags[self.active_tag_info[1]]; self.loop_counter = 0; self.anim_timer = 0
            else: self.play_next_in_queue()
        else:
            if self.attack_buffer > 0:
                self.attack_buffer -= 1; slot = f"ComboAttack_{self.combo_step+1}"
                if self.profiles[0].mappings.get(slot): self.active_action_slot = None; self.trigger_action(slot); return
            self.active_tag_info = None; self.active_action_slot = None; self.attack_buffer = 0; self.combo_step = 0; self.combo_reset_timer = 0
    def update(self, keys, ground_y, dt):
        if self.shake_timer > 0: self.shake_timer -= dt / 16.6
        if self.vfx_enabled:
            for ai in self.afterimages[:]:
                ai['alpha'] -= 15 * (dt/16.6)
                if ai['alpha'] <= 0: self.afterimages.remove(ai)
            if self.dash_timer > 0:
                self.ghost_timer += dt
                if self.ghost_timer >= 30: 
                    self.ghost_timer = 0; src_idx = self.active_tag_info[0] if self.active_tag_info else 0
                    self.afterimages.append({'x': self.x, 'y': self.y, 's': src_idx, 'f': self.frame_idx, 'right': self.facing_right, 'alpha': 180})
        if pygame.time.get_ticks() % 60 == 0:
            for src in self.sources:
                if src.check_for_reload():
                    log_debug(f"[WATCH] {src.name} reloaded."); [self.auto_map_profile(p) for p in self.profiles]
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        for i in range(2):
            if self.dash_cooldowns[i] > 0:
                self.dash_cooldowns[i] -= dt/16.6 
                if self.dash_cooldowns[i] <= 0: self.dash_charges = min(2, self.dash_charges + 1)
        if self.pbomb_pause_timer > 0:
            self.pbomb_pause_timer -= 1; self.vy = 0
            if self.pbomb_pause_timer == 0: self.vy = self.powerbomb_speed
        elif self.dash_timer > 0: self.dash_timer -= 1; self.vy = 0
        elif self.attack_move_timer > 0: self.attack_move_timer -= 1; self.vy += self.gravity * 0.5
        else:
            self.vx *= 0.82; can_move = not self.active_tag_info or self.active_action_slot == "JUMPATTACK"
            if can_move:
                if keys[pygame.K_RIGHT]: self.vx = 6.5; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -6.5; self.facing_right = False
            self.vy += self.gravity
        self.x += self.vx; self.y += self.vy; self.grounded = False
        if self.y >= ground_y: 
            if self.active_action_slot == "POWERBOMB" and self.vy > 0 and self.shake_enabled: self.shake_timer = 15; self.shake_intensity = 15
            self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
        if self.vy >= 0:
            for plat in self.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - self.vy <= plat.top + 10: self.y = plat.top; self.vy = 0; self.grounded = True; self.jumps_left = 2
        if self.grounded and (self.active_action_slot == "JUMPATTACK" or self.active_action_slot == "POWERBOMB"):
            if self.active_tag_info: self.play_next_in_queue()
        if self.cam_follow:
            self.cam_x += (self.x - self.cam_x) * 0.12; self.cam_y += (self.y + self.cam_v_offset - self.cam_y) * (0.3 if self.grounded else 0.12)
        if self.combo_reset_timer > 0 and not self.active_tag_info:
            self.combo_reset_timer -= 1
            if self.combo_reset_timer <= 0: self.combo_step = 0
        if self.visible:
            if not self.active_tag_info:
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
                m = self.profiles[0].mappings.get(state, []); target_info = m[0] if m else None
            else: target_info = self.active_tag_info
            if target_info:
                src = self.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
                if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
                if not self.is_paused or self.step_forward:
                    self.anim_timer += dt * self.playback_speed
                    if self.step_forward: self.anim_timer = src.frames[self.frame_idx]['duration']; self.step_forward = False
                if self.frame_idx < len(src.frames):
                    frame_duration = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= frame_duration:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit": self.visible = False; self.swap_timer = 500; self.active_tag_info = None; return
                            is_skill = "SKILL" in str(self.active_action_slot); is_loop = "(loop)" in target_info[1].lower()
                            if is_loop and is_skill and self.loop_counter < 1: self.frame_idx = tr[0]; self.loop_counter += 1
                            elif is_loop and not is_skill: self.frame_idx = tr[0]
                            else: self.play_next_in_queue()
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]
        for ai in self.ai_list: ai.update(ground_y, dt)
    def draw_sprite(self, screen, x, y, source_idx, f_idx, facing_right, cam_x, cam_y, cx, cy):
        if source_idx >= len(self.sources): return
        src = self.sources[source_idx]; f = src.frames[min(max(0, f_idx), len(src.frames)-1)]
        scaled = pygame.transform.scale(f['img'], (int(f['img'].get_width()*self.zoom), int(f['img'].get_height()*self.zoom)))
        ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
        if not facing_right: scaled = pygame.transform.flip(scaled, True, False); ox = -ox - scaled.get_width()
        screen.blit(scaled, (int(cx + (x - cam_x)*self.zoom + ox), int(cy + (y - cam_y)*self.zoom + oy)))
        if self.show_hitboxes:
            for name, keys in src.slices.items():
                active_key = None
                for key in keys:
                    if key['frame'] <= f_idx:
                        if active_key is None or key['frame'] > active_key['frame']: active_key = key
                if active_key:
                    b = active_key['bounds']; sx = cx + (x - cam_x) * self.zoom; sy = cy + (y - cam_y) * self.zoom
                    final_x = sx + (b['x'] - src.orig_w // 2) * self.zoom; final_y = sy + (b['y'] - src.orig_h // 2) * self.zoom
                    final_w = b['w'] * self.zoom; final_h = b['h'] * self.zoom
                    if not facing_right: final_x = sx - (b['x'] - src.orig_w // 2 + b['w']) * self.zoom
                    col = (220, 38, 38) if "hit" in name.lower() else (22, 163, 74)
                    pygame.draw.rect(screen, col, (final_x, final_y, final_w, final_h), 2)
                    if self.zoom > 1.5: txt = pygame.font.SysFont("Arial", 10).render(name, True, col); screen.blit(txt, (final_x, final_y - 12))
    def draw(self, screen, play_w, play_h):
        cx, cy = play_w // 2, play_h // 2
        off_x = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0
        off_y = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0
        cam_x, cam_y = self.cam_x + off_x, self.cam_y + off_y
        gx, gy = cx - (cam_x % 100)*self.zoom, cy - (cam_y % 100)*self.zoom
        for i in range(-10, 20):
            pygame.draw.line(screen, self.grid_color, (gx+i*100*self.zoom, 0), (gx+i*100*self.zoom, play_h), 1)
            pygame.draw.line(screen, self.grid_color, (0, gy+i*100*self.zoom), (play_w, gy+i*100*self.zoom), 1)
        if self.bg_img:
            bw, bh = int(self.bg_img.get_width()*self.bg_zoom*self.zoom*0.5), int(self.bg_img.get_height()*self.bg_zoom*self.zoom*0.5)
            bs = pygame.transform.scale(self.bg_img, (bw, bh))
            if self.bg_alpha < 255: bs.set_alpha(self.bg_alpha)
            bx = cx + (self.bg_off_x - cam_x * self.bg_parallax) * self.zoom - bw // 2
            by = cy + (self.bg_off_y - cam_y * self.bg_parallax) * self.zoom - bh // 2
            screen.blit(bs, (bx, by))
        for p in self.platforms: pygame.draw.rect(screen, (80,80,100), (cx+(p.x-cam_x)*self.zoom, cy+(p.y-cam_y)*self.zoom, p.w*self.zoom, p.h*self.zoom), border_radius=int(3*self.zoom))
        pygame.draw.line(screen, (100,100,100), (cx+(0-cam_x)*self.zoom, cy+(500-cam_y)*self.zoom), (cx+(5000-cam_x)*self.zoom, cy+(500-cam_y)*self.zoom), 2)
        if self.vfx_enabled:
            for ai in self.afterimages:
                src = self.sources[ai['s']]; f = src.frames[min(ai['f'], len(src.frames)-1)]; img = f['img'].copy()
                img.fill((100, 150, 255, ai['alpha']), special_flags=pygame.BLEND_RGBA_MULT)
                scaled = pygame.transform.scale(img, (int(img.get_width()*self.zoom), int(img.get_height()*self.zoom)))
                ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
                if not ai['right']: scaled = pygame.transform.flip(scaled, True, False); ox = -ox - scaled.get_width()
                screen.blit(scaled, (int(cx + (ai['x'] - cam_x)*self.zoom + ox), int(cy + (ai['y'] - cam_y)*self.zoom + oy)))
        if self.visible:
            cur_s = self.active_tag_info[0] if self.active_tag_info else 0
            if not self.active_tag_info:
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
                m = self.profiles[0].mappings.get(state, []); cur_s = m[0][0] if m else 0
            self.draw_sprite(screen, self.x, self.y, cur_s, self.frame_idx, self.facing_right, cam_x, cam_y, cx, cy)
        for ai in self.ai_list:
            if ai.visible:
                ai_s = ai.active_tag_info[0] if ai.active_tag_info else ai.profile.source_idx
                self.draw_sprite(screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right, cam_x, cam_y, cx, cy)
            adx, ady = (ai.x-cam_x)*self.zoom, (ai.y-cam_y)*self.zoom
            if abs(adx)>play_w//2 or abs(ady)>play_h//2:
                ang = math.atan2(ady, adx); px, py = cx+math.cos(ang)*(play_w//2-40), cy+math.sin(ang)*(play_h//2-40)
                pygame.draw.circle(screen, (220,38,38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(ang)*8, py-math.sin(ang)*8), 2)
        
        # Viewport Guide (640x360)
        if self.show_viewport:
            vw, vh = self.target_w * self.zoom, self.target_h * self.zoom
            v_rect = pygame.Rect(cx - vw//2, cy - vh//2, vw, vh)
            # Draw darkened area outside viewport
            overlay = pygame.Surface((play_w, play_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160)) # Semi-transparent black
            pygame.draw.rect(overlay, (0, 0, 0, 0), v_rect) # Punch a hole for viewport
            screen.blit(overlay, (0, 0))
            # Draw thin border
            pygame.draw.rect(screen, (255, 255, 255), v_rect, 1)
            # Label
            v_txt = pygame.font.SysFont("Arial", 12).render(f"Viewport: {self.target_w}x{self.target_h} (16:9)", True, (255,255,255))
            screen.blit(v_txt, (v_rect.x, v_rect.y - 18))

def main():
    pygame.init(); screen = pygame.display.set_mode((1350, 850), pygame.RESIZABLE); clock = pygame.time.Clock(); player = None; selected_slot = None; show_settings = False; slot_scroll = 0; tag_scroll = 0; settings_scroll = 0; font_s = pygame.font.SysFont("Arial", 12); font_b = pygame.font.SysFont("Arial", 14, bold=True); font_h = pygame.font.SysFont("Arial", 11); is_dragging_cam = False; last_m_pos = (0,0)
    folds = {"PHYSICS": True, "AI & COMBAT": True, "JUICE & VFX": True, "LAYERS": True, "VIEWPORT": True, "BG IMAGE": True, "BG COLOR": True}
    while True:
        dt = clock.tick(60); sw, sh = screen.get_size(); sidebar_w = 450; play_w = sw - sidebar_w; play_h = sh - 70; m_pos = pygame.mouse.get_pos(); bg_col = player.bg_color if player else [15, 15, 18]; screen.fill(bg_col)
        if player: player.update(pygame.key.get_pressed(), 500, dt); player.draw(screen, play_w, play_h)
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)); pygame.draw.rect(screen, (35, 35, 40), (0, 0, play_w, 70))
        new_proj = pygame.Rect(10, 5, 120, 30); pygame.draw.rect(screen, (220, 38, 38), new_proj, border_radius=5); screen.blit(font_b.render("NEW PROJECT", True, (255,255,255)), (20, 10))
        add_src = pygame.Rect(140, 5, 100, 30); pygame.draw.rect(screen, (59, 130, 246), add_src, border_radius=5); screen.blit(font_b.render("+ SOURCE", True, (255,255,255)), (155, 10))
        add_npc = pygame.Rect(250, 5, 90, 30); pygame.draw.rect(screen, (22, 163, 74), add_npc, border_radius=5); screen.blit(font_b.render("+ NPC", True, (255,255,255)), (270, 10))
        settings_btn = pygame.Rect(play_w - 120, 5, 110, 30); pygame.draw.rect(screen, (50, 50, 60), settings_btn, border_radius=5); screen.blit(font_b.render("⚙ SETTINGS", True, (255,255,255)), (settings_btn.x+15, 10))
        if player:
            for i, prof in enumerate(player.profiles):
                tab = pygame.Rect(350+i*95, 5, 90, 30); col = (59,130,246) if player.cur_profile_idx==i else (60,60,70); pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(prof.name[:12], True, (255,255,255)), (tab.x+5, 12))
            for i, src in enumerate(player.sources):
                tab = pygame.Rect(10+i*110, 38, 105, 28); col = (100,100,120) if player.cur_source_idx==i else (45,45,55); pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(src.name[:12], True, (255,255,255)), (tab.x+5, 44))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.DROPFILE:
                if not player: player = AsepritePlayer(event.file)
                else: sid = player.add_source(event.file); player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and m_pos[0] < play_w: is_dragging_cam = True; last_m_pos = m_pos; player.cam_follow = False
                if new_proj.collidepoint(m_pos):
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: player = AsepritePlayer(p)
                if add_src.collidepoint(m_pos) and player:
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: player.add_source(p)
                if add_npc.collidepoint(m_pos) and player:
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: sid = player.add_source(p); player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
                if settings_btn.collidepoint(m_pos): show_settings = not show_settings; settings_scroll = 0
                if player:
                    for i in range(len(player.profiles)):
                        if pygame.Rect(350+i*95, 5, 90, 30).collidepoint(m_pos): player.cur_profile_idx = i
                    for i in range(len(player.sources)):
                        if pygame.Rect(10+i*110, 38, 105, 28).collidepoint(m_pos): player.cur_source_idx = i
                    if play_w < m_pos[0] < sw:
                        if show_settings:
                            if event.button == 4: settings_scroll = min(0, settings_scroll + 40)
                            if event.button == 5: settings_scroll -= 40
                        else:
                            if m_pos[1] < 450:
                                if event.button == 4: slot_scroll = min(0, slot_scroll + 40)
                                if event.button == 5: slot_scroll -= 40
                            else:
                                if event.button == 4: tag_scroll = min(0, tag_scroll + 40)
                                if event.button == 5: tag_scroll -= 40
                            if event.button == 1:
                                cur_p = player.profiles[player.cur_profile_idx]
                                for i, action in enumerate(cur_p.mappings.keys()):
                                    rect = pygame.Rect(play_w+20, 80+i*38+slot_scroll, sidebar_w-40, 34)
                                    if rect.collidepoint(m_pos) and 80 < rect.top < 450: selected_slot = action
                                if selected_slot:
                                    src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                                    for idx, tag in enumerate(src.tag_list):
                                        t_rect = pygame.Rect(play_w+20, 480+idx*25+tag_scroll, sidebar_w-40, 22)
                                        if t_rect.collidepoint(m_pos) and t_rect.top >= 475:
                                            target = (player.cur_source_idx, tag)
                                            if target in cur_p.mappings[selected_slot]: cur_p.mappings[selected_slot].remove(target)
                                            else: cur_p.mappings[selected_slot].append(target)
                if event.button == 3 and play_w < m_pos[0] < sw and player:
                    cur_p = player.profiles[player.cur_profile_idx]
                    for i, action in enumerate(cur_p.mappings.keys()):
                        if pygame.Rect(play_w+20, 80+i*38+slot_scroll, sidebar_w-40, 34).collidepoint(m_pos): cur_p.mappings[action] = []
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: is_dragging_cam = False
            if event.type == pygame.KEYDOWN and player:
                if event.key == pygame.K_F5:
                    log_debug("[SYSTEM] Manual Reload."); [s.export_and_load() for s in player.sources]; [player.auto_map_profile(p) for p in player.profiles]
                if event.key in [pygame.K_SPACE, pygame.K_UP] and player.jumps_left > 0: player.vy = player.jump_power; player.grounded = False; player.jumps_left -= 1
                if event.key == pygame.K_z: player.handle_attack(pygame.key.get_pressed())
                if event.key == pygame.K_x: player.trigger_action("DASH")
                if event.key == pygame.K_c: player.trigger_action("SKILL 1")
                if event.key == pygame.K_b: player.trigger_action("SKILL 2")
                if event.key == pygame.K_n: player.trigger_action("SKILL 3")
                if event.key == pygame.K_v: player.trigger_action("HURT")
                if event.key == pygame.K_t: player.trigger_action("Swap_Exit")
                if event.key == pygame.K_f: player.cam_follow = True
                if event.key == pygame.K_h: player.show_hitboxes = not player.show_hitboxes
                if event.key == pygame.K_p: player.is_paused = not player.is_paused
                if event.key == pygame.K_o: player.step_forward = True
                if event.key == pygame.K_LEFTBRACKET: player.playback_speed = max(0.1, player.playback_speed - 0.1)
                if event.key == pygame.K_RIGHTBRACKET: player.playback_speed = min(5.0, player.playback_speed + 0.1)
            if event.type == pygame.MOUSEWHEEL and player and m_pos[0] < play_w: player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0))
        if is_dragging_cam and player:
            dx, dy = m_pos[0] - last_m_pos[0], m_pos[1] - last_m_pos[1]; player.cam_x -= dx / player.zoom; player.cam_y -= dy / player.zoom; last_m_pos = m_pos
        if player:
            cur_p = player.profiles[player.cur_profile_idx]; cur_s = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
            if show_settings:
                set_surf = pygame.Surface((sidebar_w, sh), pygame.SRCALPHA); cy = 60 + settings_scroll
                for cat in folds.keys():
                    hr = pygame.Rect(10, cy, sidebar_w-20, 30); pygame.draw.rect(set_surf, (50,50,60), hr, border_radius=5); set_surf.blit(font_b.render(f"{'+' if not folds[cat] else '-'} {cat}", True, (255,255,255)), (hr.x+10, hr.y+7)); cy += 35
                    if folds[cat]:
                        if cat == "PHYSICS":
                            for i, (l, mn, mx, at, inv) in enumerate([("Dash Vel",10,50,"dash_speed",0), ("Jump Pow",10,25,"jump_power",1), ("PBomb Spd",10,60,"powerbomb_speed",0), ("Cam Offset",-400,100,"cam_v_offset",0)]):
                                y = cy+i*45; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); sl = pygame.Rect(80, y+5, sidebar_w-120, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn) if not inv else (-v-mn)/(mx-mn); pygame.draw.circle(set_surf, (59,130,246), (int(80+n*(sidebar_w-120)), y+9), 8)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+80, y, sidebar_w-120, 20).inflate(0,10).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+80))/(sidebar_w-120)*(mx-mn) if not inv else -(mn+(m_pos[0]-(play_w+80))/(sidebar_w-120)*(mx-mn))); player.save_settings()
                            cy += 185
                        elif cat == "AI & COMBAT":
                            for i, (l, mn, mx, at) in enumerate([("Atk Forward",0,30,"atk_forward_v")]):
                                y = cy+i*45; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); sl = pygame.Rect(80, y+5, sidebar_w-120, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(set_surf, (59,130,246), (int(80+n*(sidebar_w-120)), y+9), 8)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+80, y, sidebar_w-120, 20).inflate(0,10).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+80))/(sidebar_w-120)*(mx-mn)); player.save_settings()
                            cy += 60
                        elif cat == "JUICE & VFX":
                            for i, (l, at) in enumerate([("Enable Shake", "shake_enabled"), ("Enable Ghost", "vfx_enabled")]):
                                y = cy+i*40; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = getattr(player, at); pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10); pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(m_pos):
                                    if not hasattr(player, "_btn_lock"): setattr(player, at, not val); player._btn_lock = 10; player.save_settings()
                            y = cy + 85; set_surf.blit(font_s.render("Shake Power", True, (150,150,150)), (20, y)); sl = pygame.Rect(80, y+5, sidebar_w-120, 8); pygame.draw.rect(set_surf, (60,60,70), sl); n = player.base_shake / 3.0; pygame.draw.circle(set_surf, (220, 38, 38), (int(80+n*(sidebar_w-120)), y+9), 8)
                            if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+80, y, sidebar_w-120, 20).inflate(0,10).collidepoint(m_pos): player.base_shake = ((m_pos[0]-(play_w+80))/(sidebar_w-120)) * 3.0; player.save_settings()
                            if hasattr(player, "_btn_lock"): 
                                player._btn_lock -= 1
                                if player._btn_lock <= 0: delattr(player, "_btn_lock")
                            cy += 130
                        elif cat == "LAYERS":
                            src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                            if not src.layers:
                                set_surf.blit(font_s.render("No layers found or multi-layer not supported", True, (100,100,100)), (20, cy)); cy += 30
                            for l_name in src.layers:
                                ly = cy; is_vis = l_name in src.visible_layers
                                l_rect = pygame.Rect(15, ly-2, sidebar_w-30, 24); hvr = pygame.Rect(play_w+15, ly-2, sidebar_w-30, 24).collidepoint(m_pos)
                                if hvr: pygame.draw.rect(set_surf, (60,60,70), l_rect, border_radius=4)
                                pygame.draw.rect(set_surf, (22, 163, 74) if is_vis else (60, 60, 70), (20, ly+2, 16, 16), border_radius=3)
                                set_surf.blit(font_s.render(l_name[:30], True, (255,255,255) if is_vis else (150,150,150)), (45, ly+2))
                                if pygame.mouse.get_pressed()[0] and hvr:
                                    if not hasattr(player, "_btn_lock"):
                                        if is_vis: src.visible_layers.remove(l_name)
                                        else: src.visible_layers.add(l_name)
                                        src.export_and_load(); player.auto_map_profile(player.profiles[player.cur_profile_idx])
                                        player._btn_lock = 15
                                cy += 28
                            cy += 10
                        elif cat == "VIEWPORT":
                            y = cy; set_surf.blit(font_s.render("Show 640x360 Guide", True, (150,150,150)), (20, y))
                            btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = player.show_viewport
                            pygame.draw.rect(set_surf, (59, 130, 246) if val else (60, 60, 70), btn, border_radius=10)
                            pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                            if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(m_pos):
                                if not hasattr(player, "_btn_lock"): player.show_viewport = not val; player._btn_lock = 15; player.save_settings()
                            cy += 40
                        elif cat == "BG IMAGE":
                            bg_btn = pygame.Rect(20, cy, 150, 30); pygame.draw.rect(set_surf, (100,100,110), bg_btn, border_radius=5); set_surf.blit(font_b.render("LOAD BG IMG", True, (255,255,255)), (bg_btn.x+25, bg_btn.y+5))
                            if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20, cy, 150, 30).collidepoint(m_pos):
                                p = select_file([("Image", "*.png *.jpg *.bmp")]); 
                                if p: player.bg_img = pygame.image.load(p).convert_alpha(); player.save_settings()
                            cy += 40
                            bg_ctrls = [("BG-X",-2000,2000,"bg_off_x"), ("BG-Y",-2000,2000,"bg_off_y"), ("Scale",0.1,10,"bg_zoom"), ("Alpha",0,255,"bg_alpha"), ("Parallax",0,1,"bg_parallax")]
                            for i, (l, mn, mx, at) in enumerate(bg_ctrls):
                                y = cy+i*40; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); sl = pygame.Rect(80, y+5, sidebar_w-120, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(set_surf, (220,38,38), (int(80+n*(sidebar_w-120)), y+9), 8)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+80, y, sidebar_w-120, 20).inflate(0,10).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+80))/(sidebar_w-120)*(mx-mn)); player.save_settings()
                            cy += 210
                        elif cat == "BG COLOR":
                            for i, c in enumerate(['R','G','B']):
                                y = cy+i*35; sl = pygame.Rect(20, y+15, sidebar_w-40, 8); pygame.draw.rect(set_surf, (60,60,70), sl); pygame.draw.circle(set_surf, (220, 38, 38) if i==0 else (22, 163, 74) if i==1 else (59, 130, 246), (int(20+player.bg_color[i]/255*(sidebar_w-40)), y+19), 8)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20, y+15, sidebar_w-40, 20).collidepoint(m_pos): player.bg_color[i] = int((m_pos[0]-(play_w+20))/(sidebar_w-40)*255); player.save_settings()
                            cy += 120
                            ps = [(15,15,18), (120,120,120), (240,240,240), (0,255,0)]
                            for i, p in enumerate(ps):
                                pr = pygame.Rect(20+i*45, cy, 35, 30); pygame.draw.rect(set_surf, p, pr, border_radius=3)
                                if pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20+i*45, cy, 35, 30).collidepoint(m_pos): player.bg_color = list(p); player.save_settings()
                            cy += 60
                screen.blit(set_surf, (play_w, 0)); pygame.draw.line(screen, (59, 130, 246), (play_w, 0), (play_w, sh), 2)
            else:
                slot_clip = pygame.Surface((sidebar_w-20, 380), pygame.SRCALPHA)
                for i, action in enumerate(cur_p.mappings.keys()):
                    rect = pygame.Rect(10, i*38+slot_scroll, sidebar_w-40, 34); is_sel = selected_slot == action; col = (59,130,246) if is_sel else (45,45,50); pygame.draw.rect(slot_clip, col, rect, border_radius=5); slot_clip.blit(font_b.render(action, True, (255,255,255)), (rect.x+10, rect.y+3))
                    ms = ", ".join([f"{m[1]}" for m in cur_p.mappings[action]]); slot_clip.blit(font_s.render(f"-> {ms[:45]}", True, (200,200,200) if not is_sel else (255,255,255)), (rect.x+10, rect.y+18))
                screen.blit(slot_clip, (play_w+10, 85))
                list_area = pygame.Rect(play_w+15, 475, sidebar_w-30, sh-490); pygame.draw.rect(screen, (20,20,25), list_area, border_radius=5); src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]; screen.blit(font_b.render(f"TAGS FROM: {src.name[:20]}", True, (100,100,100)), (play_w+20, 455)); clip_surf = pygame.Surface((sidebar_w-40, sh-495), pygame.SRCALPHA)
                for idx, tag in enumerate(src.tag_list):
                    t_rect = pygame.Rect(0, idx*25+tag_scroll, sidebar_w-40, 22); is_mapped = selected_slot and (player.cur_source_idx, tag) in cur_p.mappings[selected_slot]; hvr = t_rect.move(play_w+20, 475).collidepoint(m_pos); t_col = (59,130,246) if is_mapped else ((70,70,80) if hvr else (40,40,45)); pygame.draw.rect(clip_surf, t_col, t_rect, border_radius=3); clip_surf.blit(font_s.render(tag, True, (255,255,255)), (t_rect.x+10, t_rect.y+4))
                screen.blit(clip_surf, (play_w+20, 475))
            for i in range(2):
                col = (59, 130, 246) if i < player.dash_charges else (60, 60, 70); pygame.draw.rect(screen, col, (play_w - 80 + i*35, sh - 100, 30, 10), border_radius=3)
            pygame.draw.rect(screen, (30, 30, 35), (0, sh-40, play_w, 40)); pygame.draw.line(screen, (50,50,60), (0, sh-40), (play_w, sh-40), 1)
            controls = [("Z", "Atk"), ("X", "Dash"), ("C/B/N", "Skill"), ("T", "Swap"), ("P", "Pause" if not player.is_paused else "Play", (220,38,38) if player.is_paused else (255,255,255)), ("O", "Step"), ("[ ]", f"Speed:{player.playback_speed:.1f}"), ("F5", "Refresh"), ("H", "Hitbox"), ("R-Drag", "Cam"), ("F", "Reset Cam")]
            tx = 20
            for k, desc, *extra in controls:
                col = extra[0] if extra else (255,255,255); pygame.draw.rect(screen, (45,45,50), (tx-5, sh-32, font_h.size(k)[0]+font_h.size(desc)[0]+25, 24), border_radius=4); screen.blit(font_h.render(k, True, (59,130,246)), (tx, sh-27)); screen.blit(font_h.render(f": {desc}", True, col), (tx+font_h.size(k)[0], sh-27)); tx += font_h.size(k)[0]+font_h.size(desc)[0]+35
            if player.attack_buffer > 0:
                for b in range(player.attack_buffer): pygame.draw.circle(screen, (220,38,38), (play_w-120-b*15, sh-20), 5)
        pygame.display.flip()

if __name__ == "__main__": main()
