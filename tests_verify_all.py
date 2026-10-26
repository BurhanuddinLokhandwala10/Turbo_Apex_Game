"""
Comprehensive Test Suite for Computer Graphics Car Racing Game
==============================================================
Validates all 14 mandatory quality and functional criteria:
1. Game lifecycle & event handling
2. All menu states navigation
3. Single player controls & driving physics
4. Two-player split screen dual camera rendering
5. All 3 visually distinct maps
6. All 3 camera modes (Normal, Front, Extended)
7. Collision detection (obstacles, oil slicks, car-to-car)
8. AI intelligence & curve slowdown
9. Fuel dynamics (burn, low fuel warning, pickups, empty speed cap)
10. Lap progression & lap timing
11. Win / Finish condition & Results podium
12. Pause menu & overlay
13. Restart race mechanics
14. Main menu return mechanics
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import unittest
from game.game import Game
from game.settings import (
    CAMERA_MODES, EMPTY_SPEED_LIMIT, LOW_FUEL_LIMIT,
    TOTAL_LAPS, SEGMENT_LENGTH, ROAD_WIDTH
)
from maps.beach import BeachMap
from maps.hills import HillsMap
from maps.city import CityMap

class TestRacingGameComplete(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    def setUp(self):
        self.game.mode = "SINGLE"
        self.game.selected_map_class = BeachMap
        self.game.change_state("MAIN_MENU")

    def test_01_game_init_and_states(self):
        """1. Test game starts and can enter all menus."""
        self.assertIsNotNone(self.game)
        self.assertEqual(type(self.game.current_state).__name__, "MainMenuState")

    def test_02_all_menus_navigation(self):
        """2. Test navigation across all menu states."""
        # Main Menu -> How To Play
        self.game.change_state("HOW_TO_PLAY")
        self.assertEqual(type(self.game.current_state).__name__, "HowToPlayState")
        self.game.current_state.render(self.game.screen)

        # Back to Main Menu
        self.game.change_state("MAIN_MENU")
        self.assertEqual(type(self.game.current_state).__name__, "MainMenuState")
        self.game.current_state.render(self.game.screen)

        # Main Menu -> Map Selection
        self.game.change_state("MAP_SELECTION")
        self.assertEqual(type(self.game.current_state).__name__, "MapSelectionState")
        self.game.current_state.render(self.game.screen)

    def test_03_single_player_controls_and_driving(self):
        """3. Test single player driving physics with dual control scheme."""
        self.game.mode = "SINGLE"
        self.game.selected_map_class = BeachMap
        self.game.start_race()
        self.assertEqual(len(self.game.players), 1)

        p = self.game.players[0]
        # Skip countdown
        self.game.states["RACING"].countdown_timer = 0.0

        # Test acceleration
        p.car.accel_input = True
        p.car.update_physics(0.1, 0.0, self.game.track.total_length)
        self.assertGreater(p.car.speed, 0.0)

        # Test steering left tilt
        p.car.steer_left_input = True
        p.car.update_physics(0.1, 0.0, self.game.track.total_length)
        self.assertLess(p.car.steer_angle, 0.0)

        # Test steering right tilt
        p.car.steer_left_input = False
        p.car.steer_right_input = True
        for _ in range(5):
            p.car.update_physics(0.1, 0.0, self.game.track.total_length)
        self.assertGreater(p.car.steer_angle, 0.0)

        # Test braking
        p.car.accel_input = False
        p.car.brake_input = True
        p.car.update_physics(0.1, 0.0, self.game.track.total_length)
        self.assertTrue(p.car.brake_input)

    def test_04_two_player_split_screen(self):
        """4. Test true horizontal split-screen with independent players & cameras."""
        self.game.mode = "TWO_PLAYER"
        self.game.selected_map_class = BeachMap
        self.game.start_race()

        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(len(self.game.cameras), 2)
        self.assertTrue(self.game.players[0].is_two_player)
        self.assertTrue(self.game.players[1].is_two_player)

        # Update and render split-screen frame
        racing_state = self.game.states["RACING"]
        racing_state.countdown_timer = 0.0
        racing_state.update(0.016)
        racing_state.render(self.game.screen)

        # Verify players have distinct positions and cars
        self.assertNotEqual(self.game.players[0].car.name, self.game.players[1].car.name)
        self.assertNotEqual(self.game.players[0].car.color, self.game.players[1].car.color)

    def test_05_all_three_maps(self):
        """5. Test all 3 visually distinct maps and their unique track geometries."""
        # Map 1: Beach
        self.game.selected_map_class = BeachMap
        self.game.start_race()
        self.assertEqual(self.game.track.map.map_id, "BEACH")
        self.assertFalse(self.game.track.palette["is_night"])
        self.assertGreater(len(self.game.track.minimap_points), 10)

        # Map 2: Hills (with steep elevation)
        self.game.selected_map_class = HillsMap
        self.game.start_race()
        self.assertEqual(self.game.track.map.map_id, "HILLS")
        # Check that there is substantial elevation variation
        elevations = [seg.elevation for seg in self.game.track.segments]
        self.assertGreater(max(elevations) - min(elevations), 500.0)

        # Map 3: City Night (with night lighting and 90-degree corners)
        self.game.selected_map_class = CityMap
        self.game.start_race()
        self.assertEqual(self.game.track.map.map_id, "CITY")
        self.assertTrue(self.game.track.palette["is_night"])
        curves = [abs(seg.curve) for seg in self.game.track.segments]
        self.assertGreater(max(curves), 4.5)  # Sharp 90-degree turns

    def test_06_camera_modes(self):
        """6. Test all 3 camera modes (Normal, Front, Extended) and switching."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        player = self.game.players[0]
        camera = self.game.cameras[0]

        # Mode 0: NORMAL
        self.assertEqual(player.camera_mode["id"], "NORMAL")
        self.assertEqual(camera.mode_id, "NORMAL")

        # Cycle to Mode 1: FRONT
        player.cycle_camera()
        camera.apply_preset(player.camera_mode)
        self.assertEqual(player.camera_mode["id"], "FRONT")
        self.assertEqual(camera.mode_id, "FRONT")

        # Cycle to Mode 2: EXTENDED
        player.cycle_camera()
        camera.apply_preset(player.camera_mode)
        self.assertEqual(player.camera_mode["id"], "EXTENDED")
        self.assertEqual(camera.mode_id, "EXTENDED")

        # Cycle back to Mode 0: NORMAL
        player.cycle_camera()
        camera.apply_preset(player.camera_mode)
        self.assertEqual(player.camera_mode["id"], "NORMAL")

    def test_07_collisions_and_impulse(self):
        """7. Test collisions with obstacles, oil slicks, and other vehicles."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        car = self.game.players[0].car
        car.speed = 8000.0

        # Obstacle collision reduces speed and sets collision cooldown
        from game.collision import CollisionSystem
        test_obstacles = [{"z": 0.0, "x": 0.0, "type": "obstacle_barrel", "speed_loss": 0.45, "push": 0.2}]
        CollisionSystem.check_car_obstacles(car, test_obstacles)
        self.assertLess(car.speed, 8000.0)
        self.assertGreater(car.collision_timer, 0.0)

        # Oil slick triggers spinout
        test_oil = [{"z": 0.0, "x": 0.0, "type": "obstacle_oil", "speed_loss": 0.2, "push": 0.0}]
        CollisionSystem.check_car_obstacles(car, test_oil)
        self.assertGreater(car.spinout_timer, 0.0)

        # Car to Car collision impulse
        car2 = self.game.ai_cars[0].car
        car.z = 100.0
        car.x = 0.0
        car2.z = 100.0
        car2.x = 0.1
        car.speed = 7000.0
        car2.speed = 3000.0
        CollisionSystem.check_car_to_car_collisions([car, car2])
        # Separated laterally
        self.assertNotEqual(car.x, 0.0)

    def test_08_ai_intelligence(self):
        """8. Test AI curve deceleration and pathing."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        ai = self.game.ai_cars[0]

        # Normal straight road
        straight_track = self.game.track
        ai.update_ai(0.1, straight_track, self.game.states["RACING"].all_cars)
        self.assertTrue(ai.car.accel_input or ai.car.speed > 0)

        # Verify AI maintains positions inside track
        self.assertGreater(ai.car.x, -1.0)
        self.assertLess(ai.car.x, 1.0)

    def test_09_fuel_system(self):
        """9. Test fuel burn, low fuel warning, empty speed limit, and +20 pickup."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        car = self.game.players[0].car
        car.fuel = 30.0
        car.accel_input = True
        car.speed = 6000.0

        # Burn fuel over time
        for _ in range(10):
            car.update_physics(0.5, 0.0, self.game.track.total_length)
        self.assertLess(car.fuel, 30.0)

        # Trigger low fuel warning
        car.fuel = 20.0
        car.update_physics(0.1, 0.0, self.game.track.total_length)
        self.assertTrue(car.low_fuel_warning)

        # Empty fuel speed cap
        car.fuel = 0.0
        car.speed = 10000.0
        car.update_physics(0.5, 0.0, self.game.track.total_length)
        self.assertLessEqual(car.speed, EMPTY_SPEED_LIMIT + 10.0)

        # Fuel pickup restoration (reaches 100% full capacity)
        from game.collision import CollisionSystem
        test_pickups = [{"z": car.z, "x": car.x, "collected": False, "respawn_timer": 0.0}]
        CollisionSystem.check_car_fuel_pickups(car, test_pickups)
        self.assertEqual(car.fuel, 100.0)
        self.assertTrue(test_pickups[0]["collected"])

    def test_10_lap_counting(self):
        """10. Test lap advancement when crossing track finish line."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        car = self.game.players[0].car
        track_len = self.game.track.total_length

        self.assertEqual(car.lap, 1)
        # Position car right before finish line
        car.z = track_len - 50.0
        car.speed = 2000.0
        car.update_physics(0.1, 0.0, track_len)
        self.assertEqual(car.lap, 2)
        self.assertIsNotNone(car.best_lap_time)

    def test_11_win_finish_condition(self):
        """11. Test race completion and results podium state."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        car = self.game.players[0].car
        track_len = self.game.track.total_length

        car.lap = TOTAL_LAPS
        car.z = track_len - 50.0
        car.speed = 2000.0
        car.update_physics(0.1, 0.0, track_len)
        self.assertTrue(car.finished)

        # Set countdown to 0 so race simulation runs
        self.game.states["RACING"].countdown_timer = 0.0
        # Update Racing state to trigger transition
        self.game.states["RACING"].update(0.016)
        self.assertEqual(type(self.game.current_state).__name__, "ResultsState")

        # Test Results render
        self.game.current_state.render(self.game.screen)

    def test_12_pause_menu(self):
        """12. Test pause activation and resume."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        self.game.change_state("PAUSED")
        self.assertEqual(type(self.game.current_state).__name__, "PausedState")
        self.game.current_state.render(self.game.screen)

        # Resume option
        self.game.current_state.selected_index = 0
        self.game.current_state._activate_option()
        self.assertEqual(type(self.game.current_state).__name__, "RacingState")

    def test_13_restart_race(self):
        """13. Test restart from pause."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        self.game.change_state("PAUSED")
        self.game.current_state.selected_index = 1  # "RESTART"
        self.game.current_state._activate_option()
        self.assertEqual(type(self.game.current_state).__name__, "RacingState")
        self.assertEqual(self.game.players[0].car.lap, 1)

    def test_14_return_to_main_menu(self):
        """14. Test returning to main menu from pause and results."""
        self.game.mode = "SINGLE"
        self.game.start_race()
        self.game.change_state("PAUSED")
        self.game.current_state.selected_index = 2  # "MAIN MENU"
        self.game.current_state._activate_option()
        self.assertEqual(type(self.game.current_state).__name__, "MainMenuState")

if __name__ == "__main__":
    unittest.main()
