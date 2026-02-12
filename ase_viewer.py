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

# Direct Log Function
def log_debug(msg):
    with open("ase_debug.log", "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")
    print(msg)

# Clean old log
if os.path.exists("ase_debug.log"): os.remove("ase_debug.log")
log_debug("[SYSTEM] v19 Hybrid-Profile Started")

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
        root = tk.Tk(); root.withdraw()
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
        root = tk.Tk(); root.withdraw()
        path = filedialog.askopenfilename(filetypes=ftypes)
        root.destroy()
        return path
    except: return None

class AseSource:
    def __init__(self, file_path, source_id):
        self.id = source_id; self.file_path = file_path; self.name = os.path.basename(file_path)
        self.frames = []; self.tags = {}; self.tag_list = []; self.orig_w = self.orig_h = 0
        self.export_and_load()
    def export_and_load(self):
        try:
            exe = ase_manager.get_path(); png_p = f"temp_{self.id}.png"; json_p = f"temp_{self.id}.json"
            subprocess.run([exe, "-b", self.file_path, "--trim", "--sheet", png_p, "--data", json_p, "--format", "json-array", "--list-tags"], check=True, capture_output=True)
            sheet = pygame.image.load(png_p).convert_alpha()
            with open(json_p, 'r') as f: data = json.load(f)
            self.orig_w, self.orig_h = data['frames'][0]['sourceSize']['w'], data['frames'][0]['sourceSize']['h']
            for f in data['frames']:
                r, s = f['frame'], f['spriteSourceSize']
                surf = pygame.Surface((r['w'], r['h']), pygame.SRCALPHA); surf.blit(sheet, (0, 0), (r['x'], r['y'], r['w'], r['h']))
                self.frames.append({'img': surf, 'ox': s['x'] - self.orig_w // 2, 'oy': s['y'] - self.orig_h // 2})
            if 'meta' in data and 'frameTags' in data['meta']:
                for t in data['meta']['frameTags']: self.tags[t['name']] = (t['from'], t['to'])
            self.tag_list = sorted(list(self.tags.keys()))
            for p in [png_p, json_p]: 
                if os.path.exists(p): os.remove(p)
            log_debug(f"[LOAD] {self.name} Loaded.")
        except Exception as e: log_debug(f"[ERROR] Load failed: {e}")

class AseProfile:
    def __init__(self, name, source_idx):
        self.name = name; self.source_idx = source_idx
        self.mappings = { "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ComboAttack_1": [], "ComboAttack_2": [], "ComboAttack_3": [], "ComboAttack_4": [], "JUMPATTACK": [], "POWERBOMB": [], "DASH": [], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HURT": [] }

class AseAI:
    def __init__(self, master, profile):
        self.master = master; self.profile = profile; self.spawn_x = random.randint(300, 1500); self.x, self.y = self.spawn_x, 500
        self.vx = self.vy = 0; self.grounded = True; self.facing_right = random.choice([True, False])
        self.frame_idx = 0; self.anim_timer = 0; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.ai_timer = random.randint(30, 90); self.decision = "IDLE"
    def update(self, ground_y):
        self.ai_timer -= 1; dist_p = self.master.x - self.x
        if self.ai_timer <= 0:
            if abs(dist_p) < 600: self.decision = random.choice(["IDLE", "CHASE", "ATTACK", "DASH", "JUMP"])
            else: self.decision = random.choice(["IDLE", "WALK_L", "WALK_R"])
            self.ai_timer = random.randint(40, 120)
            if self.decision == "ATTACK" and abs(dist_p) < 200: self.facing_right = dist_p > 0; self.trigger_action(f"ComboAttack_{random.randint(1,4)}")
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
        target_info = None
        if not self.active_tag_info:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            m = self.profile.mappings.get(state, []); target_info = m[0] if m else None
        else: target_info = self.active_tag_info
        if target_info:
            src = self.master.sources[target_info[0]]; tr = src.tags[target_info[1]]
            if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]
            self.anim_timer += 1
            if self.anim_timer > 6:
                self.frame_idx += 1
                if self.active_tag_info and self.frame_idx > self.action_end_frame:
                    if "(loop)" in target_info[1].lower(): self.frame_idx = tr[0]
                    elif self.action_queue: self.active_tag_info = self.action_queue.pop(0); s = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = s.tags[self.active_tag_info[1]]
                    else: self.active_tag_info = None
                elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                self.anim_timer = 0
    def trigger_action(self, slot):
        tags = self.profile.mappings.get(slot, [])
        if tags:
            self.action_queue = list(tags); self.active_tag_info = self.action_queue.pop(0)
            src = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = src.tags[self.active_tag_info[1]]
            if slot == "DASH": self.vx = 25 if self.facing_right else -25

class AsepritePlayer:
    def __init__(self, initial_path):
        self.sources = []; self.profiles = []; self.cur_profile_idx = 0; self.cur_source_idx = 0
        self.add_source(initial_path); self.add_profile("PLAYER", 0)
        self.x, self.y = 400, 500; self.vx = self.vy = 0; self.grounded = False; self.jumps_left = 2; self.facing_right = True; self.zoom = 3.0; self.dash_speed = 35.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 15.0; self.powerbomb_speed = 35.0; self.pbomb_pause_timer = 0; self.loop_counter = 0
        self.cam_x, self.cam_y = 400, 300; self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20), pygame.Rect(-200, 250, 300, 20), pygame.Rect(900, 300, 400, 20)]
        self.bg_img = None; self.bg_off_x = self.bg_off_y = 0; self.bg_zoom = 1.0; self.bg_alpha = 255; self.bg_parallax = 0.1; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]
        self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0; self.active_action_slot = None; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0; self.ai_list = []
    def add_source(self, path):
        new_source = AseSource(path, len(self.sources)); self.sources.append(new_source); self.cur_source_idx = new_source.id
        return new_source.id
    def add_profile(self, name, source_idx, is_npc=False):
        new_profile = AseProfile(name, source_idx); self.profiles.append(new_profile); self.auto_map_profile(new_profile)
        if is_npc: self.ai_list.append(AseAI(self, new_profile))
    def auto_map_profile(self, profile):
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
        if not self.grounded:
            if keys[pygame.K_DOWN]: self.trigger_action("POWERBOMB", keys)
            else: self.trigger_action("JUMPATTACK", keys)
        else:
            slot = f"ComboAttack_{self.combo_step+1}"
            if self.profiles[0].mappings.get(slot): self.combo_reset_timer = 60; self.trigger_action(slot, keys); self.combo_step = (self.combo_step+1)%4
    def trigger_action(self, slot, keys=None):
        profile = self.profiles[0]; tags = profile.mappings.get(slot, [])
        if not tags and slot != "DASH": return
        if slot == "DASH" and self.dash_charges > 0:
            self.dash_charges -= 1
            for i in range(2): 
                if self.dash_cooldowns[i] <= 0: self.dash_cooldowns[i] = 90; break
            self.dash_timer = 12; self.vx = self.dash_speed if self.facing_right else -self.dash_speed; self.vy = 0; self.active_action_slot = "DASH"; self.action_queue = list(tags); self.play_next_in_queue(); return
        if tags:
            self.active_action_slot = slot; self.action_queue = list(tags); self.loop_counter = 0
            if slot == "POWERBOMB": self.pbomb_pause_timer = 15; self.vy = 0; self.vx = 0
            elif "ComboAttack" in slot and keys:
                if keys[pygame.K_RIGHT]: self.vx = self.atk_forward_v; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -self.atk_forward_v; self.facing_right = False
            self.play_next_in_queue()
    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag_info = self.action_queue.pop(0); src = self.sources[self.active_tag_info[0]]
            if self.active_tag_info[1] in src.tags: self.frame_idx, self.action_end_frame = src.tags[self.active_tag_info[1]]; self.loop_counter = 0
            else: self.play_next_in_queue()
        else: self.active_tag_info = None; self.active_action_slot = None
    def update(self, keys, ground_y, play_w, play_h):
        for i in range(2):
            if self.dash_cooldowns[i] > 0:
                self.dash_cooldowns[i] -= 1
                if self.dash_cooldowns[i] <= 0: self.dash_charges = min(2, self.dash_charges + 1)
        if self.pbomb_pause_timer > 0:
            self.pbomb_pause_timer -= 1; self.vy = 0
            if self.pbomb_pause_timer == 0: self.vy = self.powerbomb_speed
        elif self.dash_timer > 0: self.dash_timer -= 1; self.vy = 0
        else:
            self.vx *= 0.82; can_move = not self.active_tag_info or self.active_action_slot == "JUMPATTACK"
            if can_move:
                if keys[pygame.K_RIGHT]: self.vx = 6.5; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -6.5; self.facing_right = False
            self.vy += self.gravity
        self.x += self.vx; self.y += self.vy; self.grounded = False
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
        if self.vy >= 0:
            for plat in self.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - self.vy <= plat.top + 10: self.y = plat.top; self.vy = 0; self.grounded = True; self.jumps_left = 2
        if self.grounded and self.active_action_slot in ["POWERBOMB", "JUMPATTACK"]:
            if self.active_tag_info and "(loop)" in self.active_tag_info[1].lower(): self.play_next_in_queue()
        self.cam_x += (self.x - self.cam_x) * 0.12; self.cam_y += (self.y - self.cam_y) * (0.3 if self.grounded else 0.12)
        if self.combo_reset_timer > 0:
            self.combo_reset_timer -= 1
            if self.combo_reset_timer <= 0: self.combo_step = 0
        if not self.active_tag_info:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            m = self.profiles[0].mappings.get(state, []); target_info = m[0] if m else None
        else: target_info = self.active_tag_info
        if target_info:
            src = self.sources[target_info[0]]; tr = src.tags[target_info[1]]
            if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]
            self.anim_timer += 1
            if self.anim_timer > 6:
                self.frame_idx += 1
                if self.active_tag_info and self.frame_idx > self.action_end_frame:
                    is_skill = "SKILL" in str(self.active_action_slot); is_loop = "(loop)" in target_info[1].lower()
                    if is_loop and is_skill and self.loop_counter < 1: self.frame_idx = tr[0]; self.loop_counter += 1
                    elif is_loop and not is_skill: self.frame_idx = tr[0]
                    else: self.play_next_in_queue()
                elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                self.anim_timer = 0
        for ai in self.ai_list: ai.update(ground_y)
    def draw_sprite(self, screen, x, y, source_idx, f_idx, facing_right, cam_x, cam_y, cx, cy):
        if source_idx >= len(self.sources): return
        src = self.sources[source_idx]; f = src.frames[min(f_idx, len(src.frames)-1)]
        scaled = pygame.transform.scale(f['img'], (int(f['img'].get_width()*self.zoom), int(f['img'].get_height()*self.zoom)))
        ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
        if not facing_right: scaled = pygame.transform.flip(scaled, True, False); ox = -ox - scaled.get_width()
        screen.blit(scaled, (int(cx + (x - cam_x)*self.zoom + ox), int(cy + (y - cam_y)*self.zoom + oy)))
    def draw(self, screen, play_w, play_h):
        cx, cy = play_w // 2, play_h // 2
        gx, gy = cx - (self.cam_x % 100)*self.zoom, cy - (self.cam_y % 100)*self.zoom
        for i in range(-10, 20):
            pygame.draw.line(screen, self.grid_color, (gx+i*100*self.zoom, 0), (gx+i*100*self.zoom, play_h), 1)
            pygame.draw.line(screen, self.grid_color, (0, gy+i*100*self.zoom), (play_w, gy+i*100*self.zoom), 1)
        if self.bg_img:
            bw, bh = int(self.bg_img.get_width()*self.bg_zoom*self.zoom*0.5), int(self.bg_img.get_height()*self.bg_zoom*self.zoom*0.5)
            bs = pygame.transform.scale(self.bg_img, (bw, bh))
            if self.bg_alpha < 255: bs.set_alpha(self.bg_alpha)
            bx = cx + (self.bg_off_x - self.cam_x * self.bg_parallax) * self.zoom - bw // 2
            by = cy + (self.bg_off_y - self.cam_y * self.bg_parallax) * self.zoom - bh // 2
            screen.blit(bs, (bx, by))
        for p in self.platforms: pygame.draw.rect(screen, (80,80,100), (cx+(p.x-self.cam_x)*self.zoom, cy+(p.y-self.cam_y)*self.zoom, p.w*self.zoom, p.h*self.zoom), border_radius=int(3*self.zoom))
        pygame.draw.line(screen, (100,100,100), (cx+(0-self.cam_x)*self.zoom, cy+(500-self.cam_y)*self.zoom), (cx+(5000-self.cam_x)*self.zoom, cy+(500-self.cam_y)*self.zoom), 2)
        cur_s = self.active_tag_info[0] if self.active_tag_info else 0
        if not self.active_tag_info:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            m = self.profiles[0].mappings.get(state, []); cur_s = m[0][0] if m else 0
        self.draw_sprite(screen, self.x, self.y, cur_s, self.frame_idx, self.facing_right, self.cam_x, self.cam_y, cx, cy)
        for ai in self.ai_list:
            ai_s = ai.active_tag_info[0] if ai.active_tag_info else ai.profile.source_idx
            self.draw_sprite(screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right, self.cam_x, self.cam_y, cx, cy)
            adx, ady = (ai.x-self.cam_x)*self.zoom, (ai.y-self.cam_y)*self.zoom
            if abs(adx)>play_w//2 or abs(ady)>play_h//2:
                ang = math.atan2(ady, adx); px, py = cx+math.cos(ang)*(play_w//2-40), cy+math.sin(ang)*(play_h//2-40)
                pygame.draw.circle(screen, (220,38,38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(ang)*8, py-math.sin(ang)*8), 2)

def main():
    pygame.init(); screen = pygame.display.set_mode((1350, 850), pygame.RESIZABLE); clock = pygame.time.Clock(); player = None; selected_slot = None; show_settings = False; slot_scroll = 0; tag_scroll = 0; font_s = pygame.font.SysFont("Arial", 12); font_b = pygame.font.SysFont("Arial", 14, bold=True)
    folds = {"PHYSICS": True, "AI & COMBAT": True, "BG IMAGE": True, "BG COLOR": True}
    while True:
        sw, sh = screen.get_size(); sidebar_w = 450; play_w = sw - sidebar_w; play_h = sh - 70; m_pos = pygame.mouse.get_pos(); bg_col = player.bg_color if player else [15, 15, 18]; screen.fill(bg_col)
        if player: player.update(pygame.key.get_pressed(), 500, play_w, play_h); player.draw(screen, play_w, play_h)
        # UI Layout
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)); pygame.draw.rect(screen, (35, 35, 40), (0, 0, play_w, 70))
        new_proj = pygame.Rect(10, 5, 120, 30); pygame.draw.rect(screen, (220, 38, 38), new_proj, border_radius=5); screen.blit(font_b.render("NEW PROJECT", True, (255,255,255)), (20, 10))
        add_src = pygame.Rect(140, 5, 100, 30); pygame.draw.rect(screen, (59, 130, 246), add_src, border_radius=5); screen.blit(font_b.render("+ SOURCE", True, (255,255,255)), (155, 10))
        add_npc = pygame.Rect(250, 5, 90, 30); pygame.draw.rect(screen, (22, 163, 74), add_npc, border_radius=5); screen.blit(font_b.render("+ NPC", True, (255,255,255)), (270, 10))
        settings_btn = pygame.Rect(play_w - 120, 5, 110, 30); pygame.draw.rect(screen, (50, 50, 60), settings_btn, border_radius=5); screen.blit(font_b.render("⚙ SETTINGS", True, (255,255,255)), (settings_btn.x+15, 10))
        if player:
            # Profile Tabs (Row 1)
            for i, prof in enumerate(player.profiles):
                tab = pygame.Rect(350+i*95, 5, 90, 30); col = (59,130,246) if player.cur_profile_idx==i else (60,60,70); pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(prof.name[:12], True, (255,255,255)), (tab.x+5, 12))
            # Source Tabs (Row 2)
            for i, src in enumerate(player.sources):
                tab = pygame.Rect(10+i*110, 38, 105, 28); col = (100,100,120) if player.cur_source_idx==i else (45,45,55); pygame.draw.rect(screen, col, tab, border_radius=5); screen.blit(font_s.render(src.name[:12], True, (255,255,255)), (tab.x+5, 44))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.DROPFILE:
                if not player: player = AsepritePlayer(event.file)
                else: player.add_source(event.file)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_proj.collidepoint(m_pos):
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: player = AsepritePlayer(p)
                if add_src.collidepoint(m_pos) and player:
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: player.add_source(p)
                if add_npc.collidepoint(m_pos) and player:
                    p = select_file([("Aseprite", "*.aseprite *.ase")]); 
                    if p: sid = player.add_source(p); player.add_profile(f"NPC_{len(player.profiles)}", sid, is_npc=True)
                if settings_btn.collidepoint(m_pos): show_settings = not show_settings
                if player:
                    for i in range(len(player.profiles)):
                        if pygame.Rect(350+i*95, 5, 90, 30).collidepoint(m_pos): player.cur_profile_idx = i
                    for i in range(len(player.sources)):
                        if pygame.Rect(10+i*110, 38, 105, 28).collidepoint(m_pos): player.cur_source_idx = i
                    if play_w < m_pos[0] < sw:
                        if not show_settings:
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
                                    src = player.sources[player.cur_source_idx]
                                    for idx, tag in enumerate(src.tag_list):
                                        t_rect = pygame.Rect(play_w+20, 480+idx*25+tag_scroll, sidebar_w-40, 22)
                                        if t_rect.collidepoint(m_pos) and t_rect.top >= 475:
                                            target = (player.cur_source_idx, tag); 
                                            if target in cur_p.mappings[selected_slot]: cur_p.mappings[selected_slot].remove(target)
                                            else: cur_p.mappings[selected_slot].append(target)
                if event.button == 3 and player:
                    cur_p = player.profiles[player.cur_profile_idx]
                    for i, action in enumerate(cur_p.mappings.keys()):
                        if pygame.Rect(play_w+20, 80+i*38+slot_scroll, sidebar_w-40, 34).collidepoint(m_pos): cur_p.mappings[action] = []
            if event.type == pygame.KEYDOWN and player:
                if event.key in [pygame.K_SPACE, pygame.K_UP] and player.jumps_left > 0: player.vy = player.jump_power; player.grounded = False; player.jumps_left -= 1
                if event.key == pygame.K_z: player.handle_attack(pygame.key.get_pressed())
                if event.key == pygame.K_x: player.trigger_action("DASH")
                if event.key == pygame.K_c: player.trigger_action("SKILL 1")
                if event.key == pygame.K_b: player.trigger_action("SKILL 2")
                if event.key == pygame.K_n: player.trigger_action("SKILL 3")
                if event.key == pygame.K_v: player.trigger_action("HURT")
            if event.type == pygame.MOUSEWHEEL and player and m_pos[0] < play_w: player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0))
        if player:
            cur_p = player.profiles[player.cur_profile_idx]; cur_s = player.sources[player.cur_source_idx]
            if show_settings:
                pygame.draw.rect(screen, (35, 35, 40), (play_w, 0, sidebar_w, sh)); pygame.draw.line(screen, (59, 130, 246), (play_w, 0), (play_w, sh), 2); cy = 60
                for cat in folds.keys():
                    hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30); pygame.draw.rect(screen, (50,50,60), hr, border_radius=5); screen.blit(font_b.render(f"{'+' if not folds[cat] else '-'} {cat}", True, (255,255,255)), (hr.x+10, hr.y+7)); cy += 35
                    if folds[cat]:
                        if cat == "PHYSICS":
                            for i, (l, mn, mx, at, inv) in enumerate([("Dash Vel",10,50,"dash_speed",0), ("Jump Pow",10,25,"jump_power",1), ("PBomb Spd",10,60,"powerbomb_speed",0)]):
                                y = cy+i*45; screen.blit(font_s.render(l, True, (150,150,150)), (play_w+20, y)); sl = pygame.Rect(play_w+20, y+18, sidebar_w-40, 8); pygame.draw.rect(screen, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn) if not inv else (-v-mn)/(mx-mn); pygame.draw.circle(screen, (59,130,246), (int(play_w+20+n*(sidebar_w-40)), y+22), 8)
                                if pygame.mouse.get_pressed()[0] and sl.inflate(0,20).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+20))/(sidebar_w-40)*(mx-mn) if not inv else -(mn+(m_pos[0]-(play_w+20))/(sidebar_w-40)*(mx-mn)))
                            cy += 140
                        elif cat == "AI & COMBAT":
                            for i, (l, mn, mx, at) in enumerate([("Atk Forward",0,30,"atk_forward_v")]):
                                y = cy+i*45; screen.blit(font_s.render(l, True, (150,150,150)), (play_w+20, y)); sl = pygame.Rect(play_w+20, y+18, sidebar_w-40, 8); pygame.draw.rect(screen, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(screen, (59,130,246), (int(play_w+20+n*(sidebar_w-40)), y+22), 8)
                                if pygame.mouse.get_pressed()[0] and sl.inflate(0,20).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+20))/(sidebar_w-40)*(mx-mn))
                            cy += 100
                        elif cat == "BG IMAGE":
                            bg_btn = pygame.Rect(play_w+20, cy, 150, 30); pygame.draw.rect(screen, (100,100,110), bg_btn, border_radius=5); screen.blit(font_b.render("LOAD BG IMG", True, (255,255,255)), (bg_btn.x+25, bg_btn.y+5))
                            if pygame.mouse.get_pressed()[0] and bg_btn.collidepoint(m_pos):
                                p = select_file([("Image", "*.png *.jpg *.bmp")]); 
                                if p: player.bg_img = pygame.image.load(p).convert_alpha()
                            cy += 40
                            bg_ctrls = [("BG-X",-2000,2000,"bg_off_x"), ("BG-Y",-2000,2000,"bg_off_y"), ("Scale",0.1,10,"bg_zoom"), ("Alpha",0,255,"bg_alpha"), ("Parallax",0,1,"bg_parallax")]
                            for i, (l, mn, mx, at) in enumerate(bg_ctrls):
                                y = cy+i*40; screen.blit(font_s.render(l, True, (150,150,150)), (play_w+20, y)); sl = pygame.Rect(play_w+80, y+5, sidebar_w-120, 8); pygame.draw.rect(screen, (60,60,70), sl); v = getattr(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(screen, (220,38,38), (int(play_w+80+n*(sidebar_w-120)), y+9), 8)
                                if pygame.mouse.get_pressed()[0] and sl.inflate(0,20).collidepoint(m_pos): setattr(player, at, mn+(m_pos[0]-(play_w+80))/(sidebar_w-120)*(mx-mn))
                            cy += 210
                        elif cat == "BG COLOR":
                            for i, c in enumerate(['R','G','B']):
                                y = cy+i*35; sl = pygame.Rect(play_w+20, y+15, sidebar_w-40, 8); pygame.draw.rect(screen, (60,60,70), sl); pygame.draw.circle(screen, (220,38,38) if i==0 else (22,163,74) if i==1 else (59,130,246), (int(play_w+20+player.bg_color[i]/255*(sidebar_w-40)), y+19), 8)
                                if pygame.mouse.get_pressed()[0] and sl.inflate(0,20).collidepoint(m_pos): player.bg_color[i] = int((m_pos[0]-(play_w+20))/(sidebar_w-40)*255)
                            cy += 120
            else:
                slot_clip = pygame.Surface((sidebar_w-20, 380), pygame.SRCALPHA)
                for i, action in enumerate(cur_p.mappings.keys()):
                    rect = pygame.Rect(10, i*38+slot_scroll, sidebar_w-40, 34); is_sel = selected_slot == action; col = (59,130,246) if is_sel else (45,45,50); pygame.draw.rect(slot_clip, col, rect, border_radius=5); slot_clip.blit(font_b.render(action, True, (255,255,255)), (rect.x+10, rect.y+3))
                    ms = ", ".join([f"{m[1]}" for m in cur_p.mappings[action]]); slot_clip.blit(font_s.render(f"-> {ms[:45]}", True, (200,200,200) if not is_sel else (255,255,255)), (rect.x+10, rect.y+18))
                screen.blit(slot_clip, (play_w+10, 85))
                list_area = pygame.Rect(play_w+15, 475, sidebar_w-30, sh-490); pygame.draw.rect(screen, (20,20,25), list_area, border_radius=5); screen.blit(font_b.render(f"TAGS FROM: {cur_s.name[:20]}", True, (100,100,100)), (play_w+20, 455)); clip_surf = pygame.Surface((sidebar_w-40, sh-495), pygame.SRCALPHA)
                for idx, tag in enumerate(cur_s.tag_list):
                    t_rect = pygame.Rect(0, idx*25+tag_scroll, sidebar_w-40, 22); is_mapped = selected_slot and (player.cur_source_idx, tag) in cur_p.mappings[selected_slot]; hvr = t_rect.move(play_w+20, 475).collidepoint(m_pos); t_col = (59,130,246) if is_mapped else ((70,70,80) if hvr else (40,40,45)); pygame.draw.rect(clip_surf, t_col, t_rect, border_radius=3); clip_surf.blit(font_s.render(tag, True, (255,255,255)), (t_rect.x+10, t_rect.y+4))
                screen.blit(clip_surf, (play_w+20, 475))
            for i in range(2):
                col = (59, 130, 246) if i < player.dash_charges else (60, 60, 70); pygame.draw.rect(screen, col, (20 + i*35, 75, 30, 10), border_radius=3)
            pygame.draw.rect(screen, (30,30,35), (0, sh-40, play_w, 40)); guide = f"Editing: {cur_p.name} | From File: {cur_s.name} | Click Taps to switch Profile/Source"; screen.blit(font_s.render(guide, True, (255,255,255)), (20, sh-25))
        pygame.display.flip(); clock.tick(60)

if __name__ == "__main__": main()
