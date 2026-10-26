"""
Main Game Controller & State Dispatcher
=======================================
Coordinates Pygame initialization, display management, delta-time clock,
audio manager, player allocation, and finite state machine transitions.
"""

import sys
import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    CAR_COLORS, CAMERA_MODES
)
from game.player import Player
from game.ai import AICar
from game.track import Track
from game.camera import Camera
from game.sound import SoundManager
from game.states import (
    MainMenuState, MapSelectionState, HowToPlayState,
    RacingState, PausedState, ResultsState
)
from maps.beach import BeachMap

class Game:
    """Central game orchestrator."""

    def __init__(self):
        pygame.init()
        pygame.font.init()

        # Window & Display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Audio
        self.sound_manager = SoundManager.get_instance()

        # Match Configuration
        self.mode = "SINGLE"  # "SINGLE" or "TWO_PLAYER"
        self.selected_map_class = BeachMap
        self.track = None
        self.players = []
        self.ai_cars = []
        self.cameras = []

        # State Machine Initialization
        self.states = {}
        self.current_state = None
        self._init_states()
        self.change_state("MAIN_MENU")

    def _init_states(self):
        """Constructs available states."""
        self.states["MAIN_MENU"] = MainMenuState(self)
        self.states["MAP_SELECTION"] = MapSelectionState(self)
        self.states["HOW_TO_PLAY"] = HowToPlayState(self)
        self.states["PAUSED"] = PausedState(self)
        self.states["RESULTS"] = ResultsState(self)

    def change_state(self, state_name):
        """Transitions to another state."""
        if state_name in self.states:
            self.current_state = self.states[state_name]

    def start_race(self):
        """Initializes a new race with chosen mode and track."""
        # 1. Load Track
        self.track = Track()
        # Instantiate selected map
        self.track.map = self.selected_map_class()
        self.track.segments = self.track.map.segments
        self.track.total_length = self.track.map.total_length
        self.track.total_segments = self.track.map.total_segments
        self.track.obstacles = self.track.map.obstacles
        self.track.fuel_pickups = self.track.map.fuel_pickups
        self.track.minimap_points = self.track.map.minimap_points
        self.track.palette = self.track.map.palette
        self.track.sky_surface = self.track.map.sky_surface

        # 2. Allocate Players & Cameras
        self.players = []
        self.cameras = []

        if self.mode == "SINGLE":
            # Single Player (Dual WASD + Arrow controls)
            p1 = Player(player_id=1, name="Player 1", color=CAR_COLORS["PLAYER_1"], is_two_player=False)
            p1.car.z = 0.0
            p1.car.x = 0.0
            self.players.append(p1)
            self.cameras.append(Camera(CAMERA_MODES[0]))

            # 5 AI Competitors
            self.ai_cars = [
                AICar("Apex Falcon", CAR_COLORS["AI_1"], initial_z=350.0, initial_x=-0.45, skill_level=0.92),
                AICar("Viper Strike", CAR_COLORS["AI_2"], initial_z=600.0, initial_x=0.45, skill_level=0.88),
                AICar("Thunder Storm", CAR_COLORS["AI_3"], initial_z=900.0, initial_x=-0.20, skill_level=0.84),
                AICar("Shadow Runner", CAR_COLORS["AI_4"], initial_z=1200.0, initial_x=0.20, skill_level=0.80),
                AICar("Cyber Phantom", CAR_COLORS["AI_5"], initial_z=1500.0, initial_x=-0.50, skill_level=0.76)
            ]
        else:
            # Two Player Split-Screen
            p1 = Player(player_id=1, name="Player 1", color=CAR_COLORS["PLAYER_1"], is_two_player=True)
            p1.car.z = 0.0
            p1.car.x = -0.35
            self.players.append(p1)
            self.cameras.append(Camera(CAMERA_MODES[0]))

            p2 = Player(player_id=2, name="Player 2", color=CAR_COLORS["PLAYER_2"], is_two_player=True)
            p2.car.z = 0.0
            p2.car.x = 0.35
            self.players.append(p2)
            self.cameras.append(Camera(CAMERA_MODES[0]))

            # 4 AI Competitors
            self.ai_cars = [
                AICar("Apex Falcon", CAR_COLORS["AI_1"], initial_z=450.0, initial_x=-0.45, skill_level=0.90),
                AICar("Viper Strike", CAR_COLORS["AI_2"], initial_z=750.0, initial_x=0.45, skill_level=0.85),
                AICar("Thunder Storm", CAR_COLORS["AI_3"], initial_z=1100.0, initial_x=0.0, skill_level=0.82),
                AICar("Shadow Runner", CAR_COLORS["AI_4"], initial_z=1450.0, initial_x=-0.30, skill_level=0.78)
            ]

        # 3. Create fresh RacingState
        self.states["RACING"] = RacingState(self)
        self.change_state("RACING")

    def run(self):
        """Main game loop ticking at target 60 FPS."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Prevent spiral of death on long lag spike
            dt = min(0.05, dt)

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    if self.current_state:
                        self.current_state.handle_event(event)

            # State Logic Update
            if self.current_state:
                self.current_state.update(dt)

            # State Frame Render
            if self.current_state:
                self.current_state.render(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()
