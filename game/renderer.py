"""
Computer Graphics Pseudo-3D Perspective Projection & Render Pipeline
====================================================================
Implements textbook Computer Graphics algorithms:
1. Pinhole Perspective Projection: (x_proj = x / z * d, y_proj = y / z * d)
2. Road Segment Scanline / Trapezoid Rasterization
3. Painter's Algorithm Depth-Sorting for Billboards, Obstacles, and Vehicles
4. Occlusion Clipping against Mountain Horizon Crests
5. Parallax Horizon Scrolling for Multi-Layered Backdrops
6. True Split-Screen Multi-Viewport Camera Rendering
"""

import math
import pygame
from game.settings import (
    ROAD_WIDTH, SEGMENT_LENGTH, DRAW_DISTANCE,
    COLOR_WHITE, COLOR_BLACK, SCREEN_WIDTH, SCREEN_HEIGHT
)
from game.props import PropGenerator

class Renderer:
    """Core Computer Graphics Rasterizer & Projection Engine."""

    def __init__(self):
        self.prop_gen = PropGenerator
        self._scaled_prop_cache = {}

    def project_point(self, world_x, world_y, world_z, cam_x, cam_y, cam_z, cam_depth, view_w, view_h):
        """
        Projects a 3D World Space Point (wx, wy, wz) to 2D Screen Space (sx, sy, sw, scale).
        CG Mathematical Formula:
            dx = wx - cam_x
            dy = wy - cam_y
            dz = wz - cam_z
            scale = cam_depth / dz
            sx = (view_w / 2) + (scale * dx * view_w / 2)
            sy = (view_h / 2) - (scale * dy * view_h / 2)
            sw = scale * ROAD_WIDTH * (view_w / 2)
        """
        dz = world_z - cam_z
        if dz <= 0.0:
            return 0, 0, 0, 0.0

        scale = cam_depth / dz
        sx = int((view_w / 2.0) + (scale * (world_x - cam_x) * (view_w / 2.0)))
        sy = int((view_h / 2.0) - (scale * (world_y - cam_y) * (view_h / 2.0)))
        sw = int(scale * ROAD_WIDTH * (view_w / 2.0))
        return sx, sy, sw, scale

    def render_viewport(self, surface, track, camera, player_car, other_cars, dt):
        """
        Renders a complete race scene onto an arbitrary viewport surface.
        Supports single-player full screen or two-player split-screen halves.
        """
        view_w, view_h = surface.get_size()
        cam_x = camera.x + camera.shake_x
        cam_y = camera.y + camera.shake_y
        cam_z = camera.z
        cam_depth = camera.depth

        total_segments = track.total_segments
        total_length = track.total_length
        base_segment = track.get_segment_at(cam_z)
        if not base_segment:
            return
        base_index = base_segment.index

        # Apply track elevation to camera eye altitude
        cam_y_total = cam_y + base_segment.p1["world"][1]

        # ---------------------------------------------------------------------
        # STEP 1: PARALLAX BACKGROUND RENDERING
        # ---------------------------------------------------------------------
        self._render_parallax_sky(surface, track, camera, base_segment, view_w, view_h)

        # ---------------------------------------------------------------------
        # STEP 2: ROAD SEGMENT PROJECTION & TRAPEZOID RASTERIZATION
        # ---------------------------------------------------------------------
        max_y = view_h  # Occlusion clipping horizon buffer
        draw_queue = [] # Sprites, obstacles, and cars for Painter's algorithm
        x_accum = 0.0
        dx_accum = - (base_segment.curve * (cam_z % SEGMENT_LENGTH) / SEGMENT_LENGTH)

        # Pass 1: Near to Far for Road Polygons & Occlusion Tracking
        for n in range(DRAW_DISTANCE):
            seg_idx = (base_index + n) % total_segments
            seg = track.segments[seg_idx]

            # Track longitudinal looping offset
            looped = 1 if (base_index + n) >= total_segments else 0
            seg_z1 = seg.p1["world"][2] + (looped * total_length)
            seg_z2 = seg.p2["world"][2] + (looped * total_length)

            # Curved track lateral displacement accumulation
            seg_x1 = x_accum
            seg_x2 = x_accum + dx_accum
            dx_accum += seg.curve
            x_accum = seg_x2

            # Project entering and exiting segment points into 2D Screen Space
            sx1, sy1, sw1, scale1 = self.project_point(
                seg_x1, seg.p1["world"][1], seg_z1,
                cam_x, cam_y_total, cam_z, cam_depth, view_w, view_h
            )
            sx2, sy2, sw2, scale2 = self.project_point(
                seg_x2, seg.p2["world"][1], seg_z2,
                cam_x, cam_y_total, cam_z, cam_depth, view_w, view_h
            )

            # Cache screen coordinates on segment for object positioning
            seg.p1["screen"] = [sx1, sy1, sw1, scale1]
            seg.p2["screen"] = [sx2, sy2, sw2, scale2]

            # Hidden surface clipping (Behind camera, inverted polygon, or occluded by hill)
            if scale1 <= 0.0 or sy2 >= sy1 or sy2 >= max_y:
                continue

            # Clip bottom of trapezoid if entering the viewport from below
            if sy1 > max_y:
                t = (max_y - sy2) / float(sy1 - sy2)
                draw_x1 = int(sx2 + (sx1 - sx2) * t)
                draw_w1 = int(sw2 + (sw1 - sw2) * t)
                draw_y1 = max_y
            else:
                draw_x1 = sx1
                draw_w1 = sw1
                draw_y1 = sy1

            # Rasterize Road Trapezoids
            self._render_segment_trapezoids(surface, draw_x1, draw_y1, draw_w1, sx2, sy2, sw2, seg.color, view_w)

            # Update horizon occlusion buffer
            max_y = sy2
            seg.clip = max_y

            # Enqueue roadside billboard scenery props
            for prop in seg.sprites:
                draw_queue.append({
                    "kind": "prop",
                    "z": seg_z1,
                    "seg": seg,
                    "prop_type": prop["type"],
                    "offset_x": prop["offset_x"],
                    "scale_mod": prop.get("scale", 1.0)
                })

        # ---------------------------------------------------------------------
        # STEP 3: ENQUEUE INTERACTIVE OBSTACLES, FUEL, & OPPONENT VEHICLES
        # ---------------------------------------------------------------------
        # Interactive Obstacles within draw distance
        for obs in track.obstacles:
            rel_z = (obs["z"] - cam_z) % total_length
            if 0 < rel_z < (DRAW_DISTANCE * SEGMENT_LENGTH):
                seg = track.get_segment_at(obs["z"])
                if seg:
                    draw_queue.append({
                        "kind": "obstacle",
                        "z": cam_z + rel_z,
                        "seg": seg,
                        "prop_type": obs["type"],
                        "offset_x": obs["x"] * 1.0,
                        "scale_mod": 1.0
                    })

        # Fuel Canisters within draw distance
        for fuel_can in track.fuel_pickups:
            if fuel_can["collected"]:
                continue
            rel_z = (fuel_can["z"] - cam_z) % total_length
            if 0 < rel_z < (DRAW_DISTANCE * SEGMENT_LENGTH):
                seg = track.get_segment_at(fuel_can["z"])
                if seg:
                    draw_queue.append({
                        "kind": "fuel",
                        "z": cam_z + rel_z,
                        "seg": seg,
                        "prop_type": "pickup_fuel",
                        "offset_x": fuel_can["x"] * 1.0,
                        "scale_mod": 1.15
                    })

        # Opponent Vehicles & Other Players within draw distance
        for other in other_cars:
            if other is player_car:
                continue
            rel_z = (other.z - cam_z) % total_length
            if 0 < rel_z < (DRAW_DISTANCE * SEGMENT_LENGTH):
                seg = track.get_segment_at(other.z)
                if seg:
                    draw_queue.append({
                        "kind": "car",
                        "z": cam_z + rel_z,
                        "seg": seg,
                        "car": other,
                        "offset_x": other.x,
                        "scale_mod": 1.0
                    })

        # ---------------------------------------------------------------------
        # STEP 4: PAINTER'S ALGORITHM (BACK-TO-FRONT DEPTH SORTING)
        # ---------------------------------------------------------------------
        # CG Concept: Painter's Algorithm handles correct occlusion of billboards & 3D models
        draw_queue.sort(key=lambda item: item["z"], reverse=True)

        for item in draw_queue:
            seg = item["seg"]
            scale = seg.p1["screen"][3]
            if scale <= 0.0:
                continue

            # Calculate screen projection center
            sprite_x = int(seg.p1["screen"][0] + (scale * item["offset_x"] * ROAD_WIDTH * (view_w / 2.0)))
            sprite_y = seg.p1["screen"][1]

            # Clip against hill crest occlusion line
            if sprite_y > seg.clip and seg.clip > 0:
                # Still draw if partially visible
                pass

            if item["kind"] in ("prop", "obstacle", "fuel"):
                self._draw_billboard(surface, item["prop_type"], sprite_x, sprite_y, scale, item["scale_mod"], view_w)
            elif item["kind"] == "car":
                self._draw_other_car(surface, item["car"], sprite_x, sprite_y, scale, view_w, track.palette.get("is_night", False))

        # ---------------------------------------------------------------------
        # STEP 5: PLAYER VEHICLE RENDERING
        # ---------------------------------------------------------------------
        self._render_player_car(surface, camera, player_car, view_w, view_h, track.palette.get("is_night", False))

    # =========================================================================
    # RASTERIZATION HELPERS
    # =========================================================================

    def _render_parallax_sky(self, surface, track, camera, base_seg, view_w, view_h):
        """Draws multi-layer parallax backdrop scrolled by road curvature."""
        if track.sky_surface:
            sky = track.sky_surface
            sky_w, sky_h = sky.get_size()
            # Parallax scroll factor based on lateral car position and road curve
            scroll_x = int((camera.x * 0.05 + base_seg.curve * 2.0)) % sky_w
            # Tile sky across viewport
            surface.blit(sky, (-scroll_x, 0))
            if sky_w - scroll_x < view_w:
                surface.blit(sky, (sky_w - scroll_x, 0))
        else:
            surface.fill(track.palette["sky_top"])

    def _render_segment_trapezoids(self, surface, x1, y1, w1, x2, y2, w2, color, view_w):
        """
        Renders the trapezoidal scanline slices for ground, rumble strips,
        asphalt surface, and lane divider dashes.
        CG Concept: Scanline Polygon Rasterization with Trapezoids.
        """
        h = y1 - y2
        if h <= 0:
            return

        # 1. Off-Road Ground Terrain (Full width backdrop)
        ground_poly = [(0, y2), (view_w, y2), (view_w, y1), (0, y1)]
        pygame.draw.polygon(surface, color["ground"], ground_poly)

        # Rumble strip curb widths
        r1 = max(2, int(w1 * 0.16))
        r2 = max(2, int(w2 * 0.16))

        # 2. Left Rumble Strip Curb
        rumble_left = [(x1 - w1 - r1, y1), (x1 - w1, y1), (x2 - w2, y2), (x2 - w2 - r2, y2)]
        pygame.draw.polygon(surface, color["rumble"], rumble_left)

        # 3. Right Rumble Strip Curb
        rumble_right = [(x1 + w1, y1), (x1 + w1 + r1, y1), (x2 + w2 + r2, y2), (x2 + w2, y2)]
        pygame.draw.polygon(surface, color["rumble"], rumble_right)

        # 4. Asphalt Road Surface
        road_poly = [(x1 - w1, y1), (x1 + w1, y1), (x2 + w2, y2), (x2 - w2, y2)]
        pygame.draw.polygon(surface, color["road"], road_poly)

        # 5. Lane Dashed Markings
        if color["lane"]:
            lw1 = max(1, int(w1 * 0.025))
            lw2 = max(1, int(w2 * 0.025))
            # Center lane dash
            lane_poly = [(x1 - lw1, y1), (x1 + lw1, y1), (x2 + lw2, y2), (x2 - lw2, y2)]
            pygame.draw.polygon(surface, color["lane"], lane_poly)

    def _draw_billboard(self, surface, prop_type, screen_x, screen_y, scale, scale_mod, view_w):
        """Scales and blits a billboard prop using perspective scaling."""
        sprite = self.prop_gen.get_prop(prop_type)
        sw, sh = sprite.get_size()

        # Perspective depth scaling normalized to road width
        # Target visual size = fraction of on-screen road width
        road_screen_w = scale * ROAD_WIDTH * (view_w / 2.0)
        # Billboard should be ~30% of road width, adjusted by source aspect ratio
        frac = 0.30 * scale_mod
        target_w = int(road_screen_w * frac)
        target_h = int(target_w * (sh / max(1, sw)))

        # Performance cap: prevent enormous sprites from killing FPS
        max_dim = 400
        if target_w > max_dim:
            target_h = int(target_h * max_dim / target_w)
            target_w = max_dim
        if target_h > max_dim:
            target_w = int(target_w * max_dim / target_h)
            target_h = max_dim

        if target_w < 2 or target_h < 2:
            return

        # Cache scaled surfaces to ensure high frame rate
        cache_key = (prop_type, target_w, target_h)
        if cache_key in self._scaled_prop_cache:
            scaled_surf = self._scaled_prop_cache[cache_key]
        else:
            scaled_surf = pygame.transform.smoothscale(sprite, (target_w, target_h))
            if len(self._scaled_prop_cache) < 600:
                self._scaled_prop_cache[cache_key] = scaled_surf

        dest_x = screen_x - target_w // 2
        dest_y = screen_y - target_h
        surface.blit(scaled_surf, (dest_x, dest_y))

    def _draw_other_car(self, surface, car, screen_x, screen_y, scale, view_w, is_night):
        """Draws opponent vehicle in 3D world with distance scaling and drop shadow."""
        car_sprite = car.get_rendered_sprite(is_night=is_night)
        cw, ch = car_sprite.get_size()

        # Scale other cars to ~40% of on-screen road width (matches player car size)
        road_screen_w = scale * ROAD_WIDTH * (view_w / 2.0)
        target_w = int(road_screen_w * 0.40)
        target_h = int(target_w * (ch / max(1, cw)))

        # Performance cap
        max_dim = 300
        if target_w > max_dim:
            target_h = int(target_h * max_dim / target_w)
            target_w = max_dim

        if target_w < 4 or target_h < 4:
            return

        scaled_car = pygame.transform.smoothscale(car_sprite, (target_w, target_h))
        dest_x = screen_x - target_w // 2
        dest_y = screen_y - target_h + int(target_h * 0.15)
        surface.blit(scaled_car, (dest_x, dest_y))

    def _render_player_car(self, surface, camera, car, view_w, view_h, is_night):
        """
        Renders the active player's vehicle at the bottom of their viewport.
        Applies camera height, scale preset, steer tilt, and night headlights.
        """
        # Dynamic car screen positioning based on camera preset (Normal/Front/Extended)
        car_screen_y = int(view_h * camera.car_y_ratio)
        car_center_x = int(view_w / 2.0 + (car.x * ROAD_WIDTH - camera.x) * 0.28 + (car.steer_angle * 1.5))

        # Collision flash effect
        if car.collision_timer > 0.0 and int(car.collision_timer * 20) % 2 == 0:
            # Flashing white on impact
            pass

        # Night track: render headlight light cones projected forward onto road
        if is_night:
            beam_surf = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
            # Left Headlight Beam Cone
            left_cone = [
                (car_center_x - 45, car_screen_y - 25),
                (car_center_x - 130, car_screen_y - 180),
                (car_center_x - 15, car_screen_y - 180)
            ]
            pygame.draw.polygon(beam_surf, (255, 255, 220, 45), left_cone)
            # Right Headlight Beam Cone
            right_cone = [
                (car_center_x + 45, car_screen_y - 25),
                (car_center_x + 15, car_screen_y - 180),
                (car_center_x + 130, car_screen_y - 180)
            ]
            pygame.draw.polygon(beam_surf, (255, 255, 220, 45), right_cone)
            surface.blit(beam_surf, (0, 0))

        # Retrieve procedural car sprite with steer tilt & brake lights
        car_sprite = car.get_rendered_sprite(is_night=is_night)
        cw, ch = car_sprite.get_size()

        # Scale based on camera zoom factor
        final_w = int(cw * camera.car_scale * (view_h / 720.0) * 1.55)
        final_h = int(ch * camera.car_scale * (view_h / 720.0) * 1.55)
        scaled_sprite = pygame.transform.smoothscale(car_sprite, (final_w, final_h))

        # Blit car centered above tires
        dest_x = car_center_x - final_w // 2
        dest_y = car_screen_y - final_h + 10
        surface.blit(scaled_sprite, (dest_x, dest_y))
