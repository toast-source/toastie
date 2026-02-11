import pygame
import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog

ASEPRITE_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe"

def select_file(ftypes):
    try:
        root = tk.Tk(); root.withdraw()
        path = filedialog.askopenfilename(filetypes=ftypes)
        root.destroy()
        return path
    except: return None

class AsepritePlayer:
    def __init__(self, file_path):
        self.frames = []; self.tags = {}
        self.file_name = os.path.basename(file_path)
        self.export_and_load(file_path)
        
        # Physics
        self.x, self.y = 400, 500
        self.vx = self.vy = 0
        self.grounded = True
        self.jumps_left = 2
        self.facing_right = True
        self.zoom = 3.0
        self.dash_speed = 25.0
        
        # Background Image Settings
        self.bg_img = None
        self.bg_offset = [0, 0]
        self.bg_zoom = 1.0
        self.bg_color = [15, 15, 18]
        
        # Playback
        self.frame_idx = 0
        self.anim_timer = 0
        self.tag_list = sorted(list(self.tags.keys()))
        self.mappings = {
            "IDLE": [], "WALK": [], "JUMP": [], "FALL": [],
            "ATTACK 1": [], "ATTACK 2": [], "ATTACK 3": [], "ATTACK 4": [],
            "JUMP ATTACK": [], "DASH": [], "SKILL": [], "HURT": []
        }
        self.combo_step = 0
        self.combo_reset_timer = 0
        self.active_action_slot = None
        self.action_queue = []
        self.active_tag = None
        self.action_end_frame = -1

    def export_and_load(self, file_path):
        try:
            cmd = [ASEPRITE_PATH, "-b", file_path, "--trim", "--sheet", "temp.png",
                   "--data", "temp.json", "--format", "json-array", "--list-tags"]
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
        except Exception as e: print(f"Load Error: {e}")

    def handle_attack(self):
        if not self.grounded: self.trigger_action("JUMP ATTACK")
        else:
            self.combo_reset_timer = 60
            self.trigger_action(f"ATTACK {self.combo_step + 1}")
            self.combo_step = (self.combo_step + 1) % 4

    def trigger_action(self, slot):
        tags = self.mappings.get(slot, [])
        if tags or slot == "DASH": # Dash can always trigger if speed is set
            self.active_action_slot = slot
            self.action_queue = list(tags)
            self.play_next_in_queue()
            if slot == "DASH": self.vx = self.dash_speed if self.facing_right else -self.dash_speed

    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag = self.action_queue.pop(0)
            if self.active_tag in self.tags: self.frame_idx, self.action_end_frame = self.tags[self.active_tag]
            else: self.play_next_in_queue()
        else: self.active_tag = None; self.active_action_slot = None

    def update(self, keys, ground_y):
        self.vx *= 0.85
        if not self.active_tag:
            if keys[pygame.K_RIGHT]: self.vx = 6; self.facing_right = True
            elif keys[pygame.K_LEFT]: self.vx = -6; self.facing_right = False
        
        self.vy += 0.8
        self.x += self.vx; self.y += self.vy
        if self.y > ground_y: self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
        
        if self.combo_reset_timer > 0:
            self.combo_reset_timer -= 1
            if self.combo_reset_timer <= 0: self.combo_step = 0

        if not self.active_tag:
            state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
            mapped = self.mappings.get(state, [])
            target = mapped[0] if mapped and mapped[0] in self.tags else None
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

    def draw(self, screen, play_w, screen_h):
        # 1. Draw Background Image
        if self.bg_img:
            bw, bh = int(self.bg_img.get_width() * self.bg_zoom), int(self.bg_img.get_height() * self.bg_zoom)
            b_scaled = pygame.transform.scale(self.bg_img, (bw, bh))
            screen.blit(b_scaled, (play_w//2 + self.bg_offset[0] - bw//2, screen_h//2 + self.bg_offset[1] - bh//2))

        # 2. Draw Sprite
        if not self.frames: return
        f = self.frames[min(self.frame_idx, len(self.frames)-1)]
        img = f['img']
        sw, sh = int(img.get_width() * self.zoom), int(img.get_height() * self.zoom)
        scaled = pygame.transform.scale(img, (sw, sh))
        ox, oy = f['ox'] * self.zoom, f['oy'] * self.zoom
        if not self.facing_right: scaled = pygame.transform.flip(scaled, True, False); ox = -ox - sw
        screen.blit(scaled, (int(self.x + ox), int(self.y + oy)))
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), 4)

