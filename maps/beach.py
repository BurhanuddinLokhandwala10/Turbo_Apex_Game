"""
Map 1 — Sunny Beach Coast
=========================
A vibrant oceanfront coastal speedway featuring golden sandy shores,
palm trees, gentle sweeping seaside curves, beach obstacles, and bright skies.
"""

import math
import random
import pygame
from maps.base_map import BaseMap
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class BeachMap(BaseMap):
    """Beach track implementation."""

    def __init__(self):
        super().__init__(
            map_id="BEACH",
            name="COASTAL BAYWAY",
            difficulty="EASY - MEDIUM",
            preview_desc="Tropical ocean highway with sweeping seaside turns and sand dunes."
        )
        self.best_time = "01:28.40"

        # Tropical Coastal Palette
        self.palette = {
            "sky_top": (25, 120, 220),       # Deep azure blue
            "sky_bottom": (135, 205, 250),   # Light ocean cyan
            "ground_light": (235, 210, 145), # Sunny golden sand
            "ground_dark": (220, 195, 130),  # Dune shadow sand
            "road_light": (118, 120, 128),   # Coastal asphalt
            "road_dark": (108, 110, 118),    # Shaded asphalt
            "rumble_light": (255, 255, 255), # White curb
            "rumble_dark": (225, 40, 40),    # Red curb
            "lane": (255, 255, 255),         # White lane markings
            "is_night": False
        }
        self.build_track()

    def _generate_road_geometry(self):
        """Constructs the road layout with seaside bends and gentle coastal undulations."""
        # Section 1: Starting Ocean Grid & Boulevard
        self.add_straight(120)

        # Section 2: Sweeping Long Ocean Curve Right
        self.add_road(enter=40, hold=120, leave=40, curve=1.8, y=100.0)

        # Section 3: Coastal Headland Rise & Turn Left
        self.add_road(enter=35, hold=90, leave=35, curve=-2.2, y=-150.0)

        # Section 4: Beach Dune Straightaway
        self.add_straight(100)

        # Section 5: Palm Lagoon S-Curve (Chicane)
        self.add_road(enter=30, hold=60, leave=30, curve=3.0, y=80.0)
        self.add_road(enter=30, hold=60, leave=30, curve=-3.0, y=-80.0)

        # Section 6: Shoreline High-Speed Straight
        self.add_straight(140)

        # Section 7: Lighthouse Hairpin Bend
        self.add_road(enter=45, hold=110, leave=45, curve=-3.6, y=120.0)

        # Section 8: Final Ocean Sweep to Start/Finish Line
        self.add_road(enter=35, hold=80, leave=35, curve=1.5, y=-70.0)
        self.add_straight(80)

    def _generate_scenery_and_props(self):
        """Places palm trees, rocks, and beach props along road boundaries."""
        rng = random.Random(101)
        for i in range(0, self.total_segments, 8):
            seg = self.segments[i]
            # Left side palm trees
            if rng.random() < 0.65:
                offset = -1.4 - rng.random() * 1.5
                seg.sprites.append({"type": "tree_palm", "offset_x": offset, "scale": 1.0})
            # Right side palm trees or beach rocks
            if rng.random() < 0.65:
                offset = 1.4 + rng.random() * 1.5
                prop_type = "tree_palm" if rng.random() < 0.75 else "rock_boulder"
                seg.sprites.append({"type": prop_type, "offset_x": offset, "scale": 0.95})

    def _generate_obstacles_and_fuel(self):
        """Places fuel canisters spaced far apart for exciting collection gameplay. No obstacles."""
        rng = random.Random(202)
        # Fuel canisters only, spaced every 35 segments for thrill
        for i in range(90, self.total_segments - 40, 35):
            z = i * 200.0
            lane_x = rng.choice([-0.5, 0.0, 0.5])
            self.fuel_pickups.append({
                "z": z,
                "x": lane_x,
                "collected": False,
                "respawn_timer": 0.0
            })

    def _build_background_surfaces(self):
        """Constructs tropical sky and parallax ocean horizon."""
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT // 2 + 60
        surf = pygame.Surface((w, h))

        # Vertical Sky Gradient (Azure to Light Ocean Cyan)
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

        # Shining Tropical Sun
        pygame.draw.circle(surf, (255, 255, 220, 180), (w - 180, 75), 45)
        pygame.draw.circle(surf, (255, 240, 130), (w - 180, 75), 32)

        # Fluffy Cumulus Clouds
        cloud_color = (255, 255, 255, 200)
        for cx, cy, rad in [(220, 65, 38), (255, 55, 48), (295, 65, 36),
                            (680, 95, 34), (715, 85, 44), (750, 95, 32),
                            (1050, 60, 40), (1085, 50, 50), (1125, 60, 38)]:
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), rad)

        # Distant Turquoise Ocean Line at Horizon
        ocean_rect = pygame.Rect(0, h - 50, w, 50)
        pygame.draw.rect(surf, (20, 145, 195), ocean_rect)
        # White water break line
        pygame.draw.line(surf, (220, 245, 255), (0, h - 50), (w, h - 50), 2)
        # Ocean wave reflections
        for wx in range(0, w, 40):
            pygame.draw.line(surf, (70, 190, 230), (wx, h - 35), (wx + 25, h - 35), 1)
            pygame.draw.line(surf, (70, 190, 230), (wx + 15, h - 20), (wx + 35, h - 20), 1)

        self.sky_surface = surf
