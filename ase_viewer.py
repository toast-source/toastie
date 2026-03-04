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

class CachedFont:
    def __init__(self, font):
        self.font = font
        self.cache = {}
    def render(self, text, antialias, color):
        key = (text, color)
        if key not in self.cache:
            self.cache[key] = self.font.render(text, antialias, color)
        return self.cache[key]
    def size(self, text):
        return self.font.size(text)

# Clean old log
if os.path.exists("ase_debug.log"): os.remove("ase_debug.log")
log_debug("[SYSTEM] v45 Rollback & Logic Refinement")

class AsePathManager:
    def __init__(self):
        self.config_path = "config.json"
        self.path = self.load_config()
        if not self.path or not os.path.exists(self.path):
            self.path = self.find_aseprite()
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f: return json.load(f).get("aseprite_path")
            except: return None
        return None
    def save_config(self, path):
        try:
            with open(self.config_path, "w") as f: json.dump({"aseprite_path": path}, f)
        except Exception as e: log_debug(f"[ERROR] Config save failed: {e}")
    def find_aseprite(self):
        candidates = [r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe", r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe", r"C:\Program Files\Aseprite\Aseprite.exe", r"D:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe"]
        for c in candidates:
            if os.path.exists(c): return c
        return None
    def get_path(self):
        if self.path and os.path.exists(self.path): return self.path
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        selected = filedialog.askopenfilename(title="Select Aseprite.exe", filetypes=[("Executable", "Aseprite.exe")]); root.destroy()
        if selected: self.path = selected; self.save_config(selected); return selected
        else: pygame.quit(); sys.exit()

ase_manager = AsePathManager()

def select_file(ftypes):
    try:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        path = filedialog.askopenfilename(filetypes=ftypes); root.destroy()
        return path
    except: return None

class AseSource:
    def __init__(self, file_path, source_id):
        self.id = source_id; self.file_path = os.path.abspath(file_path); self.name = os.path.basename(file_path)
        self.frames = []; self.tags = {}; self.tag_list = []; self.slices = {}; self.orig_w = self.orig_h = 0
        self.layers = []; self.visible_layers = set(); self.last_mtime = os.path.getmtime(self.file_path); self.cache = {}
        self.fetch_layers(); self.export_and_load()
    def clear_cache(self): self.cache = {}
    def get_frame(self, f_idx, zoom, facing_right):
        key = (f_idx, zoom, facing_right)
        if key in self.cache: return self.cache[key]
        if not self.frames: return None
        f = self.frames[min(max(0, f_idx), len(self.frames)-1)]; img = f['img']; scaled = pygame.transform.scale(img, (int(img.get_width()*zoom), int(img.get_height()*zoom)))
        if not facing_right: scaled = pygame.transform.flip(scaled, True, False)
        self.cache[key] = scaled; return scaled
    def fetch_layers(self):
        try:
            exe = ase_manager.get_path(); startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run([exe, "-b", "--list-layers", self.file_path], check=True, capture_output=True, text=True, startupinfo=startupinfo)
            self.layers = [l.strip() for l in res.stdout.split("\n") if l.strip()]; self.visible_layers = set(self.layers)
        except: self.layers = []
    def check_for_reload(self):
        try:
            current_mtime = os.path.getmtime(self.file_path)
            if current_mtime > self.last_mtime:
                self.last_mtime = current_mtime; self.export_and_load(); self.clear_cache(); return True
        except: pass
        return False
    def export_and_load(self):
        png_p = f"temp_{self.id}.png"; json_p = f"temp_{self.id}.json"; self.frames = []; self.tags = {}; self.slices = {}
        try:
            exe = ase_manager.get_path(); startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW; cmd = [exe, "-b"]
            if len(self.visible_layers) < len(self.layers):
                for l in self.layers:
                    if l in self.visible_layers: cmd.extend(["--layer", l])
            cmd.extend([self.file_path, "--trim", "--sheet", png_p, "--data", json_p, "--format", "json-array", "--list-tags", "--list-slices"])
            subprocess.run(cmd, check=True, capture_output=True, startupinfo=startupinfo); sheet = pygame.image.load(png_p).convert_alpha()
            with open(json_p, 'r', encoding='utf-8') as f: data = json.load(f)
            self.orig_w, self.orig_h = data['frames'][0]['sourceSize']['w'], data['frames'][0]['sourceSize']['h']
            for f in data['frames']:
                r, s = f['frame'], f['spriteSourceSize']; surf = pygame.Surface((r['w'], r['h']), pygame.SRCALPHA); surf.blit(sheet, (0, 0), (r['x'], r['y'], r['w'], r['h']))
                self.frames.append({'img': surf, 'ox': s['x'] - self.orig_w // 2, 'oy': s['y'] - self.orig_h // 2, 'duration': f.get('duration', 100)})
            if 'meta' in data:
                if 'frameTags' in data['meta']:
                    for t in data['meta']['frameTags']: self.tags[t['name']] = (t['from'], t['to'])
                if 'slices' in data['meta']:
                    for s in data['meta']['slices']: self.slices[s['name']] = s['keys']
            self.tag_list = sorted(list(self.tags.keys())); log_debug(f"[LOAD] {self.name} Success.")
        except Exception as e: log_debug(f"[ERROR] Load failed: {e}")
        finally:
            for p in [png_p, json_p]: 
                if os.path.exists(p): os.remove(p)

class AseProfile:
    def __init__(self, name, source_idx):
        self.name = name; self.source_idx = source_idx
        self.mappings = { "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ComboAttack_1": [], "ComboAttack_2": [], "ComboAttack_3": [], "ComboAttack_4": [], "JUMPATTACK": [], "POWERBOMB": [], "DASH": [], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [], "Swap_Exit": [], "Break1": [], "Break2": [] }

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, image=None):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.color = color; self.size = size; self.lifetime = lifetime; self.max_life = lifetime
        self.image = image
        self.rotation = random.uniform(0, 360) if image else 0
        self.rot_speed = random.uniform(-10, 10) if image else 0
        self.cached_surface = None; self.cached_zoom = -1; self.cached_rotation = -1
    def update(self, dt, gravity, ground_y, platforms):
        self.lifetime -= dt
        # Optimization: Skip expensive physics and collision logic if particle is at rest
        if abs(self.vx) < 0.1 and abs(self.vy) < 0.1 and self.y >= ground_y - 10:
            return

        self.vy += gravity * (dt/16.6); self.x += self.vx * (dt/16.6); self.y += self.vy * (dt/16.6)
        if self.image: self.rotation += self.rot_speed * (dt/16.6)
        
        # Simple floor/platform collision for bounce
        hit_ground = False
        if self.y >= ground_y: 
            self.y = ground_y; hit_ground = True
        
        # Only check platform collisions if falling down
        if self.vy > 0 and not hit_ground:
            for p in platforms:
                if p.collidepoint(self.x, self.y):
                    self.y = p.top; hit_ground = True; break
                
        if hit_ground:
            if abs(self.vy) < 2.0: 
                self.vy = 0; self.rot_speed = 0; self.vx *= 0.5
            else: 
                self.vy *= -0.5; self.vx *= 0.8

class AseAI:
    def __init__(self, master, profile, is_temp=False, is_prop=False, hp=1):
        self.master = master; self.profile = profile
        self.spawn_x = master.x + (100 if master.facing_right else -100)
        self.spawn_y = master.y - 100
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = True; self.facing_right = random.choice([True, False]); self.frame_idx = 0; self.anim_timer = 0; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.ai_timer = random.randint(30, 90); self.decision = "IDLE"; self.swap_timer = 0; self.visible = True; self.active_action_slot = None
        self.is_temp = is_temp; self.attack_buffer = 0; self.combo_step = 0
        self.is_prop = is_prop; self.hit_cooldown = 0; self.is_dead = False
        if is_prop:
            self.prop_state = 0 # 0: IDLE, 1: Break1, 2: Break2
            self.stage_hp = 3
            self.hp = 999 # Use stage_hp instead
        else:
            self.hp = hp
    def update(self, ground_y, dt):
        if self.hit_cooldown > 0: self.hit_cooldown -= dt
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        if self.is_prop:
            self.vx *= 0.85
        elif not self.is_temp:
            self.ai_timer -= (dt/16.6); dist_p = self.master.x - self.x
            if self.ai_timer <= 0:
                choices = ["IDLE", "CHASE", "ATTACK", "DASH", "JUMP", "SWAP"] if abs(dist_p) < 600 else ["IDLE", "WALK_L", "WALK_R"]
                self.decision = random.choice(choices); self.ai_timer = random.randint(40, 120)
                if self.decision == "SWAP": self.trigger_action("Swap_Exit")
                elif self.decision == "ATTACK" and abs(dist_p) < 200: self.facing_right = dist_p > 0; self.trigger_action(f"ComboAttack_{random.randint(1,4)}")
                elif self.decision == "DASH": self.facing_right = dist_p > 0; self.trigger_action("DASH")
                elif self.decision == "JUMP" and self.grounded: self.vy = self.master.jump_power; self.grounded = False
            self.vx *= 0.85
            if not self.active_tag_info:
                if self.decision == "WALK_R": self.vx = 2.6; self.facing_right = True
                elif self.decision == "WALK_L": self.vx = -2.6; self.facing_right = False
                elif self.decision == "CHASE": self.vx = 3.6 if dist_p > 0 else -3.6; self.facing_right = dist_p > 0
                if abs(dist_p) < 100: self.decision = "IDLE"
        else:
            self.vx *= 0.85
        if self.active_tag_info and self.active_tag_info[1] == "DASH": self.vy = 0
        else: self.vy += self.master.gravity
        self.x += self.vx * (dt/16.6); self.y += self.vy * (dt/16.6)
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True
        if self.vy >= 0:
            for plat in self.master.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - (self.vy * (dt/16.6)) <= plat.top + 10: self.y = plat.top; self.vy = 0; self.grounded = True
        target_info = None
        if not self.active_tag_info:
            if self.is_temp:
                self.trigger_action("Swap_Exit")
                if not self.active_tag_info: self.visible = False; return
                target_info = self.active_tag_info
            else:
                if self.is_prop:
                    state = "IDLE" if getattr(self, 'prop_state', 0) == 0 else (f"Break{getattr(self, 'prop_state', 0)}")
                else:
                    state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
                
                m = self.profile.mappings.get(state, []) if self.profile else []
                # Fallback to IDLE if Break1/Break2 mappings aren't found
                if not m and self.is_prop and state != "IDLE": m = self.profile.mappings.get("IDLE", [])
                target_info = m[0] if m else None
        else: target_info = self.active_tag_info
        if target_info and target_info[0] >= 0 and target_info[0] < len(self.master.sources):
            src = self.master.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
            if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
            if not self.master.is_paused:
                self.anim_timer += dt
                if self.frame_idx < len(src.frames):
                    dur = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= dur:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit": self.visible = False; self.active_tag_info = None; self.active_action_slot = None; return
                            if "(loop)" in target_info[1].lower(): self.frame_idx = tr[0]
                            elif self.is_temp and not self.action_queue:
                                if getattr(self, 'attack_buffer', 0) > 0:
                                    self.attack_buffer -= 1
                                    self.combo_step = (getattr(self, 'combo_step', 0) % 4) + 1
                                    self.trigger_action(f"ComboAttack_{self.combo_step}")
                                else:
                                    self.trigger_action("Swap_Exit")
                                    if not self.active_tag_info: self.visible = False
                                return
                            elif self.action_queue:
                                self.active_tag_info = self.action_queue.pop(0)
                                if self.active_tag_info[0] >= 0 and self.active_tag_info[0] < len(self.master.sources):
                                    s = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = s.tags.get(self.active_tag_info[1], (0,0))
                                else:
                                    self.active_tag_info = None; self.active_action_slot = None
                            else: self.active_tag_info = None; self.active_action_slot = None
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]
    def trigger_action(self, slot):
        tags = self.profile.mappings.get(slot, [])
        if tags:
            self.active_action_slot = slot; self.action_queue = list(tags); self.active_tag_info = self.action_queue.pop(0)
            if self.active_tag_info[0] >= 0 and self.active_tag_info[0] < len(self.master.sources):
                src = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = src.tags.get(self.active_tag_info[1], (0,0)); self.anim_timer = 0
                if slot == "DASH": self.vx = 8 if self.facing_right else -8
            else:
                self.active_tag_info = None; self.active_action_slot = None; self.action_queue = []

