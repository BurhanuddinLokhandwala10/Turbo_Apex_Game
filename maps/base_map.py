"""
Base Track & Map Specification
===============================
Provides the foundational data model for segment-based pseudo-3D tracks,
including 3D road points, curvature, elevation, color schemes, roadside
scenery, obstacles, fuel pickups, and 2D minimap projection.
"""

import math
import random
import pygame
from game.settings import SEGMENT_LENGTH, ROAD_WIDTH, RUMBLE_LENGTH

class RoadSegment:
    """Represents a single cross-section slice of the race track."""

    def __init__(self, index):
        self.index = index
        # 3D World Coordinate Points: p1 (entry), p2 (exit)
        self.p1 = {"world": [0.0, 0.0, index * SEGMENT_LENGTH], "screen": [0, 0, 0, 0.0]}
        self.p2 = {"world": [0.0, 0.0, (index + 1) * SEGMENT_LENGTH], "screen": [0, 0, 0, 0.0]}

        self.curve = 0.0       # Horizontal curvature derivative
        self.elevation = 0.0   # World elevation Y coordinate
        self.clip = 0.0        # Horizon clipping plane for occlusion
        self.sprites = []      # Roadside billboard decorations / props
        self.cars = []         # Cars currently occupying this segment
        self.color = {}        # Active color palette for this segment

