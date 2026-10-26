"""
Map 3 — Cyberpunk City Night Circuit
====================================
An exhilarating downtown urban street circuit under the stars, featuring
neon-lit skyscrapers, street lamps casting glowing light cones, sharp 90-degree
corners, long high-speed avenues, and reflective wet asphalt.
"""

import math
import random
import pygame
from maps.base_map import BaseMap
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class CityMap(BaseMap):
    """City Night Circuit track implementation."""

    def __init__(self):
        super().__init__(
            map_id="CITY",
            name="NEON METROPOLIS",
            difficulty="MEDIUM - HARD",
            preview_desc="High-speed nocturnal street circuit with 90-degree corners and neon skylines."
        )
        self.best_time = "01:32.15"

        # Cyber City Night Palette
        self.palette = {
            "sky_top": (10, 10, 24),         # Midnight void
            "sky_bottom": (35, 25, 55),      # Neon urban smog / indigo
            "ground_light": (35, 38, 45),    # Urban concrete sidewalk
            "ground_dark": (26, 28, 35),     # Shaded sidewalk
            "road_light": (48, 50, 58),      # Dark reflective asphalt
            "road_dark": (38, 40, 48),       # Midnight asphalt
            "rumble_light": (0, 220, 245),   # Neon Cyan curb
            "rumble_dark": (240, 30, 140),   # Neon Magenta curb
            "lane": (255, 240, 100),         # Glowing sodium yellow dash
            "is_night": True
        }
        self.build_track()

    def _generate_road_geometry(self):
        """Constructs an urban grid circuit with 90-degree turns and fast avenues."""
        # 1. Main Broadway Avenue Straightaway
        self.add_straight(150)

        # 2. 90-Degree Sharp Right Turn (Downtown Intersection)
        self.add_road(enter=25, hold=50, leave=25, curve=5.2, y=0.0)

        # 3. Financial District Cross Street
        self.add_straight(100)

        # 4. 90-Degree Sharp Left Turn
        self.add_road(enter=25, hold=50, leave=25, curve=-5.2, y=0.0)

        # 5. Elevated Overpass Freeway Section (Climb & Overlook)
        self.add_road(enter=35, hold=70, leave=35, curve=1.2, y=550.0)
        self.add_straight(90)
        self.add_road(enter=35, hold=70, leave=35, curve=-1.2, y=-550.0)

        # 6. Neon Tunnel S-Bends (Chicane)
        self.add_road(enter=25, hold=45, leave=25, curve=3.8, y=0.0)
        self.add_road(enter=25, hold=45, leave=25, curve=-3.8, y=0.0)

        # 7. Long High-Speed Boulevard
        self.add_straight(160)

        # 8. Final 90-Degree Turn into the Finish Grid
        self.add_road(enter=30, hold=60, leave=30, curve=4.8, y=0.0)
        self.add_straight(70)

    def _generate_scenery_and_props(self):
        """Populates illuminated skyscrapers and street lamps with light cones."""
        rng = random.Random(505)
        for i in range(0, self.total_segments, 7):
            seg = self.segments[i]
            # Left side buildings & street lamps
            if rng.random() < 0.70:
                is_lamp = (i % 6 == 0)
                offset = -1.25 if is_lamp else (-1.6 - rng.random() * 1.5)
                prop_type = "streetlight" if is_lamp else "building_skyscraper"
                seg.sprites.append({"type": prop_type, "offset_x": offset, "scale": 1.0})

            # Right side buildings & street lamps
            if rng.random() < 0.70:
                is_lamp = ((i + 3) % 6 == 0)
                offset = 1.25 if is_lamp else (1.6 + rng.random() * 1.5)
                prop_type = "streetlight" if is_lamp else "building_skyscraper"
                seg.sprites.append({"type": prop_type, "offset_x": offset, "scale": 1.0})

    def _generate_obstacles_and_fuel(self):
        """Places fuel canisters spaced far apart for exciting collection gameplay. No obstacles."""
        rng = random.Random(606)
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
        """Constructs cyberpunk night sky, moon, stars, and illuminated skyline."""
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT // 2 + 60
        surf = pygame.Surface((w, h))

        # Vertical Midnight Sky Gradient
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

        # Night Sky Stars
        star_rng = random.Random(777)
        for _ in range(90):
            sx = star_rng.randint(0, w)
            sy = star_rng.randint(5, h - 90)
            brightness = star_rng.randint(160, 255)
            surf.set_at((sx, sy), (brightness, brightness, 255))

        # Crescent Moon with Soft Glow
        pygame.draw.circle(surf, (255, 255, 230, 40), (w - 220, 60), 32)
        pygame.draw.circle(surf, (255, 255, 230), (w - 220, 60), 22)
        pygame.draw.circle(surf, top_c, (w - 212, 54), 19)

        # Distant Skyline Silhouette (Layer 1 - Deep Indigo)
        rng = random.Random(888)
        bx = 0
        while bx < w:
            bw = rng.randint(45, 90)
            bh = rng.randint(90, 180)
            rect = pygame.Rect(bx, h - bh, bw, bh)
            pygame.draw.rect(surf, (22, 24, 42), rect)
            bx += bw - 8

        # Midground Neon Skyscrapers (Layer 2 - High detail with antenna lights)
        bx = 10
        rng = random.Random(999)
        while bx < w:
            bw = rng.randint(55, 110)
            bh = rng.randint(70, 140)
            rect = pygame.Rect(bx, h - bh, bw, bh)
            pygame.draw.rect(surf, (32, 36, 60), rect)
            pygame.draw.rect(surf, (55, 65, 100), rect, 1)

            # Glowing window matrix on background buildings
            for wy in range(h - bh + 15, h - 15, 16):
                for wx in range(bx + 8, bx + bw - 12, 14):
                    if rng.random() < 0.45:
                        win_col = rng.choice([(255, 215, 100), (0, 220, 245), (255, 90, 180)])
                        pygame.draw.rect(surf, win_col, (wx, wy, 6, 8))

            bx += bw + rng.randint(5, 20)

        self.sky_surface = surf