class AsepritePlayer:
    def __init__(self, initial_path=None):
        self.sources = []; self.profiles = []; self.cur_profile_idx = 0; self.cur_source_idx = 0; self.spawn_x, self.spawn_y = 400, 500; self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = False; self.jumps_left = 2; self.facing_right = True; self.zoom = 3.0; self.dash_speed = 12.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 15.0; self.powerbomb_speed = 35.0; self.cam_v_offset = -120; self.pbomb_pause_timer = 0; self.loop_counter = 0; self.cam_x, self.cam_y = 400, 300; self.cam_follow = True; self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20), pygame.Rect(-200, 250, 300, 20), pygame.Rect(900, 300, 400, 20)]
        self.bg_layers = []; self.active_bg_layer = 0; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]
        self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0; self.active_action_slot = None; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0; self.attack_move_timer = 0; self.ai_list = []; self.temp_ai_list = []; self.prop_list = []; self.target_ai_count = 0; self.swap_timer = 0; self.visible = True; self.playback_speed = 1.0; self.is_paused = False; self.step_forward = False; self.show_hitboxes = True; self.target_w, self.target_h = 640, 360; self.show_viewport = True; self.shake_timer = 0; self.shake_intensity = 0; self.shake_enabled = True; self.base_shake = 0.2; self.debris_force = 0.3; self.afterimages = []; self.particles = []; self.vfx_enabled = True; self.ghost_timer = 0; self.platform_alpha = 150; self.edit_platforms = False; self.selected_plat = None; self.drag_offset = (0,0); self.drop_through_timer = 0
        if pygame.font.get_init():
            self.font_10 = CachedFont(pygame.font.SysFont("Arial", 10))
            self.font_12 = CachedFont(pygame.font.SysFont("Arial", 12))
        else:
            self.font_10 = None; self.font_12 = None
        self.key_map = {"ATTACK": pygame.K_z, "DASH": pygame.K_x, "JUMP": pygame.K_SPACE, "SKILL1": pygame.K_c, "SKILL2": pygame.K_b, "SKILL3": pygame.K_n, "SUMMON": pygame.K_g, "SWAP": pygame.K_t, "HURT": pygame.K_v}
        self.popup = None
        if initial_path: self.add_source(initial_path); self.add_profile("PLAYER", 0)
    def update_bg_cache(self):
        zoom_changed = getattr(self, '_last_bg_zoom', None) != self.zoom
        if zoom_changed: self._last_bg_zoom = self.zoom
        
        for bg in self.bg_layers:
            if zoom_changed or bg.get('needs_update', True) or bg.get('cached_bg') is None:
                if bg.get('img'):
                    bw, bh = int(bg['img'].get_width()*bg['zoom']*self.zoom*0.5), int(bg['img'].get_height()*bg['zoom']*self.zoom*0.5)
                    bg['cached_bg'] = pygame.transform.scale(bg['img'], (max(1, bw), max(1, bh)))
                    if bg['alpha'] < 255: bg['cached_bg'].set_alpha(bg['alpha'])
                bg['needs_update'] = False
    def save_settings(self):
        bg_layers_data = []
        for bg in self.bg_layers:
            bg_layers_data.append({"path": bg.get('path', ''), "off_x": bg.get('off_x', 0), "off_y": bg.get('off_y', 0), "zoom": bg.get('zoom', 2.0), "alpha": bg.get('alpha', 255), "parallax": bg.get('parallax', 1.0), "loop_x": bg.get('loop_x', False)})
        data = {"physics": {"dash_speed": self.dash_speed, "jump_power": self.jump_power, "powerbomb_speed": self.powerbomb_speed, "cam_v_offset": self.cam_v_offset}, "combat": {"atk_forward_v": self.atk_forward_v}, "vfx": {"shake_enabled": self.shake_enabled, "vfx_enabled": self.vfx_enabled, "base_shake": self.base_shake, "debris_force": self.debris_force}, "viewport": {"show_viewport": self.show_viewport, "target_w": self.target_w, "target_h": self.target_h}, "bg": {"bg_color": self.bg_color, "layers": bg_layers_data}, "ai": {"target_ai_count": self.target_ai_count}, "platforms": {"alpha": self.platform_alpha}}
        try:
            with open("ase_settings.json", "w") as f: json.dump(data, f, indent=4)
        except: pass
    def load_settings(self):
        if not hasattr(self, "key_map"):
            self.key_map = {"ATTACK": pygame.K_z, "DASH": pygame.K_x, "JUMP": pygame.K_SPACE, "SKILL1": pygame.K_c, "SKILL2": pygame.K_b, "SKILL3": pygame.K_n, "SUMMON": pygame.K_g, "SWAP": pygame.K_t, "HURT": pygame.K_v}
        self.popup = None # {'msg': str, 'cb': func}
        if os.path.exists("ase_settings.json"):
            try:
                with open("ase_settings.json", "r") as f:
                    data = json.load(f)
                    for cat_name, cat in data.items():
                        if isinstance(cat, dict):
                            if cat_name == "bg":
                                if "bg_color" in cat: self.bg_color = cat["bg_color"]
                                if "layers" in cat:
                                    self.bg_layers = []
                                    for l_data in cat["layers"]:
                                        path = l_data.get("path", "")
                                        if path and not os.path.exists(path): path = os.path.basename(path)
                                        layer = {"path": path, "off_x": l_data.get("off_x", 0), "off_y": l_data.get("off_y", 0), "zoom": l_data.get("zoom", 2.0), "alpha": l_data.get("alpha", 255), "parallax": l_data.get("parallax", 1.0), "loop_x": l_data.get("loop_x", False), "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                                        if os.path.exists(path):
                                            layer["img"] = pygame.image.load(path).convert_alpha()
                                            layer["last_mtime"] = os.path.getmtime(path)
                                        self.bg_layers.append(layer)
                                elif "bg_path" in cat: # Legacy support
                                    path = cat["bg_path"]
                                    if path and not os.path.exists(path): path = os.path.basename(path)
                                    layer = {"path": path, "off_x": cat.get("bg_off_x", 0), "off_y": cat.get("bg_off_y", 0), "zoom": cat.get("bg_zoom", 2.0), "alpha": cat.get("bg_alpha", 255), "parallax": cat.get("bg_parallax", 1.0), "loop_x": False, "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                                    if os.path.exists(path):
                                        layer["img"] = pygame.image.load(path).convert_alpha()
                                        layer["last_mtime"] = os.path.getmtime(path)
                                    self.bg_layers = [layer]
                            else:
                                for k, v in cat.items():
                                    if k == "alpha" and "platforms" in data: self.platform_alpha = v
                                    elif hasattr(self, k): setattr(self, k, v)
                    if "controls" in data:
                        self.key_map = data["controls"]
                        if "JUMP" not in self.key_map: self.key_map["JUMP"] = pygame.K_SPACE
            except: pass
    def save_project(self):
        project = {"sources": [s.file_path for s in self.sources], "profiles": [{"name": p.name, "source_idx": p.source_idx, "mappings": p.mappings} for p in self.profiles], "ai_count": self.target_ai_count, "platforms": [[p.x, p.y, p.w, p.h] for p in self.platforms], "solid_boxes": [[b.x, b.y, b.w, b.h] for b in self.solid_boxes]}
        try:
            with open("ase_project.json", "w") as f: json.dump(project, f, indent=4)
        except: pass
    def load_project(self):
        if os.path.exists("ase_project.json"):
            try:
                with open("ase_project.json", "r") as f:
                    p = json.load(f); [self.add_source(src_p) for src_p in p.get("sources", []) if os.path.exists(src_p)]
                    for prof_data in p.get("profiles", []):
                        new_prof = AseProfile(prof_data["name"], prof_data["source_idx"]); new_prof.mappings = prof_data["mappings"]; self.profiles.append(new_prof)
                    if not self.profiles and self.sources: self.add_profile("PLAYER", 0)
                    self.target_ai_count = p.get("ai_count", self.target_ai_count)
                    if "platforms" in p: self.platforms = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in p["platforms"]]
                    if "solid_boxes" in p: self.solid_boxes = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in p["solid_boxes"]]
                    else: self.solid_boxes = []
            except: pass
        else: self.solid_boxes = []

    def load_example(self):
        proj_data = {"sources": ["C:\\Users\\SOUTHPAW GAMES\\Desktop\\새 폴더\\Cailin_00_Public.aseprite", "C:\\Users\\SOUTHPAW GAMES\\Desktop\\새 폴더\\Nisariel_00_Public_02.aseprite"], "profiles": [{"name": "PLAYER", "source_idx": 0, "mappings": {"IDLE": [[0, "Idle_(Loop)"]], "WALK": [[0, "Walk_(Loop)"]], "JUMP": [[0, "Jump_(Loop)"]], "FALL": [[0, "Fall_Ready"], [0, "Fall_(Loop)"]], "ComboAttack_1": [[0, "ComboAttack_1_Ready"], [0, "ComboAttack_1"]], "ComboAttack_2": [[0, "ComboAttack_2_Ready"], [0, "ComboAttack_2"]], "ComboAttack_3": [[0, "ComboAttack_3_Ready"], [0, "ComboAttack_3"]], "ComboAttack_4": [], "JUMPATTACK": [[0, "JumpAttack_Ready"], [0, "JumpAttack"]], "POWERBOMB": [[0, "PowerBomb_Ready"], [0, "PowerBomb_(Loop)"], [0, "PowerBomb_End"]], "DASH": [[0, "Dash"]], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [[0, "Swap_Enter"]], "Swap_Exit": [[0, "Swap_Exit_Ready"], [0, "Swap_Exit"]]}}, {"name": "NPC_1", "source_idx": 1, "mappings": {"IDLE": [[1, "Idle_(Loop)"]], "WALK": [[1, "Walk_(Loop)"]], "JUMP": [[1, "Jump(Loop)"]], "FALL": [[1, "Fall_Ready"], [1, "Fall_(Loop)"]], "ComboAttack_1": [[1, "ComboAttack_1_Ready"], [1, "ComboAttack_1"]], "ComboAttack_2": [[1, "ComboAttack_2"]], "ComboAttack_3": [[1, "ComboAttack_3_Ready"], [1, "ComboAttack_3"]], "ComboAttack_4": [[1, "ComboAttack_4_Ready"], [1, "ComboAttack_4"]], "JUMPATTACK": [[1, "JumpAttack_Ready"], [1, "JumpAttack"]], "POWERBOMB": [[1, "PowerBomb"], [1, "PowerBomb_(Loop)"], [1, "PowerBomb_End"]], "DASH": [[1, "Dash"]], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [[1, "Swap_Enter"]], "Swap_Exit": [[1, "Swap_Exit_Ready"], [1, "Swap_Exit"]]}}], "ai_count": 0, "platforms": [[262, 372, 200, 20], [500, 200, 200, 20], [-146, 248, 300, 20], [900, 300, 400, 20], [-1027, 207, 927, 51], [-164, 69, 254, 25]], "solid_boxes": [[-628, 254, 349, 275], [-739, -287, 614, 208]]}
        set_data = {"physics": {"dash_speed": 12.0, "jump_power": -18.0, "powerbomb_speed": 35.0, "cam_v_offset": -120}, "combat": {"atk_forward_v": 15.0}, "vfx": {"shake_enabled": True, "vfx_enabled": True, "base_shake": 0.2}, "viewport": {"show_viewport": True, "target_w": 640, "target_h": 360}, "bg": {"bg_color": [17, 15, 18], "layers": [{"path": "C:/Users/SOUTHPAW GAMES/Desktop/새 폴더/로비 컨셉94 (1).png", "off_x": 0, "off_y": -130.0, "zoom": 2.0, "alpha": 255, "parallax": 0.9862068965517241}]}, "ai": {"target_ai_count": 0}, "platforms": {"alpha": 5.275862068965517}}
        
        # Apply settings
        for cat_name, cat in set_data.items():
            if isinstance(cat, dict):
                if cat_name == "bg":
                    if "bg_color" in cat: self.bg_color = cat["bg_color"]
                    if "layers" in cat:
                        self.bg_layers = []
                        for l_data in cat["layers"]:
                            path = l_data.get("path", "")
                            if path and not os.path.exists(path): path = os.path.basename(path)
                            layer = {"path": path, "off_x": l_data.get("off_x", 0), "off_y": l_data.get("off_y", 0), "zoom": l_data.get("zoom", 2.0), "alpha": l_data.get("alpha", 255), "parallax": l_data.get("parallax", 1.0), "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                            if os.path.exists(path):
                                layer["img"] = pygame.image.load(path).convert_alpha()
                                layer["last_mtime"] = os.path.getmtime(path)
                            self.bg_layers.append(layer)
                else:
                    for k, v in cat.items():
                        if k == "alpha" and "platforms" in set_data: self.platform_alpha = v
                        elif hasattr(self, k): setattr(self, k, v)
                
        # Apply project
        self.sources = []; self.profiles = []; self.ai_list = []; self.temp_ai_list = []
        for src_p in proj_data.get("sources", []):
            if not os.path.exists(src_p): src_p = os.path.basename(src_p)
            if os.path.exists(src_p): self.add_source(src_p)
        for prof_data in proj_data.get("profiles", []):
            new_prof = AseProfile(prof_data["name"], prof_data["source_idx"]); new_prof.mappings = prof_data["mappings"]; self.profiles.append(new_prof)
            if prof_data["name"] != "PLAYER": self.ai_list.append(AseAI(self, new_prof))
        
        self.platforms = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data["platforms"]]
        self.solid_boxes = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data.get("solid_boxes", [])]
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx, self.vy = 0, 0
        self.cam_x, self.cam_y = self.x, self.y
        self.save_settings(); self.save_project()

    def load_example2(self):
        proj_data = {"sources": ["C:\\Users\\SOUTHPAW GAMES\\Desktop\\새 폴더\\Cailin_00_Public.aseprite", "C:\\Users\\SOUTHPAW GAMES\\Desktop\\새 폴더\\Nisariel_00_Public_02.aseprite"], "profiles": [{"name": "PLAYER", "source_idx": 0, "mappings": {"IDLE": [[0, "Idle_(Loop)"]], "WALK": [[0, "Walk_(Loop)"]], "JUMP": [[0, "Jump_(Loop)"]], "FALL": [[0, "Fall_Ready"], [0, "Fall_(Loop)"]], "ComboAttack_1": [[0, "ComboAttack_1_Ready"], [0, "ComboAttack_1"]], "ComboAttack_2": [[0, "ComboAttack_2_Ready"], [0, "ComboAttack_2"]], "ComboAttack_3": [[0, "ComboAttack_3_Ready"], [0, "ComboAttack_3"]], "ComboAttack_4": [], "JUMPATTACK": [[0, "JumpAttack_Ready"], [0, "JumpAttack"]], "POWERBOMB": [[0, "PowerBomb_Ready"], [0, "PowerBomb_(Loop)"], [0, "PowerBomb_End"]], "DASH": [[0, "Dash"]], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [[0, "Swap_Enter"]], "Swap_Exit": [[0, "Swap_Exit_Ready"], [0, "Swap_Exit"]]}}, {"name": "NPC_1", "source_idx": 1, "mappings": {"IDLE": [[1, "Idle_(Loop)"]], "WALK": [[1, "Walk_(Loop)"]], "JUMP": [[1, "Jump(Loop)"]], "FALL": [[1, "Fall_Ready"], [1, "Fall_(Loop)"]], "ComboAttack_1": [[1, "ComboAttack_1_Ready"], [1, "ComboAttack_1"]], "ComboAttack_2": [[1, "ComboAttack_2"]], "ComboAttack_3": [[1, "ComboAttack_3_Ready"], [1, "ComboAttack_3"]], "ComboAttack_4": [[1, "ComboAttack_4_Ready"], [1, "ComboAttack_4"]], "JUMPATTACK": [[1, "JumpAttack_Ready"], [1, "JumpAttack"]], "POWERBOMB": [[1, "PowerBomb"], [1, "PowerBomb_(Loop)"], [1, "PowerBomb_End"]], "DASH": [[1, "Dash"]], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [[1, "Swap_Enter"]], "Swap_Exit": [[1, "Swap_Exit_Ready"], [1, "Swap_Exit"]]}}], "ai_count": 0, "platforms": [[262, 372, 200, 20], [500, 200, 200, 20], [-146, 248, 300, 20], [900, 300, 400, 20], [-1027, 207, 927, 51], [-164, 69, 254, 25]], "solid_boxes": [[-628, 254, 349, 275], [-739, -287, 614, 208]]}
        set_data = {"physics": {"dash_speed": 12.0, "jump_power": -18.0, "powerbomb_speed": 35.0, "cam_v_offset": -100.0}, "combat": {"atk_forward_v": 15.0}, "vfx": {"shake_enabled": True, "vfx_enabled": True, "base_shake": 0.2}, "viewport": {"show_viewport": True, "target_w": 640, "target_h": 360}, "bg": {"bg_color": [15, 15, 18], "layers": [{"path": "C:/Users/SOUTHPAW GAMES/Downloads/00.png", "off_x": 0, "off_y": -13, "zoom": 2.0, "alpha": 255, "parallax": 0.0, "loop_x": False}, {"path": "C:/Users/SOUTHPAW GAMES/Downloads/01.png", "off_x": 0, "off_y": -27, "zoom": 2.0, "alpha": 255, "parallax": 0.05, "loop_x": False}, {"path": "C:/Users/SOUTHPAW GAMES/Downloads/# 2번_완성본.png", "off_x": 0, "off_y": -137, "zoom": 2.0, "alpha": 125, "parallax": 0.06, "loop_x": False}, {"path": "C:/Users/SOUTHPAW GAMES/Downloads/# 3번_완성본.png", "off_x": 0, "off_y": -220, "zoom": 2.0, "alpha": 255, "parallax": 0.5344827586206895, "loop_x": True}, {"path": "C:/Users/SOUTHPAW GAMES/Downloads/# 4번_완성본.png", "off_x": 0, "off_y": -234, "zoom": 2.0, "alpha": 255, "parallax": 0.703448275862069, "loop_x": True}, {"path": "C:/Users/SOUTHPAW GAMES/Downloads/레이어 3.png", "off_x": 0, "off_y": 137, "zoom": 2.0, "alpha": 255, "parallax": 1.0, "loop_x": True}]}, "ai": {"target_ai_count": 0}, "platforms": {"alpha": 150}}
        
        # Apply settings
        for cat_name, cat in set_data.items():
            if isinstance(cat, dict):
                if cat_name == "bg":
                    if "bg_color" in cat: self.bg_color = cat["bg_color"]
                    if "layers" in cat:
                        self.bg_layers = []
                        for l_data in cat["layers"]:
                            path = l_data.get("path", "")
                            if path and not os.path.exists(path): path = os.path.basename(path)
                            layer = {"path": path, "off_x": l_data.get("off_x", 0), "off_y": l_data.get("off_y", 0), "zoom": l_data.get("zoom", 2.0), "alpha": l_data.get("alpha", 255), "parallax": l_data.get("parallax", 1.0), "loop_x": l_data.get("loop_x", False), "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                            if os.path.exists(path):
                                layer["img"] = pygame.image.load(path).convert_alpha()
                                layer["last_mtime"] = os.path.getmtime(path)
                            self.bg_layers.append(layer)
                else:
                    for k, v in cat.items():
                        if k == "alpha" and "platforms" in set_data: self.platform_alpha = v
                        elif hasattr(self, k): setattr(self, k, v)
                
        # Apply project
        self.sources = []; self.profiles = []; self.ai_list = []; self.temp_ai_list = []
        for src_p in proj_data.get("sources", []):
            if not os.path.exists(src_p): src_p = os.path.basename(src_p)
            if os.path.exists(src_p): self.add_source(src_p)
        for prof_data in proj_data.get("profiles", []):
            new_prof = AseProfile(prof_data["name"], prof_data["source_idx"]); new_prof.mappings = prof_data["mappings"]; self.profiles.append(new_prof)
            if prof_data["name"] != "PLAYER": self.ai_list.append(AseAI(self, new_prof))
        
        self.platforms = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data["platforms"]]
        self.solid_boxes = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data.get("solid_boxes", [])]
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx, self.vy = 0, 0
        self.cam_x, self.cam_y = self.x, self.y
        self.save_settings(); self.save_project()
    def add_source(self, path, is_prop_source=False):
        try:
            new_source = AseSource(path, len(self.sources))
            new_source.is_prop_source = is_prop_source
            self.sources.append(new_source); self.cur_source_idx = new_source.id; return new_source.id
        except: return 0

    def remove_source_by_index(self, i):
        if i < 0 or i >= len(self.sources): return
        # Adjust sources
        self.sources.pop(i)
        for idx, s in enumerate(self.sources):
            s.id = idx # Update internal IDs to match new list indices
            
        if self.cur_source_idx > i: self.cur_source_idx -= 1
        elif self.cur_source_idx >= len(self.sources): self.cur_source_idx = max(0, len(self.sources)-1)
        
        # Shift profile indices
        for prof in self.profiles:
            if prof.source_idx > i: prof.source_idx -= 1
            for slot, mappings in prof.mappings.items():
                prof.mappings[slot] = [m for m in mappings if m[0] != i]
                for mapping in prof.mappings[slot]:
                    if mapping[0] > i: mapping[0] -= 1
                    
        # Shift active action indices for all entities
        for ent in [self] + self.ai_list + getattr(self, 'prop_list', []):
            if ent.active_tag_info and ent.active_tag_info[0] == i:
                ent.active_tag_info = None; ent.active_action_slot = None
            elif ent.active_tag_info and ent.active_tag_info[0] > i: ent.active_tag_info[0] -= 1
            ent.action_queue = [act for act in ent.action_queue if act[0] != i]
            for act in ent.action_queue:
                if act[0] > i: act[0] -= 1

    def add_profile(self, name, source_idx, is_npc=False):
        new_profile = AseProfile(name, source_idx); self.profiles.append(new_profile); self.auto_map_profile(new_profile)
        if is_npc: self.ai_list.append(AseAI(self, new_profile))
    def auto_map_profile(self, profile):
        if profile.source_idx >= len(self.sources): return
        source = self.sources[profile.source_idx]; suffix = re.compile(r"(_|\s)?\(?(ready|loop|end)\)?", re.IGNORECASE)
        for slot in profile.mappings.keys():
            base_slot = slot.lower().replace("ComboAttack_", "attack").replace(" ", "").replace("_", ""); matches = []
            for t in source.tag_list:
                clean_t = suffix.sub("", t).lower().replace(" ", "").replace("_", "")
                if clean_t == base_slot or (base_slot == "walk" and clean_t == "move"): matches.append([profile.source_idx, t])
            def sort_key(item): tl = item[1].lower(); return 0 if "ready" in tl else (2 if "end" in tl else 1)
            profile.mappings[slot] = sorted(matches, key=sort_key)
    def handle_attack(self, keys):
        if self.swap_timer > 0: return
        if not self.grounded:
            if keys[pygame.K_DOWN]: self.trigger_action("POWERBOMB", keys)
            else: self.trigger_action("JUMPATTACK", keys)
        elif self.profiles:
            # Check current attack slot and buffering
            if self.active_action_slot and "ComboAttack" in str(self.active_action_slot):
                if self.attack_buffer < 1: self.attack_buffer += 1
            else:
                # If reset timer expired, start from 1
                if self.combo_reset_timer <= 0: self.combo_step = 0
                slot = f"ComboAttack_{self.combo_step + 1}"
                # Check if this slot exists and has tags
                p = self.profiles[0]
                if not p.mappings.get(slot, []):
                    self.combo_step = 0
                    slot = "ComboAttack_1"
                self.trigger_action(slot, keys)

    def trigger_action(self, slot, keys=None):
        if self.swap_timer > 0 or not self.profiles: return
        # Dash can interrupt everything
        if slot == "DASH":
            if self.dash_charges > 0:
                log_debug(f"[ACTION] DASH triggered")
                self.dash_charges -= 1; self.dash_timer = 200; self.vx = self.dash_speed if self.facing_right else -self.dash_speed; self.vy = 0; self.active_action_slot = "DASH"; self.action_queue = list(self.profiles[0].mappings.get(slot, [])); self.play_next_in_queue()
                for i in range(2): 
                    if self.dash_cooldowns[i] <= 0: self.dash_cooldowns[i] = 1500; break
            return
        
        # Don't restart the same action unless it's a specific one
        if self.active_action_slot == slot and slot not in ["JUMP"]: return
        if self.active_action_slot and "ComboAttack" in str(self.active_action_slot) and "ComboAttack" not in slot: return
        
        profile = self.profiles[0]
        tags = profile.mappings.get(slot, [])
        
        if not tags and slot == "Swap_Exit":
             self.visible = False; return
             
        if not tags and slot == "FALL": # Fallback for Fall if no mapping
             self.active_action_slot = None; self.active_tag_info = None; return

        if tags:
            log_debug(f"[ACTION] Triggering {slot}")
            self.active_action_slot = slot; self.action_queue = list(tags); self.loop_counter = 0; self.anim_timer = 0
            if "ComboAttack" in slot:
                # Update combo step
                self.combo_step = int(slot.split("_")[-1])
                self.combo_reset_timer = 1000 # 1 second window
                curr_keys = keys if keys is not None else pygame.key.get_pressed()
                if curr_keys[pygame.K_RIGHT] or curr_keys[pygame.K_LEFT]: 
                    self.attack_move_timer = 200; self.facing_right = curr_keys[pygame.K_RIGHT]; mv = self.atk_forward_v * 0.5
                    self.vx = mv if self.facing_right else -mv
                else: self.attack_move_timer = 0; self.vx = 0
            elif slot == "POWERBOMB": self.pbomb_pause_timer = 250; self.vy = 0; self.vx = 0
            elif slot == "FALL":
                # Explicit Sequence for Fall: Try to find Fall_Ready then Fall_Loop
                ready_tags = [t for t in tags if "ready" in t[1].lower()]
                loop_tags = [t for t in tags if "loop" in t[1].lower()]
                if ready_tags and loop_tags:
                    if getattr(self, "drop_through_timer", 0) > 0:
                        log_debug(f"[FALL] Drop Through Sequence: Loop({loop_tags[0][1]})")
                        self.action_queue = list(loop_tags)
                    else:
                        log_debug(f"[FALL] Sequence: Ready({ready_tags[0][1]}) -> Loop({loop_tags[0][1]})")
                        self.action_queue = list(ready_tags + loop_tags)
                elif tags:
                    log_debug(f"[FALL] Tags: {[t[1] for t in tags]}")
                    self.action_queue = list(tags)
            self.play_next_in_queue()

    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag_info = self.action_queue.pop(0)
            if not self.active_tag_info or self.active_tag_info[0] < 0 or self.active_tag_info[0] >= len(self.sources):
                self.active_tag_info = None
                self.active_action_slot = None
                self.action_queue = []
                return
            src = self.sources[self.active_tag_info[0]]
            if self.active_tag_info[1] in src.tags: 
                self.frame_idx, self.action_end_frame = src.tags[self.active_tag_info[1]]
                log_debug(f"  [QUEUE] Start Tag: {self.active_tag_info[1]} (Frames {self.frame_idx}-{self.action_end_frame})")
                self.loop_counter = 0; self.anim_timer = 0
            else: self.play_next_in_queue()
        else:
            log_debug(f"  [QUEUE] Empty for {self.active_action_slot}")
            if self.attack_buffer > 0:
                self.attack_buffer -= 1
                next_step = self.combo_step + 1
                if next_step > 4: next_step = 1
                slot = f"ComboAttack_{next_step}"
                # If next combo doesn't exist, stop
                if not self.profiles[0].mappings.get(slot, []):
                    self.active_action_slot = None; self.active_tag_info = None; self.attack_buffer = 0
                else:
                    self.active_action_slot = None; self.trigger_action(slot)
                return
            self.active_tag_info = None; self.active_action_slot = None; self.attack_buffer = 0
            if getattr(self, 'pending_swap', False): self.execute_swap()

    def execute_swap(self):
        if len(self.profiles) <= 1: return
        target_idx = getattr(self, 'swap_target_idx', 0)
        if target_idx == 0 or target_idx >= len(self.profiles):
            target_idx = 1
            
        self.pending_swap = False
        target_p = self.profiles[target_idx]
        
        # Old Player -> Temporary AI for Exit
        temp_ai = AseAI(self, self.profiles[0], is_temp=True)
        temp_ai.x, temp_ai.y = self.x, self.y
        temp_ai.vx, temp_ai.vy = self.vx, self.vy
        temp_ai.facing_right = self.facing_right
        
        # Inherit current action and attack buffer
        temp_ai.active_tag_info = self.active_tag_info
        temp_ai.action_queue = list(self.action_queue)
        temp_ai.active_action_slot = self.active_action_slot
        temp_ai.attack_buffer = getattr(self, 'attack_buffer', 0)
        temp_ai.combo_step = getattr(self, 'combo_step', 0)
        temp_ai.frame_idx = self.frame_idx
        temp_ai.anim_timer = self.anim_timer
        
        if not temp_ai.active_action_slot:
            temp_ai.trigger_action("Swap_Exit")
            
        self.temp_ai_list.append(temp_ai)
        
        # Swap profiles array
        self.profiles[0], self.profiles[target_idx] = target_p, self.profiles[0]
        
        # Setup new player position (Behind the exiting character)
        offset = -40 if temp_ai.facing_right else 40
        self.x = temp_ai.x + offset
        self.y = temp_ai.y
        self.facing_right = temp_ai.facing_right
        
        # If the target profile was an active AI, remove it
        target_ai = next((ai for ai in self.ai_list if ai.profile == target_p), None)
        if target_ai:
            self.ai_list.remove(target_ai)
            
        self.vx, self.vy = 0, 0
        self.active_tag_info = None; self.action_queue = []; self.active_action_slot = None
        self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0
        self.trigger_action("Swap_Enter")
        self.swap_vfx_timer = 400
        self.swap_vfx_max_timer = 400
        self.visible = True

    def check_hits(self):
        if not self.active_tag_info or self.active_tag_info[0] < 0 or self.active_tag_info[0] >= len(self.sources): return
        src = self.sources[self.active_tag_info[0]]
        hitboxes = []
        has_hit_slice = False
        for name, keys in src.slices.items():
            if "hit" in name.lower():
                has_hit_slice = True
                active_key = None
                for key in keys:
                    if key['frame'] <= self.frame_idx:
                        if active_key is None or key['frame'] > active_key['frame']: active_key = key
                if active_key:
                    b = active_key['bounds']
                    ox = (b['x'] - src.orig_w // 2) if self.facing_right else -(b['x'] - src.orig_w // 2 + b['w'])
                    hitboxes.append(pygame.Rect(self.x + ox, self.y + b['y'] - src.orig_h // 2, b['w'], b['h']))
        
        # Auto-generate hitbox if none exists and this is an attack
        if not has_hit_slice and self.active_action_slot:
            slot_l = self.active_action_slot.lower()
            tag_name_l = self.active_tag_info[1].lower()
            if ("attack" in slot_l or "powerbomb" in slot_l or "dash" in slot_l or "skill" in slot_l) and "ready" not in tag_name_l and "end" not in tag_name_l:
                tr = src.tags.get(self.active_tag_info[1], (0, 0))
                # Only hit on the first frame of the attack animation to prevent multi-hits per action
                if self.frame_idx == tr[0]:
                    hw, hh = 60, 50
                    ox = 10 if self.facing_right else -10 - hw
                    hitboxes.append(pygame.Rect(self.x + ox, self.y - 50, hw, hh))

        if not hitboxes: return

        for ai in self.ai_list[:] + getattr(self, 'prop_list', [])[:]:
            if ai.hit_cooldown <= 0 and ai.visible and not ai.is_dead:
                ai_rect = pygame.Rect(ai.x - 20, ai.y - 60, 40, 60) # Default approximate hurtbox
                for hb in hitboxes:
                    if hb.colliderect(ai_rect):
                        ai.hp -= 1; ai.hit_cooldown = 500
                        if self.shake_enabled: self.shake_timer = 10; self.shake_intensity = 5
                        
                        # Generate Hit Particles
                        hit_particles_spawned = False
                        if getattr(ai, 'is_prop', False) and ai.profile.source_idx >= 0 and ai.profile.source_idx < len(self.sources):
                            prop_src = self.sources[ai.profile.source_idx]
                            hit_tag = next((t for t in prop_src.tags.keys() if "particles" in t.lower()), None)
                            if hit_tag:
                                h_frame = prop_src.tags[hit_tag][0]
                                hit_img = prop_src.get_frame(h_frame, 1.0, True)
                                if hit_img:
                                    for s_name, s_keys in prop_src.slices.items():
                                        if "particle" in s_name.lower():
                                            active_key = None
                                            for key in s_keys:
                                                if key['frame'] <= h_frame:
                                                    if active_key is None or key['frame'] > active_key['frame']: active_key = key
                                            if active_key:
                                                b = active_key['bounds']
                                                try:
                                                    cropped = pygame.Surface((b['w'], b['h']), pygame.SRCALPHA)
                                                    f_info = prop_src.frames[h_frame]
                                                    crop_x = b['x'] - prop_src.orig_w // 2 - f_info['ox']
                                                    crop_y = b['y'] - prop_src.orig_h // 2 - f_info['oy']
                                                    cropped.blit(hit_img, (-crop_x, -crop_y))
                                                    px = ai.x + random.uniform(-15, 15)
                                                    py = ai.y - 30 + random.uniform(-10, 10)
                                                    self.particles.append(Particle(px, py, random.uniform(-10, 10)*self.debris_force, random.uniform(-15, -5)*self.debris_force, (255, 255, 255), 10, random.randint(600, 1000), image=cropped))
                                                    hit_particles_spawned = True
                                                except: pass
                                                
                        if not hit_particles_spawned:
                            for _ in range(8):
                                self.particles.append(Particle(ai.x, ai.y - 30, random.uniform(-10, 10)*self.debris_force, random.uniform(-15, -5)*self.debris_force, (200, 200, 200) if getattr(ai, 'is_prop', False) else (220, 38, 38), random.uniform(2, 5), random.randint(300, 600)))
                        
                        if getattr(ai, 'is_prop', False):
                            ai.stage_hp -= 1
                            if ai.stage_hp <= 0:
                                ai.prop_state += 1 # Advance to next break state
                                
                                # Check if the next Break state actually exists in the Aseprite file.
                                # If Break1 or Break2 doesn't exist, immediately skip to destruction (state 3).
                                if ai.prop_state < 3:
                                    next_state_name = f"Break{ai.prop_state}"
                                    if not ai.profile.mappings.get(next_state_name, []):
                                        ai.prop_state = 3 # Fast-forward to total destruction
                                
                                if ai.prop_state >= 3:
                                    ai.is_dead = True
                                    # --- Prop Destruction Logic ---
                                    # Generate precise debris from the "Parts" tag and its internal Slices
                                    debris_created = False
                                    if ai.profile.source_idx >= 0 and ai.profile.source_idx < len(self.sources):
                                        prop_src = self.sources[ai.profile.source_idx]
                                        # Look for a tag named 'Parts' (case-insensitive)
                                        parts_tag = next((t for t in prop_src.tags.keys() if "parts" in t.lower()), None)
                                        if parts_tag:
                                            p_frame = prop_src.tags[parts_tag][0]
                                            full_frame_img = prop_src.get_frame(p_frame, 1.0, True) # Unscaled original frame
                                            if full_frame_img:
                                                for s_name, s_keys in prop_src.slices.items():
                                                    active_key = None
                                                    for key in s_keys:
                                                        if key['frame'] <= p_frame:
                                                            if active_key is None or key['frame'] > active_key['frame']:
                                                                active_key = key
                                                    if active_key:
                                                        b = active_key['bounds']
                                                        try:
                                                            # Crop the exact slice area from the Aseprite canvas
                                                            cropped = pygame.Surface((b['w'], b['h']), pygame.SRCALPHA)
                                                            f_info = prop_src.frames[p_frame]
                                                            crop_x = b['x'] - prop_src.orig_w // 2 - f_info['ox']
                                                            crop_y = b['y'] - prop_src.orig_h // 2 - f_info['oy']
                                                            cropped.blit(full_frame_img, (-crop_x, -crop_y))
                                                            
                                                            # Calculate precise spawn location of the debris in the game world 
                                                            # based on the slice's visual offset from the prop's center pivot
                                                            if ai.facing_right:
                                                                px = ai.x + (b['x'] - prop_src.orig_w // 2) + b['w'] / 2
                                                            else:
                                                                px = ai.x - (b['x'] - prop_src.orig_w // 2 + b['w']) + b['w'] / 2
                                                            py = ai.y + (b['y'] - prop_src.orig_h // 2) + b['h'] / 2
                                                            
                                                            self.particles.append(Particle(px, py, random.uniform(-15, 15)*self.debris_force, random.uniform(-20, -5)*self.debris_force, (255, 255, 255), 10, 10000, image=cropped))
                                                            debris_created = True
                                                        except Exception as e:
                                                            log_debug(f"Failed to crop prop slice: {e}")
                                    
                                    # Fallback: Auto-slice the current frame into a 3x3 grid if no Parts tag exists
                                    if not debris_created and ai.profile.source_idx >= 0 and ai.profile.source_idx < len(self.sources):
                                        prop_src = self.sources[ai.profile.source_idx]
                                        full_frame_img = prop_src.get_frame(ai.frame_idx, 1.0, ai.facing_right)
                                        if full_frame_img:
                                            w, h = full_frame_img.get_width(), full_frame_img.get_height()
                                            cols, rows = 3, 3
                                            cw, ch = w // cols, h // rows
                                            if cw > 0 and ch > 0:
                                                f_info = prop_src.frames[ai.frame_idx]
                                                start_x = ai.x + f_info['ox'] if ai.facing_right else ai.x - f_info['ox'] - w
                                                start_y = ai.y + f_info['oy']
                                                
                                                for row in range(rows):
                                                    for col in range(cols):
                                                        try:
                                                            cropped = pygame.Surface((cw, ch), pygame.SRCALPHA)
                                                            cropped.blit(full_frame_img, (-col * cw, -row * ch))
                                                            
                                                            # Skip completely empty/transparent chunks
                                                            if not cropped.get_bounding_rect().width: continue
                                                            
                                                            px = start_x + col * cw + cw//2
                                                            py = start_y + row * ch + ch//2
                                                            
                                                            self.particles.append(Particle(px, py, random.uniform(-15, 15)*self.debris_force, random.uniform(-20, -5)*self.debris_force, (255, 255, 255), max(cw, ch), 10000, image=cropped))
                                                            debris_created = True
                                                        except Exception as e:
                                                            log_debug(f"Auto-slice failed: {e}")
                                    
                                    # Ultimate Fallback: Just in case the image was too small to slice
                                    if not debris_created:
                                        for _ in range(15):
                                            self.particles.append(Particle(ai.x, ai.y - 20, random.uniform(-15, 15)*self.debris_force, random.uniform(-20, -5)*self.debris_force, (139, 69, 19), random.uniform(4, 8), random.randint(500, 1000)))
                                    
                                    if ai in getattr(self, 'prop_list', []): self.prop_list.remove(ai)
                                else:
                                    # Reset HP for the next stage (Break1 or Break2)
                                    ai.stage_hp = 3
                        else:
                            ai.hp -= 1
                            if ai.hp <= 0:
                                ai.is_dead = True
                                ai.trigger_action("HURT")
                        break # Only hit once per attack frame

        # Check hits on interactive debris particles
        for p in getattr(self, 'particles', []):
            if getattr(p, 'hit_cooldown', 0) > 0:
                p.hit_cooldown -= 16.6
                continue
            pw = p.image.get_width() if p.image else p.size
            ph = p.image.get_height() if p.image else p.size
            p_rect = pygame.Rect(p.x - pw/2, p.y - ph/2, pw, ph)
            for hb in hitboxes:
                if hb.colliderect(p_rect):
                    p.vx = (random.uniform(5, 20) if self.facing_right else random.uniform(-20, -5)) * self.debris_force
                    p.vy = random.uniform(-15, -5) * self.debris_force
                    p.rot_speed = random.uniform(-30, 30)
                    p.lifetime = min(p.max_life, p.lifetime + 2000) # Give it some extra life if kicked
                    p.hit_cooldown = 300 # Prevent multi-hits
                    break

    def update(self, keys, ground_y, dt):
        if hasattr(self, "_btn_lock"):
            self._btn_lock -= 1
            if self._btn_lock <= 0: delattr(self, "_btn_lock")
            
        self.check_hits()
        
        # Update particles
        for p in self.particles[:]:
            p.update(dt, self.gravity, ground_y, self.platforms)
            if p.lifetime <= 0: self.particles.remove(p)
            
        while len(self.ai_list) < self.target_ai_count:
            if len(self.profiles) > 1: self.ai_list.append(AseAI(self, self.profiles[1]))
            elif self.profiles: self.ai_list.append(AseAI(self, self.profiles[0]))
            else: break
        while len(self.ai_list) > self.target_ai_count: self.ai_list.pop()
        if self.drop_through_timer > 0: self.drop_through_timer -= dt
        if self.shake_timer > 0: self.shake_timer -= dt / 16.6
        if getattr(self, 'swap_vfx_timer', 0) > 0: self.swap_vfx_timer -= dt
        if self.vfx_enabled:
            for ai in self.afterimages[:]:
                ai['alpha'] -= 15 * (dt/16.6)
                if ai['alpha'] <= 0: self.afterimages.remove(ai)
            if self.dash_timer > 0:
                self.ghost_timer += dt
                if self.ghost_timer >= 30: 
                    self.ghost_timer = 0; s_idx = self.active_tag_info[0] if self.active_tag_info else 0; self.afterimages.append({'x': self.x, 'y': self.y, 's': s_idx, 'f': self.frame_idx, 'right': self.facing_right, 'alpha': 180})
        if pygame.time.get_ticks() % 60 == 0:
            for src in self.sources:
                if src.check_for_reload(): [self.auto_map_profile(p) for p in self.profiles]
            # Check BG Reload
            for bg in self.bg_layers:
                if bg.get('path') and os.path.exists(bg['path']):
                    try:
                        mt = os.path.getmtime(bg['path'])
                        if mt > bg.get('last_mtime', 0):
                            bg['img'] = pygame.image.load(bg['path']).convert_alpha()
                            bg['needs_update'] = True
                            bg['last_mtime'] = mt
                            log_debug(f"[BG] Auto-reloaded background image: {bg['path']}")
                    except: pass
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        for i in range(2):
            if self.dash_cooldowns[i] > 0:
                self.dash_cooldowns[i] -= dt
                if self.dash_cooldowns[i] <= 0: self.dash_charges = min(2, self.dash_charges + 1)
        if self.pbomb_pause_timer > 0:
            self.pbomb_pause_timer -= dt; self.vy = 0
            if self.pbomb_pause_timer <= 0: self.vy = self.powerbomb_speed; self.pbomb_pause_timer = 0
        elif self.dash_timer > 0: self.dash_timer -= dt; self.vy = 0
        elif self.attack_move_timer > 0: self.attack_move_timer -= dt; self.vy += self.gravity * 0.5
        else:
            self.vx *= 0.82; can_move = not self.active_tag_info or self.active_action_slot in ["FALL", "JUMPATTACK"]
            if can_move:
                if keys[pygame.K_RIGHT]: self.vx = 4.2; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -4.2; self.facing_right = False
            self.vy += self.gravity * (dt / 16.6)
        # X-Axis Movement & Collision
        self.x += self.vx * (dt/16.6)
        if hasattr(self, "solid_boxes"):
            player_rect = pygame.Rect(self.x-10, self.y-50, 20, 50) # Approx Hitbox
            for box in self.solid_boxes:
                if box.colliderect(player_rect):
                    if self.vx > 0: self.x = box.left - 10
                    elif self.vx < 0: self.x = box.right + 10
                    self.vx = 0

        # Y-Axis Movement & Collision
        self.y += self.vy * (dt/16.6); self.grounded = False
        if hasattr(self, "solid_boxes"):
            player_rect = pygame.Rect(self.x-10, self.y-50, 20, 50)
            for box in self.solid_boxes:
                if box.colliderect(player_rect):
                    if self.vy > 0: 
                        self.y = box.top + 50; self.grounded = True; self.vy = 0; self.jumps_left = 2
                        if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None
                    elif self.vy < 0: self.y = box.bottom + 50; self.vy = 0
        
        # Grounding Logic
        if self.y >= ground_y: 
            if self.active_action_slot == "POWERBOMB" and self.vy > 0 and self.shake_enabled: self.shake_timer = 15; self.shake_intensity = 15
            self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
            if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None
        if self.vy >= 0 and self.drop_through_timer <= 0:
            for plat in self.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - (self.vy * (dt/16.6)) <= plat.top + 10: 
                    # PowerBomb Impact on Platform
                    if self.active_action_slot == "POWERBOMB" and self.shake_enabled: self.shake_timer = 15; self.shake_intensity = 15
                    self.y = plat.top; self.vy = 0; self.grounded = True; self.jumps_left = 2
                    if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None
        
        if self.grounded and (self.active_action_slot == "JUMPATTACK" or self.active_action_slot == "POWERBOMB"):
            if self.active_tag_info: self.play_next_in_queue()
        if self.cam_follow:
            self.cam_x += (self.x - self.cam_x) * 0.25; self.cam_y += (self.y + self.cam_v_offset - self.cam_y) * (0.3 if self.grounded else 0.25)
        
        # Combo Reset Logic
        if self.combo_reset_timer > 0:
            self.combo_reset_timer -= dt
            if self.combo_reset_timer <= 0: self.combo_step = 0
            
        if self.visible:
            if not self.active_tag_info:
                # Early Fall Trigger: Change state to FALL when upward velocity slows down (vy > -4.0)
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < -4.0 else "FALL"))
                if state == "FALL" and self.active_action_slot != "FALL" and self.active_action_slot != "POWERBOMB": self.trigger_action("FALL")
                if not self.active_tag_info:
                    m = self.profiles[0].mappings.get(state, []) if self.profiles else []; target_info = m[0] if m else None
                else: target_info = self.active_tag_info
            else: target_info = self.active_tag_info
            
            if target_info and target_info[0] >= 0 and target_info[0] < len(self.sources):
                src = self.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
                if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
                if not self.is_paused or self.step_forward:
                    self.anim_timer += dt
                    if self.step_forward: self.anim_timer = src.frames[self.frame_idx]['duration']; self.step_forward = False
                if self.frame_idx < len(src.frames):
                    dur = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= dur:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit": self.visible = False; self.swap_timer = 500; self.active_tag_info = None; return
                            is_skill = "SKILL" in str(self.active_action_slot)
                            is_loop = "(loop)" in target_info[1].lower()
                            is_fall = self.active_action_slot == "FALL"
                            
                            if is_loop:
                                if is_fall or not is_skill: self.frame_idx = tr[0] # Continuous loop
                                elif is_skill and self.loop_counter < 1: self.frame_idx = tr[0]; self.loop_counter += 1
                                else: self.play_next_in_queue()
                            else: self.play_next_in_queue()
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]
        for ai in self.ai_list: ai.update(ground_y, dt)
        for prop in getattr(self, 'prop_list', []): prop.update(ground_y, dt)
        for ai in getattr(self, 'temp_ai_list', [])[:]:
            ai.update(ground_y, dt)
            if not ai.visible: self.temp_ai_list.remove(ai)

    def draw_sprite(self, screen, x, y, source_idx, f_idx, facing_right, cam_x, cam_y, cx, cy, entity=None):
        if source_idx < 0 or source_idx >= len(self.sources): return
        src = self.sources[source_idx]; scaled = src.get_frame(f_idx, self.zoom, facing_right)
        if not scaled: return
        f = src.frames[min(max(0, f_idx), len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
        if not facing_right: ox = -ox - scaled.get_width()
        screen.blit(scaled, (int(cx + (x - cam_x)*self.zoom + ox), int(cy + (y - cam_y)*self.zoom + oy)))
        if self.show_hitboxes:
            has_hit_slice = False
            has_hurt_slice = False
            for name, keys in src.slices.items():
                active_key = None
                for key in keys:
                    if key['frame'] <= f_idx:
                        if active_key is None or key['frame'] > active_key['frame']: active_key = key
                if active_key:
                    if "hit" in name.lower(): has_hit_slice = True
                    elif "hurt" in name.lower() or "body" in name.lower(): has_hurt_slice = True
                    b = active_key['bounds']; sx = cx + (x - cam_x) * self.zoom; sy = cy + (y - cam_y) * self.zoom; final_x = sx + (b['x'] - src.orig_w // 2) * self.zoom; final_y = sy + (b['y'] - src.orig_h // 2) * self.zoom; final_w = b['w'] * self.zoom; final_h = b['h'] * self.zoom
                    if not facing_right: final_x = sx - (b['x'] - src.orig_w // 2 + b['w']) * self.zoom
                    col = (220, 38, 38) if "hit" in name.lower() else (22, 163, 74); pygame.draw.rect(screen, col, (final_x, final_y, final_w, final_h), 2)
                    if self.zoom > 1.5 and getattr(self, 'font_10', None): txt = self.font_10.render(name, True, col); screen.blit(txt, (final_x, final_y - 12))
            
            # Auto-generate default hurtbox
            if not has_hurt_slice:
                hx, hy = cx + (x - cam_x - 20) * self.zoom, cy + (y - cam_y - 60) * self.zoom
                pygame.draw.rect(screen, (22, 163, 74), (hx, hy, 40*self.zoom, 60*self.zoom), 2)
                if self.zoom > 1.5 and getattr(self, 'font_10', None): screen.blit(self.font_10.render("Auto_Hurtbox", True, (22, 163, 74)), (hx, hy - 12))
                
            # Auto-generate default hitbox for attacks
            if not has_hit_slice and entity and getattr(entity, 'active_action_slot', None):
                slot_l = entity.active_action_slot.lower()
                tag_name_l = entity.active_tag_info[1].lower() if entity.active_tag_info else ""
                if ("attack" in slot_l or "powerbomb" in slot_l or "dash" in slot_l or "skill" in slot_l) and "ready" not in tag_name_l and "end" not in tag_name_l:
                    if entity.active_tag_info:
                        tr = src.tags.get(entity.active_tag_info[1], (0, 0))
                        if f_idx == tr[0] and not getattr(entity, 'is_prop', False):
                            hw, hh = 60, 50
                            hox = 10 if facing_right else -10 - hw
                            hx = cx + (x - cam_x + hox) * self.zoom
                            hy = cy + (y - cam_y - 50) * self.zoom
                            pygame.draw.rect(screen, (220, 38, 38), (hx, hy, hw*self.zoom, hh*self.zoom), 2)
                            if self.zoom > 1.5 and getattr(self, 'font_10', None): screen.blit(self.font_10.render("Auto_Hitbox", True, (220, 38, 38)), (hx, hy - 12))

    def get_overlay(self, w, h, color):
        if not hasattr(self, '_overlays'): self._overlays = {}
        key = (w, h, color)
        if key not in self._overlays:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill(color)
            self._overlays[key] = surf
        return self._overlays[key]
        
    def get_viewport_overlay(self, w, h, vr):
        if not hasattr(self, '_vp_overlay') or getattr(self, '_vp_overlay_key', None) != (w, h, vr.x, vr.y, vr.w, vr.h):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 160))
            pygame.draw.rect(surf, (0, 0, 0, 0), vr) # Cut transparent hole
            self._vp_overlay = surf
            self._vp_overlay_key = (w, h, vr.x, vr.y, vr.w, vr.h)
        return self._vp_overlay

    def draw(self, screen, play_w, play_h):
        if not hasattr(self, "solid_boxes"): self.solid_boxes = []
        cx, cy = play_w // 2, play_h // 2; off_x = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; off_y = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; cam_x, cam_y = self.cam_x + off_x, self.cam_y + off_y; gx, gy = cx - (cam_x % 100)*self.zoom, cy - (cam_y % 100)*self.zoom
        for i in range(-10, 20): pygame.draw.line(screen, self.grid_color, (int(gx+i*100*self.zoom), 0), (int(gx+i*100*self.zoom), play_h), 1); pygame.draw.line(screen, self.grid_color, (0, int(gy+i*100*self.zoom)), (play_w, int(gy+i*100*self.zoom)), 1)
        self.update_bg_cache()
        for bg in self.bg_layers:
            if bg.get('cached_bg'):
                bg_w = bg['cached_bg'].get_width()
                bg_h = bg['cached_bg'].get_height()
                bx = cx + (self.spawn_x - cam_x) * bg.get('parallax', 1.0) * self.zoom + bg.get('off_x', 0) * self.zoom - bg_w // 2
                by = cy + (self.spawn_y - cam_y) * bg.get('parallax', 1.0) * self.zoom + bg.get('off_y', 0) * self.zoom - bg_h // 2
                
                # Vertical Culling (Skip if entirely above or below the viewport)
                if by > play_h or by + bg_h < 0:
                    continue

                if bg.get('loop_x') and bg_w > 0:
                    start_x = bx % bg_w
                    if start_x > 0: start_x -= bg_w
                    
                    for draw_x in range(int(start_x), int(play_w), int(bg_w)):
                        # Horizontal Culling per tile
                        if draw_x > play_w or draw_x + bg_w < 0: continue
                        screen.blit(bg['cached_bg'], (draw_x, int(by)))
                else:
                    # Horizontal Culling for non-looping background
                    if bx > play_w or bx + bg_w < 0: continue
                    screen.blit(bg['cached_bg'], (int(bx), int(by)))
        
        # Draw Platforms
        for i, p in enumerate(self.platforms): 
            px, py, pw, ph = int(cx+(p.x-cam_x)*self.zoom), int(cy+(p.y-cam_y)*self.zoom), int(p.w*self.zoom), int(p.h*self.zoom)
            if px + pw < 0 or px > play_w or py + ph < 0 or py > play_h: continue # Culling
            
            p_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            col = (255, 255, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i else (80, 80, 100, self.platform_alpha)
            pygame.draw.rect(p_surf, col, (0, 0, pw, ph), border_radius=int(3*self.zoom))
            if self.edit_platforms and self.selected_plat == i:
                # Resize Handle (Bottom-Right)
                pygame.draw.rect(p_surf, (255, 0, 0), (pw-10, ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(p_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                pygame.draw.line(p_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                pygame.draw.line(p_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
            screen.blit(p_surf, (px, py))

        # Draw Solid Boxes
        for i, b in enumerate(self.solid_boxes):
            px, py, pw, ph = int(cx+(b.x-cam_x)*self.zoom), int(cy+(b.y-cam_y)*self.zoom), int(b.w*self.zoom), int(b.h*self.zoom)
            if px + pw < 0 or px > play_w or py + ph < 0 or py > play_h: continue # Culling
            
            b_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            col = (255, 100, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i + 1000 else (50, 50, 60, self.platform_alpha)
            pygame.draw.rect(b_surf, col, (0, 0, pw, ph))
            if self.edit_platforms and self.selected_plat == i + 1000:
                pygame.draw.rect(b_surf, (255, 0, 0), (pw-10, ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(b_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                pygame.draw.line(b_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                pygame.draw.line(b_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
            screen.blit(b_surf, (px, py))

        # Draw Props in Edit Mode
        if self.edit_platforms:
            for i, prop in enumerate(getattr(self, "prop_list", [])):
                pw, ph = int(40*self.zoom), int(60*self.zoom)
                px, py = int(cx+(prop.x-cam_x)*self.zoom - pw//2), int(cy+(prop.y-cam_y)*self.zoom - ph)
                
                col = (255, 140, 0, 150) if self.selected_plat == i + 2000 else (100, 100, 100, 100)
                pr_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
                pygame.draw.rect(pr_surf, col, (0, 0, pw, ph), border_radius=int(3*self.zoom))
                
                if self.selected_plat == i + 2000:
                    # Delete Button (Top-Right)
                    pygame.draw.rect(pr_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                    pygame.draw.line(pr_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                    pygame.draw.line(pr_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
                screen.blit(pr_surf, (px, py))
        
        pygame.draw.line(screen, (100,100,100), (int(cx+(0-cam_x)*self.zoom), int(cy+(500-cam_y)*self.zoom)), (int(cx+(5000-cam_x)*self.zoom), int(cy+(500-cam_y)*self.zoom)), 2)
        if self.vfx_enabled:
            for ai in self.afterimages:
                src = self.sources[ai['s']]; sc = src.get_frame(ai['f'], self.zoom, ai['right'])
                if sc:
                    img = sc.copy(); img.fill((100, 150, 255, ai['alpha']), special_flags=pygame.BLEND_RGBA_MULT); f = src.frames[min(ai['f'], len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
                    if not ai['right']: ox = -ox - sc.get_width()
                    screen.blit(img, (int(cx + (ai['x'] - cam_x)*self.zoom + ox), int(cy + (ai['y'] - cam_y)*self.zoom + oy)))
        if self.visible:
            cur_s = self.active_tag_info[0] if self.active_tag_info else 0
            if not self.active_tag_info:
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL")); m = self.profiles[0].mappings.get(state, []) if self.profiles else []; cur_s = m[0][0] if m else 0
            self.draw_sprite(screen, self.x, self.y, cur_s, self.frame_idx, self.facing_right, cam_x, cam_y, cx, cy, entity=self)
            
            # --- SWAP VFX: Yellow Stroke (Outline) ---
            if getattr(self, "swap_vfx_timer", 0) > 0:
                prog = (self.swap_vfx_max_timer - self.swap_vfx_timer) / self.swap_vfx_max_timer
                src = self.sources[cur_s]; sc = src.get_frame(self.frame_idx, self.zoom, self.facing_right)
                
                if sc:
                    # Caching Logic for VFX
                    current_key = (self.frame_idx, self.facing_right, cur_s)
                    if not hasattr(self, "last_vfx_key") or self.last_vfx_key != current_key:
                        mask = pygame.mask.from_surface(sc)
                        self.cached_vfx_points = mask.outline()
                        self.last_vfx_key = current_key
                    
                    points = getattr(self, "cached_vfx_points", [])
                    if points and len(points) > 2:
                        alpha = int(255 * (1.0 - prog))
                        f = src.frames[min(max(0, self.frame_idx), len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
                        if not self.facing_right: ox = -ox - sc.get_width()
                        bx = int(cx + (self.x - cam_x)*self.zoom + ox)
                        by = int(cy + (self.y - cam_y)*self.zoom + oy)
                        
                        stroke_surf = pygame.Surface((sc.get_width(), sc.get_height()), pygame.SRCALPHA)
                        pygame.draw.lines(stroke_surf, (255, 255, 0, alpha), True, points, max(1, int(self.zoom)))
                        screen.blit(stroke_surf, (bx, by))

        for ai in self.ai_list + getattr(self, 'prop_list', []) + getattr(self, 'temp_ai_list', []):
            if ai.visible: ai_s = ai.active_tag_info[0] if ai.active_tag_info else ai.profile.source_idx; self.draw_sprite(screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right, cam_x, cam_y, cx, cy, entity=ai)
            adx, ady = (ai.x-cam_x)*self.zoom, (ai.y-cam_y)*self.zoom
            if abs(adx)>play_w//2 or abs(ady)>play_h//2: ang = math.atan2(ady, adx); px, py = cx+math.cos(ang)*(play_w//2-40), cy+math.sin(ang)*(play_h//2-40); pygame.draw.circle(screen, (220,38,38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(ang)*8, py-math.sin(ang)*8), 2)
            
        # Draw Particles
        for p in getattr(self, 'particles', []):
            px = int(cx + (p.x - cam_x) * self.zoom)
            py = int(cy + (p.y - cam_y) * self.zoom)
            s = int(p.size * self.zoom)
            if p.image:
                iw, ih = int(p.image.get_width()*self.zoom), int(p.image.get_height()*self.zoom)
                if px + iw > 0 and px - iw < play_w and py + ih > 0 and py - ih < play_h:
                    if p.cached_zoom != self.zoom or abs(p.cached_rotation - p.rotation) > 1.0 or p.cached_surface is None:
                        scaled_img = pygame.transform.scale(p.image, (max(1, iw), max(1, ih)))
                        p.cached_surface = pygame.transform.rotate(scaled_img, p.rotation)
                        p.cached_zoom = self.zoom
                        p.cached_rotation = p.rotation
                    
                    rect = p.cached_surface.get_rect(center=(px, py))
                    screen.blit(p.cached_surface, rect.topleft)
            else:
                if px + s > 0 and px < play_w and py + s > 0 and py < play_h:
                    pygame.draw.rect(screen, p.color, (px, py, s, s))
                
        if self.show_viewport:
            vw, vh = self.target_w * self.zoom, self.target_h * self.zoom; vr = pygame.Rect(cx - vw//2, cy - vh//2, vw, vh)
            overlay = self.get_viewport_overlay(play_w, play_h, vr)
            screen.blit(overlay, (0, 0)); pygame.draw.rect(screen, (255, 255, 255), vr, 1)
            if getattr(self, 'font_12', None): screen.blit(self.font_12.render(f"Viewport: {self.target_w}x{self.target_h} (16:9)", True, (255,255,255)), (vr.x, vr.y - 18))
        
        # Popup Overlay Draw
        if self.popup:
            msg_w, msg_h = 300, 150; cx, cy = screen.get_width()//2, screen.get_height()//2
            overlay = self.get_overlay(screen.get_width(), screen.get_height(), (0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(screen, (40, 40, 45), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), border_radius=10)
            pygame.draw.rect(screen, (60, 60, 65), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), 2, border_radius=10)
            
            # Use globally available font_b and font_s from main() scoping or just assume they exist
            # Note: since font_b is built in main(), drawing it here will just access it globally.
            screen.blit(font_b.render("Confirm Action", True, (255, 255, 255)), (cx-50, cy-50))
            screen.blit(font_s.render(self.popup['msg'], True, (200, 200, 200)), (cx-len(self.popup['msg'])*3, cy-20))
            
            yes_btn = pygame.Rect(cx-80, cy+20, 60, 30); no_btn = pygame.Rect(cx+20, cy+20, 60, 30)
            pygame.draw.rect(screen, (59, 130, 246), yes_btn, border_radius=5)
            pygame.draw.rect(screen, (220, 38, 38), no_btn, border_radius=5)
            screen.blit(font_b.render("YES", True, (255,255,255)), (yes_btn.x+15, yes_btn.y+5))
            screen.blit(font_b.render("NO", True, (255,255,255)), (no_btn.x+20, no_btn.y+5))

def main():
    pygame.init(); screen = pygame.display.set_mode((1350, 850), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1); clock = pygame.time.Clock(); player = AsepritePlayer(); show_settings = False; slot_scroll = tag_scroll = settings_scroll = 0; font_s = CachedFont(pygame.font.SysFont("Arial", 12)); font_b = CachedFont(pygame.font.SysFont("Arial", 14, bold=True)); font_h = CachedFont(pygame.font.SysFont("Arial", 11)); is_dragging_cam = False; last_m_pos = (0,0); selected_slot = None; folds = {"PROPS": True, "PHYSICS": True, "AI & COMBAT": True, "JUICE & VFX": True, "LAYERS": True, "CAMERA": True, "BG IMAGE": True, "BG COLOR": True, "CONTROLS": False}
    binding_key = None; active_input_attr = None; input_text = ""
    while True:
        raw_dt = clock.tick(60)
        dt = raw_dt * player.playback_speed if player else raw_dt
        sw, sh = screen.get_size(); sidebar_w = 450; play_w = sw - sidebar_w; play_h = sh - 70; m_pos = pygame.mouse.get_pos()
        
        # [OPTIMIZATION] Restrict drawing strictly to the visible game area to prevent massive overdraw under UI panels
        screen.set_clip(pygame.Rect(0, 70, play_w, play_h))
        screen.fill(player.bg_color)
        
        if player: player.update(pygame.key.get_pressed(), 500, dt); player.draw(screen, play_w, play_h)
        
        # Reset clip for UI
        screen.set_clip(None)
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)); pygame.draw.rect(screen, (35, 35, 40), (0, 0, play_w, 70))
        
        # --- TOP UI ROW 1 (Project & Files) ---
        # Group 1: File Management
        new_proj = pygame.Rect(10, 5, 60, 28); pygame.draw.rect(screen, (220, 38, 38), new_proj, border_radius=5); screen.blit(font_b.render("NEW", True, (255,255,255)), (new_proj.x+12, 10))
        
        has_prev = os.path.exists("ase_project.json")
        load_prev = pygame.Rect(75, 5, 60, 28); pygame.draw.rect(screen, (59, 130, 246) if has_prev else (60, 60, 70), load_prev, border_radius=5); screen.blit(font_b.render("LOAD", True, (255,255,255) if has_prev else (120, 120, 120)), (load_prev.x+10, 10))
        
        sv_proj = pygame.Rect(140, 5, 60, 28); pygame.draw.rect(screen, (100, 100, 110), sv_proj, border_radius=5); screen.blit(font_b.render("SAVE", True, (255,255,255)), (sv_proj.x+12, 10))
        
        pygame.draw.line(screen, (80, 80, 90), (210, 5), (210, 33), 2) # Separator
        
        # Group 2: Examples
        example_btn = pygame.Rect(220, 5, 50, 28); pygame.draw.rect(screen, (34, 139, 34), example_btn, border_radius=5); screen.blit(font_b.render("EX 1", True, (255,255,255)), (example_btn.x+10, 10))
        ex2_btn = pygame.Rect(275, 5, 50, 28); pygame.draw.rect(screen, (34, 139, 34), ex2_btn, border_radius=5); screen.blit(font_b.render("EX 2", True, (255,255,255)), (ex2_btn.x+10, 10))
        
        pygame.draw.line(screen, (80, 80, 90), (335, 5), (335, 33), 2) # Separator

        # Group 3: Asset Addition
        add_src = pygame.Rect(345, 5, 60, 28); pygame.draw.rect(screen, (59, 130, 246), add_src, border_radius=5); screen.blit(font_b.render("+ SRC", True, (255,255,255)), (add_src.x+10, 10))
        add_npc = pygame.Rect(410, 5, 60, 28); pygame.draw.rect(screen, (22, 163, 74), add_npc, border_radius=5); screen.blit(font_b.render("+ NPC", True, (255,255,255)), (add_npc.x+10, 10))
        add_prop = pygame.Rect(475, 5, 65, 28); pygame.draw.rect(screen, (220, 140, 38), add_prop, border_radius=5); screen.blit(font_b.render("+ PROP", True, (255,255,255)), (add_prop.x+8, 10))
        
        pygame.draw.line(screen, (80, 80, 90), (550, 5), (550, 33), 2) # Separator

        # --- TOP UI ROW 2 (Tools & Settings) ---
        edit_p_btn = pygame.Rect(10, 38, 100, 28); pygame.draw.rect(screen, (220, 38, 38) if player.edit_platforms else (60, 60, 70), edit_p_btn, border_radius=5); screen.blit(font_b.render("EDIT PLAT", True, (255,255,255)), (edit_p_btn.x+15, 43))
        
        add_p_btn = pygame.Rect(115, 38, 80, 28); 
        add_b_btn = pygame.Rect(205, 38, 80, 28);
        if player.edit_platforms:
            pygame.draw.rect(screen, (59, 130, 246), add_p_btn, border_radius=5); screen.blit(font_b.render("+ PLAT", True, (255,255,255)), (add_p_btn.x+15, 43))
            pygame.draw.rect(screen, (255, 140, 0), add_b_btn, border_radius=5); screen.blit(font_b.render("+ BOX", True, (255,255,255)), (add_b_btn.x+15, 43))
            
        settings_btn = pygame.Rect(play_w - 110, 5, 100, 28); pygame.draw.rect(screen, (50, 50, 60), settings_btn, border_radius=5); screen.blit(font_b.render("⚙ SETUP", True, (255,255,255)), (settings_btn.x+20, 10))

        # --- TABS ---
        if player:
            # Profile Tabs (Row 1, Right side)
            tab_offset = 0
            for i, p in enumerate(player.profiles):
                if getattr(p, 'is_prop_profile', False): continue
                tab = pygame.Rect(560+tab_offset*95, 5, 90, 28); col = (59,130,246) if player.cur_profile_idx==i else (60,60,70)
                if tab.right < play_w - 120: # Avoid Settings btn
                    pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(p.name[:12], True, (255,255,255)), (tab.x+5, 12))
                tab_offset += 1
            
            # Source Tabs (Row 2, Right side)
            tab_offset_s = 0
            for i, s in enumerate(player.sources): 
                if getattr(s, 'is_prop_source', False): continue
                tab = pygame.Rect(400+tab_offset_s*110, 38, 105, 28); col = (100,100,120) if player.cur_source_idx==i else (45,45,55)
                if tab.right < play_w:
                    pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(s.name[:12], True, (255,255,255)), (tab.x+5, 44))
                tab_offset_s += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if player: player.save_project(); player.save_settings()
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
            if event.type == pygame.DROPFILE:
                if not player.profiles: player.add_source(event.file); player.add_profile("PLAYER", 0)
                else: sid = player.add_source(event.file); player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player.popup:
                    # Popup Handling (Yes/No)
                    msg_w, msg_h = 300, 150; cx, cy = screen.get_width()//2, screen.get_height()//2
                    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 128)); screen.blit(overlay, (0, 0))
                    
                    pygame.draw.rect(screen, (40, 40, 45), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), border_radius=10)
                    pygame.draw.rect(screen, (60, 60, 65), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), 2, border_radius=10)
                    
                    screen.blit(font_b.render("Confirm Action", True, (255, 255, 255)), (cx-50, cy-50))
                    screen.blit(font_s.render(player.popup['msg'], True, (200, 200, 200)), (cx-len(player.popup['msg'])*3, cy-20))
                    
                    yes_btn = pygame.Rect(cx-80, cy+20, 60, 30); no_btn = pygame.Rect(cx+20, cy+20, 60, 30)
                    pygame.draw.rect(screen, (59, 130, 246), yes_btn, border_radius=5)
                    pygame.draw.rect(screen, (220, 38, 38), no_btn, border_radius=5)
                    screen.blit(font_b.render("YES", True, (255,255,255)), (yes_btn.x+15, yes_btn.y+5))
                    screen.blit(font_b.render("NO", True, (255,255,255)), (no_btn.x+20, no_btn.y+5))
                    
                    if yes_btn.collidepoint(m_pos):
                        if player.popup['cb']: player.popup['cb']()
                        player.popup = None
                    elif no_btn.collidepoint(m_pos):
                        player.popup = None
                else:
                    if event.button == 3 and m_pos[0] < play_w: is_dragging_cam = True; last_m_pos = m_pos; player.cam_follow = False
                    if event.button == 1:
                        # Top Bar Interaction
                        if m_pos[1] < 70 and m_pos[0] < play_w:
                            # Row 1 Buttons
                            if new_proj.collidepoint(m_pos): 
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: player = AsepritePlayer(p)
                            elif example_btn.collidepoint(m_pos) and player:
                                player.load_example()
                            elif ex2_btn.collidepoint(m_pos) and player:
                                player.load_example2()
                            elif load_prev.collidepoint(m_pos) and has_prev: player.load_settings(); player.load_project()
                            elif sv_proj.collidepoint(m_pos) and player: player.save_settings(); player.save_project()
                            elif add_src.collidepoint(m_pos) and player: 
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: player.add_source(p)
                            elif add_npc.collidepoint(m_pos) and player: 
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: 
                                    sid = player.add_source(p)
                                    player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
                                    player.target_ai_count += 1
                            elif add_prop.collidepoint(m_pos) and player:
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: 
                                    sid = player.add_source(p, is_prop_source=True)
                                    new_prof = AseProfile(f"PROP_{len(player.profiles)}", sid)
                                    new_prof.is_prop_profile = True
                                    player.profiles.append(new_prof)
                                    player.auto_map_profile(new_prof)
                                    player.prop_list.append(AseAI(player, new_prof, is_prop=True, hp=3))
                            elif settings_btn.collidepoint(m_pos): show_settings = not show_settings; settings_scroll = 0
                            
                            # Row 2 Buttons
                            elif edit_p_btn.collidepoint(m_pos): player.edit_platforms = not player.edit_platforms; player.selected_plat = None
                            elif player.edit_platforms and add_p_btn.collidepoint(m_pos):
                                cx, cy = play_w // 2, play_h // 2
                                cam_x, cam_y = player.cam_x, player.cam_y
                                player.platforms.append(pygame.Rect(cam_x, cam_y, 200, 20))
                            elif player.edit_platforms and add_b_btn.collidepoint(m_pos):
                                cx, cy = play_w // 2, play_h // 2
                                cam_x, cam_y = player.cam_x, player.cam_y
                                if not hasattr(player, "solid_boxes"): player.solid_boxes = []
                                player.solid_boxes.append(pygame.Rect(cam_x, cam_y, 100, 100))
                            
                            # Tabs
                            elif player:
                                tab_offset = 0
                                for i, p in enumerate(player.profiles):
                                    if getattr(p, 'is_prop_profile', False): continue
                                    if pygame.Rect(560+tab_offset*95, 5, 90, 28).collidepoint(m_pos): 
                                        log_debug(f"[UI] Clicked Profile Tab: {p.name} (idx: {i})")
                                        if player.cur_profile_idx != i:
                                            def _switch_profile_active(idx=i):
                                                log_debug(f"[UI] Switched active profile to: {idx}")
                                                setattr(player, 'cur_profile_idx', idx)
                                            player.popup = {'msg': f"Switch to {p.name}?", 'cb': _switch_profile_active}
                                        else:
                                            log_debug(f"[UI] Profile {i} is already active.")
                                    tab_offset += 1
                                    
                                tab_offset_s = 0
                                for i, s in enumerate(player.sources):
                                    if getattr(s, 'is_prop_source', False): continue
                                    if pygame.Rect(400+tab_offset_s*110, 38, 105, 28).collidepoint(m_pos): 
                                        log_debug(f"[UI] Clicked Source Tab: {s.name} (idx: {i})")
                                        if player.cur_source_idx != i:
                                            player.cur_source_idx = i # Always select the source to view tags
                                            log_debug(f"[UI] Changed active source view to: {i}")
                                            if player.profiles:
                                                p = player.profiles[player.cur_profile_idx]
                                                if p.source_idx != i:
                                                    def _switch_prof(idx=i):
                                                        p = player.profiles[player.cur_profile_idx]
                                                        p.source_idx = idx
                                                        player.auto_map_profile(p)
                                                        log_debug(f"[UI] Mapped profile {p.name} to source {idx}")
                                                    player.popup = {'msg': "Map profile to this source?", 'cb': _switch_prof}
                                                else:
                                                    log_debug("[UI] Profile is already mapped to this source.")
                                    tab_offset_s += 1

                        elif player.edit_platforms and m_pos[0] < play_w and m_pos[1] > 70:
                            cx, cy = play_w // 2, play_h // 2
                            cam_x, cam_y = player.cam_x, player.cam_y
                            hit = False
                            
                            if getattr(player, 'selected_plat', None) is not None:
                                if player.selected_plat < 1000 and player.selected_plat < len(player.platforms):
                                    p = player.platforms[player.selected_plat]
                                    px, py, pw = cx+(p.x-cam_x)*player.zoom, cy+(p.y-cam_y)*player.zoom, p.w*player.zoom
                                    if pygame.Rect(px+pw-15, py-15, 30, 30).collidepoint(m_pos):
                                        player.platforms.pop(player.selected_plat)
                                        player.selected_plat = None; hit = True
                                elif player.selected_plat >= 1000 and player.selected_plat < 2000 and (player.selected_plat - 1000) < len(getattr(player, "solid_boxes", [])):
                                    b = player.solid_boxes[player.selected_plat - 1000]
                                    px, py, pw = cx+(b.x-cam_x)*player.zoom, cy+(b.y-cam_y)*player.zoom, b.w*player.zoom
                                    if pygame.Rect(px+pw-15, py-15, 30, 30).collidepoint(m_pos):
                                        player.solid_boxes.pop(player.selected_plat - 1000)
                                        player.selected_plat = None; hit = True
                                elif player.selected_plat >= 2000 and (player.selected_plat - 2000) < len(getattr(player, "prop_list", [])):
                                    prop = player.prop_list[player.selected_plat - 2000]
                                    px, py, pw = cx+(prop.x-cam_x)*player.zoom, cy+(prop.y-cam_y)*player.zoom, 40*player.zoom
                                    if pygame.Rect(px+pw-15, py-60*player.zoom-15, 30, 30).collidepoint(m_pos):
                                        player.prop_list.pop(player.selected_plat - 2000)
                                        player.selected_plat = None; hit = True

                            if not hit:
                                # Check Props first
                                for i, prop in enumerate(getattr(player, "prop_list", [])):
                                    rect = pygame.Rect(cx+(prop.x-cam_x)*player.zoom - 20*player.zoom, cy+(prop.y-cam_y)*player.zoom - 60*player.zoom, 40*player.zoom, 60*player.zoom)
                                    if rect.collidepoint(m_pos):
                                        player.selected_plat = i + 2000; player.resize_mode = False
                                        player.drag_offset = (prop.x - (cam_x + (m_pos[0]-cx)/player.zoom), prop.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                        hit = True; break
                                # Check Platforms
                                if not hit:
                                    for i, p in enumerate(player.platforms):
                                        rect = pygame.Rect(cx+(p.x-cam_x)*player.zoom, cy+(p.y-cam_y)*player.zoom, p.w*player.zoom, p.h*player.zoom)
                                        handle = pygame.Rect(rect.right-10, rect.bottom-10, 10, 10)
                                        if handle.collidepoint(m_pos):
                                            player.selected_plat = i; player.resize_mode = True; hit = True; break
                                        elif rect.collidepoint(m_pos):
                                            player.selected_plat = i; player.resize_mode = False
                                            player.drag_offset = (p.x - (cam_x + (m_pos[0]-cx)/player.zoom), p.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                            hit = True; break
                                # Check Boxes if not hit
                                if not hit and hasattr(player, "solid_boxes"):
                                    for i, b in enumerate(player.solid_boxes):
                                        rect = pygame.Rect(cx+(b.x-cam_x)*player.zoom, cy+(b.y-cam_y)*player.zoom, b.w*player.zoom, b.h*player.zoom)
                                        handle = pygame.Rect(rect.right-10, rect.bottom-10, 10, 10)
                                        if handle.collidepoint(m_pos):
                                            player.selected_plat = i + 1000; player.resize_mode = True; hit = True; break
                                        elif rect.collidepoint(m_pos):
                                            player.selected_plat = i + 1000; player.resize_mode = False
                                            player.drag_offset = (b.x - (cam_x + (m_pos[0]-cx)/player.zoom), b.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                            hit = True; break
                            if not hit: player.selected_plat = None

                        elif play_w < m_pos[0] < sw:
                            if show_settings:
                                cy = 60 + settings_scroll
                                for cat in folds.keys():
                                    hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30)
                                    if hr.collidepoint(m_pos): folds[cat] = not folds[cat]
                                    cy += 35
                                    if folds[cat]:
                                        if cat == "PROPS":
                                            for i, s in enumerate([s for s in player.sources if getattr(s, 'is_prop_source', False)]):
                                                ly = cy
                                                spawn_btn = pygame.Rect(sidebar_w-110, ly, 50, 24)
                                                export_btn = pygame.Rect(sidebar_w-55, ly, 45, 24)
                                                
                                                if not hasattr(player, "_btn_lock"):
                                                    # Spawn Button (Left Click)
                                                    if pygame.Rect(play_w+spawn_btn.x, spawn_btn.y, spawn_btn.w, spawn_btn.h).collidepoint(m_pos):
                                                        new_prof = AseProfile(f"PROP_{len(player.profiles)}", s.id)
                                                        new_prof.is_prop_profile = True
                                                        player.profiles.append(new_prof)
                                                        player.auto_map_profile(new_prof)
                                                        player.prop_list.append(AseAI(player, new_prof, is_prop=True, hp=3))
                                                        player._btn_lock = 15
                                                    # Export Button (Left Click)
                                                    elif pygame.Rect(play_w+export_btn.x, export_btn.y, export_btn.w, export_btn.h).collidepoint(m_pos):
                                                        def _do_export(source=s):
                                                            folder = filedialog.askdirectory()
                                                            if folder:
                                                                export_targets = []
                                                                parts_tag = next((t for t in source.tags.keys() if "parts" in t.lower()), None)
                                                                if parts_tag: export_targets.append((parts_tag, False)) # False means exclude 'particle' slices
                                                                ptc_tag = next((t for t in source.tags.keys() if "particles" in t.lower()), None)
                                                                if ptc_tag: export_targets.append((ptc_tag, True)) # True means ONLY include 'particle' slices
                                                                
                                                                for tag_name, only_particles in export_targets:
                                                                    p_frame = source.tags[tag_name][0]
                                                                    full_frame_img = source.get_frame(p_frame, 1.0, True)
                                                                    if full_frame_img:
                                                                        for s_name, s_keys in source.slices.items():
                                                                            is_ptc_slice = "particle" in s_name.lower()
                                                                            if only_particles and not is_ptc_slice: continue
                                                                            if not only_particles and is_ptc_slice: continue
                                                                            
                                                                            active_key = None
                                                                            for key in s_keys:
                                                                                if key['frame'] <= p_frame:
                                                                                    if active_key is None or key['frame'] > active_key['frame']:
                                                                                        active_key = key
                                                                            if active_key:
                                                                                b = active_key['bounds']
                                                                                try:
                                                                                    cropped = pygame.Surface((b['w'], b['h']), pygame.SRCALPHA)
                                                                                    f_info = source.frames[p_frame]
                                                                                    crop_x = b['x'] - source.orig_w // 2 - f_info['ox']
                                                                                    crop_y = b['y'] - source.orig_h // 2 - f_info['oy']
                                                                                    cropped.blit(full_frame_img, (-crop_x, -crop_y))
                                                                                    safe_name = "".join([c for c in s_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
                                                                                    pygame.image.save(cropped, os.path.join(folder, f"{safe_name}.png"))
                                                                                except Exception as e:
                                                                                    log_debug(f"Export slice failed: {e}")
                                                        player.popup = {'msg': "Save slices as PNG?", 'cb': _do_export}
                                                        player._btn_lock = 15
                                                
                                                cy += 35
                                            cy += 10
                                        elif cat == "PHYSICS": cy += 185
                                        elif cat == "AI & COMBAT": cy += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                                        elif cat == "JUICE & VFX": cy += 175
                                        elif cat == "LAYERS" and player.sources: cy += 28 * len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers) + 10
                                        elif cat == "CAMERA": cy += 85
                                        elif cat == "BG IMAGE": cy += 25 + max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10 + (270 if player.active_bg_layer < len(player.bg_layers) else 0)
                                        elif cat == "BG COLOR": cy += 170
                                        elif cat == "CONTROLS": cy += len(player.key_map) * 30 + 10
                            else:
                                cur_p = player.profiles[player.cur_profile_idx]
                                # 1. Slot Area Selection (80 ~ 450)
                                if 80 < m_pos[1] < 450:
                                    for i, action in enumerate(cur_p.mappings.keys()):
                                        rect = pygame.Rect(play_w+20, 85+i*38+slot_scroll, sidebar_w-40, 34)
                                        if rect.collidepoint(m_pos): 
                                            selected_slot = action
                                
                                # 2. Tag Area Selection (475 ~ Bottom)
                                elif m_pos[1] >= 475:
                                    if selected_slot and player.sources:
                                        src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                                        for idx, tag in enumerate(src.tag_list):
                                            # Match the draw coordinate (475)
                                            tr = pygame.Rect(play_w+20, 475+idx*25+tag_scroll, sidebar_w-40, 22)
                                            if tr.collidepoint(m_pos):
                                                target = [player.cur_source_idx, tag]
                                                if target in cur_p.mappings[selected_slot]: 
                                                    cur_p.mappings[selected_slot].remove(target)
                                                else: 
                                                    cur_p.mappings[selected_slot].append(target)
                
                    # Right Click Handling (Remove Tabs / Clear Mappings)
                    elif event.button == 3 and player:
                        if m_pos[1] < 70 and m_pos[0] < play_w:
                            # Remove Profile (NPC)
                            for i, p in enumerate(player.profiles):
                                if pygame.Rect(400+i*95, 5, 90, 28).collidepoint(m_pos):
                                    if i == 0: continue # Don't remove PLAYER
                                    player.profiles.pop(i)
                                    player.ai_list = [ai for ai in player.ai_list if ai.profile != p]
                                    if player.cur_profile_idx >= len(player.profiles): player.cur_profile_idx = max(0, len(player.profiles)-1)
                                    break
                            # Remove Source
                            for i, s in enumerate(player.sources):
                                if pygame.Rect(400+i*110, 38, 105, 28).collidepoint(m_pos):
                                    used = False
                                    for prof in player.profiles:
                                        if prof.source_idx == i: used = True; break
                                    if not used:
                                        player.sources.pop(i)
                                        if player.cur_source_idx > i: player.cur_source_idx -= 1
                                        elif player.cur_source_idx >= len(player.sources): player.cur_source_idx = max(0, len(player.sources)-1)
                                        # Shift profile indices
                                        for prof in player.profiles:
                                            if prof.source_idx > i: prof.source_idx -= 1
                                            for slot, mappings in prof.mappings.items():
                                                prof.mappings[slot] = [m for m in mappings if m[0] != i]
                                                for mapping in prof.mappings[slot]:
                                                    if mapping[0] > i: mapping[0] -= 1
                                        # Shift active action indices
                                        for ent in [player] + player.ai_list:
                                            if ent.active_tag_info and ent.active_tag_info[0] == i:
                                                ent.active_tag_info = None; ent.active_action_slot = None
                                            elif ent.active_tag_info and ent.active_tag_info[0] > i: ent.active_tag_info[0] -= 1
                                            ent.action_queue = [act for act in ent.action_queue if act[0] != i]
                                            for act in ent.action_queue:
                                                if act[0] > i: act[0] -= 1
                                    else:
                                        log_debug("[WARN] Cannot remove source in use.")
                                    break
                        elif play_w < m_pos[0] < sw:
                            if show_settings and m_pos[1] > 70:
                                cy = 60 + settings_scroll
                                for cat in folds.keys():
                                    hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30)
                                    cy += 35
                                    if folds[cat]:
                                        if cat == "PROPS":
                                            for s in [src for src in player.sources if getattr(src, 'is_prop_source', False)]:
                                                if pygame.Rect(play_w+20, cy-2, sidebar_w-40, 28).collidepoint(m_pos):
                                                    # Remove all props using this profile
                                                    player.prop_list = [p for p in getattr(player, 'prop_list', []) if p.profile.source_idx != s.id]
                                                    player.remove_source_by_index(s.id)
                                                    player.save_settings()
                                                    break # Break loop after modifying list
                                                cy += 35
                                            cy += 10
                                        elif cat == "PHYSICS": cy += 185
                                        elif cat == "AI & COMBAT": cy += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                                        elif cat == "JUICE & VFX": cy += 175
                                        elif cat == "LAYERS" and player.sources: cy += 28 * len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers) + 10
                                        elif cat == "CAMERA": cy += 85
                                        elif cat == "BG IMAGE": cy += 25 + max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10 + (270 if player.active_bg_layer < len(player.bg_layers) else 0)
                                        elif cat == "BG COLOR": cy += 170
                                        elif cat == "CONTROLS": cy += len(player.key_map) * 30 + 10
                            elif not show_settings and player.profiles:
                                cur_p = player.profiles[player.cur_profile_idx]
                                for i, action in enumerate(cur_p.mappings.keys()):
                                    if pygame.Rect(play_w+20, 85+i*38+slot_scroll, sidebar_w-40, 34).collidepoint(m_pos): cur_p.mappings[action] = []
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3: is_dragging_cam = False
            if event.type == pygame.KEYDOWN and player:
                if active_input_attr:
                    if event.key == pygame.K_RETURN:
                        try:
                            val = float(input_text)
                            if active_input_attr in ['target_ai_count', 'bg_color_0', 'bg_color_1', 'bg_color_2']: val = int(val)
                            
                            if active_input_attr.startswith('bg_color_'):
                                idx = int(active_input_attr.split('_')[-1])
                                player.bg_color[idx] = max(0, min(255, int(val)))
                            elif active_input_attr.startswith('bglayer_'):
                                parts = active_input_attr.split('_', 2)
                                l_idx = int(parts[1])
                                l_attr = parts[2]
                                player.bg_layers[l_idx][l_attr] = int(val) if "alpha" in l_attr or "off" in l_attr else float(val)
                                player.bg_layers[l_idx]['needs_update'] = True
                            else:
                                setattr(player, active_input_attr, val)
                            player.save_settings()
                            if "bg_" in active_input_attr or "bglayer_" in active_input_attr: player.bg_needs_update = True
                        except ValueError:
                            pass # Ignore invalid inputs
                        active_input_attr = None
                    elif event.key == pygame.K_ESCAPE:
                        active_input_attr = None
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                elif binding_key:
                    if event.key != pygame.K_ESCAPE:
                        existing_owner = next((k for k, v in player.key_map.items() if v == event.key), None)
                        if existing_owner:
                            player.key_map[existing_owner] = player.key_map[binding_key]
                        player.key_map[binding_key] = event.key
                        player.save_settings()
                    binding_key = None
                else:
                    if "JUMP" not in player.key_map: player.key_map["JUMP"] = pygame.K_SPACE
                    k = event.key; km = player.key_map
                    if k == pygame.K_F5: 
                        [s.export_and_load() for s in player.sources]; [player.auto_map_profile(p) for p in player.profiles]; [s.clear_cache() for s in player.sources]
                    elif k in [pygame.K_DELETE, pygame.K_BACKSPACE] and getattr(player, 'edit_platforms', False) and player.selected_plat is not None:
                        if player.selected_plat < 1000 and player.selected_plat < len(player.platforms):
                            player.platforms.pop(player.selected_plat)
                        elif player.selected_plat >= 1000 and (player.selected_plat - 1000) < len(getattr(player, 'solid_boxes', [])):
                            player.solid_boxes.pop(player.selected_plat - 1000)
                        player.selected_plat = None
                    elif k == km.get("JUMP") or k == pygame.K_UP:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_DOWN] and player.grounded:
                            player.drop_through_timer = 200; player.vy = 5; player.grounded = False
                        elif player.jumps_left > 0:
                            player.vy = player.jump_power; player.grounded = False; player.jumps_left -= 1
                    elif k == km.get("SUMMON", pygame.K_g):
                        for i, ai in enumerate(player.ai_list):
                            offset = random.choice([-80, 80]) * (i + 1)
                            ai.x, ai.y = player.x + offset, player.y
                            ai.trigger_action("Swap_Enter")
                    elif k == km.get("ATTACK"): player.handle_attack(pygame.key.get_pressed())
                    elif k == km.get("DASH"): player.trigger_action("DASH")
                    elif k == km.get("SKILL1"): player.trigger_action("SKILL 1")
                    elif k == km.get("SKILL2"): player.trigger_action("SKILL 2")
                    elif k == km.get("SKILL3"): player.trigger_action("SKILL 3")
                    elif k == km.get("HURT"): player.trigger_action("HURT")
                    elif k == km.get("SWAP"): 
                        if hasattr(player, 'execute_swap'): player.execute_swap()
                    elif k == pygame.K_f: player.cam_follow = True
                    elif k == pygame.K_h: player.show_hitboxes = not player.show_hitboxes
                    elif k == pygame.K_p: player.is_paused = not player.is_paused
                    elif k == pygame.K_o: player.step_forward = True
                    elif k == pygame.K_LEFTBRACKET: player.playback_speed = max(0.1, player.playback_speed - 0.1)
                    elif k == pygame.K_RIGHTBRACKET: player.playback_speed = min(5.0, player.playback_speed + 0.1)
            if event.type == pygame.MOUSEWHEEL and player:
                log_debug(f"[WHEEL] m_pos:{m_pos}, play_w:{play_w}, event.y:{event.y}")
                if m_pos[0] < play_w:
                    player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0)); [s.clear_cache() for s in player.sources]; player.bg_needs_update = True
                else:
                    delta = event.y * 40
                    if show_settings: 
                        # Dynamic Settings Height Calculation
                        calc_h = 60
                        for cat in folds.keys():
                            calc_h += 35
                            if folds[cat]:
                                if cat == "PROPS": calc_h += len([s for s in player.sources if getattr(s, 'is_prop_source', False)]) * 35 + 10
                                elif cat == "PHYSICS": calc_h += 185
                                elif cat == "AI & COMBAT": calc_h += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                                elif cat == "JUICE & VFX": calc_h += 175
                                elif cat == "LAYERS" and player.sources: calc_h += 28 * len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers) + 10
                                elif cat == "CAMERA": calc_h += 85
                                elif cat == "BG IMAGE": calc_h += 25 + max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10 + (270 if player.active_bg_layer < len(player.bg_layers) else 0)
                                elif cat == "BG COLOR": calc_h += 170
                                elif cat == "CONTROLS": calc_h += len(player.key_map) * 30 + 10
                        settings_scroll = max(min(0, settings_scroll + delta), -max(0, calc_h - sh + 100))
                    elif m_pos[1] < 460: 
                        # Slot Scroll Limit
                        if player.profiles:
                            cur_p = player.profiles[player.cur_profile_idx]
                            total_h = len(cur_p.mappings) * 38
                            slot_scroll = max(min(0, slot_scroll + delta), -max(0, total_h - 380))
                    else: 
                        # Tag Scroll Limit
                        if player.sources:
                            src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                            total_h = len(src.tag_list) * 25
                            tag_scroll = max(min(0, tag_scroll + delta), -max(0, total_h - (sh - 495)))
            if event.type == pygame.MOUSEMOTION and player:
                if player.edit_platforms and player.selected_plat is not None and pygame.mouse.get_pressed()[0]:
                    cx, cy = play_w // 2, play_h // 2
                    cam_x, cam_y = player.cam_x, player.cam_y
                    
                    if hasattr(player, 'resize_mode') and player.resize_mode:
                        mx, my = (m_pos[0]-cx)/player.zoom + cam_x, (m_pos[1]-cy)/player.zoom + cam_y
                        if player.selected_plat < 1000:
                            p = player.platforms[player.selected_plat]
                            p.w = max(20, mx - p.x); p.h = max(20, my - p.y)
                        else:
                            b = player.solid_boxes[player.selected_plat - 1000]
                            b.w = max(20, mx - b.x); b.h = max(20, my - b.y)
                    else:
                        mx, my = (m_pos[0]-cx)/player.zoom + cam_x, (m_pos[1]-cy)/player.zoom + cam_y
                        if player.selected_plat < 1000:
                            player.platforms[player.selected_plat].x = mx + player.drag_offset[0]
                            player.platforms[player.selected_plat].y = my + player.drag_offset[1]
                        elif player.selected_plat < 2000:
                            player.solid_boxes[player.selected_plat - 1000].x = mx + player.drag_offset[0]
                            player.solid_boxes[player.selected_plat - 1000].y = my + player.drag_offset[1]
                        else:
                            player.prop_list[player.selected_plat - 2000].x = mx + player.drag_offset[0]
                            player.prop_list[player.selected_plat - 2000].y = my + player.drag_offset[1]
                
                elif is_dragging_cam: 
                    dx, dy = m_pos[0] - last_m_pos[0], m_pos[1] - last_m_pos[1]
                    player.cam_x -= dx / player.zoom; player.cam_y -= dy / player.zoom; last_m_pos = m_pos
        if player.profiles:
            cur_p = player.profiles[player.cur_profile_idx]
            if show_settings:
                set_surf = pygame.Surface((sidebar_w, sh), pygame.SRCALPHA); cy = 60 + settings_scroll
                for cat in folds.keys():
                    hr = pygame.Rect(10, cy, sidebar_w-20, 30); pygame.draw.rect(set_surf, (50,50,60), hr, border_radius=5); set_surf.blit(font_b.render(f"{'+' if not folds[cat] else '-'} {cat}", True, (255,255,255)), (hr.x+10, hr.y+7)); cy += 35
                    if folds[cat]:
                        if cat == "PROPS":
                            for i, s in enumerate([s for s in player.sources if getattr(s, 'is_prop_source', False)]):
                                ly = cy
                                pygame.draw.rect(set_surf, (60,60,70), (20, ly-2, sidebar_w-40, 28), border_radius=4)
                                set_surf.blit(font_s.render(s.name[:30], True, (255,255,255)), (30, ly+4))
                                spawn_btn = pygame.Rect(sidebar_w-110, ly, 50, 24)
                                pygame.draw.rect(set_surf, (34, 139, 34), spawn_btn, border_radius=4)
                                set_surf.blit(font_h.render("SPAWN", True, (255,255,255)), (spawn_btn.x+5, spawn_btn.y+5))
                                export_btn = pygame.Rect(sidebar_w-55, ly, 45, 24)
                                pygame.draw.rect(set_surf, (59, 130, 246), export_btn, border_radius=4)
                                set_surf.blit(font_h.render("SAVE", True, (255,255,255)), (export_btn.x+7, export_btn.y+5))
                                cy += 35
                            cy += 10
                        elif cat == "PHYSICS":
                            for i, (l, mn, mx, at, inv) in enumerate([("Dash Vel",10,50,"dash_speed",0), ("Jump Pow",10,25,"jump_power",1), ("PBomb Spd",10,60,"powerbomb_speed",0), ("Plat Alpha",0,255,"platform_alpha",0)]):
                                y = cy+i*45; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); 
                                # Slider Bar
                                sl = pygame.Rect(110, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn) if not inv else (-v-mn)/(mx-mn); 
                                pygame.draw.circle(set_surf, (59,130,246), (int(110+n*(sidebar_w-160)), y+9), 8)
                                # Value Text
                                txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else (f"{int(v)}" if at in ["platform_alpha", "cam_v_offset"] else f"{v:.1f}"))
                                bg_c = (30,30,35) if active_input_attr == at else (45,45,50)
                                pygame.draw.rect(set_surf, bg_c, (sidebar_w-45, y-2, 40, 18), border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (sidebar_w-42, y))
                                
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                    if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                        if active_input_attr != at: active_input_attr = at; input_text = str(int(v)) if at in ["platform_alpha", "cam_v_offset"] else str(round(v, 1))
                                    elif pygame.Rect(play_w+110, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                        active_input_attr = None
                                        setattr(player, at, mn+(m_pos[0]-(play_w+110))/(sidebar_w-160)*(mx-mn) if not inv else -(mn+(m_pos[0]-(play_w+110))/(sidebar_w-160)*(mx-mn))); player.save_settings()
                            cy += 185
                        elif cat == "AI & COMBAT":
                            for i, (l, mn, mx, at) in enumerate([("AI Count",0,10,"target_ai_count"), ("Atk Forward",0,30,"atk_forward_v")]):
                                y = cy+i*45; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); sl = pygame.Rect(110, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(set_surf, (59,130,246), (int(110+n*(sidebar_w-160)), y+9), 8)
                                txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else (f"{int(v)}" if at == "target_ai_count" else f"{v:.1f}"))
                                pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == at else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (sidebar_w-42, y))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                    if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                        if active_input_attr != at: active_input_attr = at; input_text = str(int(v)) if at == "target_ai_count" else str(round(v, 1))
                                    elif pygame.Rect(play_w+110, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                        active_input_attr = None
                                        setattr(player, at, mn+(m_pos[0]-(play_w+110))/(sidebar_w-160)*(mx-mn) if at != "target_ai_count" else int(mn+(m_pos[0]-(play_w+110))/(sidebar_w-160)*(mx-mn))); player.save_settings()
                            
                            y = cy + 90
                            set_surf.blit(font_s.render("Swap Target:", True, (150,150,150)), (20, y))
                            j_offset = 0
                            for j in range(1, len(player.profiles)):
                                if getattr(player.profiles[j], 'is_prop_profile', False): continue
                                btn = pygame.Rect(110 + (j_offset%4)*55, y - 5 + (j_offset//4)*30, 50, 24)
                                is_sel = getattr(player, 'swap_target_idx', 0) == j
                                pygame.draw.rect(set_surf, (59,130,246) if is_sel else (60,60,70), btn, border_radius=4)
                                set_surf.blit(font_h.render(f"NPC {j}", True, (255,255,255)), (btn.x+8, btn.y+5))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, btn.y, btn.w, btn.h).collidepoint(m_pos):
                                    player.swap_target_idx = j; player.save_settings()
                                j_offset += 1
                            cy += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                        elif cat == "JUICE & VFX":
                            for i, (l, at) in enumerate([("Enable Shake", "shake_enabled"), ("Enable Ghost", "vfx_enabled")]):
                                y = cy+i*40; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = getattr(player, at); pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10); pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(m_pos):
                                    if not hasattr(player, "_btn_lock"): setattr(player, at, not val); player._btn_lock = 10; player.save_settings()
                            y = cy + 85; set_surf.blit(font_s.render("Shake Power", True, (150,150,150)), (20, y)); 
                            sl = pygame.Rect(110, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl); n = player.base_shake / 3.0; 
                            pygame.draw.circle(set_surf, (220, 38, 38), (int(110+n*(sidebar_w-160)), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == "base_shake" and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == "base_shake" else f"{player.base_shake:.1f}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == "base_shake" else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == "base_shake" else (200,200,200)), (sidebar_w-42, y))
                            
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                    if active_input_attr != "base_shake": active_input_attr = "base_shake"; input_text = str(round(player.base_shake, 1))
                                elif pygame.Rect(play_w+110, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                    active_input_attr = None
                                    player.base_shake = ((m_pos[0]-(play_w+110))/(sidebar_w-160)) * 3.0; player.save_settings()

                            y = cy + 130; set_surf.blit(font_s.render("Debris Force", True, (150,150,150)), (20, y)); 
                            sl = pygame.Rect(110, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl); n = player.debris_force / 5.0; 
                            pygame.draw.circle(set_surf, (220, 140, 38), (int(110+n*(sidebar_w-160)), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == "debris_force" and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == "debris_force" else f"{player.debris_force:.1f}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == "debris_force" else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == "debris_force" else (200,200,200)), (sidebar_w-42, y))
                            
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                    if active_input_attr != "debris_force": active_input_attr = "debris_force"; input_text = str(round(player.debris_force, 1))
                                elif pygame.Rect(play_w+110, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                    active_input_attr = None
                                    player.debris_force = ((m_pos[0]-(play_w+110))/(sidebar_w-160)) * 5.0; player.save_settings()

                            cy += 175
                        elif cat == "LAYERS" and player.sources:
                            src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                            for l_name in src.layers:
                                ly = cy; is_vis = l_name in src.visible_layers; l_rect = pygame.Rect(15, ly-2, sidebar_w-30, 24); hvr = pygame.Rect(play_w+15, ly-2, sidebar_w-30, 24).collidepoint(m_pos)
                                if hvr: pygame.draw.rect(set_surf, (60,60,70), l_rect, border_radius=4)
                                pygame.draw.rect(set_surf, (22, 163, 74) if is_vis else (60, 60, 70), (20, ly+2, 16, 16), border_radius=3); set_surf.blit(font_s.render(l_name[:30], True, (255,255,255) if is_vis else (150,150,150)), (45, ly+2))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and hvr and not hasattr(player, "_btn_lock"):
                                    if is_vis: src.visible_layers.remove(l_name)
                                    else: src.visible_layers.add(l_name)
                                    src.export_and_load(); player.auto_map_profile(cur_p); player._btn_lock = 15; src.clear_cache()
                                cy += 28
                            cy += 10
                        elif cat == "CAMERA":
                            # Cam Offset Slider
                            y = cy; mn, mx, at = -500, 300, "cam_v_offset"
                            set_surf.blit(font_s.render("Cam Offset", True, (150,150,150)), (20, y))
                            sl = pygame.Rect(110, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl)
                            v = getattr(player, at); n = (v-mn)/(mx-mn)
                            pygame.draw.circle(set_surf, (59,130,246), (int(110+n*(sidebar_w-160)), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else f"{int(v)}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == at else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (sidebar_w-42, y))
                            
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                    if active_input_attr != at: active_input_attr = at; input_text = str(int(v))
                                elif pygame.Rect(play_w+110, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                    active_input_attr = None
                                    setattr(player, at, mn+(m_pos[0]-(play_w+110))/(sidebar_w-160)*(mx-mn)); player.save_settings()
                            
                            # Show Guide Button
                            y = cy + 45; set_surf.blit(font_s.render("Show 640x360 Guide", True, (150,150,150)), (20, y)); btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = player.show_viewport; pygame.draw.rect(set_surf, (59, 130, 246) if val else (60, 60, 70), btn, border_radius=10); pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(m_pos):
                                if not hasattr(player, "_btn_lock"): player.show_viewport = not val; player._btn_lock = 15; player.save_settings()
                            cy += 85
                        elif cat == "BG IMAGE":
                            # Layers header
                            set_surf.blit(font_s.render("Layers:", True, (150,150,150)), (20, cy))
                            add_lyr_btn = pygame.Rect(sidebar_w-45, cy-5, 25, 20); pygame.draw.rect(set_surf, (22, 163, 74), add_lyr_btn, border_radius=4); set_surf.blit(font_b.render("+", True, (255,255,255)), (add_lyr_btn.x+8, add_lyr_btn.y+3))
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+add_lyr_btn.x, add_lyr_btn.y, add_lyr_btn.w, add_lyr_btn.h).collidepoint(m_pos) and not hasattr(player, "_btn_lock"):
                                player.bg_layers.append({"path": "", "off_x": 0, "off_y": 0, "zoom": 2.0, "alpha": 255, "parallax": 1.0, "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0})
                                player.active_bg_layer = len(player.bg_layers) - 1
                                player._btn_lock = 15; player.save_settings()
                            cy += 25
                            
                            # Layer Tabs
                            for l_i in range(len(player.bg_layers)):
                                tab_rect = pygame.Rect(20 + (l_i%5)*45, cy + (l_i//5)*30, 40, 24)
                                is_sel = player.active_bg_layer == l_i
                                pygame.draw.rect(set_surf, (59, 130, 246) if is_sel else (60, 60, 70), tab_rect, border_radius=4)
                                set_surf.blit(font_h.render(f"L{l_i}", True, (255,255,255)), (tab_rect.x+10, tab_rect.y+5))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+tab_rect.x, tab_rect.y, tab_rect.w, tab_rect.h).collidepoint(m_pos): player.active_bg_layer = l_i
                            
                            cy += max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10
                            
                            if player.active_bg_layer < len(player.bg_layers):
                                l_idx = player.active_bg_layer
                                l_data = player.bg_layers[l_idx]
                                
                                # Move / Delete row
                                bg_btn = pygame.Rect(20, cy, 80, 25); pygame.draw.rect(set_surf, (100,100,110), bg_btn, border_radius=5); set_surf.blit(font_h.render("LOAD IMG", True, (255,255,255)), (bg_btn.x+10, bg_btn.y+5))
                                up_btn = pygame.Rect(110, cy, 30, 25); pygame.draw.rect(set_surf, (80,80,90), up_btn, border_radius=5); set_surf.blit(font_h.render("UP", True, (255,255,255)), (up_btn.x+8, up_btn.y+5))
                                dn_btn = pygame.Rect(150, cy, 30, 25); pygame.draw.rect(set_surf, (80,80,90), dn_btn, border_radius=5); set_surf.blit(font_h.render("DN", True, (255,255,255)), (dn_btn.x+8, dn_btn.y+5))
                                del_btn = pygame.Rect(190, cy, 40, 25); pygame.draw.rect(set_surf, (220,38,38), del_btn, border_radius=5); set_surf.blit(font_h.render("DEL", True, (255,255,255)), (del_btn.x+10, del_btn.y+5))
                                
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and not hasattr(player, "_btn_lock"):
                                    if pygame.Rect(play_w+bg_btn.x, bg_btn.y, bg_btn.w, bg_btn.h).collidepoint(m_pos):
                                        p = select_file([("Image", "*.png *.jpg *.bmp")])
                                        if p: 
                                            l_data['path'] = p; l_data['img'] = pygame.image.load(p).convert_alpha()
                                            l_data['needs_update'] = True; l_data['last_mtime'] = os.path.getmtime(p)
                                            player.save_settings()
                                        player._btn_lock = 15
                                    elif pygame.Rect(play_w+up_btn.x, up_btn.y, up_btn.w, up_btn.h).collidepoint(m_pos) and l_idx > 0:
                                        player.bg_layers[l_idx], player.bg_layers[l_idx-1] = player.bg_layers[l_idx-1], player.bg_layers[l_idx]
                                        player.active_bg_layer -= 1; player._btn_lock = 15; player.save_settings()
                                    elif pygame.Rect(play_w+dn_btn.x, dn_btn.y, dn_btn.w, dn_btn.h).collidepoint(m_pos) and l_idx < len(player.bg_layers)-1:
                                        player.bg_layers[l_idx], player.bg_layers[l_idx+1] = player.bg_layers[l_idx+1], player.bg_layers[l_idx]
                                        player.active_bg_layer += 1; player._btn_lock = 15; player.save_settings()
                                    elif pygame.Rect(play_w+del_btn.x, del_btn.y, del_btn.w, del_btn.h).collidepoint(m_pos):
                                        player.bg_layers.pop(l_idx)
                                        player.active_bg_layer = max(0, l_idx - 1)
                                        player._btn_lock = 15; player.save_settings()
                                
                                cy += 40
                                
                                if l_idx < len(player.bg_layers): # Check if valid
                                    for i, (l, mn, mx, at) in enumerate([("X Offset",-2000,2000,"off_x"), ("Y Offset",-2000,2000,"off_y"), ("Scale",0.1,10,"zoom"), ("Alpha",0,255,"alpha"), ("Parallax",-2.0,5.0,"parallax")]):
                                        y = cy+i*40; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y))
                                        sl = pygame.Rect(80, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl)
                                        v = l_data.get(at, 0); n = max(0, min(1, (v-mn)/(mx-mn)))
                                        pygame.draw.circle(set_surf, (220,38,38), (int(80+n*(sidebar_w-160)), y+9), 8)
                                        
                                        is_int_at = "off" in at or "alpha" in at
                                        attr_name = f"bglayer_{l_idx}_{at}"
                                        txt_val = input_text + "|" if active_input_attr == attr_name and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == attr_name else (f"{int(v)}" if is_int_at else f"{v:.2f}"))
                                        pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == attr_name else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                                        set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == attr_name else (200,200,200)), (sidebar_w-42, y))
                                        
                                        if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                            if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                                if active_input_attr != attr_name: active_input_attr = attr_name; input_text = str(int(v)) if is_int_at else str(round(v, 2))
                                            elif pygame.Rect(play_w+80, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                                active_input_attr = None
                                                l_data[at] = mn+(m_pos[0]-(play_w+80))/(sidebar_w-160)*(mx-mn)
                                                if is_int_at: l_data[at] = int(l_data[at])
                                                l_data['needs_update'] = True
                                                player.save_settings()
                                    
                                    # Loop X Toggle
                                    ly = cy + 200
                                    set_surf.blit(font_s.render("Loop X", True, (150,150,150)), (20, ly))
                                    btn = pygame.Rect(sidebar_w-60, ly-5, 40, 20)
                                    val = l_data.get('loop_x', False)
                                    pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10)
                                    pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                                    
                                    if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, ly-5, btn.w, btn.h).collidepoint(m_pos):
                                        if not hasattr(player, "_btn_lock"):
                                            l_data['loop_x'] = not val
                                            l_data['needs_update'] = True
                                            player._btn_lock = 15; player.save_settings()
                                            
                                    cy += 230
                        elif cat == "BG COLOR":
                            for i, c in enumerate(['R','G','B']):
                                y = cy+i*35; set_surf.blit(font_s.render(c, True, (150,150,150)), (20, y)); sl = pygame.Rect(40, y+5, sidebar_w-120, 8); pygame.draw.rect(set_surf, (60,60,70), sl); pygame.draw.circle(set_surf, (220, 38, 38) if i==0 else (22, 163, 74) if i==1 else (59, 130, 246), (int(40+player.bg_color[i]/255*(sidebar_w-120)), y+9), 8)
                                
                                attr_name = f"bg_color_{i}"
                                txt_val = input_text + "|" if active_input_attr == attr_name and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == attr_name else str(player.bg_color[i]))
                                pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == attr_name else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == attr_name else (200,200,200)), (sidebar_w-42, y))
                                
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                    if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                        if active_input_attr != attr_name: active_input_attr = attr_name; input_text = str(player.bg_color[i])
                                    elif pygame.Rect(play_w+40, y, sidebar_w-120, 20).collidepoint(m_pos):
                                        active_input_attr = None
                                        player.bg_color[i] = int((m_pos[0]-(play_w+40))/(sidebar_w-120)*255); player.save_settings()
                            cy += 110
                            for i, p in enumerate([(15,15,18), (120,120,120), (240,240,240), (34,139,34)]):
                                pr = pygame.Rect(20+i*45, cy, 35, 30); pygame.draw.rect(set_surf, p, pr, border_radius=3)
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20+i*45, cy, 35, 30).collidepoint(m_pos): player.bg_color = list(p); player.save_settings()
                            cy += 60
                        elif cat == "CONTROLS":
                            for i, (act, k) in enumerate(player.key_map.items()):
                                y = cy+i*30; set_surf.blit(font_s.render(act, True, (150,150,150)), (20, y))
                                k_name = "PRESS KEY" if binding_key == act else pygame.key.name(k).upper()
                                col = (220, 38, 38) if binding_key == act else (60, 60, 70)
                                btn = pygame.Rect(120, y-2, 100, 20)
                                pygame.draw.rect(set_surf, col, btn, border_radius=4)
                                set_surf.blit(font_s.render(k_name, True, (255,255,255)), (125, y+2))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+120, y-2, 100, 20).collidepoint(m_pos):
                                    if not hasattr(player, '_btn_lock'): binding_key = act; player._btn_lock = 10
                            cy += len(player.key_map) * 30 + 10
                screen.blit(set_surf, (play_w, 0)); pygame.draw.line(screen, (59, 130, 246), (play_w, 0), (play_w, sh), 2)
            else:
                slot_clip = pygame.Surface((sidebar_w-20, 380), pygame.SRCALPHA)
                for i, a in enumerate(cur_p.mappings.keys()):
                    r = pygame.Rect(10, i*38+slot_scroll, sidebar_w-40, 34); is_sel = selected_slot == a; pygame.draw.rect(slot_clip, (59,130,246) if is_sel else (45,45,50), r, border_radius=5); slot_clip.blit(font_b.render(a, True, (255,255,255)), (r.x+10, r.y+3))
                    ms = ", ".join([f"{m[1]}" for m in cur_p.mappings[a]]); slot_clip.blit(font_s.render(f"-> {ms[:45]}", True, (200,200,200) if not is_sel else (255,255,255)), (r.x+10, r.y+18))
                screen.blit(slot_clip, (play_w+10, 85))
                if player.sources:
                    pygame.draw.rect(screen, (20,20,25), (play_w+15, 475, sidebar_w-30, sh-490), border_radius=5); src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]; screen.blit(font_b.render(f"TAGS FROM: {src.name[:20]}", True, (100,100,100)), (play_w+20, 455)); cs = pygame.Surface((sidebar_w-40, sh-495), pygame.SRCALPHA)
                    for idx, t in enumerate(src.tag_list):
                        tr = pygame.Rect(0, idx*25+tag_scroll, sidebar_w-40, 22); is_m = selected_slot and [player.cur_source_idx, t] in cur_p.mappings[selected_slot]; h = tr.move(play_w+20, 475).collidepoint(m_pos); pygame.draw.rect(cs, (59,130,246) if is_m else ((70,70,80) if h else (40,40,45)), tr, border_radius=3); cs.blit(font_s.render(t, True, (255,255,255)), (tr.x+10, tr.y+4))
                    screen.blit(cs, (play_w+20, 475))
            for i in range(2): pygame.draw.rect(screen, (59,130,246) if i < player.dash_charges else (60,60,70), (play_w - 80 + i*35, sh - 100, 30, 10), border_radius=3)
            # Combo Stack Display
            if player.combo_step > 0:
                for i in range(4):
                    col = (220, 38, 38) if i < player.combo_step else (60, 60, 70)
                    pygame.draw.rect(screen, col, (play_w - 150 + i*35, sh - 130, 30, 10), border_radius=3)
                screen.blit(font_h.render(f"COMBO STEP: {player.combo_step}", True, (255,255,255)), (play_w - 150, sh - 145))
            pygame.draw.rect(screen, (30, 30, 35), (0, sh-40, play_w, 40)); ctrl = [("Z", "Atk"), ("X", "Dash"), ("C/B/N", "Skill"), ("T", "Swap"), ("P", "Pause"), ("O", "Step"), ("[ ]", f"Spd:{player.playback_speed:.1f}"), ("F5", "Refresh"), ("H", "Hitbox"), ("R-Drag", "Cam"), ("F", "Reset")]
            tx = 20
            for k, d in ctrl: pygame.draw.rect(screen, (45,45,50), (tx-5, sh-32, font_h.size(k)[0]+font_h.size(d)[0]+25, 24), border_radius=4); screen.blit(font_h.render(k, True, (59,130,246)), (tx, sh-27)); screen.blit(font_h.render(f": {d}", True, (255,255,255)), (tx+font_h.size(k)[0], sh-27)); tx += font_h.size(k)[0]+font_h.size(d)[0]+35
        # Render FPS and Zoom
        fps = int(clock.get_fps())
        fps_color = (22, 163, 74) if fps >= 55 else ((220, 160, 38) if fps >= 30 else (220, 38, 38))
        screen.blit(font_b.render(f"FPS: {fps} | Zoom: {player.zoom:.1f}x", True, fps_color), (10, 75))

        if fps > 0 and fps < 55:
            now = pygame.time.get_ticks()
            if not hasattr(player, 'last_fps_log') or now - player.last_fps_log > 2000:
                log_debug(f"[PERF] Low FPS: {fps} | Res: {play_w}x{play_h} | Zoom: {player.zoom:.1f}x | BGs: {len(player.bg_layers)} | NPCs: {len(player.ai_list)} | AIs: {len(player.afterimages)}")
                player.last_fps_log = now

        pygame.display.flip()

if __name__ == "__main__": main()