def main():
    pygame.init()
    screen = pygame.display.set_mode((1250, 850), pygame.RESIZABLE)
    pygame.display.set_caption("Aseprite Pro Master v5")
    clock = pygame.time.Clock()
    
    player = None; selected_slot = None; show_settings = False
    slot_scroll = 0; tag_scroll = 0
    font_s = pygame.font.SysFont("Arial", 12); font_b = pygame.font.SysFont("Arial", 14, bold=True)

    while True:
        sw, sh = screen.get_size()
        sidebar_w = 400; play_w = sw - sidebar_w; ground_y = sh - 200
        m_pos = pygame.mouse.get_pos()
        
        bg = player.bg_color if player else [15, 15, 18]
        screen.fill(bg)
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)) # Sidebar
        
        settings_btn = pygame.Rect(play_w - 110, 20, 100, 35)
        open_btn = pygame.Rect(play_w + 20, 20, sidebar_w - 40, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE: screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.DROPFILE: player = AsepritePlayer(event.file)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Scroll handling based on mouse position
                if play_w < m_pos[0] < sw:
                    if m_pos[1] < 500: # Slot Area
                        if event.button == 4: slot_scroll = min(0, slot_scroll + 40)
                        if event.button == 5: slot_scroll -= 40
                    else: # Tag List Area
                        if event.button == 4: tag_scroll = min(0, tag_scroll + 40)
                        if event.button == 5: tag_scroll -= 40
                
                if event.button == 1:
                    if settings_btn.collidepoint(m_pos): show_settings = not show_settings
                    if open_btn.collidepoint(m_pos):
                        p = select_file([("Aseprite", "*.aseprite *.ase")])
                        if p: player = AsepritePlayer(p)
                    
                    if player and not show_settings:
                        # Mapping Slot
                        for i, action in enumerate(player.mappings.keys()):
                            rect = pygame.Rect(play_w + 20, 100 + i*42 + slot_scroll, sidebar_w - 40, 38)
                            if rect.collidepoint(m_pos) and 80 < rect.top < 500: selected_slot = action
                        # Tag Item
                        if selected_slot:
                            for idx, tag in enumerate(player.tag_list):
                                t_rect = pygame.Rect(play_w + 20, 550 + idx*25 + tag_scroll, sidebar_w - 40, 22)
                                if t_rect.collidepoint(m_pos) and t_rect.top >= 540:
                                    if tag in player.mappings[selected_slot]: player.mappings[selected_slot].remove(tag)
                                    else: player.mappings[selected_slot].append(tag)
                
                if event.button == 3 and player:
                    for i, action in enumerate(player.mappings.keys()):
                        if pygame.Rect(play_w+20, 100+i*42+slot_scroll, sidebar_w-40, 38).collidepoint(m_pos): player.mappings[action] = []

            if event.type == pygame.KEYDOWN and player:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if player.jumps_left > 0: player.vy = -16; player.grounded = False; player.jumps_left -= 1
                if event.key == pygame.K_z: player.handle_attack()
                if event.key == pygame.K_x: player.trigger_action("DASH") # Cancels any current action
                if event.key == pygame.K_c: player.trigger_action("SKILL")
                if event.key == pygame.K_v: player.trigger_action("HURT")

            if event.type == pygame.MOUSEWHEEL and player and m_pos[0] < play_w:
                player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0))

        if player:
            player.update(pygame.key.get_pressed(), ground_y)
            player.draw(screen, play_w, sh)
            
            # Sidebar UI
            pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh))
            screen.blit(font_b.render("MAPPING SLOTS", True, (150,150,150)), (play_w + 20, 70))
            slot_clip = pygame.Surface((sidebar_w - 20, 400), pygame.SRCALPHA)
            for i, action in enumerate(player.mappings.keys()):
                rect = pygame.Rect(10, i*42 + slot_scroll, sidebar_w - 40, 38)
                col = (59, 130, 246) if selected_slot == action else (45, 45, 50)
                pygame.draw.rect(slot_clip, col, rect, border_radius=5)
                slot_clip.blit(font_b.render(action, True, (255,255,255)), (rect.x+10, rect.y+3))
                tags_str = ", ".join(player.mappings[action])
                slot_clip.blit(font_s.render(f"-> {tags_str[:35]}", True, (200,200,200)), (rect.x+10, rect.y+20))
            screen.blit(slot_clip, (play_w + 10, 100))

            # Tag List
            list_area = pygame.Rect(play_w + 15, 540, sidebar_w - 30, sh - 555)
            pygame.draw.rect(screen, (20, 20, 25), list_area, border_radius=5)
            screen.blit(font_b.render(f"TAG LIST FOR {selected_slot}", True, (100,100,100)), (play_w + 20, 520))
            clip_surf = pygame.Surface((sidebar_w - 40, sh - 560), pygame.SRCALPHA)
            for idx, tag in enumerate(player.tag_list):
                t_rect = pygame.Rect(0, idx*25 + tag_scroll, sidebar_w - 40, 22)
                is_mapped = selected_slot and tag in player.mappings[selected_slot]
                hvr = t_rect.move(play_w+20, 550).collidepoint(m_pos)
                t_col = (59, 130, 246) if is_mapped else ((70, 70, 80) if hvr else (40, 40, 45))
                pygame.draw.rect(clip_surf, t_col, t_rect, border_radius=3)
                clip_surf.blit(font_s.render(tag, True, (255,255,255)), (t_rect.x+10, t_rect.y+4))
            screen.blit(clip_surf, (play_w + 20, 550))

            if show_settings:
                pygame.draw.rect(screen, (35, 35, 40), (play_w, 0, sidebar_w, sh))
                pygame.draw.line(screen, (59, 130, 246), (play_w, 0), (play_w, sh), 2)
                screen.blit(font_b.render("PROGRAM SETTINGS", True, (59, 130, 246)), (play_w + 20, 20))
                # BG Image Button
                bg_btn = pygame.Rect(play_w + 20, 60, 150, 35)
                pygame.draw.rect(screen, (100, 100, 110), bg_btn, border_radius=5)
                screen.blit(font_b.render("LOAD BG IMG", True, (255,255,255)), (bg_btn.x+30, bg_btn.y+8))
                if pygame.mouse.get_pressed()[0] and bg_btn.collidepoint(m_pos):
                    p = select_file([("Image", "*.png *.jpg *.bmp")])
                    if p: player.bg_img = pygame.image.load(p).convert_alpha()
                
                # BG Controls
                for i, lab in enumerate(["BG-X", "BG-Y", "BG-SCALE"]):
                    screen.blit(font_s.render(lab, True, (150,150,150)), (play_w+20, 110+i*55))
                    sl = pygame.Rect(play_w+20, 130+i*55, sidebar_w-40, 8)
                    pygame.draw.rect(screen, (60, 60, 70), sl)
                    val = player.bg_offset[0] if i==0 else (player.bg_offset[1] if i==1 else player.bg_zoom)
                    norm = (val + 500)/1000 if i<2 else val/5
                    pygame.draw.circle(screen, (59, 130, 246), (int(play_w+20 + norm*(sidebar_w-40)), 134+i*55), 8)
                    if pygame.mouse.get_pressed()[0] and sl.inflate(0, 20).collidepoint(m_pos):
                        new_v = (m_pos[0] - (play_w+20))/(sidebar_w-40)
                        if i==0: player.bg_offset[0] = new_v*1000 - 500
                        elif i==1: player.bg_offset[1] = new_v*1000 - 500
                        else: player.bg_zoom = max(0.1, new_v*5)

            screen.blit(font_b.render(f"DASH CANCEL ENABLED | ACTION: {player.active_action_slot or 'AUTO'}", True, (0,255,0)), (10, 10))
        
        pygame.draw.rect(screen, (50, 50, 60), settings_btn, border_radius=5)
        screen.blit(font_b.render("SETTINGS", True, (255,255,255)), (settings_btn.x+15, settings_btn.y+8))
        pygame.draw.rect(screen, (59, 130, 246), open_btn, border_radius=5)
        screen.blit(font_b.render("OPEN ASEPRITE", True, (255,255,255)), (open_btn.centerx-55, open_btn.y+12))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
