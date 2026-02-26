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
        self.mappings = { "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ComboAttack_1": [], "ComboAttack_2": [], "ComboAttack_3": [], "ComboAttack_4": [], "JUMPATTACK": [], "POWERBOMB": [], "DASH": [], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [], "Swap_Enter": [], "Swap_Exit": [] }

class AseAI:
    def __init__(self, master, profile, is_temp=False):
        self.master = master; self.profile = profile; self.spawn_x, self.spawn_y = random.randint(600, 900), 500
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = True; self.facing_right = random.choice([True, False]); self.frame_idx = 0; self.anim_timer = 0; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.ai_timer = random.randint(30, 90); self.decision = "IDLE"; self.swap_timer = 0; self.visible = True; self.active_action_slot = None
        self.is_temp = is_temp; self.attack_buffer = 0; self.combo_step = 0
    def update(self, ground_y, dt):
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        if not self.is_temp:
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
                if self.decision == "WALK_R": self.vx = 4; self.facing_right = True
                elif self.decision == "WALK_L": self.vx = -4; self.facing_right = False
                elif self.decision == "CHASE": self.vx = 5.5 if dist_p > 0 else -5.5; self.facing_right = dist_p > 0
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
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
                m = self.profile.mappings.get(state, []) if self.profile else []; target_info = m[0] if m else None
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
        self.sources = []; self.profiles = []; self.cur_profile_idx = 0; self.cur_source_idx = 0; self.spawn_x, self.spawn_y = 400, 500; self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = False; self.jumps_left = 2; self.facing_right = True; self.zoom = 3.0; self.dash_speed = 12.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 15.0; self.powerbomb_speed = 35.0; self.cam_v_offset = -120; self.pbomb_pause_timer = 0; self.loop_counter = 0; self.cam_x, self.cam_y = 400, 300; self.cam_follow = True; self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20), pygame.Rect(-200, 250, 300, 20), pygame.Rect(900, 300, 400, 20)]; self.bg_img = None; self.bg_path = None; self.bg_off_x = self.bg_off_y = 0; self.bg_zoom = 2.0; self.bg_alpha = 255; self.bg_parallax = 0.1; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]; self.cached_bg = None; self.bg_needs_update = True; self.bg_last_mtime = 0; self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0; self.active_action_slot = None; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0; self.attack_move_timer = 0; self.ai_list = []; self.temp_ai_list = []; self.target_ai_count = 0; self.swap_timer = 0; self.visible = True; self.playback_speed = 1.0; self.is_paused = False; self.step_forward = False; self.show_hitboxes = True; self.target_w, self.target_h = 640, 360; self.show_viewport = True; self.shake_timer = 0; self.shake_intensity = 0; self.shake_enabled = True; self.base_shake = 1.0; self.afterimages = []; self.vfx_enabled = True; self.ghost_timer = 0; self.platform_alpha = 150; self.edit_platforms = False; self.selected_plat = None; self.drag_offset = (0,0); self.drop_through_timer = 0
        self.key_map = {"ATTACK": pygame.K_z, "DASH": pygame.K_x, "JUMP": pygame.K_SPACE, "SKILL1": pygame.K_c, "SKILL2": pygame.K_b, "SKILL3": pygame.K_n, "SUMMON": pygame.K_g, "SWAP": pygame.K_t, "HURT": pygame.K_v}
        self.popup = None
        if initial_path: self.add_source(initial_path); self.add_profile("PLAYER", 0)
    def update_bg_cache(self):
        if self.bg_img:
            bw, bh = int(self.bg_img.get_width()*self.bg_zoom*self.zoom*0.5), int(self.bg_img.get_height()*self.bg_zoom*self.zoom*0.5); self.cached_bg = pygame.transform.scale(self.bg_img, (bw, bh))
            if self.bg_alpha < 255: self.cached_bg.set_alpha(self.bg_alpha)
        self.bg_needs_update = False
    def save_settings(self):
        data = {"physics": {"dash_speed": self.dash_speed, "jump_power": self.jump_power, "powerbomb_speed": self.powerbomb_speed, "cam_v_offset": self.cam_v_offset}, "combat": {"atk_forward_v": self.atk_forward_v}, "vfx": {"shake_enabled": self.shake_enabled, "vfx_enabled": self.vfx_enabled, "base_shake": self.base_shake}, "viewport": {"show_viewport": self.show_viewport, "target_w": self.target_w, "target_h": self.target_h}, "bg": {"bg_color": self.bg_color, "bg_alpha": self.bg_alpha, "bg_zoom": self.bg_zoom, "bg_parallax": self.bg_parallax, "bg_off_x": self.bg_off_x, "bg_off_y": self.bg_off_y, "bg_path": self.bg_path}, "ai": {"target_ai_count": self.target_ai_count}, "platforms": {"alpha": self.platform_alpha}}
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
                    for cat in data.values():
                        if isinstance(cat, dict):
                            for k, v in cat.items():
                                if k == "alpha" and "platforms" in data: self.platform_alpha = v
                                elif hasattr(self, k): setattr(self, k, v)
                    if "controls" in data:
                        self.key_map = data["controls"]
                        if "JUMP" not in self.key_map: self.key_map["JUMP"] = pygame.K_SPACE
                if self.bg_path and os.path.exists(self.bg_path): 
                    self.bg_img = pygame.image.load(self.bg_path).convert_alpha(); self.bg_needs_update = True; self.bg_last_mtime = os.path.getmtime(self.bg_path)
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
        set_data = {"physics": {"dash_speed": 12.0, "jump_power": -18.0, "powerbomb_speed": 35.0, "cam_v_offset": -120}, "combat": {"atk_forward_v": 15.0}, "vfx": {"shake_enabled": True, "vfx_enabled": True, "base_shake": 1.0}, "viewport": {"show_viewport": True, "target_w": 640, "target_h": 360}, "bg": {"bg_color": [17, 15, 18], "bg_alpha": 255, "bg_zoom": 2.0, "bg_parallax": 0.9862068965517241, "bg_off_x": 0, "bg_off_y": -130.0, "bg_path": "C:/Users/SOUTHPAW GAMES/Desktop/새 폴더/로비 컨셉94 (1).png"}, "ai": {"target_ai_count": 0}, "platforms": {"alpha": 5.275862068965517}}
        
        # Apply settings
        for cat in set_data.values():
            if isinstance(cat, dict):
                for k, v in cat.items():
                    if k == "alpha" and "platforms" in set_data: self.platform_alpha = v
                    elif hasattr(self, k): setattr(self, k, v)
        self.bg_path = set_data["bg"].get("bg_path", "")
        if self.bg_path:
            if not os.path.exists(self.bg_path): self.bg_path = os.path.basename(self.bg_path)
            if os.path.exists(self.bg_path):
                self.bg_img = pygame.image.load(self.bg_path).convert_alpha()
                self.bg_needs_update = True
                self.bg_last_mtime = os.path.getmtime(self.bg_path)
                
        # Apply project
        self.sources = []; self.profiles = []; self.ai_list = []; self.temp_ai_list = []
        for src_p in proj_data.get("sources", []):
            if not os.path.exists(src_p): src_p = os.path.basename(src_p)
            if os.path.exists(src_p): self.add_source(src_p)
        for prof_data in proj_data.get("profiles", []):
            new_prof = AseProfile(prof_data["name"], prof_data["source_idx"]); new_prof.mappings = prof_data["mappings"]; self.profiles.append(new_prof)
            if prof_data["name"] != "PLAYER": self.ai_list.append(AseAI(self, new_prof))
        
        self.platforms = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data["platforms"]]
        self.solid_boxes = [pygame.Rect(d[0], d[1], d[2], d[3]) for d in proj_data["solid_boxes"]]
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx, self.vy = 0, 0
        self.cam_x, self.cam_y = self.x, self.y
        self.save_settings(); self.save_project()
    def add_source(self, path):
        try:
            new_source = AseSource(path, len(self.sources)); self.sources.append(new_source); self.cur_source_idx = new_source.id; return new_source.id
        except: return 0
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

    def update(self, keys, ground_y, dt):
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
            if self.bg_path and os.path.exists(self.bg_path):
                try:
                    mt = os.path.getmtime(self.bg_path)
                    if mt > self.bg_last_mtime:
                        self.bg_img = pygame.image.load(self.bg_path).convert_alpha()
                        self.bg_needs_update = True
                        self.bg_last_mtime = mt
                        log_debug("[BG] Auto-reloaded background image.")
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
                if keys[pygame.K_RIGHT]: self.vx = 6.5; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -6.5; self.facing_right = False
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
        for ai in getattr(self, 'temp_ai_list', [])[:]:
            ai.update(ground_y, dt)
            if not ai.visible: self.temp_ai_list.remove(ai)

    def draw_sprite(self, screen, x, y, source_idx, f_idx, facing_right, cam_x, cam_y, cx, cy):
        if source_idx < 0 or source_idx >= len(self.sources): return
        src = self.sources[source_idx]; scaled = src.get_frame(f_idx, self.zoom, facing_right)
        if not scaled: return
        f = src.frames[min(max(0, f_idx), len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
        if not facing_right: ox = -ox - scaled.get_width()
        screen.blit(scaled, (int(cx + (x - cam_x)*self.zoom + ox), int(cy + (y - cam_y)*self.zoom + oy)))
        if self.show_hitboxes:
            for name, keys in src.slices.items():
                active_key = None
                for key in keys:
                    if key['frame'] <= f_idx:
                        if active_key is None or key['frame'] > active_key['frame']: active_key = key
                if active_key:
                    b = active_key['bounds']; sx = cx + (x - cam_x) * self.zoom; sy = cy + (y - cam_y) * self.zoom; final_x = sx + (b['x'] - src.orig_w // 2) * self.zoom; final_y = sy + (b['y'] - src.orig_h // 2) * self.zoom; final_w = b['w'] * self.zoom; final_h = b['h'] * self.zoom
                    if not facing_right: final_x = sx - (b['x'] - src.orig_w // 2 + b['w']) * self.zoom
                    col = (220, 38, 38) if "hit" in name.lower() else (22, 163, 74); pygame.draw.rect(screen, col, (final_x, final_y, final_w, final_h), 2)
                    if self.zoom > 1.5: txt = pygame.font.SysFont("Arial", 10).render(name, True, col); screen.blit(txt, (final_x, final_y - 12))
    def draw(self, screen, play_w, play_h):
        if not hasattr(self, "solid_boxes"): self.solid_boxes = []
        cx, cy = play_w // 2, play_h // 2; off_x = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; off_y = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; cam_x, cam_y = self.cam_x + off_x, self.cam_y + off_y; gx, gy = cx - (cam_x % 100)*self.zoom, cy - (cam_y % 100)*self.zoom
        for i in range(-10, 20): pygame.draw.line(screen, self.grid_color, (int(gx+i*100*self.zoom), 0), (int(gx+i*100*self.zoom), play_h), 1); pygame.draw.line(screen, self.grid_color, (0, int(gy+i*100*self.zoom)), (play_w, int(gy+i*100*self.zoom)), 1)
        if self.bg_img:
            if self.bg_needs_update or self.cached_bg is None: self.update_bg_cache()
            bx = cx + (self.spawn_x - cam_x) * self.bg_parallax * self.zoom + self.bg_off_x * self.zoom - self.cached_bg.get_width() // 2; by = cy + (self.spawn_y - cam_y) * self.bg_parallax * self.zoom + self.bg_off_y * self.zoom - self.cached_bg.get_height() // 2; screen.blit(self.cached_bg, (int(bx), int(by)))
        
        # Draw Platforms
        plat_surf = pygame.Surface((play_w, play_h), pygame.SRCALPHA)
        for i, p in enumerate(self.platforms): 
            px, py, pw, ph = int(cx+(p.x-cam_x)*self.zoom), int(cy+(p.y-cam_y)*self.zoom), int(p.w*self.zoom), int(p.h*self.zoom)
            col = (255, 255, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i else (80, 80, 100, self.platform_alpha)
            pygame.draw.rect(plat_surf, col, (px, py, pw, ph), border_radius=int(3*self.zoom))
            if self.edit_platforms and self.selected_plat == i:
                # Resize Handle (Bottom-Right)
                pygame.draw.rect(plat_surf, (255, 0, 0), (px+pw-10, py+ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(plat_surf, (220, 38, 38), (px+pw-15, py-15, 30, 30), border_radius=15)
                pygame.draw.line(plat_surf, (255, 255, 255), (px+pw-7, py-7), (px+pw+7, py+7), 3)
                pygame.draw.line(plat_surf, (255, 255, 255), (px+pw+7, py-7), (px+pw-7, py+7), 3)

        # Draw Solid Boxes
        for i, b in enumerate(self.solid_boxes):
            px, py, pw, ph = int(cx+(b.x-cam_x)*self.zoom), int(cy+(b.y-cam_y)*self.zoom), int(b.w*self.zoom), int(b.h*self.zoom)
            col = (255, 100, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i + 1000 else (50, 50, 60, self.platform_alpha) # Use offset ID for boxes
            pygame.draw.rect(plat_surf, col, (px, py, pw, ph))
            if self.edit_platforms and self.selected_plat == i + 1000:
                pygame.draw.rect(plat_surf, (255, 0, 0), (px+pw-10, py+ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(plat_surf, (220, 38, 38), (px+pw-15, py-15, 30, 30), border_radius=15)
                pygame.draw.line(plat_surf, (255, 255, 255), (px+pw-7, py-7), (px+pw+7, py+7), 3)
                pygame.draw.line(plat_surf, (255, 255, 255), (px+pw+7, py-7), (px+pw-7, py+7), 3)

        screen.blit(plat_surf, (0,0))
        
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
            self.draw_sprite(screen, self.x, self.y, cur_s, self.frame_idx, self.facing_right, cam_x, cam_y, cx, cy)
            
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

        for ai in self.ai_list + getattr(self, 'temp_ai_list', []):
            if ai.visible: ai_s = ai.active_tag_info[0] if ai.active_tag_info else ai.profile.source_idx; self.draw_sprite(screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right, cam_x, cam_y, cx, cy)
            adx, ady = (ai.x-cam_x)*self.zoom, (ai.y-cam_y)*self.zoom
            if abs(adx)>play_w//2 or abs(ady)>play_h//2: ang = math.atan2(ady, adx); px, py = cx+math.cos(ang)*(play_w//2-40), cy+math.sin(ang)*(play_h//2-40); pygame.draw.circle(screen, (220,38,38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(ang)*8, py-math.sin(ang)*8), 2)
        if self.show_viewport:
            vw, vh = self.target_w * self.zoom, self.target_h * self.zoom; vr = pygame.Rect(cx - vw//2, cy - vh//2, vw, vh); overlay = pygame.Surface((play_w, play_h), pygame.SRCALPHA); overlay.fill((0, 0, 0, 160)); pygame.draw.rect(overlay, (0, 0, 0, 0), vr); screen.blit(overlay, (0, 0)); pygame.draw.rect(screen, (255, 255, 255), vr, 1); screen.blit(pygame.font.SysFont("Arial", 12).render(f"Viewport: {self.target_w}x{self.target_h} (16:9)", True, (255,255,255)), (vr.x, vr.y - 18))
        
        # Popup Overlay Draw
        if self.popup:
            msg_w, msg_h = 300, 150; cx, cy = screen.get_width()//2, screen.get_height()//2
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128)); screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(screen, (40, 40, 45), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), border_radius=10)
            pygame.draw.rect(screen, (60, 60, 65), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), 2, border_radius=10)
            
            font_b = pygame.font.SysFont("Arial", 14, bold=True); font_s = pygame.font.SysFont("Arial", 12)
            screen.blit(font_b.render("Confirm Action", True, (255, 255, 255)), (cx-50, cy-50))
            screen.blit(font_s.render(self.popup['msg'], True, (200, 200, 200)), (cx-len(self.popup['msg'])*3, cy-20))
            
            yes_btn = pygame.Rect(cx-80, cy+20, 60, 30); no_btn = pygame.Rect(cx+20, cy+20, 60, 30)
            pygame.draw.rect(screen, (59, 130, 246), yes_btn, border_radius=5)
            pygame.draw.rect(screen, (220, 38, 38), no_btn, border_radius=5)
            screen.blit(font_b.render("YES", True, (255,255,255)), (yes_btn.x+15, yes_btn.y+5))
            screen.blit(font_b.render("NO", True, (255,255,255)), (no_btn.x+20, no_btn.y+5))

def main():
    pygame.init(); screen = pygame.display.set_mode((1350, 850), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1); clock = pygame.time.Clock(); player = AsepritePlayer(); show_settings = False; slot_scroll = tag_scroll = settings_scroll = 0; font_s = pygame.font.SysFont("Arial", 12); font_b = pygame.font.SysFont("Arial", 14, bold=True); font_h = pygame.font.SysFont("Arial", 11); is_dragging_cam = False; last_m_pos = (0,0); selected_slot = None; folds = {"PHYSICS": True, "AI & COMBAT": True, "JUICE & VFX": True, "LAYERS": True, "CAMERA": True, "BG IMAGE": True, "BG COLOR": True, "CONTROLS": False}
    binding_key = None; active_input_attr = None; input_text = ""
    while True:
        raw_dt = clock.tick(60)
        dt = raw_dt * player.playback_speed if player else raw_dt
        sw, sh = screen.get_size(); sidebar_w = 450; play_w = sw - sidebar_w; play_h = sh - 70; m_pos = pygame.mouse.get_pos(); screen.fill(player.bg_color)
        if player: player.update(pygame.key.get_pressed(), 500, dt); player.draw(screen, play_w, play_h)
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)); pygame.draw.rect(screen, (35, 35, 40), (0, 0, play_w, 70))
        
        # --- TOP UI ROW 1 (Project & Files) ---
        new_proj = pygame.Rect(10, 5, 80, 28); pygame.draw.rect(screen, (220, 38, 38), new_proj, border_radius=5); screen.blit(font_b.render("NEW", True, (255,255,255)), (new_proj.x+20, 10))
        
        example_btn = pygame.Rect(95, 5, 80, 28); pygame.draw.rect(screen, (34, 139, 34), example_btn, border_radius=5); screen.blit(font_b.render("EXAMPLE", True, (255,255,255)), (example_btn.x+10, 10))
        
        load_prev = pygame.Rect(180, 5, 70, 28); has_prev = os.path.exists("ase_project.json")
        pygame.draw.rect(screen, (59, 130, 246) if has_prev else (60, 60, 70), load_prev, border_radius=5); screen.blit(font_b.render("LOAD", True, (255,255,255) if has_prev else (120, 120, 120)), (load_prev.x+15, 10))
        
        add_src = pygame.Rect(255, 5, 70, 28); pygame.draw.rect(screen, (59, 130, 246), add_src, border_radius=5); screen.blit(font_b.render("+ SRC", True, (255,255,255)), (add_src.x+15, 10))
        
        add_npc = pygame.Rect(330, 5, 70, 28); pygame.draw.rect(screen, (22, 163, 74), add_npc, border_radius=5); screen.blit(font_b.render("+ NPC", True, (255,255,255)), (add_npc.x+15, 10))

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
            for i, p in enumerate(player.profiles): 
                tab = pygame.Rect(400+i*95, 5, 90, 28); col = (59,130,246) if player.cur_profile_idx==i else (60,60,70)
                if tab.right < play_w - 120: # Avoid Settings btn
                    pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(p.name[:12], True, (255,255,255)), (tab.x+5, 12))
            
            # Source Tabs (Row 2, Right side)
            for i, s in enumerate(player.sources): 
                tab = pygame.Rect(400+i*110, 38, 105, 28); col = (100,100,120) if player.cur_source_idx==i else (45,45,55)
                if tab.right < play_w:
                    pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(s.name[:12], True, (255,255,255)), (tab.x+5, 44))
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
                            elif load_prev.collidepoint(m_pos) and has_prev: player.load_settings(); player.load_project()
                            elif add_src.collidepoint(m_pos) and player: 
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: player.add_source(p)
                            elif add_npc.collidepoint(m_pos) and player: 
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: sid = player.add_source(p); player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
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
                                for i in range(len(player.profiles)):
                                    if pygame.Rect(400+i*95, 5, 90, 28).collidepoint(m_pos): 
                                        if player.cur_profile_idx != i:
                                            player.popup = {'msg': "Switch Profile?", 'cb': lambda i=i: setattr(player, 'cur_profile_idx', i)}
                                for i in range(len(player.sources)):
                                    if pygame.Rect(400+i*110, 38, 105, 28).collidepoint(m_pos): 
                                        if player.cur_source_idx != i:
                                            player.cur_source_idx = i # Always select the source to view tags
                                            if player.profiles:
                                                p = player.profiles[player.cur_profile_idx]
                                                if p.source_idx != i:
                                                    def _switch_prof(idx=i):
                                                        p = player.profiles[player.cur_profile_idx]
                                                        p.source_idx = idx
                                                        player.auto_map_profile(p)
                                                    player.popup = {'msg': "Map profile to this source?", 'cb': _switch_prof}

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
                                elif player.selected_plat >= 1000 and (player.selected_plat - 1000) < len(getattr(player, "solid_boxes", [])):
                                    b = player.solid_boxes[player.selected_plat - 1000]
                                    px, py, pw = cx+(b.x-cam_x)*player.zoom, cy+(b.y-cam_y)*player.zoom, b.w*player.zoom
                                    if pygame.Rect(px+pw-15, py-15, 30, 30).collidepoint(m_pos):
                                        player.solid_boxes.pop(player.selected_plat - 1000)
                                        player.selected_plat = None; hit = True

                            if not hit:
                                # Check Platforms
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
                                if m_pos[1] > 70: # Only process clicks below the top bar
                                    cy = 60 + settings_scroll
                                    for cat in folds.keys():
                                        hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30)
                                        if hr.collidepoint(m_pos): folds[cat] = not folds[cat]
                                        cy += 35
                                        if folds[cat]:
                                            if cat == "PHYSICS": cy += 185
                                            elif cat == "AI & COMBAT": cy += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                                            elif cat == "JUICE & VFX": cy += 130
                                            elif cat == "LAYERS" and player.sources: cy += 28 * len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers) + 10
                                            elif cat == "CAMERA": cy += 85
                                            elif cat == "BG IMAGE": cy += 250
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
                        elif play_w < m_pos[0] < sw and player.profiles:
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
                            else:
                                setattr(player, active_input_attr, val)
                            player.save_settings()
                            if "bg_" in active_input_attr: player.bg_needs_update = True
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
                                if cat == "PHYSICS": calc_h += 185
                                elif cat == "AI & COMBAT": calc_h += 120 + max(0, ((len(player.profiles)-2)//4)*30)
                                elif cat == "JUICE & VFX": calc_h += 130
                                elif cat == "LAYERS" and player.sources: calc_h += 28 * len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers) + 10
                                elif cat == "CAMERA": calc_h += 85
                                elif cat == "BG IMAGE": calc_h += 250
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
                        else:
                            player.solid_boxes[player.selected_plat - 1000].x = mx + player.drag_offset[0]
                            player.solid_boxes[player.selected_plat - 1000].y = my + player.drag_offset[1]
                
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
                        if cat == "PHYSICS":
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
                            for j in range(1, len(player.profiles)):
                                btn = pygame.Rect(110 + ((j-1)%4)*55, y - 5 + ((j-1)//4)*30, 50, 24)
                                is_sel = getattr(player, 'swap_target_idx', 0) == j
                                pygame.draw.rect(set_surf, (59,130,246) if is_sel else (60,60,70), btn, border_radius=4)
                                set_surf.blit(font_h.render(f"NPC {j}", True, (255,255,255)), (btn.x+8, btn.y+5))
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, btn.y, btn.w, btn.h).collidepoint(m_pos):
                                    player.swap_target_idx = j; player.save_settings()
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
                            if hasattr(player, "_btn_lock"): 
                                player._btn_lock -= 1; 
                                if player._btn_lock <= 0: delattr(player, "_btn_lock")
                            cy += 130
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
                            bg_btn = pygame.Rect(20, cy, 150, 30); pygame.draw.rect(set_surf, (100,100,110), bg_btn, border_radius=5); set_surf.blit(font_b.render("LOAD BG IMG", True, (255,255,255)), (bg_btn.x+25, bg_btn.y+5))
                            if m_pos[1] > 70 and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20, cy, 150, 30).collidepoint(m_pos):
                                p = select_file([("Image", "*.png *.jpg *.bmp")]); 
                                if p: player.bg_img = pygame.image.load(p).convert_alpha(); player.bg_path = p; player.bg_needs_update = True; player.save_settings()
                            cy += 40
                            for i, (l, mn, mx, at) in enumerate([("BG-X",-2000,2000,"bg_off_x"), ("BG-Y",-2000,2000,"bg_off_y"), ("Scale",0.1,10,"bg_zoom"), ("Alpha",0,255,"bg_alpha"), ("Parallax",0,1,"bg_parallax")]):
                                y = cy+i*40; set_surf.blit(font_s.render(l, True, (150,150,150)), (20, y)); sl = pygame.Rect(80, y+5, sidebar_w-160, 8); pygame.draw.rect(set_surf, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(set_surf, (220,38,38), (int(80+n*(sidebar_w-160)), y+9), 8)
                                
                                is_int_at = "off" in at or "alpha" in at
                                txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else (f"{int(v)}" if is_int_at else f"{v:.2f}"))
                                pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == at else (45,45,50), (sidebar_w-45, y-2, 40, 18), border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (sidebar_w-42, y))
                                
                                if m_pos[1] > 70 and pygame.mouse.get_pressed()[0]:
                                    if pygame.Rect(play_w+sidebar_w-45, y-2, 40, 18).collidepoint(m_pos):
                                        if active_input_attr != at: active_input_attr = at; input_text = str(int(v)) if is_int_at else str(round(v, 2))
                                    elif pygame.Rect(play_w+80, y, sidebar_w-160, 20).inflate(0,10).collidepoint(m_pos):
                                        active_input_attr = None
                                        setattr(player, at, mn+(m_pos[0]-(play_w+80))/(sidebar_w-160)*(mx-mn)); player.save_settings(); player.bg_needs_update = True
                            cy += 210
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
        pygame.display.flip()

if __name__ == "__main__": main()
