"""
Procedural Environment & Billboard Prop Generator
==================================================
Procedurally generates textured sprites for roadside scenery, obstacles,
and fuel canisters using Pygame vector drawing and color gradients.
"""

import math
import pygame
from game.settings import COLOR_WHITE, COLOR_BLACK

class PropGenerator:
    """Creates cached procedural sprite surfaces for billboard rendering."""

    _cache = {}

    @classmethod
    def get_prop(cls, prop_type):
        """Returns a cached Surface for a given prop type."""
        if prop_type in cls._cache:
            return cls._cache[prop_type]

        method = getattr(cls, f"_create_{prop_type}", None)
        if method:
            surf = method()
            cls._cache[prop_type] = surf
            return surf

        # Default fallback box
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 200, 200), (0, 0, 40, 40))
        cls._cache[prop_type] = surf
        return surf

    # -------------------------------------------------------------------------
    # SCENERY PROPS
    # -------------------------------------------------------------------------

    @classmethod
    def _create_tree_palm(cls):
        """Tropical palm tree for Beach map."""
        w, h = 180, 240
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Trunk shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 70), (w // 2 - 25, h - 14, 50, 14))
        # Curved Trunk (Segmented bark)
        points = []
        for i in range(12):
            t = i / 11.0
            tx = (w // 2) - 15 + math.sin(t * 1.8) * 35
            ty = (h - 10) - t * (h - 50)
            points.append((tx, ty))
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            pygame.draw.line(surf, (140, 95, 55), p1, p2, int(18 - i * 0.8))
            pygame.draw.line(surf, (110, 70, 35), (p1[0] - 2, p1[1]), (p2[0] - 2, p2[1]), int(8 - i * 0.4))

        # Palm Fronds (Lush green arched leaves)
        top_x, top_y = points[-1]
        leaf_colors = [(34, 150, 45), (45, 185, 55), (25, 125, 35), (60, 210, 70)]
        angles = [-160, -125, -90, -55, -20, 20, 55, 90, 125, 160]
        for idx, ang in enumerate(angles):
            col = leaf_colors[idx % len(leaf_colors)]
            rad = math.radians(ang)
            # Arched bezier-like curve
            mid_rad = math.radians(ang + (15 if ang > 0 else -15))
            mid_x = top_x + math.sin(rad) * 55
            mid_y = top_y - math.cos(rad) * 45
            end_x = top_x + math.sin(rad) * 85
            end_y = top_y - math.cos(rad) * 60 + 35
            pygame.draw.line(surf, col, (top_x, top_y), (mid_x, mid_y), 7)
            pygame.draw.line(surf, col, (mid_x, mid_y), (end_x, end_y), 4)

        return surf

    @classmethod
    def _create_tree_pine(cls):
        """Coniferous pine tree for Mountain/Hills map."""
        w, h = 160, 240
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2
        # Ground shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (cx - 30, h - 16, 60, 16))
        # Trunk
        pygame.draw.rect(surf, (90, 55, 30), (cx - 10, h - 45, 20, 40), border_radius=3)
        # Tiered pine foliage (3 overlapping triangles)
        layers = [
            (h - 35, 140, 80, (20, 95, 35)),
            (h - 90, 115, 75, (28, 120, 45)),
            (h - 145, 90, 70, (38, 145, 55)),
            (h - 195, 60, 55, (50, 175, 65))
        ]
        for base_y, width, height, col in layers:
            poly = [
                (cx - width // 2, base_y),
                (cx + width // 2, base_y),
                (cx, base_y - height)
            ]
            pygame.draw.polygon(surf, col, poly)
            # Shadow on left half for 3D depth
            shadow_poly = [(cx - width // 2, base_y), (cx, base_y), (cx, base_y - height)]
            darker_col = (max(0, col[0] - 15), max(0, col[1] - 30), max(0, col[2] - 15))
            pygame.draw.polygon(surf, darker_col, shadow_poly)

        return surf

    @classmethod
    def _create_building_skyscraper(cls):
        """Illuminated skyscraper for City Night map."""
        w, h = 200, 340
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Main structure
        body_rect = pygame.Rect(10, 30, w - 20, h - 30)
        pygame.draw.rect(surf, (18, 22, 38), body_rect)
        pygame.draw.rect(surf, (45, 55, 85), body_rect, 2)
        # Roof antenna / spire
        pygame.draw.line(surf, (180, 180, 200), (w // 2, 0), (w // 2, 30), 3)
        pygame.draw.circle(surf, (255, 40, 40), (w // 2, 3), 4)

        # Illuminated windows grid (Random glowing warm/cyan lights)
        win_w, win_h = 8, 12
        cols = (w - 40) // (win_w + 6)
        rows = (h - 60) // (win_h + 8)

        window_colors = [
            (255, 235, 130),  # Warm amber
            (100, 220, 255),  # Cyan office
            (255, 110, 180),  # Neon pink
            (30, 35, 55)      # Dark / off window
        ]
        import random
        rng = random.Random(42)  # Deterministic seed for consistent skyline

        for r in range(rows):
            for c in range(cols):
                wx = 20 + c * (win_w + 6)
                wy = 45 + r * (win_h + 8)
                col = rng.choice(window_colors)
                pygame.draw.rect(surf, col, (wx, wy, win_w, win_h), border_radius=1)

        return surf

    @classmethod
    def _create_streetlight(cls):
        """Street lamp with downward night lighting cone."""
        w, h = 120, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Base shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 90), (10, h - 12, 40, 12))
        # Metal pole
        pygame.draw.line(surf, (130, 135, 145), (30, h - 8), (30, 35), 6)
        # Curved lamp head
        pygame.draw.line(surf, (130, 135, 145), (30, 35), (75, 20), 5)
        pygame.draw.ellipse(surf, (60, 65, 75), (65, 18, 30, 12))
        # Glowing bulb
        pygame.draw.circle(surf, (255, 240, 160), (80, 24), 6)
        # Downward light cone (Translucent yellow gradient)
        cone_poly = [
            (80, 26),
            (115, h - 8),
            (45, h - 8)
        ]
        pygame.draw.polygon(surf, (255, 240, 160, 45), cone_poly)

        return surf

    @classmethod
    def _create_rock_boulder(cls):
        """Mountain granite boulder."""
        w, h = 140, 100
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (10, h - 22, w - 20, 22))
        points = [
            (25, h - 20), (15, h - 55), (35, h - 80), (75, h - 90),
            (115, h - 75), (130, h - 45), (120, h - 20)
        ]
        pygame.draw.polygon(surf, (110, 115, 125), points)
        # Highlight facets
        facet = [(35, h - 80), (75, h - 90), (65, h - 45), (25, h - 45)]
        pygame.draw.polygon(surf, (145, 150, 160), facet)
        return surf

    # -------------------------------------------------------------------------
    # TRACK OBSTACLES (Interactive Collisions)
    # -------------------------------------------------------------------------

    @classmethod
    def _create_obstacle_cone(cls):
        """Traffic cone with reflective white stripe."""
        w, h = 50, 65
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 90), (4, h - 12, w - 8, 12))
        # Black rubber base
        pygame.draw.rect(surf, (25, 25, 30), (6, h - 14, w - 12, 8), border_radius=2)
        # Orange cone triangle
        poly = [(12, h - 12), (w - 12, h - 12), (w // 2, 4)]
        pygame.draw.polygon(surf, (255, 95, 0), poly)
        # White reflective band
        band = [
            (17, h - 28), (w - 17, h - 28),
            (w // 2 + 5, h - 44), (w // 2 - 5, h - 44)
        ]
        pygame.draw.polygon(surf, (245, 245, 250), band)
        return surf

    @classmethod
    def _create_obstacle_barrel(cls):
        """Hazard metal drum / oil barrel."""
        w, h = 60, 80
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 90), (6, h - 14, w - 12, 14))
        # Main drum cylinder
        pygame.draw.rect(surf, (220, 45, 35), (10, 12, w - 20, h - 22), border_radius=4)
        # Metal rib rings
        pygame.draw.line(surf, (140, 20, 15), (10, 28), (w - 10, 28), 3)
        pygame.draw.line(surf, (140, 20, 15), (10, 52), (w - 10, 52), 3)
        # Yellow hazard stripe across middle
        pygame.draw.rect(surf, (255, 210, 20), (10, 34, w - 20, 14))
        # Diagonal black hazard hash lines
        for x in range(12, w - 12, 8):
            pygame.draw.line(surf, (20, 20, 25), (x, 48), (x + 6, 34), 2)
        return surf

    @classmethod
    def _create_obstacle_rock(cls):
        """Track obstacle rock/boulder."""
        w, h = 80, 55
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 90), (6, h - 14, w - 12, 14))
        points = [(12, h - 14), (8, h - 35), (28, h - 50), (55, h - 46), (72, h - 28), (68, h - 14)]
        pygame.draw.polygon(surf, (95, 90, 85), points)
        pygame.draw.polygon(surf, (135, 130, 125), [(28, h - 50), (55, h - 46), (45, h - 25), (18, h - 25)])
        return surf

    @classmethod
    def _create_obstacle_barrier(cls):
        """Construction barricade obstacle."""
        w, h = 100, 65
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (6, h - 12, w - 12, 12))
        # Legs
        pygame.draw.line(surf, (40, 40, 45), (20, h - 8), (20, 18), 5)
        pygame.draw.line(surf, (40, 40, 45), (w - 20, h - 8), (w - 20, 18), 5)
        # Crossbar board
        board_rect = pygame.Rect(10, 14, w - 20, 24)
        pygame.draw.rect(surf, (255, 255, 255), board_rect, border_radius=2)
        # Orange diagonal stripes
        for x in range(12, w - 15, 14):
            pygame.draw.line(surf, (255, 90, 0), (x, 38), (x + 10, 14), 4)
        return surf

    @classmethod
    def _create_obstacle_oil(cls):
        """Slippery black oil puddle."""
        w, h = 110, 40
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (15, 15, 20, 220), (5, 5, w - 10, h - 10))
        # Iridescent rainbow sheen highlights
        pygame.draw.ellipse(surf, (60, 40, 90, 160), (18, 12, w - 36, h - 24))
        pygame.draw.ellipse(surf, (40, 120, 140, 140), (28, 15, w - 60, h - 28))
        return surf

    # -------------------------------------------------------------------------
    # FUEL PICKUP CANISTER (+20 FUEL)
    # -------------------------------------------------------------------------

    @classmethod
    def _create_pickup_fuel(cls):
        """High-octane fuel jerrycan pickup."""
        w, h = 75, 95
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Ground glow halo
        pygame.draw.ellipse(surf, (40, 230, 100, 70), (8, h - 20, w - 16, 20))
        # Canister Body (Vibrant racing green)
        can_rect = pygame.Rect(16, 26, w - 32, h - 44)
        pygame.draw.rect(surf, (25, 190, 85), can_rect, border_radius=6)
        # Darker border
        pygame.draw.rect(surf, (15, 120, 55), can_rect, 3, border_radius=6)
        # Triple-bar top handle
        pygame.draw.rect(surf, (18, 140, 65), (24, 14, w - 48, 14), border_radius=3)
        pygame.draw.rect(surf, (0, 0, 0, 0), (30, 18, w - 60, 8))
        # Spout cap
        pygame.draw.rect(surf, (240, 240, 240), (20, 10, 10, 8), border_radius=2)
        # Fuel Jerrycan cross stamp pattern
        cx, cy = w // 2, h // 2 + 5
        pygame.draw.line(surf, (18, 140, 65), (cx - 12, cy - 12), (cx + 12, cy + 12), 3)
        pygame.draw.line(surf, (18, 140, 65), (cx - 12, cy + 12), (cx + 12, cy - 12), 3)
        # Glowing text / icon badge
        badge_rect = pygame.Rect(cx - 10, cy - 8, 20, 16)
        pygame.draw.rect(surf, (255, 255, 255), badge_rect, border_radius=2)
        font = pygame.font.SysFont("Arial", 11, bold=True)
        txt = font.render("+F", True, (20, 160, 70))
        surf.blit(txt, (cx - 7, cy - 7))
        return surf
