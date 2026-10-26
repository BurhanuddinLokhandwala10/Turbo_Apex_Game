"""
Game Settings and Constants
===========================
Configures display resolution, physics parameters, color schemes,
and camera modes for the Computer Graphics Car Racing Game.
"""

import pygame

# Window & Rendering
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "TURBO APEX - Computer Graphics Racing Championship"

# Road & World Geometry (Units in world coordinates)
ROAD_WIDTH = 2200          # Virtual width of the race track
SEGMENT_LENGTH = 200       # World Z-distance per road segment
RUMBLE_LENGTH = 3          # Segments per alternating rumble color stripe
LANES = 3                  # Number of visible driving lanes
DRAW_DISTANCE = 120        # How many segments to project into the horizon
FIELD_OF_VIEW = 100        # Camera FOV degrees
CAMERA_DEPTH = 0.84        # Camera perspective depth = 1 / tan(FOV/2)

# Physics & Car Dynamics
MAX_SPEED = 12000.0        # Max forward speed (units/sec, maps to ~240 KM/H)
ACCELERATION = 4200.0      # Forward acceleration (units/sec^2)
BRAKING_FORCE = 8500.0     # Braking deceleration (units/sec^2)
NATURAL_DECEL = 1800.0     # Natural rolling drag when coasting
OFFROAD_DECEL = 4800.0     # High friction drag on grass/sand/curb
OFFROAD_LIMIT = 3200.0     # Maximum speed allowed off-track
STEER_SPEED = 1.8          # Smooth, controlled lateral steering rate
CENTRIFUGAL = 0.16         # Balanced lateral inertia pulling car around curves

# Fuel Dynamics
INITIAL_FUEL = 100.0       # Starting fuel percentage
FUEL_BURN_BASE = 0.25      # Fuel burn per second at idle
FUEL_BURN_SPEED = 1.85     # Additional fuel burn at maximum throttle
LOW_FUEL_LIMIT = 25.0      # Threshold for low fuel warning
FUEL_PICKUP_AMOUNT = 100.0 # Fuel restored to 100% full capacity per canister
EMPTY_SPEED_LIMIT = 2600.0 # Maximum limp speed when out of fuel (~52 KM/H)

# Race System
TOTAL_LAPS = 3             # Standard race length
COUNTDOWN_SECONDS = 2.4    # Snappy 3.. 2.. 1.. GO! duration

# Camera Mode Presets
# Mode specifications: (Name, camera_height, fov_depth, car_screen_y_pct, description)
CAMERA_MODES = [
    {
        "id": "NORMAL",
        "name": "NORMAL (3rd Person)",
        "height": 1050,
        "depth": 0.84,
        "car_y": 0.86,
        "car_scale": 1.0,
        "desc": "Standard chase camera with balanced track view"
    },
    {
        "id": "FRONT",
        "name": "FRONT (Low / Chase)",
        "height": 720,
        "depth": 0.92,
        "car_y": 0.93,
        "car_scale": 1.15,
        "desc": "Low-angle high-speed hood chase camera"
    },
    {
        "id": "EXTENDED",
        "name": "EXTENDED (High / Wide)",
        "height": 1450,
        "depth": 0.76,
        "car_y": 0.78,
        "car_scale": 0.88,
        "desc": "Elevated panoramic view for anticipating sharp turns"
    }
]

# Color Palettes (RGB Tuples)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY_DARK = (30, 30, 35)
COLOR_GRAY_LIGHT = (180, 180, 190)

# UI Theme
UI_BG_DARK = (15, 18, 28)
UI_PANEL_BG = (24, 28, 44, 230)
UI_PANEL_BORDER = (55, 65, 95)
UI_ACCENT_CYAN = (0, 220, 255)
UI_ACCENT_GOLD = (255, 195, 0)
UI_ACCENT_RED = (255, 55, 75)
UI_ACCENT_GREEN = (40, 225, 120)
UI_TEXT_MUTED = (160, 170, 190)

# Car Colors (RGB)
CAR_COLORS = {
    "PLAYER_1": (225, 25, 35),      # Crimson Red
    "PLAYER_2": (20, 140, 255),     # Cobalt Blue
    "AI_1": (245, 180, 0),          # Racing Gold
    "AI_2": (35, 205, 90),          # Emerald Green
    "AI_3": (255, 90, 0),           # Blaze Orange
    "AI_4": (175, 45, 235),         # Deep Violet
    "AI_5": (0, 215, 215),          # Neon Cyan
    "AI_6": (230, 230, 240)         # Arctic White
}
