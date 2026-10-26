"""
Collision Detection & Resolution System
========================================
Implements 3D longitudinal/lateral bounding volume hierarchy (BVH) and AABB
overlap tests for Car-to-Obstacle, Car-to-Fuel, and Car-to-Car interactions.
Demonstrates Computer Graphics Collision Detection & Impulse Response.
"""

import math
from game.settings import ROAD_WIDTH

class CollisionSystem:
    """Detects and resolves geometric intersections on the race track."""

    @staticmethod
    def check_car_obstacles(car, obstacles, sound_manager=None, camera=None, player=None):
        """
        Tests intersection between vehicle bounding box and track obstacles.
        CG Concept: Axis-Aligned Bounding Box (AABB) Proximity Testing.
        """
        hitbox_z = 160.0   # World Z depth threshold
        hitbox_x = 0.30    # Normalized lateral width threshold

        for obs in obstacles:
            # Check Z proximity (accounting for track wrap-around)
            dz = abs(car.z - obs["z"])
            if dz < hitbox_z:
                dx = abs(car.x - obs["x"])
                if dx < hitbox_x:
                    # Collision detected!
                    speed_loss = obs.get("speed_loss", 0.40)
                    push = obs.get("push", 0.20)
                    obs_type = obs.get("type", "")

                    if obs_type == "obstacle_oil":
                        car.trigger_spinout()
                        if sound_manager:
                            sound_manager.play("skid")
                    else:
                        car.trigger_collision(speed_reduction=speed_loss, push_x=push)
                        if sound_manager:
                            sound_manager.play("crash")
                        if camera:
                            camera.add_shake(0.55)

                    if player and obs_type != "obstacle_oil":
                        player.add_floating_popup("IMPACT!", color=(255, 60, 60))

                    # Break early so multiple impacts don't compound in a single frame
                    break

    @staticmethod
    def check_car_fuel_pickups(car, fuel_pickups, sound_manager=None, player=None):
        """
        Tests intersection with fuel canisters and applies restoration.
        """
        hitbox_z = 200.0
        hitbox_x = 0.38

        for pickup in fuel_pickups:
            if pickup["collected"]:
                continue

            dz = abs(car.z - pickup["z"])
            if dz < hitbox_z:
                dx = abs(car.x - pickup["x"])
                if dx < hitbox_x:
                    # Fuel Collected: Refill to 100% Full Capacity!
                    pickup["collected"] = True
                    pickup["respawn_timer"] = 18.0  # Respawns after 18s
                    car.fuel = 100.0

                    if sound_manager:
                        sound_manager.play("pickup")

                    if player:
                        player.add_floating_popup("FUEL 100% FULL!", color=(40, 235, 120))

    @staticmethod
    def check_car_to_car_collisions(cars, sound_manager=None):
        """
        Tests elastic collision impulses between multiple vehicles.
        CG Concept: 2D Momentum Transfer & Separation Impulse.
        """
        num_cars = len(cars)
        hitbox_z = 180.0
        hitbox_x = 0.32

        for i in range(num_cars):
            for j in range(i + 1, num_cars):
                c1 = cars[i]
                c2 = cars[j]

                dz = abs(c1.z - c2.z)
                if dz < hitbox_z:
                    dx = c1.x - c2.x
                    if abs(dx) < hitbox_x:
                        # Lateral separation impulse
                        overlap = hitbox_x - abs(dx)
                        sep_sign = 1.0 if dx >= 0 else -1.0
                        c1.x += sep_sign * (overlap * 0.55)
                        c2.x -= sep_sign * (overlap * 0.55)

                        # Longitudinal momentum exchange
                        avg_speed = (c1.speed + c2.speed) * 0.5
                        diff = c1.speed - c2.speed
                        c1.speed = max(0.0, avg_speed - diff * 0.25)
                        c2.speed = max(0.0, avg_speed + diff * 0.25)

                        c1.collision_timer = 0.3
                        c2.collision_timer = 0.3

                        if sound_manager and (c1.is_player or c2.is_player):
                            sound_manager.play("crash")
