"""
Map 2 — Alpine Mountain Pass & Hills
====================================
A dramatic high-altitude mountain course featuring steep climbs, rapid
descents, sharp hairpin turns, pine forests, rocky cliffs, and snow-capped peaks.
Demonstrates strong 3D elevation perspective projection and curve scaling.
"""

import math
import random
import pygame
from maps.base_map import BaseMap
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class HillsMap(BaseMap):
    """Alpine Mountain Pass track implementation."""

    def __init__(self):
        super().__init__(
            map_id="HILLS",
            name="ALPINE RIDGE PASS",
            difficulty="HARD",
            preview_desc="Challenging mountain circuit with steep hills, crests, and sharp hairpins."
        )
        self.best_time = "01:38.80"

        # Alpine Nature Palette
        self.palette = {
            "sky_top": (20, 75, 175),        # Crisp mountain blue
            "sky_bottom": (120, 190, 235),   # Cool alpine haze
            "ground_light": (45, 145, 55),   # Lush pine meadow
            "ground_dark": (35, 125, 45),    # Forest green
            "road_light": (75, 78, 85),      # Dark mountain tarmac
            "road_dark": (65, 68, 75),       # Shaded tarmac
            "rumble_light": (255, 255, 255), # White curb
            "rumble_dark": (215, 30, 30),    # Red curb
            "lane": (255, 215, 0),           # Mountain yellow double line
            "is_night": False
        }
        self.build_track()

    def _generate_road_geometry(self):
        """Constructs dramatic vertical elevations, mountain crests, and hairpin turns."""
        # 1. Valley Straight
        self.add_straight(100)

        # 2. Steep Mountain Ascent (Climbing +900 units) with Gentle Curve
        self.add_road(enter=40, hold=80, leave=40, curve=2.0, y=950.0)

        # 3. Ridge Crest (Peak with sudden drop preview)
        self.add_straight(60)

        # 4. Severe Hairpin Right around Cliff Edge
        self.add_road(enter=35, hold=90, leave=35, curve=4.2, y=-400.0)

        # 5. Mountain S-Chicane through Forest
        self.add_road(enter=30, hold=60, leave=30, curve=-3.8, y=300.0)
        self.add_road(enter=30, hold=60, leave=30, curve=3.5, y=-500.0)

        # 6. High Speed Downhill Roller-Coaster Plunge
        self.add_road(enter=40, hold=110, leave=40, curve=-1.2, y=-1100.0)

        # 7. Low Valley Hairpin Left
        self.add_road(enter=40, hold=95, leave=40, curve=-4.5, y=250.0)

        # 8. Rolling Hills Undulation back to Start
        self.add_hill(num_segments=100, height=550.0)
        self.add_road(enter=30, hold=60, leave=30, curve=1.5, y=-450.0)
        self.add_straight(80)

    def _generate_scenery_and_props(self):
        """Populates dense pine trees and mountain boulders."""
        rng = random.Random(303)
        for i in range(0, self.total_segments, 7):
            seg = self.segments[i]
            # Left side alpine trees / rocks
            if rng.random() < 0.75:
                offset = -1.35 - rng.random() * 1.8
                prop_type = "tree_pine" if rng.random() < 0.8 else "rock_boulder"
                seg.sprites.append({"type": prop_type, "offset_x": offset, "scale": 1.05})
            # Right side alpine trees / rocks
            if rng.random() < 0.75:
                offset = 1.35 + rng.random() * 1.8
                prop_type = "tree_pine" if rng.random() < 0.8 else "rock_boulder"
                seg.sprites.append({"type": prop_type, "offset_x": offset, "scale": 1.05})

    def _generate_obstacles_and_fuel(self):
        """Places fuel canisters spaced far apart for exciting collection gameplay. No obstacles."""
        rng = random.Random(404)
        # Fuel canisters only, spaced every 35 segments for thrill
        for i in range(95, self.total_segments - 40, 35):
            z = i * 200.0
            lane_x = rng.choice([-0.5, 0.0, 0.5])
            self.fuel_pickups.append({
                "z": z,
                "x": lane_x,
                "collected": False,
                "respawn_timer": 0.0
            })

    def _build_background_surfaces(self):
        """Constructs alpine mountain backdrop with snow peaks."""
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT // 2 + 60
        surf = pygame.Surface((w, h))

        # Vertical Sky Gradient
        top_c = self.palette["sky_top"]
        bot_c = self.palette["sky_bottom"]
        for y in range(h):
            t = y / float(h)
            col = (
                int(top_c[0] + (bot_c[0] - top_c[0]) * t),
                int(top_c[1] + (bot_c[1] - top_c[1]) * t),
                int(top_c[2] + (bot_c[2] - top_c[2]) * t)
            )
            pygame.draw.line(surf, col, (0, y), (w, y))

        # Distant Snow-Capped Mountain Range (Layer 1)
        peaks = [
            (0, h - 80), (120, h - 170), (260, h - 90),
            (420, h - 210), (580, h - 110), (740, h - 195),
            (900, h - 100), (1060, h - 225), (1200, h - 120), (w, h - 90), (w, h), (0, h)
        ]
        pygame.draw.polygon(surf, (85, 95, 125), peaks)

        # Snow Caps on high peaks
        for px, py in [(120, h - 170), (420, h - 210), (740, h - 195), (1060, h - 225)]:
            snow_poly = [
                (px - 45, py + 45), (px, py), (px + 45, py + 45), (px + 15, py + 38), (px - 15, py + 42)
            ]
            pygame.draw.polygon(surf, (245, 250, 255), snow_poly)

        # Mid-ground Dark Pine Foothills (Layer 2)
        foothills = [
            (0, h - 50), (180, h - 110), (350, h - 60), (520, h - 120),
            (700, h - 70), (880, h - 115), (1040, h - 65), (w, h - 95), (w, h), (0, h)
        ]
        pygame.draw.polygon(surf, (35, 75, 45), foothills)

        self.sky_surface = surf
