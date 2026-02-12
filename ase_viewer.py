import pygame
import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog
import re
import random
import math

ASEPRITE_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe"

def select_file(ftypes):
    try:
        root = tk.Tk(); root.withdraw()
        path = filedialog.askopenfilename(filetypes=ftypes)
        root.destroy()
        return path
    except: return None

class AseAI:
    def __init__(self, master):
        self.master = master
        self.x, self.y = random.randint(200, 1000), 500
        self.vx = self.vy = 0
        self.grounded = True
        self.facing_right = random.choice([True, False])
        self.frame_idx = 0; self.anim_timer = 0
        self.active_tag = None; self.action_queue = []; self.action_end_frame = -1
        self.ai_timer = random.randint(30, 90); self.decision = "IDLE"

    def update(self, ground_y):
        self.ai_timer -= 1
        if self.ai_timer <= 0:
            self.decision = random.choice(["IDLE", "WALK_L", "WALK_R", "JUMP", "DASH", "ATTACK"])
            self.ai_timer = random.randint(30, 120)
            if self.decision == "ATTACK": self.trigger_action(f"ATTACK {random.randint(1,4)}")
            elif self.decision == "DASH": self.trigger_action("DASH")
            elif self.decision == "JUMP" and self.grounded: self.vy = self.master.jump_power; self.grounded = False

        self.vx *= 0.85
        if not self.active_tag:
            if self.decision == "WALK_R": self.vx = 4; self.facing_right = True
            elif self.decision == "WALK_L": self.vx = -4; self.facing_right = False
        
        if self.active_tag == "DASH": self.vy = 0
        else: self.vy += self.master.gravity

        self.x += self.vx; self.y += self.vy
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True

        target = None
        if not self.active_tag:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            mapped = self.master.mappings.get(state, [])
            target = mapped[0] if mapped and mapped[0] in self.master.tags else None
        else: target = self.active_tag

        if target and target in self.master.tags:
            t_range = self.master.tags[target]
            if self.frame_idx < t_range[0] or self.frame_idx > t_range[1]: self.frame_idx = t_range[0]
            self.anim_timer += 1
            if self.anim_timer > 6:
                self.frame_idx += 1
                if self.active_tag and self.frame_idx > self.action_end_frame:
                    if self.action_queue:
                        self.active_tag = self.action_queue.pop(0)
                        if self.active_tag in self.master.tags: self.frame_idx, self.action_end_frame = self.master.tags[self.active_tag]
                    else: self.active_tag = None
                elif self.frame_idx > t_range[1]: self.frame_idx = t_range[0]
                self.anim_timer = 0

    def trigger_action(self, slot):
        tags = self.master.mappings.get(slot, [])
        if tags:
            self.action_queue = list(tags)
            self.active_tag = self.action_queue.pop(0)
            if self.active_tag in self.master.tags:
                self.frame_idx, self.action_end_frame = self.master.tags[self.active_tag]
            if slot == "DASH": self.vx = self.master.dash_speed if self.facing_right else -self.master.dash_speed

