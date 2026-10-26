"""
Player Controller Module
========================
Handles keyboard input mappings for Single Player (dual WASD + Arrow schemes)
and Two Player split-screen (P1: WASD, P2: Arrows) modes.
"""

import pygame
from game.car import Car
from game.settings import CAMERA_MODES

class Player:
    """Wraps a Car instance with player input and camera management."""

    def __init__(self, player_id=1, name="Player 1", color=(225, 25, 35), is_two_player=False):
        self.player_id = player_id
        self.name = name
        self.is_two_player = is_two_player
        self.car = Car(name=name, color=color, is_player=True)

        # Camera selection state
        self.camera_index = 0
        self.camera_mode = CAMERA_MODES[self.camera_index]

        # Floating HUD Popups (e.g. "+20 FUEL")
        self.floating_popups = []

    def handle_input(self, keys):
        """Processes continuous keyboard state."""
        accel = False
        brake = False
        left = False
        right = False

        if not self.is_two_player:
            # SINGLE PLAYER: Both WASD AND Arrow keys work simultaneously!
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                accel = True
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                brake = True
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                left = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                right = True
        else:
            # TWO PLAYER SPLIT SCREEN: Dedicated control schemes
            if self.player_id == 1:
                # Player 1: WASD
                if keys[pygame.K_w]:
                    accel = True
                if keys[pygame.K_s]:
                    brake = True
                if keys[pygame.K_a]:
                    left = True
                if keys[pygame.K_d]:
                    right = True
            else:
                # Player 2: Arrow keys
                if keys[pygame.K_UP]:
                    accel = True
                if keys[pygame.K_DOWN]:
                    brake = True
                if keys[pygame.K_LEFT]:
                    left = True
                if keys[pygame.K_RIGHT]:
                    right = True

        self.car.accel_input = accel
        self.car.brake_input = brake
        self.car.steer_left_input = left
        self.car.steer_right_input = right

    def cycle_camera(self):
        """Cycles through the 3 camera modes: Normal -> Front -> Extended -> Normal."""
        self.camera_index = (self.camera_index + 1) % len(CAMERA_MODES)
        self.camera_mode = CAMERA_MODES[self.camera_index]
        return self.camera_mode["id"]

    def add_floating_popup(self, text, color=(40, 235, 120)):
        """Queues a floating text notification for HUD rendering."""
        self.floating_popups.append({
            "text": text,
            "color": color,
            "timer": 1.5,
            "max_timer": 1.5,
            "y_offset": 0.0
        })

    def update_popups(self, dt):
        """Updates animation of floating notifications."""
        for p in self.floating_popups:
            p["timer"] -= dt
            p["y_offset"] += 35.0 * dt
        self.floating_popups = [p for p in self.floating_popups if p["timer"] > 0]
