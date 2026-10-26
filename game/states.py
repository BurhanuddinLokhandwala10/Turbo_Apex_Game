"""
Game State Machine Architecture
===============================
Implements distinct state handlers for:
- MAIN_MENU
- MAP_SELECTION
- HOW_TO_PLAY
- COUNTDOWN & RACING
- PAUSED
- RESULTS
"""

import math
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, UI_BG_DARK, UI_PANEL_BG, UI_PANEL_BORDER,
    UI_ACCENT_CYAN, UI_ACCENT_GOLD, UI_ACCENT_RED, UI_ACCENT_GREEN, UI_TEXT_MUTED,
    COLOR_WHITE, COLOR_BLACK, TOTAL_LAPS, COUNTDOWN_SECONDS, CAR_COLORS
)
from game.player import Player
from game.ai import AICar
from game.track import Track
from game.camera import Camera
from game.renderer import Renderer
from game.hud import HUD
from game.collision import CollisionSystem
from game.fuel import FuelManager
from game.sound import SoundManager
from maps import MAP_CATALOG

class BaseState:
    """Abstract interface for all game states."""

    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass

# =============================================================================
# 1. MAIN MENU STATE
# =============================================================================

class MainMenuState(BaseState):
    """Arcade Title Screen & Mode Selection."""

    def __init__(self, game):
        super().__init__(game)
        self.options = [
            ("SINGLE PLAYER", "single_player"),
            ("TWO PLAYERS", "two_players"),
            ("HOW TO PLAY", "how_to_play"),
            ("EXIT", "exit")
        ]
        self.selected_index = 0
        self.font_title = pygame.font.SysFont("Impact, Arial Black", 68)
        self.font_sub = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_btn = pygame.font.SysFont("Impact, Arial Black", 28)
        self.sm = SoundManager.get_instance()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_option()
        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            btn_w, btn_h = 400, 56
            btn_x = (SCREEN_WIDTH - btn_w) // 2
            for i in range(len(self.options)):
                by = 280 + i * 72
                if btn_x <= mx <= btn_x + btn_w and by <= my <= by + btn_h:
                    if self.selected_index != i:
                        self.selected_index = i
                        self.sm.play("click")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            btn_w, btn_h = 400, 56
            btn_x = (SCREEN_WIDTH - btn_w) // 2
            for i in range(len(self.options)):
                by = 280 + i * 72
                if btn_x <= mx <= btn_x + btn_w and by <= my <= by + btn_h:
                    self.selected_index = i
                    self._activate_option()
                    return
            self._activate_option()

    def _activate_option(self):
        target = self.options[self.selected_index][1]
        self.sm.play("click")
        if target == "single_player":
            self.game.mode = "SINGLE"
            self.game.change_state("MAP_SELECTION")
        elif target == "two_players":
            self.game.mode = "TWO_PLAYER"
            self.game.change_state("MAP_SELECTION")
        elif target == "how_to_play":
            self.game.change_state("HOW_TO_PLAY")
        elif target == "exit":
            self.game.running = False

    def render(self, screen):
        screen.fill(UI_BG_DARK)

        # Dynamic Cyber Grid Background Lines (Computer Graphics Perspective Lines)
        t = pygame.time.get_ticks() / 1000.0
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        horizon_y = 230
        for x in range(0, SCREEN_WIDTH + 60, 80):
            # Perspective rays radiating from horizon center
            cx = SCREEN_WIDTH // 2
            pygame.draw.line(grid_surf, (30, 45, 75, 70), (cx, horizon_y), (x, SCREEN_HEIGHT), 1)
        for gy in range(horizon_y + 10, SCREEN_HEIGHT, 40):
            scale_y = (gy - horizon_y) / (SCREEN_HEIGHT - horizon_y)
            pygame.draw.line(grid_surf, (30, 50, 85, int(40 + scale_y * 110)), (0, gy), (SCREEN_WIDTH, gy), 1)
        screen.blit(grid_surf, (0, 0))

        # Glowing Title Header
        title_txt = self.font_title.render("TURBO APEX", True, UI_ACCENT_CYAN)
        shadow_txt = self.font_title.render("TURBO APEX", True, (10, 15, 25))
        tx = (SCREEN_WIDTH - title_txt.get_width()) // 2
        screen.blit(shadow_txt, (tx + 4, 94))
        screen.blit(title_txt, (tx, 90))

        sub_txt = self.font_sub.render("ADVANCED COMPUTER GRAPHICS RACING SIMULATION", True, UI_ACCENT_GOLD)
        screen.blit(sub_txt, ((SCREEN_WIDTH - sub_txt.get_width()) // 2, 175))

        # Menu Buttons
        btn_w, btn_h = 400, 56
        btn_x = (SCREEN_WIDTH - btn_w) // 2
        for idx, (label, _) in enumerate(self.options):
            by = 280 + idx * 72
            is_active = (idx == self.selected_index)

            # Button Box
            box_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            bg_col = (25, 35, 55, 240) if is_active else (18, 22, 34, 180)
            border_col = UI_ACCENT_CYAN if is_active else UI_PANEL_BORDER
            pygame.draw.rect(box_surf, bg_col, (0, 0, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(box_surf, border_col, (0, 0, btn_w, btn_h), 2 if is_active else 1, border_radius=8)

            if is_active:
                # Left accent indicator
                pygame.draw.rect(box_surf, UI_ACCENT_CYAN, (0, 0, 8, btn_h), border_top_left_radius=8, border_bottom_left_radius=8)

            screen.blit(box_surf, (btn_x, by))

            # Label
            txt_col = COLOR_WHITE if is_active else UI_TEXT_MUTED
            lbl = self.font_btn.render(label, True, txt_col)
            screen.blit(lbl, ((SCREEN_WIDTH - lbl.get_width()) // 2, by + (btn_h - lbl.get_height()) // 2))

        # Footer Hint
        hint = self.font_sub.render("UP / DOWN / W / S: Navigate   |   ENTER / SPACE: Select", True, (100, 115, 140))
        screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, SCREEN_HEIGHT - 45))

# =============================================================================
# 2. MAP SELECTION STATE
# =============================================================================

class MapSelectionState(BaseState):
    """Track Select Screen with visual previews and difficulty stats."""

    def __init__(self, game):
        super().__init__(game)
        self.map_classes = MAP_CATALOG
        self.selected_index = 0
        self.font_header = pygame.font.SysFont("Impact, Arial Black", 52)
        self.font_name = pygame.font.SysFont("Impact, Arial Black", 26)
        self.font_body = pygame.font.SysFont("Arial", 14)
        self.font_sub = pygame.font.SysFont("Arial", 16, bold=True)
        self.sm = SoundManager.get_instance()

        # Temporary instances to display track info
        self.previews = [cls() for cls in self.map_classes]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_index = (self.selected_index - 1) % len(self.previews)
                self.sm.play("click")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_index = (self.selected_index + 1) % len(self.previews)
                self.sm.play("click")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm_selection()
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state("MAIN_MENU")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            card_w = 340
            card_gap = 35
            total_w = len(self.previews) * card_w + (len(self.previews) - 1) * card_gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            for i in range(len(self.previews)):
                cx = start_x + i * (card_w + card_gap)
                if cx <= mx <= cx + card_w and 180 <= my <= 560:
                    self.selected_index = i
                    self._confirm_selection()
                    break

    def _confirm_selection(self):
        self.sm.play("click")
        selected_map_class = self.map_classes[self.selected_index]
        self.game.selected_map_class = selected_map_class
        self.game.start_race()

    def render(self, screen):
        screen.fill(UI_BG_DARK)

        # Header Title
        title = self.font_header.render("SELECT CHAMPIONSHIP TRACK", True, UI_ACCENT_CYAN)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 50))

        mode_badge = f"MODE: {'TWO PLAYER SPLIT-SCREEN' if self.game.mode == 'TWO_PLAYER' else 'SINGLE PLAYER'}"
        badge_txt = self.font_sub.render(mode_badge, True, UI_ACCENT_GOLD)
        screen.blit(badge_txt, ((SCREEN_WIDTH - badge_txt.get_width()) // 2, 120))

        # Track Cards Layout
        card_w, card_h = 350, 400
        card_gap = 35
        total_w = len(self.previews) * card_w + (len(self.previews) - 1) * card_gap
        start_x = (SCREEN_WIDTH - total_w) // 2

        for i, prev in enumerate(self.previews):
            cx = start_x + i * (card_w + card_gap)
            cy = 175
            is_active = (i == self.selected_index)

            # Card Backdrop
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_bg = (25, 34, 52, 240) if is_active else (18, 22, 32, 190)
            border_col = UI_ACCENT_CYAN if is_active else UI_PANEL_BORDER
            pygame.draw.rect(card_surf, card_bg, (0, 0, card_w, card_h), border_radius=10)
            pygame.draw.rect(card_surf, border_col, (0, 0, card_w, card_h), 3 if is_active else 1, border_radius=10)

            # Visual Map Preview Box (Render scaled snapshot of sky & minimap)
            pv_rect = pygame.Rect(15, 15, card_w - 30, 150)
            if prev.sky_surface:
                scaled_sky = pygame.transform.smoothscale(prev.sky_surface, (pv_rect.width, pv_rect.height))
                card_surf.blit(scaled_sky, pv_rect)
            pygame.draw.rect(card_surf, (50, 60, 80), pv_rect, 1, border_radius=6)

            # Mini track loop overlay inside preview box
            if prev.minimap_points:
                pts = [
                    (pv_rect.x + int(px * pv_rect.width), pv_rect.y + int(py * pv_rect.height))
                    for px, py in prev.minimap_points
                ]
                pygame.draw.lines(card_surf, (255, 255, 255, 220), True, pts, 3)

            screen.blit(card_surf, (cx, cy))

            # Track Name
            t_name = self.font_name.render(prev.name, True, COLOR_WHITE if is_active else UI_TEXT_MUTED)
            screen.blit(t_name, (cx + 20, cy + 180))

            # Difficulty & Laps
            diff_col = UI_ACCENT_RED if "HARD" in prev.difficulty else UI_ACCENT_GREEN
            diff_lbl = self.font_sub.render(f"DIFFICULTY: {prev.difficulty}", True, diff_col)
            screen.blit(diff_lbl, (cx + 20, cy + 220))

            # Description
            desc_lines = self._wrap_text(prev.preview_desc, self.font_body, card_w - 40)
            for dy_idx, line in enumerate(desc_lines):
                line_surf = self.font_body.render(line, True, UI_TEXT_MUTED)
                screen.blit(line_surf, (cx + 20, cy + 255 + dy_idx * 20))

            # Best Record Time
            time_lbl = self.font_sub.render(f"BEST TIME: {prev.best_time}", True, UI_ACCENT_GOLD)
            screen.blit(time_lbl, (cx + 20, cy + 345))

        # Bottom Hints
        hint = self.font_sub.render("LEFT / RIGHT / A / D: Choose Track   |   ENTER: Start Race   |   ESC: Back", True, (110, 125, 150))
        screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, SCREEN_HEIGHT - 45))

    def _wrap_text(self, text, font, max_w):
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

# =============================================================================
# 3. HOW TO PLAY STATE
# =============================================================================

class HowToPlayState(BaseState):
    """Controls guide and gameplay mechanics explanation."""

    def __init__(self, game):
        super().__init__(game)
        self.font_header = pygame.font.SysFont("Impact, Arial Black", 50)
        self.font_title = pygame.font.SysFont("Impact, Arial Black", 24)
        self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 15)
        self.sm = SoundManager.get_instance()

    def handle_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.sm.play("click")
            self.game.change_state("MAIN_MENU")

    def render(self, screen):
        screen.fill(UI_BG_DARK)

        header = self.font_header.render("HOW TO PLAY & CONTROLS", True, UI_ACCENT_CYAN)
        screen.blit(header, ((SCREEN_WIDTH - header.get_width()) // 2, 45))

        panel_w = 560
        panel_h = 490

        # LEFT PANEL: SINGLE PLAYER CONTROLS
        self._render_panel(screen, 60, 125, panel_w, panel_h, "SINGLE PLAYER (DUAL SCHEME)", [
            ("ACCELERATE", "W  or  UP ARROW"),
            ("BRAKE / REVERSE", "S  or  DOWN ARROW"),
            ("STEER LEFT", "A  or  LEFT ARROW"),
            ("STEER RIGHT", "D  or  RIGHT ARROW"),
            ("SWITCH CAMERA", "C (Normal / Front / Extended)"),
            ("PAUSE GAME", "ESC")
        ], note="Both WASD and Arrow Keys work at the same time in Single Player!")

        # RIGHT PANEL: TWO PLAYER SPLIT-SCREEN CONTROLS
        self._render_panel(screen, 660, 125, panel_w, panel_h, "TWO PLAYERS (SPLIT-SCREEN)", [
            ("PLAYER 1 (TOP HALF)", "WASD  +  C (Camera)"),
            ("  - Accelerate / Brake", "W  /  S"),
            ("  - Steer Left / Right", "A  /  D"),
            ("PLAYER 2 (BOTTOM HALF)", "ARROW KEYS  +  M/V (Camera)"),
            ("  - Accelerate / Brake", "UP  /  DOWN"),
            ("  - Steer Left / Right", "LEFT  /  RIGHT"),
            ("PAUSE GAME", "ESC")
        ], note="True horizontal split-screen with independent cameras and fuel!")

        # Bottom Instructions
        hint = self.font_bold.render("PRESS ANY KEY OR CLICK TO RETURN TO MENU", True, UI_ACCENT_GOLD)
        screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, SCREEN_HEIGHT - 55))

    def _render_panel(self, screen, x, y, w, h, title, items, note=""):
        p_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        p_surf.fill((20, 26, 40, 220))
        pygame.draw.rect(p_surf, UI_PANEL_BORDER, (0, 0, w, h), 1, border_radius=8)
        screen.blit(p_surf, (x, y))

        t_lbl = self.font_title.render(title, True, UI_ACCENT_GOLD)
        screen.blit(t_lbl, (x + 24, y + 20))
        pygame.draw.line(screen, UI_PANEL_BORDER, (x + 24, y + 55), (x + w - 24, y + 55), 1)

        cur_y = y + 75
        for action, key in items:
            act_txt = self.font_body.render(action, True, UI_TEXT_MUTED)
            key_txt = self.font_bold.render(key, True, COLOR_WHITE)
            screen.blit(act_txt, (x + 24, cur_y))
            screen.blit(key_txt, (x + 230, cur_y))
            cur_y += 38

        if note:
            pygame.draw.line(screen, UI_PANEL_BORDER, (x + 24, cur_y + 10), (x + w - 24, cur_y + 10), 1)
            note_txt = self.font_body.render(note, True, UI_ACCENT_CYAN)
            screen.blit(note_txt, (x + 24, cur_y + 25))

# =============================================================================
# 4. RACING & COUNTDOWN STATE
# =============================================================================

class RacingState(BaseState):
    """Active race simulation handling physics, AI, split-screen, and HUDs."""

    def __init__(self, game):
        super().__init__(game)
        self.track = game.track
        self.players = game.players
        self.ai_cars = game.ai_cars
        self.all_cars = [p.car for p in self.players] + [ai.car for ai in self.ai_cars]

        self.renderer = Renderer()
        self.hud = HUD()
        self.sm = SoundManager.get_instance()

        self.countdown_timer = COUNTDOWN_SECONDS
        self.countdown_played = {3: False, 2: False, 1: False, 0: False}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("PAUSED")
            elif event.key == pygame.K_c:
                # Cycle Player 1 Camera
                self.players[0].cycle_camera()
                self.game.cameras[0].apply_preset(self.players[0].camera_mode)
            elif event.key in (pygame.K_v, pygame.K_m) and len(self.players) > 1:
                # Cycle Player 2 Camera
                self.players[1].cycle_camera()
                self.game.cameras[1].apply_preset(self.players[1].camera_mode)
            elif event.key == pygame.K_r:
                # Quick restart race
                self.game.start_race()

    def update(self, dt):
        # 1. Player Input Handling
        keys = pygame.key.get_pressed()
        for p in self.players:
            p.handle_input(keys)
            p.update_popups(dt)

        # 2. Starting Countdown Handling
        if self.countdown_timer > 0.0:
            self.countdown_timer -= dt
            # Audio beeps (1.6s, 0.8s, 0.0s, GO!)
            if self.countdown_timer > 1.6 and not self.countdown_played[3]:
                self.sm.play("beep")
                self.countdown_played[3] = True
            elif 0.8 < self.countdown_timer <= 1.6 and not self.countdown_played[2]:
                self.sm.play("beep")
                self.countdown_played[2] = True
            elif 0.0 < self.countdown_timer <= 0.8 and not self.countdown_played[1]:
                self.sm.play("beep")
                self.countdown_played[1] = True
            elif self.countdown_timer <= 0.0 and not self.countdown_played[0]:
                self.sm.play("go")
                self.countdown_played[0] = True

            # Allow steering response during countdown so players feel immediate control, but freeze speed
            for p in self.players:
                p.car.speed = 0.0
                if p.car.steer_left_input:
                    p.car.steer_angle = -12.0
                elif p.car.steer_right_input:
                    p.car.steer_angle = 12.0
                else:
                    p.car.steer_angle = 0.0
            return

        # 3. AI Opponent Updates
        for ai in self.ai_cars:
            ai.update_ai(dt, self.track, self.all_cars)

        # 4. Player Vehicle Physics Updates
        for p in self.players:
            cur_seg = self.track.get_segment_at(p.car.z)
            curve = cur_seg.curve if cur_seg else 0.0
            p.car.update_physics(dt, curve, self.track.total_length)

        # 5. Dynamic Fuel Pickup Respawns
        FuelManager.update_pickups(self.track.fuel_pickups, dt)

        # 6. Collision System Queries
        for i, p in enumerate(self.players):
            cam = self.game.cameras[i]
            # Car to Obstacles
            CollisionSystem.check_car_obstacles(p.car, self.track.obstacles, self.sm, cam, p)
            # Car to Fuel Canisters
            CollisionSystem.check_car_fuel_pickups(p.car, self.track.fuel_pickups, self.sm, p)

        # Car to Car Momentum & Separation
        CollisionSystem.check_car_to_car_collisions(self.all_cars, self.sm)

        # 7. Update Real-Time Leaderboard Positions
        self._update_leaderboard_ranks()

        # 8. Update Camera Spring Follow
        for i, p in enumerate(self.players):
            cur_seg = self.track.get_segment_at(p.car.z)
            seg_y = cur_seg.elevation if cur_seg else 0.0
            self.game.cameras[i].update(dt, p.car, seg_y)

        # 9. Race Finish Check
        if self._check_race_finish():
            self.sm.play("victory")
            self.game.change_state("RESULTS")

    def _update_leaderboard_ranks(self):
        """Calculates real-time rank based on (laps * track_length + z)."""
        track_len = self.track.total_length
        scores = []
        for c in self.all_cars:
            score = (c.lap - 1) * track_len + c.z
            scores.append((score, c))
        scores.sort(key=lambda item: item[0], reverse=True)
        for rank, (_, c) in enumerate(scores, start=1):
            c.rank = rank

    def _check_race_finish(self):
        """Checks if race has concluded."""
        if len(self.players) == 1:
            return self.players[0].car.finished
        else:
            return self.players[0].car.finished and self.players[1].car.finished

    def render(self, screen):
        num_players = len(self.players)

        if num_players == 1:
            # -----------------------------------------------------------------
            # SINGLE PLAYER: Fullscreen Viewport (1280 x 720)
            # -----------------------------------------------------------------
            p = self.players[0]
            cam = self.game.cameras[0]
            self.renderer.render_viewport(screen, self.track, cam, p.car, self.all_cars, 0.016)
            self.hud.render(screen, p, self.track, self.all_cars, self.countdown_timer, 0.016)
        else:
            # -----------------------------------------------------------------
            # TWO PLAYER SPLIT SCREEN: True Vertical Viewports (Left & Right: 640 x 720)
            # -----------------------------------------------------------------
            half_w = SCREEN_WIDTH // 2

            # VIEWPORT 1: PLAYER 1 (Left Half: 640 x 720)
            p1 = self.players[0]
            cam1 = self.game.cameras[0]
            surf1 = screen.subsurface(pygame.Rect(0, 0, half_w, SCREEN_HEIGHT))
            self.renderer.render_viewport(surf1, self.track, cam1, p1.car, self.all_cars, 0.016)
            self.hud.render(surf1, p1, self.track, self.all_cars, self.countdown_timer, 0.016)

            # VIEWPORT 2: PLAYER 2 (Right Half: 640 x 720)
            p2 = self.players[1]
            cam2 = self.game.cameras[1]
            surf2 = screen.subsurface(pygame.Rect(half_w, 0, half_w, SCREEN_HEIGHT))
            self.renderer.render_viewport(surf2, self.track, cam2, p2.car, self.all_cars, 0.016)
            self.hud.render(surf2, p2, self.track, self.all_cars, self.countdown_timer, 0.016)

            # High-Tech Center Vertical Split Divider Bar (Neon Cyan accent line)
            pygame.draw.line(screen, (0, 0, 0), (half_w - 2, 0), (half_w - 2, SCREEN_HEIGHT), 5)
            pygame.draw.line(screen, UI_ACCENT_CYAN, (half_w, 0), (half_w, SCREEN_HEIGHT), 2)

# =============================================================================
# 5. PAUSED STATE
# =============================================================================

class PausedState(BaseState):
    """Pause menu modal overlay."""

    def __init__(self, game):
        super().__init__(game)
        self.options = ["RESUME", "RESTART", "MAIN MENU"]
        self.selected_index = 0
        self.font_header = pygame.font.SysFont("Impact, Arial Black", 54)
        self.font_btn = pygame.font.SysFont("Impact, Arial Black", 26)
        self.sm = SoundManager.get_instance()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_option()
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state("RACING")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._activate_option()

    def _activate_option(self):
        choice = self.options[self.selected_index]
        self.sm.play("click")
        if choice == "RESUME":
            self.game.change_state("RACING")
        elif choice == "RESTART":
            self.game.start_race()
        elif choice == "MAIN MENU":
            self.game.change_state("MAIN_MENU")

    def render(self, screen):
        # Render frozen race scene in background
        self.game.states["RACING"].render(screen)

        # Translucent Dark Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 22, 200))
        screen.blit(overlay, (0, 0))

        # Pause Modal Panel
        pw, ph = 400, 320
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        p_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        p_surf.fill((20, 26, 40, 240))
        pygame.draw.rect(p_surf, UI_ACCENT_CYAN, (0, 0, pw, ph), 2, border_radius=10)
        screen.blit(p_surf, (px, py))

        # Title
        hdr = self.font_header.render("PAUSED", True, UI_ACCENT_GOLD)
        screen.blit(hdr, ((SCREEN_WIDTH - hdr.get_width()) // 2, py + 25))

        # Buttons
        bw, bh = 280, 48
        bx = (SCREEN_WIDTH - bw) // 2
        for idx, label in enumerate(self.options):
            by = py + 110 + idx * 60
            is_active = (idx == self.selected_index)

            btn_box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg = (30, 42, 65, 240) if is_active else (22, 28, 42, 180)
            pygame.draw.rect(btn_box, bg, (0, 0, bw, bh), border_radius=6)
            if is_active:
                pygame.draw.rect(btn_box, UI_ACCENT_CYAN, (0, 0, bw, bh), 2, border_radius=6)
            screen.blit(btn_box, (bx, by))

            lbl = self.font_btn.render(label, True, COLOR_WHITE if is_active else UI_TEXT_MUTED)
            screen.blit(lbl, ((SCREEN_WIDTH - lbl.get_width()) // 2, by + (bh - lbl.get_height()) // 2))

# =============================================================================
# 6. RESULTS STATE
# =============================================================================

class ResultsState(BaseState):
    """Post-race standings, podium rankings, and race summary."""

    def __init__(self, game):
        super().__init__(game)
        self.options = ["REPLAY", "SELECT TRACK", "MAIN MENU"]
        self.selected_index = 0
        self.font_header = pygame.font.SysFont("Impact, Arial Black", 56)
        self.font_sub = pygame.font.SysFont("Impact, Arial Black", 28)
        self.font_row = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_btn = pygame.font.SysFont("Impact, Arial Black", 24)
        self.sm = SoundManager.get_instance()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self.sm.play("click")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate_option()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._activate_option()

    def _activate_option(self):
        choice = self.options[self.selected_index]
        self.sm.play("click")
        if choice == "REPLAY":
            self.game.start_race()
        elif choice == "SELECT TRACK":
            self.game.change_state("MAP_SELECTION")
        elif choice == "MAIN MENU":
            self.game.change_state("MAIN_MENU")

    def render(self, screen):
        screen.fill(UI_BG_DARK)

        # Header Title
        p1_won = (self.game.players[0].car.rank == 1)
        if len(self.game.players) == 1:
            verdict = "YOU WIN!" if p1_won else "RACE OVER"
            verdict_col = UI_ACCENT_GREEN if p1_won else UI_ACCENT_GOLD
        else:
            p2_won = (self.game.players[1].car.rank == 1)
            verdict = "PLAYER 1 WINS!" if p1_won else ("PLAYER 2 WINS!" if p2_won else "AI OPPONENT WINS!")
            verdict_col = UI_ACCENT_GREEN if (p1_won or p2_won) else UI_ACCENT_GOLD

        hdr = self.font_header.render(verdict, True, verdict_col)
        screen.blit(hdr, ((SCREEN_WIDTH - hdr.get_width()) // 2, 45))

        # Leaderboard Table Card
        pw, ph = 780, 360
        px = (SCREEN_WIDTH - pw) // 2
        py = 135

        p_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        p_surf.fill((20, 26, 40, 230))
        pygame.draw.rect(p_surf, UI_PANEL_BORDER, (0, 0, pw, ph), 1, border_radius=8)
        screen.blit(p_surf, (px, py))

        # Table Header
        h_pos = self.font_sub.render("RANK", True, UI_ACCENT_CYAN)
        h_car = self.font_sub.render("DRIVER / CAR", True, UI_ACCENT_CYAN)
        h_time = self.font_sub.render("TOTAL TIME", True, UI_ACCENT_CYAN)
        h_lap = self.font_sub.render("BEST LAP", True, UI_ACCENT_CYAN)

        screen.blit(h_pos, (px + 30, py + 20))
        screen.blit(h_car, (px + 150, py + 20))
        screen.blit(h_time, (px + 450, py + 20))
        screen.blit(h_lap, (px + 620, py + 20))
        pygame.draw.line(screen, UI_PANEL_BORDER, (px + 20, py + 60), (px + pw - 20, py + 60), 1)

        # Sorted Standings
        sorted_cars = sorted(self.game.states["RACING"].all_cars, key=lambda c: c.rank)
        for idx, car in enumerate(sorted_cars[:6]):
            ry = py + 75 + idx * 44

            rank_str = f"{idx + 1}"
            rank_col = UI_ACCENT_GOLD if idx == 0 else (UI_ACCENT_CYAN if idx in (1, 2) else COLOR_WHITE)
            r_txt = self.font_row.render(rank_str, True, rank_col)
            screen.blit(r_txt, (px + 45, ry))

            # Driver Name & Color Badge
            pygame.draw.rect(screen, car.color, (px + 140, ry + 2, 14, 14), border_radius=2)
            name_txt = self.font_row.render(car.name, True, COLOR_WHITE)
            screen.blit(name_txt, (px + 165, ry))

            # Total Race Time
            tmins = int(car.total_race_time // 60)
            tsecs = car.total_race_time % 60
            t_str = f"{tmins:02d}:{tsecs:05.2f}"
            t_txt = self.font_row.render(t_str, True, UI_TEXT_MUTED)
            screen.blit(t_txt, (px + 450, ry))

            # Best Lap Time
            if car.best_lap_time:
                lmins = int(car.best_lap_time // 60)
                lsecs = car.best_lap_time % 60
                l_str = f"{lmins:02d}:{lsecs:05.2f}"
            else:
                l_str = "--:--"
            l_txt = self.font_row.render(l_str, True, UI_TEXT_MUTED)
            screen.blit(l_txt, (px + 620, ry))

        # Bottom Action Buttons
        bw, bh = 200, 48
        bgap = 30
        total_bw = len(self.options) * bw + (len(self.options) - 1) * bgap
        start_bx = (SCREEN_WIDTH - total_bw) // 2
        by = 545

        for idx, label in enumerate(self.options):
            bx = start_bx + idx * (bw + bgap)
            is_active = (idx == self.selected_index)

            btn_box = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg = (30, 42, 65, 240) if is_active else (20, 26, 40, 180)
            pygame.draw.rect(btn_box, bg, (0, 0, bw, bh), border_radius=6)
            if is_active:
                pygame.draw.rect(btn_box, UI_ACCENT_CYAN, (0, 0, bw, bh), 2, border_radius=6)
            screen.blit(btn_box, (bx, by))

            lbl = self.font_btn.render(label, True, COLOR_WHITE if is_active else UI_TEXT_MUTED)
            screen.blit(lbl, (bx + (bw - lbl.get_width()) // 2, by + (bh - lbl.get_height()) // 2))
