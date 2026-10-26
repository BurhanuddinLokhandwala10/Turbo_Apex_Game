"""
Heads-Up Display (HUD) & Minimap Radar System
============================================
Renders high-polish arcade dashboard instruments:
- Lap counter, real-time leaderboard rank, race timer & best lap
- Digital speedometer in KM/H with tachometer bar
- Fuel gauge with 10-segment capacity bar and flashing low-fuel warnings
- Camera mode indicator
- Floating text feedback (+20 FUEL, IMPACT!)
- Real-time closed-circuit 2D Minimap showing all player and AI positions
"""

import math
import pygame
from game.settings import (
    COLOR_WHITE, COLOR_BLACK, UI_BG_DARK, UI_ACCENT_CYAN,
    UI_ACCENT_GOLD, UI_ACCENT_RED, UI_ACCENT_GREEN, UI_TEXT_MUTED
)

class HUD:
    """Renders dashboard telemetry and minimap for a specific player viewport."""

    def __init__(self):
        # Fonts
        self.font_large = pygame.font.SysFont("Impact, Arial Black, Arial", 32)
        self.font_medium = pygame.font.SysFont("Impact, Arial Black, Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_tiny = pygame.font.SysFont("Arial", 11, bold=True)
        self.font_countdown = pygame.font.SysFont("Impact, Arial Black, Arial", 64)

    def render(self, surface, player, track, all_cars, countdown_timer, dt):
        """Draws all HUD components for the given player."""
        view_w, view_h = surface.get_size()
        car = player.car
        is_split = (view_w < 700 or view_h < 450)  # Handles vertical and horizontal split-screen

        # 1. Top Telemetry Bar (Laps, Rank, Time, Controls Badge)
        self._render_top_bar(surface, player, car, view_w, is_split)

        # 2. Bottom-Left Gauges (Speedometer & Fuel Bar)
        self._render_gauges(surface, car, view_w, view_h, is_split)

        # 3. Bottom Camera Indicator
        self._render_camera_badge(surface, player, view_w, view_h, is_split)

        # 4. Minimap Circuit Radar (Bottom-Right with Fuel Icons)
        self._render_minimap(surface, player, track, all_cars, view_w, view_h, is_split)

        # 5. Floating Text Popups
        self._render_popups(surface, player, view_w, view_h)

        # 6. Countdown Overlay (3, 2, 1, GO!)
        if countdown_timer > -0.5:
            self._render_countdown(surface, countdown_timer, view_w, view_h, player)

    def _render_top_bar(self, surface, player, car, view_w, is_split):
        """Renders top info bar with glass-like semi-transparent backdrop."""
        bar_h = 42 if is_split else 50
        bar_surf = pygame.Surface((view_w, bar_h), pygame.SRCALPHA)
        bar_surf.fill((12, 15, 24, 210))
        pygame.draw.line(bar_surf, (45, 55, 80), (0, bar_h - 1), (view_w, bar_h - 1), 1)
        surface.blit(bar_surf, (0, 0))

        # PLAYER CONTROL BADGE (Left)
        if player.is_two_player:
            badge_text = "P1  [ W A S D ]" if player.player_id == 1 else "P2  [ ARROWS ]"
            badge_col = UI_ACCENT_RED if player.player_id == 1 else UI_ACCENT_CYAN
            box_w = 150 if is_split else 210
        else:
            badge_text = "PLAYER 1  [ WASD / ARROWS ]"
            badge_col = UI_ACCENT_CYAN
            box_w = 210

        badge_box = pygame.Surface((box_w, bar_h - 12), pygame.SRCALPHA)
        badge_box.fill((25, 30, 45, 230))
        pygame.draw.rect(badge_box, badge_col, (0, 0, box_w, bar_h - 12), 2, border_radius=4)
        surface.blit(badge_box, (10, 6))

        b_txt = self.font_small.render(badge_text, True, badge_col)
        surface.blit(b_txt, (10 + (box_w - b_txt.get_width()) // 2, (bar_h - b_txt.get_height()) // 2))

        # LAP Counter
        lap_str = f"LAP {min(car.lap, car.total_laps)}/{car.total_laps}"
        lap_txt = self.font_medium.render(lap_str, True, UI_ACCENT_GOLD)
        lap_x = box_w + 18
        surface.blit(lap_txt, (lap_x, (bar_h - lap_txt.get_height()) // 2))

        # RACE POSITION (Center)
        pos_str = f"POS {car.rank}/6"
        pos_color = UI_ACCENT_GREEN if car.rank == 1 else (UI_ACCENT_CYAN if car.rank <= 3 else COLOR_WHITE)
        pos_txt = self.font_large.render(pos_str, True, pos_color)
        pos_x = (view_w - pos_txt.get_width()) // 2 if not is_split else (lap_x + lap_txt.get_width() + 22)
        surface.blit(pos_txt, (pos_x, (bar_h - pos_txt.get_height()) // 2))

        # RACE TIMER & BEST LAP (Right)
        mins = int(car.total_race_time // 60)
        secs = car.total_race_time % 60
        time_str = f"{mins:02d}:{secs:05.2f}" if is_split else f"TIME {mins:02d}:{secs:05.2f}"
        time_txt = self.font_medium.render(time_str, True, COLOR_WHITE)
        surface.blit(time_txt, (view_w - time_txt.get_width() - 14, (bar_h - time_txt.get_height()) // 2))

    def _render_gauges(self, surface, car, view_w, view_h, is_split):
        """Renders digital speedometer and 10-step fuel gauge."""
        panel_w = 260
        panel_h = 75 if is_split else 85
        panel_x = 16
        panel_y = view_h - panel_h - 14

        # Background panel
        p_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        p_surf.fill((12, 16, 26, 215))
        pygame.draw.rect(p_surf, (45, 55, 80), (0, 0, panel_w, panel_h), 1, border_radius=6)
        surface.blit(p_surf, (panel_x, panel_y))

        # 1. SPEEDOMETER
        speed_kmh = car.get_speed_kmh()
        speed_txt = self.font_large.render(f"{speed_kmh:3d}", True, UI_ACCENT_CYAN)
        unit_txt = self.font_small.render("KM/H", True, UI_TEXT_MUTED)
        surface.blit(speed_txt, (panel_x + 12, panel_y + 8))
        surface.blit(unit_txt, (panel_x + 72, panel_y + 18))

        # Mini Speed Tachometer Bar
        tacho_w = 140
        tacho_fill = int((car.speed / car.max_speed) * tacho_w)
        pygame.draw.rect(surface, (30, 35, 50), (panel_x + 110, panel_y + 16, tacho_w, 10), border_radius=2)
        if tacho_fill > 0:
            tacho_col = UI_ACCENT_RED if speed_kmh > 210 else (UI_ACCENT_GOLD if speed_kmh > 150 else UI_ACCENT_CYAN)
            pygame.draw.rect(surface, tacho_col, (panel_x + 110, panel_y + 16, tacho_fill, 10), border_radius=2)

        # 2. FUEL SYSTEM BAR
        fuel_pct = int(max(0.0, car.fuel))
        fuel_label = self.font_small.render(f"FUEL  {fuel_pct}%", True, COLOR_WHITE)
        surface.blit(fuel_label, (panel_x + 12, panel_y + 45))

        # 10-Step Fuel Capacity Bar: ████████░░
        bar_x = panel_x + 110
        bar_y = panel_y + 47
        segment_w = 12
        segment_gap = 2
        total_steps = 10
        active_steps = int(math.ceil(car.fuel / 10.0))

        bar_color = UI_ACCENT_GREEN
        if car.fuel <= 25.0:
            bar_color = UI_ACCENT_RED
        elif car.fuel <= 50.0:
            bar_color = UI_ACCENT_GOLD

        for i in range(total_steps):
            sx = bar_x + i * (segment_w + segment_gap)
            if i < active_steps:
                pygame.draw.rect(surface, bar_color, (sx, bar_y, segment_w, 14), border_radius=2)
            else:
                pygame.draw.rect(surface, (35, 40, 55), (sx, bar_y, segment_w, 14), border_radius=2)

        # Pulsing LOW FUEL / EMPTY Warning
        if car.fuel <= 0.0:
            warn_txt = self.font_small.render("EMPTY - SPEED LIMITED!", True, UI_ACCENT_RED)
            surface.blit(warn_txt, (panel_x + 12, panel_y - 20))
        elif car.low_fuel_warning and (int(pygame.time.get_ticks() / 300) % 2 == 0):
            warn_txt = self.font_small.render("! LOW FUEL WARNING !", True, UI_ACCENT_RED)
            surface.blit(warn_txt, (panel_x + 12, panel_y - 20))

    def _render_camera_badge(self, surface, player, view_w, view_h, is_split):
        """Displays active camera mode and keybinding."""
        cam_id = player.camera_mode["id"]
        cam_hint = f"CAMERA: {cam_id} [C]"
        txt = self.font_small.render(cam_hint, True, UI_TEXT_MUTED)

        badge_w = txt.get_width() + 16
        badge_h = 24
        badge_x = (view_w - badge_w) // 2
        badge_y = view_h - badge_h - 12

        badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        badge_surf.fill((15, 20, 30, 190))
        pygame.draw.rect(badge_surf, (50, 60, 80), (0, 0, badge_w, badge_h), 1, border_radius=4)
        surface.blit(badge_surf, (badge_x, badge_y))
        surface.blit(txt, (badge_x + 8, badge_y + 4))

    def _render_minimap(self, surface, player, track, all_cars, view_w, view_h, is_split):
        """
        Renders real-time 2D closed-loop minimap with player & AI tracking dots.
        CG Concept: 2D Orthographic Projection Radar Display.
        """
        radar_w = 150
        radar_h = 105 if is_split else 125
        radar_x = view_w - radar_w - 16
        radar_y = view_h - radar_h - 14

        # Radar panel glass
        radar_surf = pygame.Surface((radar_w, radar_h), pygame.SRCALPHA)
        radar_surf.fill((12, 16, 26, 215))
        pygame.draw.rect(radar_surf, (45, 55, 80), (0, 0, radar_w, radar_h), 1, border_radius=6)
        surface.blit(radar_surf, (radar_x, radar_y))

        # Title
        title_txt = self.font_tiny.render("CIRCUIT RADAR", True, UI_TEXT_MUTED)
        surface.blit(title_txt, (radar_x + 8, radar_y + 5))

        # Draw circuit track outline polyline
        pts = track.minimap_points
        if len(pts) > 1:
            screen_pts = [(radar_x + int(px * radar_w), radar_y + int(py * radar_h)) for px, py in pts]
            pygame.draw.lines(surface, (80, 95, 125), True, screen_pts, 3)
            # Start/Finish checkered line tick
            fx, fy = screen_pts[0]
            pygame.draw.circle(surface, COLOR_WHITE, (fx, fy), 4)

        # Plot all car positions on the track loop
        total_len = max(1.0, track.total_length)
        num_pts = len(pts)

        if num_pts > 0:
            # 0. Active Fuel Canisters on Track (Green Jerrycan Icons on Minimap)
            for fuel_can in track.fuel_pickups:
                if fuel_can["collected"]:
                    continue
                pt_idx = int((fuel_can["z"] / total_len) * num_pts) % num_pts
                fkx = radar_x + int(pts[pt_idx][0] * radar_w)
                fky = radar_y + int(pts[pt_idx][1] * radar_h)
                # Mini green jerrycan icon on map
                pygame.draw.rect(surface, (25, 225, 85), (fkx - 3, fky - 3, 6, 7), border_radius=1)
                pygame.draw.rect(surface, (255, 255, 255), (fkx - 2, fky - 4, 3, 2))
                pygame.draw.circle(surface, (40, 240, 110), (fkx, fky), 5, 1)

            # 1. Opponent AI Cars (Amber dots)
            for c in all_cars:
                if c.is_player:
                    continue
                pt_idx = int((c.z / total_len) * num_pts) % num_pts
                cx = radar_x + int(pts[pt_idx][0] * radar_w)
                cy = radar_y + int(pts[pt_idx][1] * radar_h)
                pygame.draw.circle(surface, (255, 190, 0), (cx, cy), 3)

            # 2. Player 2 (Cobalt Blue dot with halo)
            for c in all_cars:
                if c.is_player and c.name == "Player 2":
                    pt_idx = int((c.z / total_len) * num_pts) % num_pts
                    cx = radar_x + int(pts[pt_idx][0] * radar_w)
                    cy = radar_y + int(pts[pt_idx][1] * radar_h)
                    pygame.draw.circle(surface, (0, 200, 255), (cx, cy), 5)
                    pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), 2)

            # 3. Player 1 (Crimson Red dot with pulsing ring)
            for c in all_cars:
                if c.is_player and c.name == "Player 1":
                    pt_idx = int((c.z / total_len) * num_pts) % num_pts
                    cx = radar_x + int(pts[pt_idx][0] * radar_w)
                    cy = radar_y + int(pts[pt_idx][1] * radar_h)
                    # Outer pulsing halo ring
                    pulse_rad = 5 + int((pygame.time.get_ticks() / 150) % 3)
                    pygame.draw.circle(surface, (255, 60, 60), (cx, cy), pulse_rad, 1)
                    pygame.draw.circle(surface, (255, 40, 40), (cx, cy), 5)
                    pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), 2)

    def _render_popups(self, surface, player, view_w, view_h):
        """Draws floating animated text popups (e.g. +20 FUEL, IMPACT!)."""
        for p in player.floating_popups:
            alpha = int(255 * (p["timer"] / p["max_timer"]))
            txt = self.font_medium.render(p["text"], True, p["color"])
            txt_surf = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
            txt_surf.blit(txt, (0, 0))
            txt_surf.set_alpha(alpha)
            x = (view_w - txt.get_width()) // 2
            y = int(view_h * 0.45 - p["y_offset"])
            surface.blit(txt_surf, (x, y))

    def _render_countdown(self, surface, timer, view_w, view_h, player=None):
        """Renders 3.. 2.. 1.. GO! starting banner with player control prompts."""
        if timer > 1.6:
            text = "3"
            color = UI_ACCENT_RED
        elif timer > 0.8:
            text = "2"
            color = UI_ACCENT_GOLD
        elif timer > 0.0:
            text = "1"
            color = UI_ACCENT_GOLD
        else:
            text = "GO!"
            color = UI_ACCENT_GREEN

        # Drop shadow & banner
        shadow_txt = self.font_countdown.render(text, True, COLOR_BLACK)
        banner_txt = self.font_countdown.render(text, True, color)
        cx = (view_w - banner_txt.get_width()) // 2
        cy = (view_h - banner_txt.get_height()) // 2 - 12
        surface.blit(shadow_txt, (cx + 3, cy + 3))
        surface.blit(banner_txt, (cx, cy))

        # Helpful sub-banner for players during countdown
        if timer > 0.0:
            if player and player.is_two_player:
                hint = "YOUR CONTROLS: W A S D" if player.player_id == 1 else "YOUR CONTROLS: ARROW KEYS"
                hint_col = UI_ACCENT_RED if player.player_id == 1 else UI_ACCENT_CYAN
            else:
                hint = "USE W A S D  OR  ARROW KEYS"
                hint_col = UI_ACCENT_CYAN

            hint_txt = self.font_medium.render(hint, True, hint_col)
            surface.blit(hint_txt, ((view_w - hint_txt.get_width()) // 2, cy + banner_txt.get_height() + 2))
