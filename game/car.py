"""
Car Physics & Procedural Rendering Engine
=========================================
Implements realistic arcade vehicle dynamics (acceleration, braking,
friction, centrifugal inertia, fuel depletion) and procedural 2D/3D sprite
generation demonstrating Computer Graphics affine transformations.
"""

import math
import pygame
from game.settings import (
    MAX_SPEED, ACCELERATION, BRAKING_FORCE, NATURAL_DECEL,
    OFFROAD_DECEL, OFFROAD_LIMIT, STEER_SPEED, CENTRIFUGAL,
    INITIAL_FUEL, FUEL_BURN_BASE, FUEL_BURN_SPEED, EMPTY_SPEED_LIMIT,
    LOW_FUEL_LIMIT, ROAD_WIDTH, TOTAL_LAPS, COLOR_WHITE, COLOR_BLACK
)

class Car:
    """Represents a racing vehicle with physics and procedural graphics."""

    def __init__(self, name="Racer", color=(220, 30, 40), stripe_color=(255, 255, 255), is_player=True):
        self.name = name
        self.color = color
        self.stripe_color = stripe_color
        self.is_player = is_player

        # Spatial Coordinates (World Space)
        # z: longitudinal distance along the track [0, total_track_length]
        # x: normalized lateral position (-1.0 = left edge, 0.0 = center, +1.0 = right edge)
        self.z = 0.0
        self.x = 0.0
        self.speed = 0.0
        self.max_speed = MAX_SPEED
        self.steer_angle = 0.0  # Visual chassis tilt in degrees for CG transformation

        # Fuel State
        self.fuel = INITIAL_FUEL
        self.low_fuel_warning = False

        # Race Progress
        self.lap = 1
        self.total_laps = TOTAL_LAPS
        self.current_lap_time = 0.0
        self.best_lap_time = None
        self.total_race_time = 0.0
        self.finished = False
        self.rank = 1

        # Control & State Flags
        self.accel_input = False
        self.brake_input = False
        self.steer_left_input = False
        self.steer_right_input = False
        self.is_offroad = False
        self.collision_timer = 0.0  # Camera shake / flash recovery
        self.spinout_timer = 0.0     # Loss of traction (oil slick)

        # Procedural Sprite Cache
        self._sprite_cache = {}
        self._render_width = 150
        self._render_height = 80

    def update_physics(self, dt, current_curve, track_length):
        """
        Updates vehicle kinematics with delta-time.
        Demonstrates physics simulation:
        v(t+dt) = v(t) + a * dt - drag * dt
        """
        if self.finished:
            # Gradual deceleration after finish line
            self.speed = max(0.0, self.speed - NATURAL_DECEL * dt)
            self.z = (self.z + self.speed * dt) % track_length
            return

        # 1. Spinout recovery handling (e.g. from oil slicks)
        if self.spinout_timer > 0.0:
            self.spinout_timer -= dt
            self.speed = max(0.0, self.speed - BRAKING_FORCE * 0.7 * dt)
            self.steer_angle += 720.0 * dt  # 360 spin animation
            self.z = (self.z + self.speed * dt) % track_length
            self._update_fuel(dt)
            return

        # 2. Track boundary and off-road physics
        self.is_offroad = abs(self.x) > 1.05
        effective_max_speed = self.max_speed

        if self.fuel <= 0.0:
            # Fuel starvation: Limp mode
            effective_max_speed = min(effective_max_speed, EMPTY_SPEED_LIMIT)
        elif self.is_offroad:
            # Off-road grass/sand surface drag
            effective_max_speed = min(effective_max_speed, OFFROAD_LIMIT)

        # 3. Longitudinal Acceleration & Deceleration
        if self.accel_input and self.fuel > 0.0:
            # Acceleration
            self.speed += ACCELERATION * dt
        elif self.brake_input:
            # Active Braking
            self.speed -= BRAKING_FORCE * dt
        else:
            # Natural rolling resistance / air drag
            drag = OFFROAD_DECEL if self.is_offroad else NATURAL_DECEL
            self.speed -= drag * dt

        # Cap speed boundaries
        self.speed = max(0.0, min(self.speed, effective_max_speed))

        # 4. Lateral Steering & Centrifugal Force (Computer Graphics Dynamics)
        speed_ratio = (self.speed / self.max_speed) if self.max_speed > 0 else 0
        target_tilt = 0.0

        # Smooth steering authority: nicely controlled and not overly sensitive
        steer_authority = 0.50 + 0.25 * speed_ratio

        if self.steer_left_input:
            target_tilt = -6.0
            self.x -= STEER_SPEED * steer_authority * dt
            if self.speed > 50:
                self.speed -= 200.0 * speed_ratio * dt
        elif self.steer_right_input:
            target_tilt = 6.0
            self.x += STEER_SPEED * steer_authority * dt
            if self.speed > 50:
                self.speed -= 200.0 * speed_ratio * dt

        # Boundary clamping to keep car on or near the track
        self.x = max(-1.60, min(1.60, self.x))

        # Centrifugal force pushing car outward on curved tracks
        if self.speed > 80:
            centrifugal_push = current_curve * CENTRIFUGAL * (speed_ratio ** 1.3) * dt
            self.x -= centrifugal_push
            self.x = max(-1.80, min(1.80, self.x))

        # Smooth Chassis Tilt Interpolation (Visual steer response)
        tilt_lerp_rate = 18.0 * dt
        self.steer_angle += (target_tilt - self.steer_angle) * min(1.0, tilt_lerp_rate)

        # 5. Longitudinal World Position Update
        prev_z = self.z
        self.z += self.speed * dt

        # Lap completion detection (Segment wrap-around)
        if prev_z > track_length * 0.9 and self.z >= track_length:
            self._complete_lap()
        self.z = self.z % track_length

        # 6. Fuel Depletion Dynamics
        self._update_fuel(dt)

        # 7. Timers
        if self.collision_timer > 0.0:
            self.collision_timer = max(0.0, self.collision_timer - dt)

        self.current_lap_time += dt
        self.total_race_time += dt

    def _update_fuel(self, dt):
        """Simulates fuel consumption proportional to throttle and speed."""
        burn_rate = FUEL_BURN_BASE
        if self.accel_input and self.speed > 100:
            speed_factor = self.speed / self.max_speed
            burn_rate += FUEL_BURN_SPEED * speed_factor

        self.fuel = max(0.0, self.fuel - burn_rate * dt)
        self.low_fuel_warning = (0.0 < self.fuel <= LOW_FUEL_LIMIT)

    def add_fuel(self, amount):
        """Adds fuel from a collected canister."""
        self.fuel = min(100.0, self.fuel + amount)

    def trigger_collision(self, speed_reduction=0.45, push_x=0.0):
        """Applies physical collision impulse."""
        self.speed = max(0.0, self.speed * (1.0 - speed_reduction))
        self.x += push_x
        self.collision_timer = 0.45
        # Minor fuel tank impact loss
        self.fuel = max(0.0, self.fuel - 2.5)

    def trigger_spinout(self):
        """Triggers a 360-degree spinout (e.g. hitting oil slicks)."""
        self.spinout_timer = 0.85
        self.speed *= 0.4

    def _complete_lap(self):
        """Handles lap advancement."""
        lap_time = self.current_lap_time
        if self.best_lap_time is None or lap_time < self.best_lap_time:
            self.best_lap_time = lap_time

        self.lap += 1
        self.current_lap_time = 0.0

        if self.lap > self.total_laps:
            self.finished = True

    def get_speed_kmh(self):
        """Converts internal world units to displayed KM/H."""
        # Scale: MAX_SPEED (12000) corresponds to 240 KM/H
        return int((self.speed / self.max_speed) * 240.0)

    # =========================================================================
    # COMPUTER GRAPHICS: PROCEDURAL CAR RENDERING WITH 2D AFFINE ROTATION
    # =========================================================================

    def get_rendered_sprite(self, is_night=False):
        """
        Returns a high-detail procedural sports car sprite with:
        - Layered aerodynamic chassis
        - Window tinted reflections
        - Racing stripes & spoiler
        - Dynamic glowing brake lights when decelerating
        - Wheels and under-body shadow
        - 2D affine rotation matrix for steer tilt
        """
        brake_state = self.brake_input
        tilt_key = round(self.steer_angle, 1)
        cache_key = (self.color, brake_state, tilt_key, is_night)

        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        w, h = self._render_width, self._render_height
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        # 1. Under-body Drop Shadow (Semi-transparent black ellipse)
        shadow_rect = pygame.Rect(12, h - 18, w - 24, 16)
        pygame.draw.ellipse(surface, (0, 0, 0, 140), shadow_rect)

        # 2. Racing Wheels / Wide Tires (Black rubber with silver rim highlights)
        # Left Tire
        pygame.draw.rect(surface, (20, 20, 20), (8, h - 42, 22, 36), border_radius=5)
        pygame.draw.rect(surface, (70, 70, 75), (10, h - 38, 7, 28), border_radius=2)
        # Right Tire
        pygame.draw.rect(surface, (20, 20, 20), (w - 30, h - 42, 22, 36), border_radius=5)
        pygame.draw.rect(surface, (70, 70, 75), (w - 17, h - 38, 7, 28), border_radius=2)

        # 3. Main Car Body (Lower rear chassis)
        body_points = [
            (20, h - 14),             # Bottom left
            (w - 20, h - 14),         # Bottom right
            (w - 18, h - 42),         # Mid right fender
            (w - 28, h - 54),         # Upper right shoulder
            (28, h - 54),             # Upper left shoulder
            (18, h - 42),             # Mid left fender
        ]
        pygame.draw.polygon(surface, self.color, body_points)

        # Darker bevel / bottom bumper diffuser
        diffuser_rect = pygame.Rect(26, h - 22, w - 52, 10)
        pygame.draw.rect(surface, (18, 18, 22), diffuser_rect, border_radius=3)
        # Dual Chrome Exhaust Pipes
        pygame.draw.circle(surface, (190, 190, 200), (38, h - 17), 4)
        pygame.draw.circle(surface, (30, 30, 30), (38, h - 17), 2)
        pygame.draw.circle(surface, (190, 190, 200), (w - 38, h - 17), 4)
        pygame.draw.circle(surface, (30, 30, 30), (w - 38, h - 17), 2)

        # 4. Aerodynamic Cabin / Roof & Tinted Rear Window
        cabin_points = [
            (34, h - 52),             # Cabin base left
            (w - 34, h - 52),         # Cabin base right
            (w - 44, h - 74),         # Roof top right
            (44, h - 74),             # Roof top left
        ]
        # Roof color (Slightly lighter shade of primary color)
        roof_color = tuple(min(255, c + 25) for c in self.color)
        pygame.draw.polygon(surface, roof_color, cabin_points)

        # Rear Window Glass (Tinted dark cyan-black)
        window_points = [
            (38, h - 53),
            (w - 38, h - 53),
            (w - 47, h - 72),
            (47, h - 72),
        ]
        pygame.draw.polygon(surface, (25, 38, 50), window_points)
        # Glass reflection shine line
        pygame.draw.line(surface, (140, 180, 210, 180), (52, h - 70), (w - 58, h - 55), 2)

        # 5. Dual Center Racing Stripes
        stripe_w = 7
        gap = 4
        cx = w // 2
        # On cabin roof
        pygame.draw.rect(surface, self.stripe_color, (cx - stripe_w - gap // 2, h - 74, stripe_w, 22))
        pygame.draw.rect(surface, self.stripe_color, (cx + gap // 2, h - 74, stripe_w, 22))
        # On rear trunk
        pygame.draw.rect(surface, self.stripe_color, (cx - stripe_w - gap // 2, h - 52, stripe_w, 30))
        pygame.draw.rect(surface, self.stripe_color, (cx + gap // 2, h - 52, stripe_w, 30))

        # 6. High-Mount GT Rear Spoiler / Wing
        # Spoiler struts
        pygame.draw.rect(surface, (30, 30, 35), (42, h - 68, 6, 16))
        pygame.draw.rect(surface, (30, 30, 35), (w - 48, h - 68, 6, 16))
        # Spoiler wing blade
        wing_color = (20, 20, 25)
        pygame.draw.rect(surface, wing_color, (22, h - 76, w - 44, 8), border_radius=2)
        # Wing endplates
        pygame.draw.rect(surface, self.color, (20, h - 80, 5, 14), border_radius=2)
        pygame.draw.rect(surface, self.color, (w - 25, h - 80, 5, 14), border_radius=2)

        # 7. Rear Tail Lights & Brake Lights
        # Left tail light
        tail_left = pygame.Rect(26, h - 48, 22, 10)
        tail_right = pygame.Rect(w - 48, h - 48, 22, 10)

        if brake_state:
            # Active Braking: Blazing Neon Red with Bloom Glow
            pygame.draw.rect(surface, (255, 30, 30), tail_left, border_radius=3)
            pygame.draw.rect(surface, (255, 30, 30), tail_right, border_radius=3)
            # Inner white-hot filament
            pygame.draw.rect(surface, (255, 230, 230), (tail_left.x + 4, tail_left.y + 2, 14, 6), border_radius=2)
            pygame.draw.rect(surface, (255, 230, 230), (tail_right.x + 4, tail_right.y + 2, 14, 6), border_radius=2)
            # Halo glow circle
            pygame.draw.circle(surface, (255, 60, 60, 110), tail_left.center, 15)
            pygame.draw.circle(surface, (255, 60, 60, 110), tail_right.center, 15)
        else:
            # Running lights: Deep ruby red
            pygame.draw.rect(surface, (170, 20, 25), tail_left, border_radius=3)
            pygame.draw.rect(surface, (170, 20, 25), tail_right, border_radius=3)
            pygame.draw.rect(surface, (240, 70, 75), (tail_left.x + 3, tail_left.y + 2, 16, 3), border_radius=1)
            pygame.draw.rect(surface, (240, 70, 75), (tail_right.x + 3, tail_right.y + 2, 16, 3), border_radius=1)

        # 8. License Plate & Model Badge
        plate_rect = pygame.Rect(cx - 16, h - 36, 32, 10)
        pygame.draw.rect(surface, (230, 230, 230), plate_rect, border_radius=2)
        pygame.draw.rect(surface, (20, 20, 25), (plate_rect.x + 3, plate_rect.y + 3, 26, 4))

        # 9. Computer Graphics: 2D Affine Rotation Transformation
        # Rotates sprite according to chassis steer tilt angle
        if abs(tilt_key) > 0.1:
            rotated_surface = pygame.transform.rotate(surface, -tilt_key)
        else:
            rotated_surface = surface

        self._sprite_cache[cache_key] = rotated_surface
        return rotated_surface
