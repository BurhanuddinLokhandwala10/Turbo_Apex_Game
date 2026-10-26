"""
Camera System with Dynamic Modes & Smooth Interpolation
======================================================
Implements smooth vehicle following, spring damping, collision trauma
shake, and three distinct switchable perspective viewpoints:
1. NORMAL   - Standard 3rd-person arcade chase camera
2. FRONT    - Low-angle high-speed hood/bumper view
3. EXTENDED - High-altitude wide-angle turn-anticipation camera
"""

import math
import random
from game.settings import ROAD_WIDTH, CAMERA_DEPTH

class Camera:
    """Manages 3D virtual eye position, orientation, and shake effects."""

    def __init__(self, mode_config):
        self.mode_id = mode_config["id"]
        self.mode_name = mode_config["name"]

        # 3D World Space Camera Position
        self.x = 0.0
        self.y = float(mode_config["height"])
        self.z = 0.0
        self.depth = float(mode_config["depth"])

        # Target interpolation for seamless camera mode transitions
        self.target_y = float(mode_config["height"])
        self.target_depth = float(mode_config["depth"])
        self.car_y_ratio = float(mode_config["car_y"])
        self.target_car_y_ratio = float(mode_config["car_y"])
        self.car_scale = float(mode_config["car_scale"])
        self.target_car_scale = float(mode_config["car_scale"])

        # Collision Camera Shake (Trauma)
        self.trauma = 0.0
        self.shake_x = 0.0
        self.shake_y = 0.0

    def apply_preset(self, mode_config):
        """Smoothly transitions camera parameters to a new preset."""
        self.mode_id = mode_config["id"]
        self.mode_name = mode_config["name"]
        self.target_y = float(mode_config["height"])
        self.target_depth = float(mode_config["depth"])
        self.target_car_y_ratio = float(mode_config["car_y"])
        self.target_car_scale = float(mode_config["car_scale"])

    def add_shake(self, amount=0.5):
        """Adds trauma for screen vibration on impact."""
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt, car, current_segment_y=0.0):
        """
        Updates camera tracking with smooth spring-damper following (lerp).
        CG Concept: View Matrix Translation and Camera Tracking.
        """
        # Smooth mode transition interpolation
        lerp_speed = 7.0 * dt
        self.y += (self.target_y - self.y) * min(1.0, lerp_speed)
        self.depth += (self.target_depth - self.depth) * min(1.0, lerp_speed)
        self.car_y_ratio += (self.target_car_y_ratio - self.car_y_ratio) * min(1.0, lerp_speed)
        self.car_scale += (self.target_car_scale - self.car_scale) * min(1.0, lerp_speed)

        # Smooth lateral camera following (slight lag creates sensation of momentum)
        target_cam_x = car.x * ROAD_WIDTH
        follow_rate = 9.0 * dt
        self.x += (target_cam_x - self.x) * min(1.0, follow_rate)

        # Camera longitudinal position (Locks with car distance)
        self.z = car.z

        # Camera altitude relative to track elevation (hills/valleys)
        # self.y tracks elevation + camera height
        base_altitude = current_segment_y + self.y

        # Screen Shake trauma decay
        if self.trauma > 0.0:
            shake_intensity = (self.trauma ** 2) * 25.0
            self.shake_x = (random.random() * 2.0 - 1.0) * shake_intensity
            self.shake_y = (random.random() * 2.0 - 1.0) * shake_intensity
            self.trauma = max(0.0, self.trauma - 2.5 * dt)
        else:
            self.shake_x = 0.0
            self.shake_y = 0.0