class BaseMap:
    """Abstract base class for all racing environments."""

    def __init__(self, map_id, name, difficulty, preview_desc):
        self.map_id = map_id
        self.name = name
        self.difficulty = difficulty
        self.preview_desc = preview_desc
        self.best_time = "01:45.00"

        # Segments container
        self.segments = []
        self.total_length = 0
        self.total_segments = 0

        # Dynamic Game Entities on the Track
        self.obstacles = []     # List of obstacle dicts: {"z", "x", "type", "w", "h", "hitbox"}
        self.fuel_pickups = []  # List of fuel pickup dicts: {"z", "x", "collected", "respawn_timer"}

        # 2D Minimap polyline cache (Normalized [0, 1] coordinates)
        self.minimap_points = []

        # Parallax Background Textures / Surfaces
        self.sky_surface = None
        self.scenery_layers = []

        # Color Palette Configuration
        self.palette = {
            "sky_top": (30, 80, 160),
            "sky_bottom": (120, 180, 240),
            "ground_light": (40, 140, 60),
            "ground_dark": (35, 125, 55),
            "road_light": (105, 105, 110),
            "road_dark": (95, 95, 100),
            "rumble_light": (240, 240, 240),
            "rumble_dark": (210, 40, 40),
            "lane": (255, 255, 255),
            "is_night": False
        }

    def build_track(self):
        """Constructs segments, scenery, obstacles, and minimap loop."""
        self._generate_road_geometry()
        self.total_segments = len(self.segments)
        self.total_length = self.total_segments * SEGMENT_LENGTH
        self._generate_scenery_and_props()
        self._generate_obstacles_and_fuel()
        self._compute_minimap_loop()
        self._build_background_surfaces()

    def _generate_road_geometry(self):
        """Implemented by child maps to add straights, curves, and hills."""
        raise NotImplementedError

    def _generate_scenery_and_props(self):
        """Implemented by child maps to place environment props."""
        raise NotImplementedError

    def _generate_obstacles_and_fuel(self):
        """Implemented by child maps to place track obstacles and fuel canisters."""
        raise NotImplementedError

    def _build_background_surfaces(self):
        """Implemented by child maps to render parallax backdrops."""
        pass

    # =========================================================================
    # GEOMETRY BUILDER HELPERS
    # =========================================================================

    def add_segment(self, curve=0.0, y=0.0):
        """Appends a new road segment with curvature and elevation."""
        n = len(self.segments)
        seg = RoadSegment(n)
        seg.curve = curve
        seg.p1["world"][1] = self.segments[n - 1].p2["world"][1] if n > 0 else 0.0
        seg.p2["world"][1] = y
        seg.elevation = (seg.p1["world"][1] + seg.p2["world"][1]) / 2.0

        # Alternate stripe colors every RUMBLE_LENGTH segments
        is_stripe = (n // RUMBLE_LENGTH) % 2 == 0
        seg.color = {
            "ground": self.palette["ground_light"] if is_stripe else self.palette["ground_dark"],
            "road": self.palette["road_light"] if is_stripe else self.palette["road_dark"],
            "rumble": self.palette["rumble_light"] if is_stripe else self.palette["rumble_dark"],
            "lane": self.palette["lane"] if is_stripe else None
        }
        self.segments.append(seg)

    def add_road(self, enter, hold, leave, curve, y=0.0):
        """
        Adds smooth transition road segments using easing / spline interpolation.
        CG Concept: Spline Curve Interpolation.
        """
        start_y = self.segments[-1].p2["world"][1] if len(self.segments) > 0 else 0.0
        end_y = start_y + y
        total = enter + hold + leave

        for i in range(enter):
            # Ease in
            t = i / enter
            cur = curve * (t * t)
            elev = start_y + (y * (i / total))
            self.add_segment(cur, elev)

        for i in range(hold):
            elev = start_y + (y * ((enter + i) / total))
            self.add_segment(curve, elev)

        for i in range(leave):
            # Ease out
            t = 1.0 - (i / leave)
            cur = curve * (t * t)
            elev = start_y + (y * ((enter + hold + i) / total))
            self.add_segment(cur, elev)

    def add_straight(self, num_segments=100):
        """Adds a straight section."""
        self.add_road(num_segments // 4, num_segments // 2, num_segments // 4, 0.0, 0.0)

    def add_hill(self, num_segments=120, height=800.0):
        """Adds an elevation hill climb and descent."""
        self.add_road(num_segments // 4, num_segments // 2, num_segments // 4, 0.0, height)
        self.add_road(num_segments // 4, num_segments // 2, num_segments // 4, 0.0, -height)

    def get_segment_at(self, z):
        """Fetches the road segment for any arbitrary world z distance."""
        if not self.segments:
            return None
        idx = int((z % self.total_length) // SEGMENT_LENGTH)
        return self.segments[idx % self.total_segments]

    # =========================================================================
    # COMPUTER GRAPHICS: 2D CLOSED-LOOP MINIMAP PROJECTION
    # =========================================================================

    def _compute_minimap_loop(self):
        """
        Numerically integrates segment curvatures into a 2D closed polygon track loop.
        CG Concept: Curvature Integration & Orthogonal Projection onto 2D Plane.
        """
        raw_points = []
        x, y = 0.0, 0.0
        angle = 0.0

        for seg in self.segments:
            # Angle rate proportional to curvature
            angle += seg.curve * 0.016
            step_len = 5.0
            x += math.sin(angle) * step_len
            y -= math.cos(angle) * step_len  # Negative Y is up
            raw_points.append((x, y))

        if not raw_points:
            return

        # Closed-loop adjustment: distribute closure error smoothly
        end_x, end_y = raw_points[-1]
        n = len(raw_points)
        corrected_points = []
        for i, (px, py) in enumerate(raw_points):
            t = i / float(n)
            cx = px - end_x * t
            cy = py - end_y * t
            corrected_points.append((cx, cy))

        # Compute bounding box
        min_x = min(p[0] for p in corrected_points)
        max_x = max(p[0] for p in corrected_points)
        min_y = min(p[1] for p in corrected_points)
        max_y = max(p[1] for p in corrected_points)

        span_x = max(1.0, max_x - min_x)
        span_y = max(1.0, max_y - min_y)

        # Normalize points to [0.08, 0.92] box for minimap radar rendering
        self.minimap_points = [
            (0.10 + 0.80 * ((px - min_x) / span_x), 0.10 + 0.80 * ((py - min_y) / span_y))
            for px, py in corrected_points
        ]