class AsepritePlayer:
    def __init__(self, file_path):
        self.frames = []; self.tags = {}
        self.file_name = os.path.basename(file_path)
        self.export_and_load(file_path)
        
        # Physics
        self.x, self.y = 400, 500; self.vx = self.vy = 0
        self.grounded = False; self.jumps_left = 2; self.facing_right = True
        self.zoom = 3.0; self.dash_speed = 35.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 3.0
        
        # World & Camera
        self.cam_x, self.cam_y = 400, 300
        self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20)]
        self.bg_img = None; self.bg_offset = [0, 0]; self.bg_zoom = 1.0; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]
        
        # Mapping
        self.tag_list = sorted(list(self.tags.keys()))
        self.mappings = { "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ATTACK 1": [], "ATTACK 2": [], "ATTACK 3": [], "ATTACK 4": [], "JUMP ATTACK": [], "DASH": [], "SKILL": [], "HURT": [] }
        self.auto_map_tags()
        
        self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0
        self.active_action_slot = None; self.active_tag = None; self.action_queue = []; self.action_end_frame = -1
        self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0
        
        # AI Management
        self.ai_list = [AseAI(self)]
        self.target_ai_count = 1

    def auto_map_tags(self):
        suffix = re.compile(r"(_|\s)?\(?loop\)?", re.IGNORECASE)
        for slot in self.mappings.keys():
            clean = slot.replace(" 1", "").replace(" 2", "").replace(" 3", "").replace(" 4", "").lower()
            for t in self.tag_list:
                if suffix.sub("", t).lower() == clean or (clean=="walk" and suffix.sub("", t).lower()=="move"):
                    if t not in self.mappings[slot]: self.mappings[slot].append(t)

    def export_and_load(self, file_path):
        try:
            cmd = [ASEPRITE_PATH, "-b", file_path, "--trim", "--sheet", "temp.png", "--data", "temp.json", "--format", "json-array", "--list-tags"]
            subprocess.run(cmd, check=True, capture_output=True)
            sheet = pygame.image.load("temp.png").convert_alpha()
            with open("temp.json", 'r') as f: data = json.load(f)
            self.orig_w, self.orig_h = data['frames'][0]['sourceSize']['w'], data['frames'][0]['sourceSize']['h']
            for f in data['frames']:
                r, s = f['frame'], f['spriteSourceSize']
                surf = pygame.Surface((r['w'], r['h']), pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), (r['x'], r['y'], r['w'], r['h']))
                self.frames.append({'img': surf, 'ox': s['x'] - self.orig_w // 2, 'oy': s['y'] - self.orig_h // 2})
            if 'meta' in data and 'frameTags' in data['meta']:
                for t in data['meta']['frameTags']: self.tags[t['name']] = (t['from'], t['to'])
        except Exception as e: print(f"Error: {e}")

    def trigger_action(self, slot):
        tags = self.mappings.get(slot, [])
        if not tags and slot != "DASH": return # 빈 슬롯 방어 코드 (튕김 방지)
        
        if slot == "DASH" and self.dash_charges > 0:
            self.dash_charges -= 1
            for i in range(2): 
                if self.dash_cooldowns[i] <= 0: self.dash_cooldowns[i] = 90; break
            self.dash_timer = 12; self.vx = self.dash_speed if self.facing_right else -self.dash_speed
            self.vy = 0; self.active_action_slot = "DASH"
            self.action_queue = list(tags); self.play_next_in_queue()
            return
        
        if tags:
            self.active_action_slot = slot; self.action_queue = list(tags); self.play_next_in_queue()

    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag = self.action_queue.pop(0)
            if self.active_tag in self.tags: self.frame_idx, self.action_end_frame = self.tags[self.active_tag]
            else: self.play_next_in_queue()
        else: self.active_tag = None; self.active_action_slot = None

    def update(self, keys, ground_y, play_w, play_h):
        # AI Count Adjustment
        while len(self.ai_list) < self.target_ai_count: self.ai_list.append(AseAI(self))
        while len(self.ai_list) > self.target_ai_count: self.ai_list.pop()

        for i in range(2):
            if self.dash_cooldowns[i] > 0:
                self.dash_cooldowns[i] -= 1
                if self.dash_cooldowns[i] <= 0: self.dash_charges = min(2, self.dash_charges + 1)

        if self.dash_timer > 0:
            self.dash_timer -= 1; self.vy = 0
        else:
            self.vx *= 0.82
            if not self.active_tag:
                if keys[pygame.K_RIGHT]: self.vx = 6.5; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -6.5; self.facing_right = False
            else:
                if "ATTACK" in str(self.active_action_slot):
                    if keys[pygame.K_RIGHT]: self.vx = self.atk_forward_v; self.facing_right = True
                    elif keys[pygame.K_LEFT]: self.vx = -self.atk_forward_v; self.facing_right = False
            self.vy += self.gravity

        self.x += self.vx; self.y += self.vy
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
        
        self.cam_x += (self.x - self.cam_x) * 0.12
        self.cam_y += (self.y - self.cam_y) * 0.12
        if self.combo_reset_timer > 0:
            self.combo_reset_timer -= 1
            if self.combo_reset_timer <= 0: self.combo_step = 0

        if not self.active_tag:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            target_list = self.mappings.get(state, [])
            target = target_list[0] if target_list and target_list[0] in self.tags else None
        else: target = self.active_tag

        if target and target in self.tags:
            t_range = self.tags[target]
            if self.frame_idx < t_range[0] or self.frame_idx > t_range[1]: self.frame_idx = t_range[0]
            self.anim_timer += 1
            if self.anim_timer > 6:
                self.frame_idx += 1
                if self.active_tag and self.frame_idx > self.action_end_frame:
                    if "(loop)" in target.lower(): self.frame_idx = t_range[0]
                    else: self.play_next_in_queue()
                elif self.frame_idx > t_range[1]: self.frame_idx = t_range[0]
                self.anim_timer = 0
        for ai in self.ai_list: ai.update(ground_y)

    def draw_sprite(self, screen, x, y, f_idx, facing_right, cam_x, cam_y, cx, cy):
        if not self.frames: return
        f = self.frames[min(f_idx, len(self.frames)-1)]
        img = f['img']
        sw, sh = int(img.get_width() * self.zoom), int(img.get_height() * self.zoom)
        scaled = pygame.transform.scale(img, (sw, sh))
        ox, oy = f['ox'] * self.zoom, f['oy'] * self.zoom
        if not facing_right: scaled = pygame.transform.flip(scaled, True, False); ox = -ox - sw
        screen.blit(scaled, (int(cx + (x - cam_x) * self.zoom + ox), int(cy + (y - cam_y) * self.zoom + oy)))

    def draw(self, screen, play_w, play_h):
        cx, cy = play_w // 2, play_h // 2
        gx = cx - (self.cam_x % 100) * self.zoom; gy = cy - (self.cam_y % 100) * self.zoom
        for i in range(-10, 20):
            pygame.draw.line(screen, self.grid_color, (gx + i*100*self.zoom, 0), (gx + i*100*self.zoom, play_h), 1)
            pygame.draw.line(screen, self.grid_color, (0, gy + i*100*self.zoom), (play_w, gy + i*100*self.zoom), 1)
        pygame.draw.line(screen, (100, 100, 100), (cx + (0-self.cam_x)*self.zoom, cy + (500-self.cam_y)*self.zoom), (cx + (5000-self.cam_x)*self.zoom, cy + (500-self.cam_y)*self.zoom), 2)
        if self.frames:
            self.draw_sprite(screen, self.x, self.y, self.frame_idx, self.facing_right, self.cam_x, self.cam_y, cx, cy)
            for ai in self.ai_list:
                self.draw_sprite(screen, ai.x, ai.y, ai.frame_idx, ai.facing_right, self.cam_x, self.cam_y, cx, cy)
                adx, ady = (ai.x - self.cam_x)*self.zoom, (ai.y - self.cam_y)*self.zoom
                if abs(adx) > play_w//2 or abs(ady) > play_h//2:
                    angle = math.atan2(ady, adx); px = cx + math.cos(angle)*(play_w//2-40); py = cy + math.sin(angle)*(play_h//2-40)
                    pygame.draw.circle(screen, (220, 38, 38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(angle)*8, py-math.sin(angle)*8), 2)

def main():
    pygame.init(); screen = pygame.display.set_mode((1300, 850), pygame.RESIZABLE)
    pygame.display.set_caption("Aseprite Pro Master v11"); clock = pygame.time.Clock(); player = None; selected_slot = None; show_settings = False
    slot_scroll = 0; tag_scroll = 0; font_s = pygame.font.SysFont("Arial", 12); font_b = pygame.font.SysFont("Arial", 14, bold=True)

    while True:
        sw, sh = screen.get_size(); sidebar_w = 400; play_w = sw - sidebar_w; play_h = sh - 40; m_pos = pygame.mouse.get_pos()
        bg_col = player.bg_color if player else [15, 15, 18]
        screen.fill(bg_col); pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh))
        settings_btn = pygame.Rect(play_w - 120, 20, 110, 40); open_btn = pygame.Rect(play_w + 20, 20, sidebar_w - 40, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.DROPFILE: player = AsepritePlayer(event.file)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_w < m_pos[0] < sw:
                    if m_pos[1] < 450:
                        if event.button == 4: slot_scroll = min(0, slot_scroll + 40)
                        if event.button == 5: slot_scroll -= 40
                    else:
                        if event.button == 4: tag_scroll = min(0, tag_scroll + 40)
                        if event.button == 5: tag_scroll -= 40
                if event.button == 1:
                    if settings_btn.collidepoint(m_pos): show_settings = not show_settings
                    if open_btn.collidepoint(m_pos):
                        p = select_file([("Aseprite", "*.aseprite *.ase")])
                        if p: player = AsepritePlayer(p)
                    if player and not show_settings:
                        for i, action in enumerate(player.mappings.keys()):
                            rect = pygame.Rect(play_w + 20, 80 + i*38 + slot_scroll, sidebar_w - 40, 34)
                            if rect.collidepoint(m_pos) and 80 < rect.top < 450: selected_slot = action
                        if selected_slot:
                            for idx, tag in enumerate(player.tag_list):
                                t_rect = pygame.Rect(play_w + 20, 500 + idx*25 + tag_scroll, sidebar_w - 40, 22)
                                if t_rect.collidepoint(m_pos) and t_rect.top >= 480:
                                    if tag in player.mappings[selected_slot]: player.mappings[selected_slot].remove(tag)
                                    else: player.mappings[selected_slot].append(tag)
            if event.type == pygame.KEYDOWN and player:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if player.jumps_left > 0: player.vy = player.jump_power; player.grounded = False; player.jumps_left -= 1
                if event.key == pygame.K_z: player.handle_attack()
                if event.key == pygame.K_x: player.trigger_action("DASH")
                if event.key == pygame.K_c: player.trigger_action("SKILL")
                if event.key == pygame.K_v: player.trigger_action("HURT")
            if event.type == pygame.MOUSEWHEEL and player and m_pos[0] < play_w:
                player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0))

        if player:
            player.update(pygame.key.get_pressed(), 500, play_w, play_h)
            player.draw(screen, play_w, play_h)
            # HUD/Settings
            pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh))
            if show_settings:
                pygame.draw.rect(screen, (35, 35, 40), (play_w, 0, sidebar_w, sh))
                pygame.draw.line(screen, (59, 130, 246), (play_w, 0), (play_w, sh), 2)
                screen.blit(font_b.render("SETTINGS PANEL", True, (59, 130, 246)), (play_w + 20, 20))
                # AI Count Slider
                screen.blit(font_s.render(f"AI Count: {player.target_ai_count}", True, (200,200,200)), (play_w + 20, 60))
                ai_sl = pygame.Rect(play_w + 20, 80, sidebar_w - 40, 8); pygame.draw.rect(screen, (60, 60, 70), ai_sl)
                pygame.draw.circle(screen, (59, 130, 246), (int(play_w + 20 + (player.target_ai_count/10)*(sidebar_w-40)), 84), 8)
                if pygame.mouse.get_pressed()[0] and ai_sl.inflate(0, 20).collidepoint(m_pos):
                    player.target_ai_count = int((m_pos[0] - (play_w+20))/(sidebar_w-40)*10)
                # Other settings (Atk, Grid etc.)
                screen.blit(font_s.render(f"Atk Forward Power: {player.atk_forward_v:.1f}", True, (200,200,200)), (play_w + 20, 110))
                at_sl = pygame.Rect(play_w + 20, 130, sidebar_w - 40, 8); pygame.draw.rect(screen, (60, 60, 70), at_sl)
                pygame.draw.circle(screen, (220, 38, 38), (int(play_w + 20 + (player.atk_forward_v/15)*(sidebar_w-40)), 134), 8)
                if pygame.mouse.get_pressed()[0] and at_sl.inflate(0, 20).collidepoint(m_pos):
                    player.atk_forward_v = (m_pos[0] - (play_w+20))/(sidebar_w-40)*15
            else:
                # Normal Mapping Slots
                slot_clip = pygame.Surface((sidebar_w - 20, 380), pygame.SRCALPHA)
                for i, action in enumerate(player.mappings.keys()):
                    rect = pygame.Rect(10, i*38 + slot_scroll, sidebar_w - 40, 34)
                    col = (59, 130, 246) if selected_slot == action else (45, 45, 50)
                    pygame.draw.rect(slot_clip, col, rect, border_radius=5)
                    slot_clip.blit(font_b.render(action, True, (255,255,255)), (rect.x+10, rect.y+3))
                    tags_str = ", ".join(player.mappings[action])
                    slot_clip.blit(font_s.render(f"-> {tags_str[:40]}", True, (200,200,200)), (rect.x+10, rect.y+18))
                screen.blit(slot_clip, (play_w + 10, 85))
            pygame.draw.rect(screen, (30, 30, 35), (0, sh-40, play_w, 40))
            guide = "Move: Arrows | Jump: Space | Attack: Z | Dash: X | Skill: C | Zoom: Wheel"
            screen.blit(font_s.render(guide, True, (255, 255, 255)), (20, sh-25))
        pygame.draw.rect(screen, (50, 50, 60), settings_btn, border_radius=5); screen.blit(font_b.render("⚙ SETTINGS", True, (255,255,255)), (settings_btn.x+15, settings_btn.y+10))
        pygame.draw.rect(screen, (59, 130, 246), open_btn, border_radius=5); screen.blit(font_b.render("OPEN ASEPRITE", True, (255,255,255)), (open_btn.centerx-55, open_btn.y+12))
        pygame.display.flip(); clock.tick(60)
if __name__ == "__main__":
    main()
