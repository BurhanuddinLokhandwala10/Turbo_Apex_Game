"""
Artificial Intelligence Racing Opponents
========================================
Implements road-aware racing AI with curve speed negotiation, dynamic lane
changing for overtaking, obstacle avoidance, and varied driving personalities.
"""

import math
import random
from game.car import Car
from game.settings import MAX_SPEED

class AICar:
    """An AI-controlled opponent vehicle."""

    def __init__(self, name="AI Driver", color=(240, 180, 0), initial_z=1000.0, initial_x=0.0, skill_level=0.85):
        self.car = Car(name=name, color=color, is_player=False)
        self.car.z = initial_z
        self.car.x = initial_x
        self.car.speed = 0.0

        # AI Driver Profile & Personality
        self.skill = skill_level  # 0.70 to 0.95
        self.target_speed = MAX_SPEED * (0.75 + 0.20 * self.skill)
        self.target_x = initial_x
        self.lane_change_cooldown = random.uniform(1.0, 3.0)
        self.wobble_phase = random.uniform(0.0, math.pi * 2)

    def update_ai(self, dt, track, all_cars):
        """
        Calculates AI steering, acceleration, and braking based on road curves
        and proximity to neighboring vehicles and obstacles.
        """
        if self.car.finished:
            self.car.update_physics(dt, 0.0, track.total_length)
            return

        current_segment = track.get_segment_at(self.car.z)
        current_curve = current_curve = current_segment.curve if current_segment else 0.0

        # 1. Curve Anticipation (Slow down into sharp turns)
        lookahead_z = (self.car.z + 1200.0) % track.total_length
        lookahead_seg = track.get_segment_at(lookahead_z)
        upcoming_curve = lookahead_seg.curve if lookahead_seg else 0.0

        curve_intensity = max(abs(current_curve), abs(upcoming_curve))
        # CG Physics: Cornering speed reduction formula
        speed_factor = 1.0 / (1.0 + (curve_intensity ** 1.3) * 0.40)
        effective_target_speed = self.target_speed * speed_factor

        # 2. Obstacle and Vehicle Detection (Radar Lookahead)
        self.lane_change_cooldown -= dt
        blocked_ahead = False
        scan_distance = 1800.0

        # Check other cars ahead
        for other in all_cars:
            if other is self.car:
                continue
            dz = (other.z - self.car.z) % track.total_length
            if 0 < dz < scan_distance and abs(other.x - self.car.x) < 0.45:
                blocked_ahead = True
                break

        # Check roadside/lane obstacles ahead
        if not blocked_ahead:
            for obs in track.obstacles:
                dz = (obs["z"] - self.car.z) % track.total_length
                if 0 < dz < scan_distance * 0.8 and abs(obs["x"] - self.car.x) < 0.35:
                    blocked_ahead = True
                    break

        # 3. Dynamic Lane Switching & Overtaking Logic
        if blocked_ahead and self.lane_change_cooldown <= 0.0:
            # Shift to adjacent open lane
            available_lanes = [-0.6, 0.0, 0.6]
            # Pick a lane different from current position
            candidate_lanes = [l for l in available_lanes if abs(l - self.car.x) > 0.3]
            if candidate_lanes:
                self.target_x = random.choice(candidate_lanes)
            self.lane_change_cooldown = random.uniform(2.0, 4.5)
        elif self.lane_change_cooldown <= 0.0 and random.random() < 0.05:
            # Gentle lane variation
            self.target_x = random.choice([-0.55, -0.2, 0.2, 0.55])
            self.lane_change_cooldown = random.uniform(3.0, 6.0)

        # 4. Apply Steering Inputs
        lane_error = self.target_x - self.car.x
        deadzone = 0.05
        if lane_error < -deadzone:
            self.car.steer_left_input = True
            self.car.steer_right_input = False
        elif lane_error > deadzone:
            self.car.steer_left_input = False
            self.car.steer_right_input = True
        else:
            self.car.steer_left_input = False
            self.car.steer_right_input = False

        # Keep AI firmly within track boundaries
        if self.car.x < -0.85:
            self.car.steer_left_input = False
            self.car.steer_right_input = True
            self.target_x = -0.4
        elif self.car.x > 0.85:
            self.car.steer_left_input = True
            self.car.steer_right_input = False
            self.target_x = 0.4

        # 5. Apply Throttle / Braking Inputs
        if self.car.speed < effective_target_speed:
            self.car.accel_input = True
            self.car.brake_input = False
        elif self.car.speed > effective_target_speed + 500.0:
            self.car.accel_input = False
            self.car.brake_input = True
        else:
            self.car.accel_input = False
            self.car.brake_input = False

        # 6. Step Car Physics
        self.car.update_physics(dt, current_curve, track.total_length)
